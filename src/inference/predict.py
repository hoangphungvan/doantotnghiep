"""
Pipeline dự đoán: đánh giá mức độ phù hợp giữa CV và JD.

Hai engine:
- "req" (mặc định khi có models/req_model.pt): mô hình mức yêu cầu ReqGNN; điểm và diễn giải lấy từ cùng một mô hình.
- "gcn": đồ thị 14 nút + Hybrid (α·GCN + (1−α)·SBERT), diễn giải bằng LLM riêng.
"""

import os
import sys
from typing import Optional

import torch

# Hỗ trợ chạy trực tiếp: python src/inference/predict.py (từ thư mục gốc dự án)
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.extraction.entity_extractor import (extract_entities, extract_from_file, normalize_path,
                                             read_pdf_text, read_text_file, PDF_TEXT_MIN_CHARS)
from src.extraction.pair_features import extract_pair_features, to_vector
from src.representation.embedding_generator import EmbeddingGenerator
from src.representation.graph_builder import build_graph
from src.modeling.model import GCNModel, target_to_grade
import json
from src.evaluation.hybrid import HYBRID_FILE, compute_semantic_scores, hybrid_score
from src.inference.explain import gcn_attribution, match_entities, recruiter_summary, requirement_details, summarize

REQ_MODEL_FILE = os.path.join(config.MODEL_DIR, "req_model.pt")


