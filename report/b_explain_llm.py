"""
"LLM chỉ diễn đạt lại" (nhận xét của cô): Gemini viết lại 100 lời giải thích sinh từ đồ thị (report/annotation/explanations_100.xlsx)
thành đoạn văn cho nhà tuyển dụng, chỉ được dùng thông tin có sẵn. Kiểm tra độ trung thành bằng một LLM KHÁC (Qwen, mã nguồn mở, qua Groq):
Qwen chỉ đọc đoạn văn (không thấy bản gốc), cho biết mỗi yêu cầu trong danh sách được nói là đã đáp ứng / chưa đáp ứng / không nhắc,
bằng chứng được nêu, và các kỹ năng được khẳng định mà không có trong danh sách (thêm thắt).
Mốc sai số của bộ kiểm tra: chạy cùng phép kiểm tra trên chính lời giải thích gốc (lý tưởng là đúng 100%).
Chạy: python report/b_explain_llm.py            (gọi LLM, lưu dần vào report/results/b_explain_llm_cache.json; chạy lại chỉ làm phần thiếu)
Ra:   report/results/b_explain_llm.json, b_explain_llm.csv (bản viết lại + kết quả kiểm tra), report/annotation/explanations_100_llm.xlsx
"""
import argparse
import json
import os
import re
import sys
import time

import numpy as np
import pandas as pd
from openai import OpenAI

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
import config
from src.extraction.entity_extractor import _call_llm

ANN = os.path.join(ROOT, "report", "annotation")
RES = os.path.join(ROOT, "report", "results")
CACHE = os.path.join(RES, "b_explain_llm_cache.json")
MET = re.compile(r"•\s*\[(Bắt buộc|Ưu tiên)\]\s*(.+?)\s+←\s+CV:\s*“(.*?)”\s*\(độ phủ ([\d.]+), trọng số (\d+)%\)")
UNMET = re.compile(r"•\s*\[(Bắt buộc|Ưu tiên)\]\s*(.+?)\s*\(trọng số (\d+)%\)(?:\s*—\s*mục gần nhất trong CV:\s*“(.*?)”\s*\(độ phủ ([\d.]+)\))?")

REPHRASE = """Dưới đây là lời giải thích có cấu trúc do một mô hình chấm độ phù hợp giữa CV và JD sinh ra. Hãy viết lại thành MỘT đoạn văn tiếng Việt (4–7 câu), dễ đọc cho nhà tuyển dụng.
Quy tắc bắt buộc:
1. Chỉ dùng thông tin có trong lời giải thích. Không thêm kỹ năng, yêu cầu, số liệu, nhận định hay lời khuyên nào khác; không tự đánh giá lại CV.
2. Nhắc tên MỌI yêu cầu trong phần "Đã đáp ứng" và "Chưa đáp ứng", giữ đúng trạng thái. Với yêu cầu đã đáp ứng, nêu mục CV làm bằng chứng.
3. Nêu mức đáp ứng có trọng số và thông tin cấp độ / kinh nghiệm (nếu có).
4. Không dùng gạch đầu dòng. Không dùng các từ "độ phủ", "attention"; có thể nói yêu cầu nào được mô hình coi là quan trọng nhất.
Chỉ trả về đoạn văn.

Lời giải thích:
{text}"""

VERIFY = """Đoạn văn sau mô tả kết quả so khớp một CV với một JD.
Với MỖI yêu cầu trong danh sách đánh số, cho biết đoạn văn nói yêu cầu đó: "dap_ung" (CV đáp ứng), "chua_dap_ung" (CV chưa đáp ứng / thiếu) hoặc "khong_nhac" (không nhắc tới).
Nếu đoạn văn nêu mục/bằng chứng trong CV cho yêu cầu đó thì chép nguyên văn bằng chứng, nếu không thì để "".
Cuối cùng liệt kê "them": các kỹ năng hoặc yêu cầu mà đoạn văn khẳng định CV có hoặc thiếu nhưng KHÔNG thuộc danh sách (không tính bằng chứng đã chép ở trên).
Trả về JSON thuần túy: {{"trang_thai": {{"1": "...", ...}}, "bang_chung": {{"1": "...", ...}}, "them": ["..."]}}

Danh sách yêu cầu:
{reqs}

Đoạn văn:
{text}"""


