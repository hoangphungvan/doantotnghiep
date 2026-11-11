"""
Trích xuất 100 văn bản gán tay bằng LLM MÃ NGUỒN MỞ (nhận xét của cô), cùng prompt/parser với Gemini (requirement_extractor).
Mặc định Qwen (trọng số mở) qua Groq; đổi --base-url/--model để chạy mô hình mở khác (vd. Ollama: http://localhost:11434/v1).
Khóa: biến GROQ_API_KEY trong .env.
Chạy: python report/c_extract_open.py [--model qwen/qwen3.8-27b]
Ra:   report/annotation/extraction_pred_100_<model>.json  (cùng dạng extraction_pred_100.json; chạy lại chỉ làm phần còn thiếu)
"""
import argparse
import json
import os
import sys
import time

import pandas as pd
from openai import OpenAI

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
import config  # noqa: F401  (nạp .env)
from src.extraction import requirement_extractor as R

ANN = os.path.join(ROOT, "report", "annotation")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen/qwen3.8-27b")
    ap.add_argument("--base-url", default="https://api.groq.com/openai/v1")
    ap.add_argument("--wait", type=float, default=65, help="giây chờ khi bị giới hạn tốc độ")
    a = ap.parse_args()
    cli = OpenAI(api_key=os.getenv("GROQ_API_KEY") or "ollama", base_url=a.base_url, timeout=300)
    docs = pd.read_excel(os.path.join(ANN, "extraction_gold_100.xlsx"), sheet_name="gan_nhan")
    out = os.path.join(ANN, f"extraction_pred_100_{a.model.replace('/', '_')}.json")
    pred = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else {}
    for r in docs.itertuples():
        if pred.get(r.doc_id):
            continue
        msgs = [{"role": "system", "content": "Bạn là trợ lý AI trích xuất thông tin có cấu trúc. Luôn trả về JSON thuần túy."},
                {"role": "user", "content": R.PROMPT.format(kind=r.loai_van_ban, rules=R.RULES[r.loai_van_ban], level_hint=R.LEVEL_HINT[r.loai_van_ban], text=r.van_ban[:8000])}]
        for k in range(10):
            try:   # cùng nhiệt độ 0,1 như lượt trích xuất Gemini; max_tokens rộng vì Qwen3 có thể trả phần <think> trước JSON
                raw = cli.chat.completions.create(model=a.model, messages=msgs, temperature=0.1, max_tokens=8000).choices[0].message.content
                res = R.parse(raw or "")
                break
            except Exception as e:
                print("  lỗi:", str(e)[:200], flush=True)
                if "429" not in str(e) and "rate" not in str(e).lower():
                    res = None
                    break
                time.sleep(a.wait)
        else:
            sys.exit("vẫn bị giới hạn tốc độ; chạy lại sau để làm tiếp")
        pred[r.doc_id] = res if res and res["items"] else None
        json.dump(pred, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(len(pred), r.doc_id, "->", len(res["items"]) if res else "LỖI", "mục", flush=True)
    print("xong:", sum(v is not None for v in pred.values()), "/", len(docs), "có kết quả ->", out)