class CJMPredictor:
    """Predictor cho Candidate-Job Matching."""

    def __init__(self, model_path: str = None,
                 device: Optional[torch.device] = None, engine: str = None):
        """
        Args:
            model_path: Đường dẫn tới file model đã train
            device: CPU hoặc CUDA
            engine: "req" | "gcn"; mặc định "req" nếu có models/req_model.pt
        """
        self.device = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.engine = engine or ("req" if os.path.exists(REQ_MODEL_FILE) else "gcn")
        if self.engine == "req":
            self._init_req(model_path or REQ_MODEL_FILE)
            return

        model_path = model_path or os.path.join(config.MODEL_DIR, "best_model.pt")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Không tìm thấy model tại: {model_path}")

        checkpoint = torch.load(model_path, weights_only=False, map_location=self.device)
        input_dim = checkpoint["input_dim"]

        self.model = GCNModel(input_dim=input_dim).to(self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()

        self.embedding_gen = EmbeddingGenerator()

        if not os.path.exists(HYBRID_FILE):
            raise FileNotFoundError(f"Không tìm thấy {HYBRID_FILE}. Chạy: python src/evaluation/fit_hybrid.py")
        with open(HYBRID_FILE, encoding="utf-8") as f:
            self.hybrid = json.load(f)

        print(f"[Predictor] Model loaded from {model_path}")
        print(f"[Predictor] Trained epoch: {checkpoint.get('epoch', '?')}")
        print(f"[Predictor] Val metrics: {checkpoint.get('val_metrics', {})}")

    def _init_req(self, path: str):
        from src.modeling.req_model import ReqGNN
        from src.representation.req_graph import Embedder
        if not os.path.exists(path):
            raise FileNotFoundError(f"Không tìm thấy {path}. Chạy: python src/modeling/train_req.py final")
        self.ckpt = torch.load(path, weights_only=False, map_location="cpu")
        self.model = ReqGNN(self.ckpt["dims"], **self.ckpt["kw"])
        self.model.load_state_dict(self.ckpt["state"])
        self.model.eval()
        self.emb = Embedder(self.ckpt["emb_model"])   # cùng model embedding lúc huấn luyện
        print(f"[Predictor] ReqGNN ({self.ckpt['config']}, {self.ckpt['emb_model']}), out-of-fold NDCG@10 {self.ckpt['oof_ndcg10']:.3f}")

    @torch.no_grad()
    def _predict_req(self, cv_text: str, jd_text: str) -> dict:
        """Điểm = sigmoid(ReqGNN); mức theo ngưỡng lưu trong checkpoint; diễn giải đọc độ phủ từng yêu cầu của chính mô hình."""
        from torch_geometric.data import Batch
        from src.extraction.requirement_extractor import LEVELS, extract_requirements, save_cache
        from src.representation.req_graph import build_pair_graph
        cv, jd = extract_requirements(cv_text, "CV"), extract_requirements(jd_text, "JD")
        save_cache()
        if not cv["items"] or not jd["items"]:
            raise ValueError("Không trích xuất được yêu cầu JD hoặc mục CV (LLM lỗi / văn bản rỗng)")
        g = Batch.from_data_list([build_pair_graph(cv, jd, self.emb, m_top=self.ckpt["m_top"])])
        score = torch.sigmoid(self.model(g)).item()
        grade = int(sum(score >= t for t in self.ckpt["thresholds"]))
        reqs = requirement_details(self.model, g, cv, jd)
        jl, cl = jd["level"], cv["level"]
        facts = {"requirements": [r for r in reqs if r["required"]], "jd_min_years": jd["total_years"], "cv_years": cv["total_years"],
                 "level_gap": (jl, cl) if jl and cl and LEVELS.index(jl) > LEVELS.index(cl) else None}
        return {
            "engine": "req",
            "score": round(score, 4),
            "grade": grade,
            "grade_label": config.GRADE_LABELS[grade],
            "label": "MATCH" if grade >= config.RELEVANT_GRADE else "NOT MATCH",
            "requirements": reqs,
            "cv_requirements": cv,
            "jd_requirements": jd,
            "explanation": recruiter_summary(grade, facts),
        }

    def predict_from_text(self, cv_text: str, jd_text: str) -> dict:
        """
        Dự đoán từ text thô.

        Returns:
            dict với keys: score, grade, label, explanation (+ chi tiết theo engine)
        """
        if self.engine == "req":
            return self._predict_req(cv_text, jd_text)
        cv_entities = extract_entities(cv_text)
        jd_entities = extract_entities(jd_text)

        return self._predict_from_entities(cv_entities, jd_entities, cv_text, jd_text)

    def predict_from_files(self, cv_path: str, jd_path: str) -> dict:
        """
        Dự đoán từ file CV và JD.
        Tự động chọn text mode hoặc Vision mode tùy loại PDF (Vision chỉ có ở engine "gcn").
        """
        if self.engine == "req":
            cv_text, jd_text = _read_any(cv_path), _read_any(jd_path)
            if not cv_text or not jd_text:
                raise ValueError("Không đọc được văn bản (PDF scan?). Dùng CJMPredictor(engine='gcn') để đọc bằng Vision.")
            return self._predict_req(cv_text, jd_text)
        cv_entities = extract_from_file(cv_path)
        jd_entities = extract_from_file(jd_path)
        return self._predict_from_entities(cv_entities, jd_entities, _read_any(cv_path), _read_any(jd_path))

    def predict_from_entities(self, cv_entities: dict, jd_entities: dict) -> dict:
        """Dự đoán từ entities đã trích xuất sẵn (chỉ engine "gcn")."""
        if self.engine == "req":
            raise ValueError("engine 'req' cần văn bản: dùng predict_from_text")
        return self._predict_from_entities(cv_entities, jd_entities)

    @torch.no_grad()
    def _predict_from_entities(self, cv_entities: dict, jd_entities: dict,
                               cv_text: str = None, jd_text: str = None) -> dict:
        """Core prediction logic. Điểm = Hybrid (α·GCN + (1−α)·SBERT); mức theo ngưỡng hiệu chỉnh; LLM (nếu có cv_text, jd_text) chỉ dùng để diễn giải."""
        cv_main, cv_feats = self.embedding_gen.build_node_features(cv_entities)
        jd_main, jd_feats = self.embedding_gen.build_node_features(jd_entities)

        data = build_graph(cv_main, cv_feats, jd_main, jd_feats)
        data = data.to(self.device)

        logits = self.model(data)
        gcn_score = torch.sigmoid(logits).item()
        sem_score = float(compute_semantic_scores([data])[0])
        score = hybrid_score(gcn_score, sem_score, self.hybrid)
        grade = target_to_grade(score)
        llm = {}
        if cv_text and jd_text:
            llm = extract_pair_features(cv_text, jd_text)
            if not to_vector(llm)["pf_valid"]:
                llm = {}   # LLM lỗi: diễn giải dựa trên đối chiếu thực thể
        match = "MATCH" if grade >= config.RELEVANT_GRADE else "NOT MATCH"

        entity_match = match_entities(cv_entities, jd_entities, self.embedding_gen)
        attribution = gcn_attribution(self.model, data)

        return {
            "score": round(score, 4),
            "gcn_score": round(gcn_score, 4),
            "semantic_score": round(sem_score, 4),
            "llm_requirements": llm.get("requirements", []),
            "llm_conditions": llm.get("conditions", []),
            "grade": grade,
            "grade_label": config.GRADE_LABELS[grade],
            "label": match,
            "cv_entities": cv_entities,
            "jd_entities": jd_entities,
            "explanation": recruiter_summary(grade, llm or None, entity_match),  # ngắn gọn, cho nhà tuyển dụng
            "explanation_detail": summarize(entity_match, attribution),  # kỹ thuật: khớp từng loại thực thể, đóng góp của nút GCN
            "entity_match": entity_match,
            "gcn_attribution": attribution,
        }

    def batch_predict(self, pairs: list[dict]) -> list[dict]:
        """
        Dự đoán hàng loạt.

        Args:
            pairs: List[dict] với keys cv_text/cv_path và jd_text/jd_path
        """
        results = []
        for pair in pairs:
            try:
                if "cv_text" in pair and "jd_text" in pair:
                    result = self.predict_from_text(pair["cv_text"], pair["jd_text"])
                elif "cv_path" in pair and "jd_path" in pair:
                    result = self.predict_from_files(pair["cv_path"], pair["jd_path"])
                else:
                    result = {"error": "Cần cv_text+jd_text hoặc cv_path+jd_path"}
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})

        return results