def parse(e):
    """Tách lời giải thích có cấu trúc thành danh sách yêu cầu (tên, trạng thái, bằng chứng)."""
    met = [{"req": m[1].strip(), "status": "dap_ung", "ev": m[2].strip()} for m in MET.findall(e)]
    body = e.split("Chưa đáp ứng:")[1] if "Chưa đáp ứng:" in e else ""
    body = body.split("yêu cầu còn lại")[0]
    unmet = [{"req": m[1].strip(), "status": "chua_dap_ung", "ev": ""} for m in UNMET.findall(body)]
    return met + unmet


def norm(s):
    return re.sub(r"[\W_]+", " ", str(s).casefold()).strip()


def ev_match(src, got):
    a, b = norm(src), norm(got)
    return bool(a) and bool(b) and (a in b or b in a)


def json_of(raw):
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw or "")
    m = re.search(r"\{[\s\S]*\}", raw)
    return json.loads(m.group()) if m else None


def qwen(cli, model, prompt, wait):
    for _ in range(12):
        try:
            raw = cli.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], temperature=0, max_tokens=6000).choices[0].message.content
            return json_of(raw)
        except json.JSONDecodeError:
            return None
        except Exception as ex:
            print("  lỗi Qwen:", str(ex)[:160], flush=True)
            if "429" not in str(ex) and "rate" not in str(ex).lower():
                return None
            time.sleep(wait)
    sys.exit("Qwen vẫn bị giới hạn tốc độ; chạy lại sau để làm tiếp")


LV = ("intern", "thực tập", "fresher", "junior", "middle", "senior", "lead", "manager")


def is_new(t, src):
    """Mục 'thêm' có thật sự là thông tin MỚI so với lời giải thích gốc không (Qwen cũng liệt kê cả dòng cấp độ / số năm diễn đạt lại).
    Dòng cấp độ / kinh nghiệm: mới nếu có con số hoặc từ chỉ cấp độ không có trong bản gốc; còn lại: mới nếu không xuất hiện trong bản gốc."""
    n = norm(t)
    if not n or n in norm(src):
        return False
    nums = set(re.findall(r"\d+(?:\.\d+)?", t.replace(",", ".")))
    lv = {x for x in LV if x in t.lower()}
    if nums or lv or re.search(r"cấp độ|kinh nghiệm|level", t, re.I):
        return not (nums <= set(re.findall(r"\d+(?:\.\d+)?", src)) and all(x in src.lower() for x in lv))
    return True


def check(facts, v, src):
    """So kết quả đọc của Qwen với sự thật gốc."""
    st, ev = (v or {}).get("trang_thai", {}), (v or {}).get("bang_chung", {})
    them = [t for t in ((v or {}).get("them", []) or []) if isinstance(t, str)]
    r = {"n": len(facts), "dung": 0, "dao": 0, "bo_sot": 0, "ev_n": 0, "ev_dung": 0, "them": len(them), "them_moi": sum(is_new(t, src) for t in them)}
    for i, f in enumerate(facts, 1):
        s = str(st.get(str(i), "khong_nhac"))
        r["dung"] += s == f["status"]
        r["dao"] += s in ("dap_ung", "chua_dap_ung") and s != f["status"]
        r["bo_sot"] += s not in ("dap_ung", "chua_dap_ung")
        if f["status"] == "dap_ung":
            r["ev_n"] += 1
            r["ev_dung"] += ev_match(f["ev"], ev.get(str(i), ""))
    return r


