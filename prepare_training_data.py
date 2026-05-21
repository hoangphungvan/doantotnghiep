"""
Tool thu thập và chuẩn bị dữ liệu training cho CJM model.

Hỗ trợ 2 chế độ nhập liệu:
  --mode text  : Nhập trực tiếp văn bản CV và JD qua terminal
  --mode file  : Chỉ định đường dẫn file PDF/TXT

Dữ liệu đã thu thập được lưu vào:
  data/training_pairs.csv  — bảng cv_path/cv_text, jd_path/jd_text, label
  data/processed/graphs/   — file .pt đồ thị đã build sẵn (tăng tốc training)

Chạy:
  python prepare_training_data.py --mode text
  python prepare_training_data.py --mode file
  python prepare_training_data.py --mode file --csv data/my_pairs.csv
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import torch
from tqdm import tqdm

import config
from entity_extractor import extract_entities, extract_from_file, normalize_path
from embedding_generator import EmbeddingGenerator
from graph_builder import build_graph


TRAINING_CSV = os.path.join(config.DATA_PROCESSED_DIR, "training_pairs.csv")
GRAPH_DIR    = config.GRAPH_DIR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_dirs():
    os.makedirs(GRAPH_DIR, exist_ok=True)
    os.makedirs(config.DATA_PROCESSED_DIR, exist_ok=True)
    os.makedirs(os.path.join(config.DATA_RAW_DIR, "cvs"), exist_ok=True)
    os.makedirs(os.path.join(config.DATA_RAW_DIR, "jds"), exist_ok=True)


def _load_existing_csv() -> list[dict]:
    """Load danh sách cặp đã thu thập trước đó."""
    if not os.path.exists(TRAINING_CSV):
        return []
    with open(TRAINING_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _save_csv(rows: list[dict]):
    """Ghi toàn bộ danh sách cặp vào CSV."""
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(TRAINING_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n[OK] Đã lưu {len(rows)} cặp vào {TRAINING_CSV}")


def _get_label() -> float:
    """Hỏi label từ người dùng: 1 = MATCH, 0 = NOT MATCH."""
    while True:
        ans = input("  Label (1=MATCH / 0=NOT MATCH): ").strip()
        if ans in ("0", "1"):
            return float(ans)
        print("  Chỉ nhập 0 hoặc 1.")


def _read_multiline(prompt: str) -> str:
    """Đọc text nhiều dòng, kết thúc khi gặp dòng trống '---'."""
    print(prompt)
    lines = []
    while True:
        line = input()
        if line.strip() == "---":
            break
        lines.append(line)
    return "\n".join(lines)


def _build_and_save_graph(idx: int, cv_entities: dict, jd_entities: dict,
                           label: float, gen: EmbeddingGenerator) -> str:
    """Build graph, lưu .pt, trả về đường dẫn."""
    cv_main, cv_feats = gen.build_node_features(cv_entities)
    jd_main, jd_feats = gen.build_node_features(jd_entities)
    data = build_graph(cv_main, cv_feats, jd_main, jd_feats, label=label)

    data.cv_entities = json.dumps(cv_entities, ensure_ascii=False)
    data.jd_entities = json.dumps(jd_entities, ensure_ascii=False)

    graph_path = os.path.join(GRAPH_DIR, f"graph_{idx:06d}.pt")
    torch.save(data, graph_path)
    return graph_path


def _show_entities(label: str, entities: dict):
    print(f"\n  [{label} Entities]")
    for k, v in entities.items():
        if v:
            print(f"    {k}: {v}")


# ---------------------------------------------------------------------------
# Mode: text
# ---------------------------------------------------------------------------

def collect_text_mode():
    """Thu thập dữ liệu bằng cách nhập văn bản trực tiếp."""
    _ensure_dirs()
    gen = EmbeddingGenerator()
    rows = _load_existing_csv()
    start_idx = len(rows)

    print("\n" + "=" * 60)
    print("  CHẾ ĐỘ NHẬP TEXT — Thu thập Training Data")
    print("=" * 60)
    print("Nhập văn bản CV và JD, kết thúc mỗi phần bằng dòng '---'")
    print("Nhập 'q' tại bất kỳ bước nào để lưu và thoát.\n")

    session_rows = []
    while True:
        pair_no = start_idx + len(session_rows) + 1
        print(f"\n--- Cặp #{pair_no} ---")

        cv_text = _read_multiline(
            "Nhập nội dung CV (gõ '---' trên dòng riêng để kết thúc):"
        )
        if cv_text.strip().lower() == "q":
            break

        jd_text = _read_multiline(
            "Nhập nội dung JD (gõ '---' trên dòng riêng để kết thúc):"
        )
        if jd_text.strip().lower() == "q":
            break

        label = _get_label()

        print("\n  [INFO] Đang trích xuất thực thể bằng LLM...")
        cv_entities = extract_entities(cv_text)
        jd_entities = extract_entities(jd_text)

        _show_entities("CV", cv_entities)
        _show_entities("JD", jd_entities)

        print("\n  [INFO] Đang build đồ thị...")
        global_idx = start_idx + len(session_rows)
        graph_path = _build_and_save_graph(global_idx, cv_entities, jd_entities, label, gen)

        row = {
            "mode":       "text",
            "cv_source":  f"pair_{pair_no}_cv",
            "jd_source":  f"pair_{pair_no}_jd",
            "label":      int(label),
            "graph_path": graph_path,
        }
        session_rows.append(row)
        print(f"  [OK] Đã lưu đồ thị: {graph_path}")

        cont = input("\nThêm cặp nữa? (y/n): ").strip().lower()
        if cont != "y":
            break

    rows.extend(session_rows)
    _save_csv(rows)
    print(f"\nTổng cộng: {len(rows)} cặp (thêm {len(session_rows)} cặp mới)")
    return rows


# ---------------------------------------------------------------------------
# Mode: file
# ---------------------------------------------------------------------------

def collect_file_mode(csv_path: str = None):
    """
    Thu thập dữ liệu từ file PDF/TXT.

    Nếu csv_path được cung cấp: batch-process toàn bộ CSV có sẵn.
    Nếu không: nhập interactive từng cặp file.
    """
    _ensure_dirs()
    gen = EmbeddingGenerator()

    if csv_path:
        _batch_from_csv(csv_path, gen)
        return

    rows = _load_existing_csv()
    start_idx = len(rows)

    print("\n" + "=" * 60)
    print("  CHẾ ĐỘ FILE — Thu thập Training Data")
    print("=" * 60)
    print("Hỗ trợ: PDF (text layer & scan), TXT")
    print("Kéo thả file vào terminal hoặc nhập đường dẫn đầy đủ.\n")

    session_rows = []
    while True:
        pair_no = start_idx + len(session_rows) + 1
        print(f"\n--- Cặp #{pair_no} ---")

        cv_path = normalize_path(input("  Đường dẫn file CV (PDF/TXT): "))
        if cv_path.lower() == "q":
            break
        if not os.path.exists(cv_path):
            print(f"  [ERROR] File không tồn tại: {cv_path}")
            continue

        jd_path = normalize_path(input("  Đường dẫn file JD (PDF/TXT): "))
        if jd_path.lower() == "q":
            break
        if not os.path.exists(jd_path):
            print(f"  [ERROR] File không tồn tại: {jd_path}")
            continue

        label = _get_label()

        print("\n  [INFO] Đang trích xuất thực thể bằng LLM...")
        cv_entities = extract_from_file(cv_path)
        jd_entities = extract_from_file(jd_path)

        _show_entities("CV", cv_entities)
        _show_entities("JD", jd_entities)

        print("\n  [INFO] Đang build đồ thị...")
        global_idx = start_idx + len(session_rows)
        graph_path = _build_and_save_graph(global_idx, cv_entities, jd_entities, label, gen)

        row = {
            "mode":       "file",
            "cv_source":  cv_path,
            "jd_source":  jd_path,
            "label":      int(label),
            "graph_path": graph_path,
        }
        session_rows.append(row)
        print(f"  [OK] Đã lưu đồ thị: {graph_path}")

        cont = input("\nThêm cặp nữa? (y/n): ").strip().lower()
        if cont != "y":
            break

    rows.extend(session_rows)
    _save_csv(rows)
    print(f"\nTổng cộng: {len(rows)} cặp (thêm {len(session_rows)} cặp mới)")
    return rows


def _batch_from_csv(csv_path: str, gen: EmbeddingGenerator):
    """
    Batch process: đọc CSV có cột cv_path, jd_path, label
    → trích xuất entities → build graph → lưu vào GRAPH_DIR.
    """
    import pandas as pd

    df = pd.read_csv(csv_path)
    required = {"cv_path", "jd_path", "label"}
    if not required.issubset(df.columns):
        print(f"[ERROR] CSV cần có cột: {required}. Hiện có: {set(df.columns)}")
        return

    rows = _load_existing_csv()
    start_idx = len(rows)
    new_rows = []

    print(f"\n[INFO] Batch processing {len(df)} cặp từ {csv_path}...\n")

    for idx, row_data in tqdm(df.iterrows(), total=len(df), desc="Processing"):
        cv_path = normalize_path(str(row_data["cv_path"]))
        jd_path = normalize_path(str(row_data["jd_path"]))
        label   = float(row_data["label"])

        if not os.path.exists(cv_path):
            print(f"[SKIP] CV không tồn tại: {cv_path}")
            continue
        if not os.path.exists(jd_path):
            print(f"[SKIP] JD không tồn tại: {jd_path}")
            continue

        try:
            cv_entities = extract_from_file(cv_path)
            jd_entities = extract_from_file(jd_path)
            global_idx  = start_idx + len(new_rows)
            graph_path  = _build_and_save_graph(global_idx, cv_entities, jd_entities, label, gen)
            new_rows.append({
                "mode":       "file",
                "cv_source":  cv_path,
                "jd_source":  jd_path,
                "label":      int(label),
                "graph_path": graph_path,
            })
        except Exception as e:
            print(f"[ERROR] Cặp {idx}: {e}")

    rows.extend(new_rows)
    _save_csv(rows)
    print(f"\n[OK] Đã xử lý {len(new_rows)}/{len(df)} cặp thành công.")


# ---------------------------------------------------------------------------
# Load prepared graphs for training
# ---------------------------------------------------------------------------

def load_all_graphs() -> list:
    """Load toàn bộ đồ thị đã build từ GRAPH_DIR."""
    files = sorted(Path(GRAPH_DIR).glob("graph_*.pt"))
    graphs = []
    for f in files:
        try:
            graphs.append(torch.load(str(f), weights_only=False))
        except Exception as e:
            print(f"[WARN] Không load được {f}: {e}")
    print(f"[INFO] Loaded {len(graphs)} graphs từ {GRAPH_DIR}")
    return graphs


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Thu thập Training Data cho CJM")
    parser.add_argument(
        "--mode", choices=["text", "file"], default="file",
        help="text: nhập trực tiếp  |  file: chỉ định đường dẫn PDF/TXT",
    )
    parser.add_argument(
        "--csv", type=str, default=None,
        help="(Chỉ mode=file) CSV có cột cv_path,jd_path,label để batch process",
    )
    args = parser.parse_args()

    if args.mode == "text":
        collect_text_mode()
    else:
        collect_file_mode(csv_path=args.csv)