def _read_any(path: str):
    """Văn bản thô của file CV/JD (hoặc jd_id); None nếu không đọc được (PDF scan) → khi đó dùng GCN đơn."""
    path = normalize_path(path)
    if os.path.exists(path):
        if path.lower().endswith(".pdf"):
            text = read_pdf_text(path)
            return text if len(text) >= PDF_TEXT_MIN_CHARS else None
        return read_text_file(path)
    return None


def predict_interactive():
    """Chế độ dự đoán tương tác qua terminal."""
    print("\n" + "=" * 60)
    print("  CANDIDATE-JOB MATCHING PREDICTOR")
    print("=" * 60)

    try:
        predictor = CJMPredictor()
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("Hãy huấn luyện model trước bằng: python main.py --mode train")
        return

    while True:
        print("\n--- Nhập dữ liệu ---")
        print("1. Nhập text trực tiếp")
        print("2. Chỉ định đường dẫn file")
        print("3. Thoát")

        choice = input("Chọn (1/2/3): ").strip()

        if choice == "1":
            print("\nNhập CV text (kết thúc bằng dòng trống '---'):")
            cv_lines = []
            while True:
                line = input()
                if line.strip() == "---":
                    break
                cv_lines.append(line)
            cv_text = "\n".join(cv_lines)

            print("\nNhập JD text (kết thúc bằng dòng trống '---'):")
            jd_lines = []
            while True:
                line = input()
                if line.strip() == "---":
                    break
                jd_lines.append(line)
            jd_text = "\n".join(jd_lines)

            result = predictor.predict_from_text(cv_text, jd_text)

        elif choice == "2":
            cv_path = normalize_path(input("Đường dẫn file CV: "))
            jd_path = normalize_path(input("Đường dẫn file JD: "))
            result = predictor.predict_from_files(cv_path, jd_path)

        elif choice == "3":
            print("Tạm biệt!")
            break
        else:
            continue

        print("\n" + "=" * 40)
        print(f"  KẾT QUẢ: {result['label']}")
        print(f"  Điểm phù hợp: {result['score']}")
        print(f"  Mức phù hợp: {result['grade']}/3 — {result['grade_label']}")
        print("=" * 40)
        print("\n  Diễn giải (VI):\n" + result["explanation"]["vi"])
        print("\n  Explanation (EN):\n" + result["explanation"]["en"])
        if input("\nXem chi tiết kỹ thuật? (y/N): ").strip().lower() == "y":
            _print_detail(result)

        if "cv_entities" in result:
            print("\n  CV Entities:")
            for k, v in result["cv_entities"].items():
                print(f"    {k}: {v}")
            print("\n  JD Entities:")
            for k, v in result["jd_entities"].items():
                print(f"    {k}: {v}")


def _print_detail(result: dict):
    """Chi tiết kỹ thuật: engine req in độ phủ từng yêu cầu; engine gcn in khớp thực thể + đóng góp nút."""
    if result.get("engine") == "req":
        for r in result["requirements"]:
            tag = "bắt buộc" if r["required"] else "ưu tiên"
            print(f"  [{'x' if r['met'] else ' '}] {r['text']} ({tag}, phủ {r['coverage']:.2f}, trọng số {r['weight']:.2f}) <- {r['best_match']}")
    else:
        print(result["explanation_detail"]["vi"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Du doan CV-JD (text/PDF)")
    parser.add_argument("--cv", type=str, help="Duong dan CV (PDF/TXT)")
    parser.add_argument("--jd", type=str, help="Duong dan JD (PDF/TXT) hoac jd_id (vd jd_0105)")
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--engine", choices=["req", "gcn"], default=None)
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()

    if args.interactive or not (args.cv and args.jd):
        predict_interactive()
    else:
        predictor = CJMPredictor(model_path=args.model, engine=args.engine)
        cv_path = normalize_path(args.cv)
        jd_path = normalize_path(args.jd)
        if os.path.exists(cv_path) and (os.path.exists(jd_path) or jd_path.lower().startswith("jd_")):
            result = predictor.predict_from_files(cv_path, jd_path)
        else:
            parser.error("Can file CV/JD hop le, hoac --jd jd_xxxx")
        print(f"\nKET QUA: {result['label']}")
        print(f"Diem: {result['score']}")
        print(f"Muc: {result['grade']}/3 — {result['grade_label']}")
        print("\n" + result["explanation"]["vi"] + "\n")
        _print_detail(result)

