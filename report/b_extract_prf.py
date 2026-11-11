"""
Chất lượng trích xuất trên 100 văn bản gán tay (nhận xét của cô): Precision/Recall/F1 theo từng loại mục.
  python report/b_extract_prf.py                       # so mọi file extraction_pred_100*.json với nhãn vàng (xlsx)
  python report/b_extract_prf.py --ref <file.json>     # chưa có nhãn vàng: lấy một file máy làm tham chiếu (chỉ là ĐỘ ĐỒNG THUẬN)

Ghép mục: trong cùng văn bản và cùng loại, ghép tham lam theo độ giống giảm dần, mỗi mục dùng một lần.
 - strict : trùng nhau sau chuẩn hóa (chữ thường, NFC, bỏ dấu câu trừ + và #).
 - lenient: strict, HOẶC chuỗi này nằm trọn trong chuỗi kia theo từ, HOẶC difflib ratio >= 0,8.
"Không phân loại": ghép bỏ qua loại (đo việc tìm đúng mục, không tính gán nhầm loại).
Văn bản được tính là đã gán khi cột nguoi_gan có chữ hoặc có ít nhất một cột loại có chữ.
Kèm: độ đúng required (mục JD đã ghép lenient), độ đúng level, MAE total_years, CI95 bootstrap theo văn bản cho F1.
"""
import argparse
import glob
import json
import os
import re
import sys
import unicodedata
from difflib import SequenceMatcher

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
ANN = os.path.join(ROOT, "report", "annotation")
TYPES = ["hard_skill", "soft_skill", "education", "role", "industry"]


def norm(s):
    s = unicodedata.normalize("NFC", str(s)).casefold()
    return re.sub(r"\s+", " ", re.sub(r"[^\w+#]+", " ", s)).strip()


def sim(a, b, mode):
    if a == b:
        return 1.0
    if mode == "strict":
        return 0.0
    if f" {a} " in f" {b} " or f" {b} " in f" {a} ":
        return 0.9
    r = SequenceMatcher(None, a, b).ratio()
    return r if r >= 0.8 else 0.0


def match(gold, pred, mode):
    """gold, pred: list chuỗi đã chuẩn hóa. Trả về list (i_gold, j_pred) đã ghép."""
    cand = sorted(((sim(g, p, mode), i, j) for i, g in enumerate(gold) for j, p in enumerate(pred)), reverse=True)
    ug, up, out = set(), set(), []
    for s, i, j in cand:
        if s > 0 and i not in ug and j not in up:
            ug.add(i), up.add(j), out.append((i, j))
    return out


def split(cell):
    return [x.strip() for x in re.split(r"[;\n]", str(cell)) if x.strip()] if isinstance(cell, str) else []


def gold_docs():
    df = pd.read_excel(os.path.join(ANN, "extraction_gold_100.xlsx"), sheet_name="gan_nhan")
    out = {}
    for r in df.to_dict("records"):
        items = {t: split(r[t]) for t in TYPES}
        if not (isinstance(r["nguoi_gan"], str) and r["nguoi_gan"].strip()) and not any(items.values()):
            continue
        opt = {norm(x) for x in split(r["required_false"])}
        lv = str(r["level"]).strip().lower() if isinstance(r["level"], str) and r["level"].strip() else None
        ty = pd.to_numeric(r["total_years"], errors="coerce")
        out[r["doc_id"]] = {"items": [{"text": x, "type": t, "required": norm(x) not in opt} for t in TYPES for x in items[t]],
                            "level": lv, "total_years": None if pd.isna(ty) else float(ty)}
    return out


def load_pred(path):
    return {k: v or {"items": [], "level": None, "total_years": None} for k, v in json.load(open(path, encoding="utf-8")).items()}


def counts(G, P, docs, mode, typed):
    """Đếm TP/FP/FN theo (văn bản, loại); typed=False gộp mọi loại thành một."""
    rows, req = [], []
    for d in docs:
        g, p = G[d]["items"], P.get(d, {"items": []})["items"]
        for t in (TYPES if typed else ["all"]):
            gi = [x for x in g if not typed or x["type"] == t]
            pi = [x for x in p if not typed or x["type"] == t]
            m = match([norm(x["text"]) for x in gi], [norm(x["text"]) for x in pi], mode)
            rows.append((d, t, len(m), len(pi) - len(m), len(gi) - len(m)))
            if not typed and mode == "lenient" and d.split("|")[1] == "JD":
                req += [gi[i]["required"] == pi[j]["required"] for i, j in m]
    return pd.DataFrame(rows, columns=["doc", "type", "tp", "fp", "fn"]), req


