"""
Demo cho hội đồng: chấm 4 cặp CV-JD mới (không nằm trong dữ liệu huấn luyện).

JD lấy từ 4 JD thật chưa từng được dùng khi gán nhãn; CV viết mới. Mức "kỳ vọng" trong pairs.csv được xác định
theo rubric v1.2 TRƯỚC khi chạy mô hình.

Chạy từ thư mục gốc dự án:  python -X utf8 demo/run_demo.py          (in kết quả)
                            python -X utf8 demo/run_demo.py --save   (ghi thêm demo/results.md)
Lần đầu cần mạng + khóa LLM trong .env để trích xuất thực thể; kết quả được cache nên các lần sau chạy offline.
"""

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import config
from src.inference.predict import CJMPredictor

pairs = pd.read_csv(os.path.join(HERE, "pairs.csv"))
predictor = CJMPredictor()
read = lambda name: open(os.path.join(HERE, name), encoding="utf-8").read()

rows, blocks = [], []
for r in pairs.itertuples():
    res = predictor.predict_from_text(read(r.cv_file), read(r.jd_file))
    rows.append((r.pair_id, r.cv_file, r.jd_file, r.expected_grade, res["grade"], res["score"], res["grade_label"]))
    blocks.append((r, res))

print("\n" + "=" * 78)
print(f"{'Cặp':<4} {'Kỳ vọng (rubric)':<17} {'Mô hình':<9} {'Điểm':<7} Nhãn mô hình")
for p, _, _, exp, got, score, label in rows:
    print(f"{p:<4} {exp:<17} {got:<9} {score:<7} {label}  {'✓' if exp == got else ('≈' if abs(exp - got) == 1 else '✗')}")
hits = sum(e == g for _, _, _, e, g, _, _ in rows)
print(f"\nĐúng mức: {hits}/{len(rows)}; lệch tối đa 1 mức: {sum(abs(e - g) <= 1 for _, _, _, e, g, _, _ in rows)}/{len(rows)}")

for r, res in blocks:
    print("\n" + "-" * 78)
    print(f"{r.pair_id}: {r.cv_file} ↔ {r.jd_file} | kỳ vọng {r.expected_grade}, mô hình {res['grade']} ({res['score']})")
    if res["mode"] == "stacker":
        unmet = [q["text"] for q in res["llm_requirements"] if not q.get("met")]
        met = [q["text"] for q in res["llm_requirements"] if q.get("met")]
        print(f"[Mô hình: GCN + LLM đọc trực tiếp] điểm GCN {res['gcn_score']}")
        print("Yêu cầu bắt buộc CV đáp ứng:", "; ".join(met) or "không có")
        print("Yêu cầu bắt buộc CV chưa đáp ứng:", "; ".join(unmet) or "không có")
        print("Điều kiện cứng chưa đáp ứng:", "; ".join(c["text"] for c in res["llm_conditions"] if not c.get("met")) or "không có")
    print(res["explanation"]["vi"])

if "--save" in sys.argv:
    with open(os.path.join(HERE, "results.md"), "w", encoding="utf-8") as f:
        f.write("# Kết quả demo (4 cặp mới)\n\n| Cặp | Kỳ vọng theo rubric | Mô hình | Điểm | Nhãn |\n|---|:---:|:---:|:---:|---|\n")
        for p, _, _, exp, got, score, label in rows:
            f.write(f"| {p} | {exp} | {got} | {score} | {label} |\n")
        f.write(f"\nĐúng mức: {hits}/{len(rows)}.\n")
        for r, res in blocks:
            f.write(f"\n## {r.pair_id}: {r.cv_file} ↔ {r.jd_file}\n\nKỳ vọng {r.expected_grade} ({r.expected_reason}); mô hình {res['grade']}.\n\n```\n{res['explanation']['vi']}\n```\n")