def boot(x, n=2000, seed=0):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    b = [x[rng.integers(len(x), size=len(x))].mean() for _ in range(n)]
    return [float(x.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verifier", default="qwen/qwen3.8-27b")
    ap.add_argument("--base-url", default="https://api.groq.com/openai/v1")
    ap.add_argument("--wait", type=float, default=65)
    a = ap.parse_args()
    E = pd.read_excel(os.path.join(ANN, "explanations_100.xlsx"), "cham")
    C = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    save = lambda: json.dump(C, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    facts = {int(r.stt): parse(r.giai_thich) for r in E.itertuples()}
    n_bullets = {int(r.stt): r.giai_thich.count("•") for r in E.itertuples()}
    assert all(len(facts[k]) == n_bullets[k] for k in facts), [k for k in facts if len(facts[k]) != n_bullets[k]]
    cli = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url=a.base_url, timeout=300)
    for r in E.itertuples():
        k = str(int(r.stt))
        c = C.setdefault(k, {})
        if not c.get("rephrase"):
            c["rephrase"] = _call_llm([{"role": "user", "content": REPHRASE.format(text=r.giai_thich)}], config.LLM_MODEL, 5, temperature=0)
            save()
        reqs = "\n".join(f"{i}. {f['req']}" for i, f in enumerate(facts[int(k)], 1))
        for src, text in (("v_goc", r.giai_thich), ("v_llm", c["rephrase"])):
            if text and src not in c:
                c[src] = qwen(cli, a.verifier, VERIFY.format(reqs=reqs, text=text), a.wait) if facts[int(k)] else {"trang_thai": {}, "bang_chung": {}, "them": []}
                save()
        print(k, "xong", flush=True)

    rows = []
    for r in E.itertuples():
        k, f = str(int(r.stt)), facts[int(r.stt)]
        c = C[k]
        for src in ("v_goc", "v_llm"):
            ck = check(f, c.get(src), r.giai_thich)
            rows.append({"stt": int(k), "ban": src, "ok_json": c.get(src) is not None, **ck,
                         "so_tu": len(str(r.giai_thich if src == "v_goc" else c["rephrase"]).split())})
    D = pd.DataFrame(rows)
    out = {}
    for src, X in D.groupby("ban"):
        X = X[X.ok_json & (X.n > 0)]
        out[src] = {"n_expl": int(len(X)), "n_req": int(X.n.sum()),
                    "ti_le_dung_trang_thai": boot(X.dung / X.n), "ti_le_dao": boot(X.dao / X.n), "ti_le_bo_sot": boot(X.bo_sot / X.n),
                    "ti_le_bang_chung_dung": boot((X.ev_dung / X.ev_n.where(X.ev_n > 0)).dropna()),
                    "bang_chung_dung_theo_yeu_cau": [int(X.ev_dung.sum()), int(X.ev_n.sum())],
                    "ti_le_qwen_bao_them": boot(X.them > 0), "ti_le_co_thong_tin_moi": boot(X.them_moi > 0), "so_muc_thong_tin_moi": int(X.them_moi.sum()),
                    "ti_le_hoan_toan_trung_thanh": boot((X.dung == X.n) & (X.ev_dung == X.ev_n) & (X.them_moi == 0)),
                    "so_tu_tb": float(X.so_tu.mean())}
        o = out[src]
        print(f"\n## {src} ({o['n_expl']} lời giải thích, {o['n_req']} yêu cầu)")
        print(f"  bằng chứng đúng theo yêu cầu: {o['bang_chung_dung_theo_yeu_cau']}, mục thông tin mới: {o['so_muc_thong_tin_moi']}")
        for m in ("ti_le_dung_trang_thai", "ti_le_dao", "ti_le_bo_sot", "ti_le_bang_chung_dung", "ti_le_qwen_bao_them", "ti_le_co_thong_tin_moi", "ti_le_hoan_toan_trung_thanh"):
            print(f"  {m:<28} {o[m][0]:.3f} [{o[m][1]:.3f}, {o[m][2]:.3f}]")
        print(f"  số từ TB {o['so_tu_tb']:.0f}")
    out["verifier"], out["rephraser"] = a.verifier, config.LLM_MODEL
    out["vi_du"] = [{"stt": int(r.stt), "goc": r.giai_thich, "llm": C[str(int(r.stt))]["rephrase"]} for r in E.itertuples() if int(r.stt) in (1, 61)]
    json.dump(out, open(os.path.join(RES, "b_explain_llm.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    D.to_csv(os.path.join(RES, "b_explain_llm.csv"), index=False)
    # tệp cho người chấm (tùy chọn): cùng định dạng explanations_100.xlsx, cột giai_thich = bản LLM viết lại
    S = E.copy()
    S["giai_thich"] = [C[str(int(k))]["rephrase"] for k in S.stt]
    for col in [c for c in S.columns if c.startswith("nguoi")]:
        S[col] = None
    S.to_excel(os.path.join(ANN, "explanations_100_llm.xlsx"), sheet_name="cham", index=False)
    print("đã lưu")
