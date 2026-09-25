"""
Pipeline đánh giá ranking: so sánh 4 phương pháp trên ground truth.

Dữ liệu nhẹ (mặc định):
    data/raw/pairs_it.csv              — 60 cặp, nhãn 0-3
    data/raw/cvs/cv_*.txt              — CV text
    data/processed/representative_jds.csv + entity_cache — JD text
    data/processed/training_pairs.csv  — map tới graph_*.pt (GCN)
    models/best_model.pt               — checkpoint GCN

Không đọc VietJobs.csv (nặng). Không đọc VietJobs_cntt.csv trừ khi
truyền --use-vietjobs-it.

Chạy:
    python src/evaluation/ranking_eval.py
    python src/evaluation/ranking_eval.py --query-axis jd
    python src/evaluation/ranking_eval.py --gcn-csv data/processed/gcn_predictions.csv
    python src/evaluation/ranking_eval.py --alpha 0.6
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Optional

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.evaluation.metrics import evaluate_ranking

REPORT_KS = [1, 5, 10]
PAIRS_CSV_DEFAULT = os.path.join(config.DATA_RAW_DIR, "pairs_it.csv")
TRAINING_CSV = os.path.join(config.DATA_PROCESSED_DIR, "training_pairs.csv")
GCN_PRED_CSV = os.path.join(config.DATA_PROCESSED_DIR, "gcn_predictions.csv")
RESULT_CSV = os.path.join(config.DATA_PROCESSED_DIR, "ranking_eval_results.csv")
RESULT_MD = os.path.join(config.DATA_PROCESSED_DIR, "ranking_eval_results.md")


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

def _norm_jd_id(value: str) -> str:
    match = re.search(r"jd_(\d+)", str(value).replace("\\", "/"), re.I)
    if match:
        return f"jd_{int(match.group(1)):04d}"
    return str(value).strip()


def _cv_basename(path: str) -> str:
    return Path(str(path).replace("\\", "/")).name


def resolve_cv_path(raw_path: str) -> Optional[str]:
    """Map đường dẫn cũ (D:\\doantotnghiep\\...) sang data/raw/cvs trên máy này."""
    if not raw_path or not str(raw_path).strip():
        return None
    name = _cv_basename(raw_path)
    if not name:
        return None
    local = os.path.join(config.DATA_RAW_DIR, "cvs", name)
    if os.path.isfile(local):
        return local
    if os.path.isfile(raw_path):
        return raw_path
    return None



def load_entity_cache() -> dict:
    path = config.ENTITY_CACHE_FILE
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _entities_to_text(entities: dict) -> str:
    if not isinstance(entities, dict):
        return ""
    parts = []
    for etype in config.ENTITY_TYPES:
        items = entities.get(etype) or []
        parts.extend(str(x) for x in items)
    return " ".join(parts)


def load_jd_text_map(use_vietjobs_it: bool = False) -> dict[str, str]:
    """
    JD text theo jd_id, ưu tiên nguồn nhẹ:
    1) representative_jds.csv (title + skills)
    2) entity_cache.json keyed by jd_xxxx
    3) (tuỳ chọn) VietJobs_cntt.csv — không dùng mặc định
    """
    texts: dict[str, str] = {}

    rep_path = os.path.join(config.DATA_PROCESSED_DIR, "representative_jds.csv")
    if os.path.exists(rep_path):
        import pandas as pd
        df = pd.read_csv(rep_path)
        for _, row in df.iterrows():
            jid = _norm_jd_id(str(row.get("jd_id", row.get("file_path", ""))))
            chunks = [
                str(row.get("job_title", "")),
                str(row.get("cluster_name", "")),
                str(row.get("hard_skills", "")),
                str(row.get("soft_skills", "")),
            ]
            texts[jid] = " ".join(c for c in chunks if c and c != "nan")

    cache = load_entity_cache()
    for key, val in cache.items():
        if not str(key).startswith("jd_"):
            continue
        jid = _norm_jd_id(key)
        extra = _entities_to_text(val)
        if extra:
            texts[jid] = (texts.get(jid, "") + " " + extra).strip()

    if use_vietjobs_it:
        from src.extraction.entity_extractor import get_jd_text_by_id
        for jid in list(texts.keys()):
            full = get_jd_text_by_id(jid)
            if full:
                texts[jid] = full

    return texts


def load_ground_truth(pairs_csv: str = None) -> list[dict]:
    """Load pairs_it.csv, resolve CV path local, chuẩn hoá jd_id + label."""
    pairs_csv = pairs_csv or PAIRS_CSV_DEFAULT
    if not os.path.exists(pairs_csv):
        raise FileNotFoundError(f"Không thấy ground truth: {pairs_csv}")

    rows = []
    with open(pairs_csv, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, raw in enumerate(reader):
            cv_raw = raw.get("cv_path") or raw.get("cv_source") or ""
            jd_raw = raw.get("jd_path") or raw.get("jd_source") or ""
            cv_path = resolve_cv_path(cv_raw)
            if cv_path is None:
                print(f"[WARN] Bỏ cặp {i}: không tìm thấy CV {cv_raw}")
                continue
            rows.append({
                "pair_index": i,
                "cv_id": _cv_basename(cv_path),
                "cv_path": cv_path,
                "jd_id": _norm_jd_id(jd_raw),
                "label": float(raw.get("label", 0)),
                "note": raw.get("note", ""),
            })
    return rows


def attach_texts(rows: list[dict], jd_texts: dict[str, str]) -> list[dict]:
    out = []
    for r in rows:
        cv_text = Path(r["cv_path"]).read_text(encoding="utf-8", errors="ignore")
        jd_text = jd_texts.get(r["jd_id"], "")
        if not jd_text:
            print(f"[WARN] Thiếu JD text cho {r['jd_id']} — dùng chuỗi rỗng.")
        item = dict(r)
        item["cv_text"] = cv_text
        item["jd_text"] = jd_text
        out.append(item)
    return out


# ---------------------------------------------------------------------------
# Model inference
# ---------------------------------------------------------------------------

def tfidf_scores(rows: list[dict]) -> np.ndarray:
    cv_texts = [r["cv_text"] for r in rows]
    jd_texts = [r["jd_text"] for r in rows]
    vectorizer = TfidfVectorizer(min_df=1)
    matrix = vectorizer.fit_transform(cv_texts + jd_texts)
    n = len(rows)
    cv_vecs, jd_vecs = matrix[:n], matrix[n:]
    return np.array(
        [cosine_similarity(cv_vecs[i], jd_vecs[i])[0, 0] for i in range(n)],
        dtype=float,
    )


def sbert_scores(rows: list[dict], model_name: str = None) -> np.ndarray:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity as sk_cos

    model_name = model_name or config.EMBEDDING_MODEL_NAME
    print(f"[SBERT] Encode {len(rows)} cặp bằng {model_name}...")
    model = SentenceTransformer(model_name)
    cv_emb = model.encode([r["cv_text"] for r in rows], convert_to_numpy=True, show_progress_bar=False)
    jd_emb = model.encode([r["jd_text"] for r in rows], convert_to_numpy=True, show_progress_bar=False)
    scores = [float(sk_cos(cv_emb[i:i + 1], jd_emb[i:i + 1])[0, 0]) for i in range(len(rows))]
    return np.array(scores, dtype=float)


def load_gcn_from_csv(path: str, rows: list[dict]) -> Optional[np.ndarray]:
    if not os.path.exists(path):
        return None
    lookup = {}
    with open(path, newline="", encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            key = (_cv_basename(rec.get("cv_id") or rec.get("cv_path") or ""),
                   _norm_jd_id(rec.get("jd_id") or rec.get("jd_path") or ""))
            lookup[key] = float(rec["score"])
    scores = []
    missing = 0
    for r in rows:
        s = lookup.get((r["cv_id"], r["jd_id"]))
        if s is None:
            missing += 1
            scores.append(0.0)
        else:
            scores.append(s)
    if missing:
        print(f"[WARN] gcn_predictions.csv thiếu {missing}/{len(rows)} cặp → gán 0.")
    return np.array(scores, dtype=float)


def load_eval_graphs() -> list:
    """Chỉ load graph được liệt kê trong training_pairs.csv (60 cặp), không load 500 file synthetic."""
    import torch

    if not os.path.exists(TRAINING_CSV):
        return []
    graphs = []
    with open(TRAINING_CSV, newline="", encoding="utf-8-sig") as f:
        for idx, rec in enumerate(csv.DictReader(f)):
            gpath = rec.get("graph_path", "")
            candidates = [
                gpath,
                os.path.join(config.GRAPH_DIR, Path(gpath).name) if gpath else "",
                os.path.join(config.GRAPH_DIR, f"graph_{idx:06d}.pt"),
            ]
            resolved = next((p for p in candidates if p and os.path.isfile(p)), None)
            if not resolved:
                print(f"[WARN] Khong thay graph cho cap {idx}")
                continue
            try:
                g = torch.load(resolved, weights_only=False)
                g._cv_id = _cv_basename(rec.get("cv_source", ""))
                g._jd_id = _norm_jd_id(rec.get("jd_source", ""))
                graphs.append(g)
            except Exception as e:
                print(f"[WARN] Khong load {resolved}: {e}")
    return graphs


def gcn_scores_from_model(rows: list[dict], model_path: str = None) -> Optional[np.ndarray]:
    import torch
    from src.modeling.model import GCNModel
    from src.evaluation.hybrid import compute_graph_scores

    graphs = load_eval_graphs()
    if not graphs:
        print("[WARN] Không có graph .pt khớp training_pairs.csv.")
        return None

    graph_index = {(g._cv_id, g._jd_id): g for g in graphs}
    ordered = []
    missing = []
    for r in rows:
        g = graph_index.get((r["cv_id"], r["jd_id"]))
        if g is None:
            missing.append((r["cv_id"], r["jd_id"]))
        else:
            ordered.append(g)
    if missing:
        print(f"[WARN] Thiếu graph cho {len(missing)} cặp. GCN sẽ bỏ qua nếu không đủ.")
        if len(ordered) != len(rows):
            return None

    model_path = model_path or os.path.join(config.MODEL_DIR, "best_model.pt")
    if not os.path.exists(model_path):
        print(f"[WARN] Chưa có model: {model_path}")
        return None

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt = torch.load(model_path, weights_only=False, map_location=device)
    model = GCNModel(input_dim=ckpt["input_dim"]).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    print(f"[GCN] Loaded {model_path} (epoch={ckpt.get('epoch', '?')}) trên {len(ordered)} graphs")
    return compute_graph_scores(model, ordered, device)


def save_gcn_predictions(rows: list[dict], scores: np.ndarray, path: str = None):
    path = path or GCN_PRED_CSV
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["cv_id", "jd_id", "label", "score"])
        writer.writeheader()
        for r, s in zip(rows, scores):
            writer.writerow({
                "cv_id": r["cv_id"],
                "jd_id": r["jd_id"],
                "label": int(r["label"]),
                "score": f"{float(s):.6f}",
            })
    print(f"[OK] Ghi {path}")


def hybrid_scores(gcn: np.ndarray, sbert: np.ndarray, alpha: float) -> np.ndarray:
    lo, hi = float(sbert.min()), float(sbert.max())
    if hi - lo < 1e-9:
        sbert_n = np.zeros_like(sbert)
    else:
        sbert_n = np.clip((sbert - lo) / (hi - lo), 0.0, 1.0)
    return alpha * gcn + (1.0 - alpha) * sbert_n


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def build_groups(rows: list[dict], scores: np.ndarray, query_axis: str) -> dict:
    groups = {}
    for r, s in zip(rows, scores):
        qid = r["jd_id"] if query_axis == "jd" else r["cv_id"]
        groups.setdefault(qid, []).append((r["label"], float(s)))
    return groups


def tune_alpha(rows, gcn, sbert, query_axis: str) -> float:
    best_a, best = 0.5, -1.0
    for a in np.linspace(0.0, 1.0, 21):
        blended = hybrid_scores(gcn, sbert, float(a))
        m = evaluate_ranking(build_groups(rows, blended, query_axis), ks=REPORT_KS)
        target = m.get("ndcg@5") or m.get("ndcg@1") or 0.0
        if target > best:
            best, best_a = target, float(a)
    return best_a


def fmt4(v) -> str:
    return f"{v:.4f}" if v is not None else "—"


def markdown_table(results: OrderedDict) -> str:
    lines = [
        "| Method | NDCG@1 | NDCG@5 | NDCG@10 | Recall@5 | Recall@10 | MRR |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, m in results.items():
        lines.append(
            f"| {name} | {fmt4(m.get('ndcg@1'))} | {fmt4(m.get('ndcg@5'))} | "
            f"{fmt4(m.get('ndcg@10'))} | {fmt4(m.get('recall@5'))} | "
            f"{fmt4(m.get('recall@10'))} | {fmt4(m.get('mrr'))} |"
        )
    return "\n".join(lines)


def save_results(results: OrderedDict, path_csv: str, path_md: str):
    os.makedirs(os.path.dirname(path_csv), exist_ok=True)
    fieldnames = ["Method", "NDCG@1", "NDCG@5", "NDCG@10", "Recall@5", "Recall@10", "MRR"]
    with open(path_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for name, m in results.items():
            writer.writerow({
                "Method": name,
                "NDCG@1": fmt4(m.get("ndcg@1")),
                "NDCG@5": fmt4(m.get("ndcg@5")),
                "NDCG@10": fmt4(m.get("ndcg@10")),
                "Recall@5": fmt4(m.get("recall@5")),
                "Recall@10": fmt4(m.get("recall@10")),
                "MRR": fmt4(m.get("mrr")),
            })
    md = markdown_table(results)
    with open(path_md, "w", encoding="utf-8") as f:
        f.write(md + "\n")
    print(f"[OK] {path_csv}")
    print(f"[OK] {path_md}")


def run_eval(pairs_csv: str = None, query_axis: str = "cv",
             alpha: str = "auto", gcn_csv: str = None,
             model_path: str = None, use_vietjobs_it: bool = False) -> OrderedDict:
    print("=" * 60)
    print("  RANKING EVALUATION PIPELINE")
    print("=" * 60)

    rows = load_ground_truth(pairs_csv)
    jd_texts = load_jd_text_map(use_vietjobs_it=use_vietjobs_it)
    rows = attach_texts(rows, jd_texts)
    print(f"[Data] {len(rows)} cặp | {len({r['cv_id'] for r in rows})} CV | "
          f"{len({r['jd_id'] for r in rows})} JD | query_axis={query_axis}")

    tfidf = tfidf_scores(rows)
    sbert = sbert_scores(rows)

    gcn = None
    if gcn_csv and os.path.exists(gcn_csv):
        print(f"[GCN] Nạp scores từ: {gcn_csv}")
        gcn = load_gcn_from_csv(gcn_csv, rows)
    elif os.path.exists(GCN_PRED_CSV):
        print(f"[GCN] Nạp scores từ file dự đoán có sẵn: {GCN_PRED_CSV}")
        gcn = load_gcn_from_csv(GCN_PRED_CSV, rows)

    if gcn is None:
        gcn = gcn_scores_from_model(rows, model_path=model_path)
        if gcn is not None:
            save_gcn_predictions(rows, gcn)

    results = OrderedDict()
    results["TF-IDF + cosine"] = evaluate_ranking(build_groups(rows, tfidf, query_axis), ks=REPORT_KS)
    results["SBERT + cosine"] = evaluate_ranking(build_groups(rows, sbert, query_axis), ks=REPORT_KS)

    if gcn is None:
        print("[GCN] Bỏ qua. Tạo file dự đoán rồi chạy lại:")
        print("      python src/evaluation/ranking_eval.py --gcn-csv data/processed/gcn_predictions.csv")
        print("      Cột bắt buộc: cv_id,jd_id,score")
        placeholder = evaluate_ranking(build_groups(rows, np.zeros(len(rows)), query_axis), ks=REPORT_KS)
        results["GCN graph only"] = placeholder
        results["Hybrid"] = placeholder
    else:
        results["GCN graph only"] = evaluate_ranking(build_groups(rows, gcn, query_axis), ks=REPORT_KS)
        a = tune_alpha(rows, gcn, sbert, query_axis) if alpha == "auto" else float(alpha)
        print(f"[Hybrid] alpha = {a:.2f}" + (" (tune NDCG@5)" if alpha == "auto" else " (cố định)"))
        blended = hybrid_scores(gcn, sbert, a)
        results["Hybrid"] = evaluate_ranking(build_groups(rows, blended, query_axis), ks=REPORT_KS)

    table = markdown_table(results)
    print("\n" + table + "\n")
    save_results(results, RESULT_CSV, RESULT_MD)
    return results


def main():
    parser = argparse.ArgumentParser(description="Đánh giá ranking 4 phương pháp trên pairs_it.csv")
    parser.add_argument("--pairs", default=PAIRS_CSV_DEFAULT)
    parser.add_argument("--query-axis", choices=["cv", "jd"], default="cv",
                        help="cv: mỗi CV xếp JD (mặc định, 5 JD/query). "
                             "jd: mỗi JD xếp CV (đúng mô hình tuyển dụng).")
    parser.add_argument("--alpha", default="auto")
    parser.add_argument("--gcn-csv", default=None,
                        help="File gcn_predictions.csv (cv_id,jd_id,score) nếu không chạy GCN")
    parser.add_argument("--model", default=None)
    parser.add_argument("--use-vietjobs-it", action="store_true",
                        help="Nạp formatted_jd_text từ VietJobs_cntt.csv (nặng hơn)")
    args = parser.parse_args()
    run_eval(
        pairs_csv=args.pairs,
        query_axis=args.query_axis,
        alpha=args.alpha,
        gcn_csv=args.gcn_csv,
        model_path=args.model,
        use_vietjobs_it=args.use_vietjobs_it,
    )


if __name__ == "__main__":
    main()
