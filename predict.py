"""
Pipeline dự đoán: đánh giá mức độ phù hợp giữa CV và JD.
"""

import os
import json
from typing import Optional

import torch
from torch_geometric.data import Data

import config
from entity_extractor import extract_entities, read_document
from embedding_generator import EmbeddingGenerator
from graph_builder import build_graph
from model import GCNModel


class CJMPredictor:
    """Predictor cho Candidate-Job Matching."""

    def __init__(self, model_path: str = None,
                 device: Optional[torch.device] = None):
        """
        Args:
            model_path: Đường dẫn tới file model đã train
            device: CPU hoặc CUDA
        """
        self.device = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        model_path = model_path or os.path.join(config.MODEL_DIR, "best_model.pt")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Không tìm thấy model tại: {model_path}")

        checkpoint = torch.load(model_path, weights_only=False, map_location=self.device)
        input_dim = checkpoint["input_dim"]

        self.model = GCNModel(input_dim=input_dim).to(self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()

        self.embedding_gen = EmbeddingGenerator()

        print(f"[Predictor] Model loaded from {model_path}")
        print(f"[Predictor] Trained epoch: {checkpoint.get('epoch', '?')}")
        print(f"[Predictor] Val metrics: {checkpoint.get('val_metrics', {})}")

    def predict_from_text(self, cv_text: str, jd_text: str) -> dict:
        """
        Dự đoán từ text thô.

        Returns:
            dict với keys: score, label, cv_entities, jd_entities
        """
        cv_entities = extract_entities(cv_text)
        jd_entities = extract_entities(jd_text)

        return self._predict_from_entities(cv_entities, jd_entities)

    def predict_from_files(self, cv_path: str, jd_path: str) -> dict:
        """Dự đoán từ file CV và JD."""
        cv_text = read_document(cv_path)
        jd_text = read_document(jd_path)
        return self.predict_from_text(cv_text, jd_text)

    def predict_from_entities(self, cv_entities: dict, jd_entities: dict) -> dict:
        """Dự đoán từ entities đã trích xuất sẵn."""
        return self._predict_from_entities(cv_entities, jd_entities)

    @torch.no_grad()
    def _predict_from_entities(self, cv_entities: dict, jd_entities: dict) -> dict:
        """Core prediction logic."""
        cv_main, cv_feats = self.embedding_gen.build_node_features(cv_entities)
        jd_main, jd_feats = self.embedding_gen.build_node_features(jd_entities)

        data = build_graph(cv_main, cv_feats, jd_main, jd_feats)
        data = data.to(self.device)

        logits = self.model(data)
        score = torch.sigmoid(logits).item()
        label = "MATCH" if score >= 0.5 else "NOT MATCH"

        return {
            "score": round(score, 4),
            "label": label,
            "cv_entities": cv_entities,
            "jd_entities": jd_entities,
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
            cv_path = input("Đường dẫn file CV: ").strip()
            jd_path = input("Đường dẫn file JD: ").strip()
            result = predictor.predict_from_files(cv_path, jd_path)

        elif choice == "3":
            print("Tạm biệt!")
            break
        else:
            continue

        print("\n" + "=" * 40)
        print(f"  KẾT QUẢ: {result['label']}")
        print(f"  Điểm phù hợp: {result['score']}")
        print("=" * 40)

        if "cv_entities" in result:
            print("\n  CV Entities:")
            for k, v in result["cv_entities"].items():
                print(f"    {k}: {v}")
            print("\n  JD Entities:")
            for k, v in result["jd_entities"].items():
                print(f"    {k}: {v}")


if __name__ == "__main__":
    predict_interactive()
