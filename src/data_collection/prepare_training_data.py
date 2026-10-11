"""
Dựng bộ dữ liệu đồ thị cho GCN từ dữ liệu đã gán nhãn.

Nguồn:
  data/raw/judgments/claude_b*.csv — nhãn (cv_id, jd_id, grade 0-3)
  data/raw/cvs_synth/<cv_id>.txt   — CV tổng hợp
  data/raw/selected_jds.csv        — JD thật; dùng cột jd_brief (đúng văn bản người chấm đã đọc)

Mỗi CV và mỗi JD chỉ gọi LLM trích xuất thực thể một lần (có cache), sau đó ghép
từng cặp thành một đồ thị 14 nút. Kết quả:
  data/processed/graphs/graph_*.pt     — mỗi cặp một đồ thị (y = grade, cv_source = cv_id)
  data/processed/dataset_manifest.csv  — idx, cv_id, jd_id, grade, graph_path

Chạy:
  python main.py --mode prepare
  python src/data_collection/prepare_training_data.py --limit-cvs 3   # chạy thử
"""

import argparse
import glob
import json
import os
import sys
from pathlib import Path

import pandas as pd
import torch
from tqdm import tqdm

# Hỗ trợ chạy trực tiếp: python src/data_collection/prepare_training_data.py
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.extraction.entity_extractor import extract_entities
from src.representation.embedding_generator import EmbeddingGenerator
from src.representation.graph_builder import build_graph

GRAPH_DIR = config.GRAPH_DIR
MANIFEST_CSV = os.path.join(config.DATA_PROCESSED_DIR, "dataset_manifest.csv")
JUDGMENTS_GLOB = os.path.join(config.DATA_RAW_DIR, "judgments", "claude_b*.csv")
CV_DIR = os.path.join(config.DATA_RAW_DIR, "cvs_synth")
JD_CSV = os.path.join(config.DATA_RAW_DIR, "selected_jds.csv")


def load_pairs() -> pd.DataFrame:
    """Gộp các file nhãn thành bảng (cv_id, jd_id, grade); báo lỗi nếu trùng cặp hoặc nhãn ngoài thang."""
    files = sorted(glob.glob(JUDGMENTS_GLOB))
    if not files:
        raise FileNotFoundError(f"Không có file nhãn: {JUDGMENTS_GLOB}")
    df = pd.concat([pd.read_csv(f, usecols=["cv_id", "jd_id", "grade"]) for f in files], ignore_index=True)
    if df.duplicated(["cv_id", "jd_id"]).any():
        raise ValueError("Có cặp (cv_id, jd_id) bị gán nhãn nhiều lần")
    if not df.grade.between(0, config.NUM_GRADES).all():
        raise ValueError(f"Có nhãn ngoài thang 0..{config.NUM_GRADES}")
    return df.sort_values(["cv_id", "jd_id"]).reset_index(drop=True)


def _read_cv(cv_id: str) -> str:
    return Path(glob.glob(os.path.join(CV_DIR, f"{cv_id}.*"))[0]).read_text(encoding="utf-8")


def _extract(texts: dict, label: str) -> dict:
    """Trích xuất thực thể cho từng id; id nào LLM trả rỗng thì bị loại (không đưa đồ thị rác vào dữ liệu)."""
    out, failed = {}, []
    for key, text in tqdm(texts.items(), desc=f"Trích xuất {label}"):
        ents = extract_entities(text)
        if any(ents.get(t) for t in config.ENTITY_TYPES):
            out[key] = ents
        else:
            failed.append(key)
    if failed:
        print(f"[WARN] {len(failed)} {label} không trích xuất được, bỏ qua: {failed}")
    return out


def build_dataset(limit_cvs: int = None) -> pd.DataFrame:
    pairs = load_pairs()
    if limit_cvs:
        pairs = pairs[pairs.cv_id.isin(sorted(pairs.cv_id.unique())[:limit_cvs])]
    jds = pd.read_csv(JD_CSV).set_index("jd_id").jd_brief

    cv_ents = _extract({c: _read_cv(c) for c in pairs.cv_id.unique()}, "CV")
    jd_ents = _extract({j: jds[j] for j in pairs.jd_id.unique()}, "JD")
    pairs = pairs[pairs.cv_id.isin(cv_ents) & pairs.jd_id.isin(jd_ents)].reset_index(drop=True)

    gen = EmbeddingGenerator()
    cv_feats = {c: gen.build_node_features(e) for c, e in cv_ents.items()}
    jd_feats = {j: gen.build_node_features(e) for j, e in jd_ents.items()}

    os.makedirs(GRAPH_DIR, exist_ok=True)
    for old in Path(GRAPH_DIR).glob("graph_*.pt"):
        old.unlink()  # tránh lẫn đồ thị của lần dựng trước

    paths = []
    for i, r in tqdm(pairs.iterrows(), total=len(pairs), desc="Dựng đồ thị"):
        data = build_graph(*cv_feats[r.cv_id], *jd_feats[r.jd_id], label=float(r.grade))
        data.cv_source, data.jd_source = r.cv_id, r.jd_id
        data.cv_entities = json.dumps(cv_ents[r.cv_id], ensure_ascii=False)
        data.jd_entities = json.dumps(jd_ents[r.jd_id], ensure_ascii=False)
        path = os.path.join(GRAPH_DIR, f"graph_{i:06d}.pt")
        torch.save(data, path)
        paths.append(path)

    pairs["graph_path"] = paths
    pairs.rename_axis("idx").to_csv(MANIFEST_CSV, encoding="utf-8")
    print(f"[OK] {len(pairs)} đồ thị, {pairs.cv_id.nunique()} CV, {pairs.jd_id.nunique()} JD → {MANIFEST_CSV}")
    print(f"     Phân bố nhãn: {pairs.grade.value_counts().sort_index().to_dict()}")
    return pairs


def load_all_graphs() -> list:
    """Load toàn bộ đồ thị đã build từ GRAPH_DIR."""
    graphs = [torch.load(str(f), weights_only=False) for f in sorted(Path(GRAPH_DIR).glob("graph_*.pt"))]
    print(f"[INFO] Loaded {len(graphs)} graphs từ {GRAPH_DIR}")
    return graphs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dựng đồ thị huấn luyện từ dữ liệu đã gán nhãn")
    parser.add_argument("--limit-cvs", type=int, default=None, help="Chỉ dùng N CV đầu (chạy thử)")
    build_dataset(parser.parse_args().limit_cvs)