def prf(c):
    tp, fp, fn = c.tp.sum(), c.fp.sum(), c.fn.sum()
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def boot_f1(c, B=1000, seed=0):
    by = c.groupby("doc")[["tp", "fp", "fn"]].sum().to_numpy()
    rng = np.random.default_rng(seed)
    f = []
    for _ in range(B):
        tp, fp, fn = by[rng.integers(len(by), size=len(by))].sum(0)
        f.append(2 * tp / (2 * tp + fp + fn) if tp else 0.0)
    return np.percentile(f, [2.5, 97.5])


def report(name, G, P):
    docs = sorted(G)
    print(f"\n=== {name}: {len(docs)} văn bản, {sum(len(G[d]['items']) for d in docs)} mục tham chiếu ===")
    for mode in ("strict", "lenient"):
        c, _ = counts(G, P, docs, mode, True)
        print(f"[{mode}] {'loại':<12}{'P':>7}{'R':>7}{'F1':>7}{'n_ref':>7}")
        for t in TYPES:
            x = c[c.type == t]
            print(f"         {t:<12}" + "".join(f"{v:>7.3f}" for v in prf(x)) + f"{int(x.tp.sum() + x.fn.sum()):>7}")
        ma = np.mean([prf(c[c.type == t])[2] for t in TYPES])
        lo, hi = boot_f1(c)
        print(f"         {'micro':<12}" + "".join(f"{v:>7.3f}" for v in prf(c)) + f"   CI95 F1 [{lo:.3f}, {hi:.3f}]   macro-F1 {ma:.3f}")
        for grp, f in (("tiếng Việt", lambda d: not d.startswith("resume-job-fit")), ("tiếng Anh", lambda d: d.startswith("resume-job-fit")),
                       ("JD", lambda d: d.split("|")[1] == "JD"), ("CV", lambda d: d.split("|")[1] == "CV")):
            x = c[c.doc.map(f)]
            if len(x):
                print(f"         {grp:<12}" + "".join(f"{v:>7.3f}" for v in prf(x)))
        u, req = counts(G, P, docs, mode, False)
        print(f"         {'không phân loại':<12}" + "".join(f"{v:>7.3f}" for v in prf(u)))
    lv = [(G[d]["level"], P.get(d, {}).get("level")) for d in docs if G[d]["level"]]
    ty = [abs(G[d]["total_years"] - P[d]["total_years"]) for d in docs if G[d]["total_years"] is not None and P.get(d, {}).get("total_years") is not None]
    _, req = counts(G, P, docs, "lenient", False)
    print(f"required đúng (mục JD đã ghép): {np.mean(req):.3f} (n={len(req)})" if req else "required: không có mục JD ghép được")
    print(f"level đúng: {np.mean([a == b for a, b in lv]):.3f} (n={len(lv)})" if lv else "level: không có tham chiếu")
    print(f"total_years MAE: {np.mean(ty):.2f} năm (n={len(ty)})" if ty else "total_years: không có cặp để so")


# tự kiểm tra
assert norm("Python, SQL!") == "python sql" and norm("C++") == "c++"
assert match(["python", "sql"], ["sql", "lập trình python"], "lenient") == [(1, 0), (0, 1)]
assert match(["python"], ["lập trình python"], "strict") == []
_c = pd.DataFrame([("d", "x", 2, 1, 1)], columns=["doc", "type", "tp", "fp", "fn"])
assert np.allclose(prf(_c), (2 / 3, 2 / 3, 2 / 3))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", help="file json của máy dùng làm tham chiếu khi chưa có nhãn vàng")
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(ANN, "extraction_pred_100*.json")))
    if a.ref:
        ref = os.path.abspath(a.ref) if os.path.exists(a.ref) else os.path.join(ANN, a.ref)
        G = {k: v for k, v in load_pred(ref).items()}
        print("THAM CHIẾU LÀ MÁY (", os.path.basename(ref), "): đây là độ đồng thuận giữa hai mô hình, KHÔNG phải P/R/F1 so với người.")
        files = [f for f in files if os.path.abspath(f) != ref]
    else:
        G = gold_docs()
        if not G:
            sys.exit("extraction_gold_100.xlsx chưa có văn bản nào được gán (cột nguoi_gan / các cột loại đều trống).")
    for f in files:
        report(os.path.basename(f), G, load_pred(f))
