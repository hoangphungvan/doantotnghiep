"""
Chuẩn hóa mục kỹ năng theo ESCO v1.2 (nhận xét của cô: "chuẩn hóa kỹ năng theo ESCO").

Mỗi mục hard_skill / soft_skill được ghép với kỹ năng ESCO gần nhất bằng embedding đa ngữ (cùng mô hình với đồ thị, mặc định BGE-M3),
so trên MỌI nhãn của khái niệm: preferredLabel, altLabels, hiddenLabels (skills_en.csv). Mục tiếng Việt ghép thẳng với nhãn tiếng Anh.
Bảng ghép (top-3 khái niệm + độ giống) lưu ở data/cache/esco_map_<mô hình>.json; ngưỡng áp dụng lúc dựng đồ thị (REQ_ESCO=<ngưỡng>):
mục có độ giống >= ngưỡng được thay bằng preferredLabel của ESCO (luật knowledge: xem accept), còn lại giữ nguyên (ESCO không có nhiều công cụ như Docker).
Ngưỡng chọn 0,85 sau khi xem mẫu ghép theo dải độ giống: dải 0,75-0,85 nhiều ghép sai (Query Optimization -> search engine optimisation).

Dựng bảng ghép: python src/representation/esco.py   (cần data/raw/esco/skills_en.csv, tải từ esco.ec.europa.eu)
"""
import json
import os
import re
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

TYPES = ("hard_skill", "soft_skill")
SKILLS_CSV = os.path.join(config.DATA_RAW_DIR, "esco", "skills_en.csv")


def map_path(model):
    return os.path.join(config.DATA_CACHE_DIR, "esco_map_" + re.sub(r"\W+", "_", model) + ".json")


_map = None


def accept(top, tau):
    """Ghép top = (uri, preferredLabel, sim, nhãn khớp, skillType) có được dùng không.
    Khái niệm loại knowledge trong ESCO gom nhiều công nghệ khác nhau vào altLabels/hiddenLabels (Tcl, Visual Basic .NET -> "computer programming"),
    thay bằng preferredLabel sẽ xóa khác biệt giữa các công cụ -> với knowledge chỉ nhận khi khớp chính preferredLabel (Photoshop -> Adobe Photoshop).
    Với skill/competence, altLabels là cách nói đồng nghĩa (làm việc nhóm ~ work in groups -> work in teams) nên nhận mọi nhãn."""
    _, pref, s, lab, kind = top
    return s >= tau and (kind != "knowledge" or lab.casefold() == pref.casefold())


def esco_text(text, typ, tau, model):
    """Nhãn ESCO nếu ghép đủ chắc (accept), ngược lại giữ văn bản gốc."""
    global _map
    if typ not in TYPES:
        return text
    if _map is None:
        _map = json.load(open(map_path(model), encoding="utf-8"))
    m = _map.get(text)
    return m["top"][0][1] if m and accept(m["top"][0], tau) else text


assert not accept(("u", "computer programming", 0.95, "Tcl", "knowledge"), 0.85)
assert accept(("u", "Adobe Photoshop", 0.92, "adobe photoshop", "knowledge"), 0.85)
assert accept(("u", "work in teams", 0.91, "work in groups", "skill/competence"), 0.85)
assert not accept(("u", "work in teams", 0.80, "work in groups", "skill/competence"), 0.85)


def labels():
    import pandas as pd
    S = pd.read_csv(SKILLS_CSV)
    lab, cid = [], []
    for r in S.itertuples():
        for col in (r.preferredLabel, r.altLabels, r.hiddenLabels):
            for t in str(col).split("\n") if isinstance(col, str) else []:
                if t.strip():
                    lab.append(t.strip()), cid.append(r.Index)
    return S, lab, np.array(cid)


def build(model):
    from sentence_transformers import SentenceTransformer
    from src.extraction import requirement_extractor as R
    from src.representation.req_graph import Embedder
    S, lab, cid = labels()
    items = sorted({x["text"] for v in R._load().values() for x in v["items"] if x["type"] in TYPES})
    print(f"{len(S)} kỹ năng ESCO, {len(lab)} nhãn; {len(items)} mục kỹ năng cần ghép", flush=True)
    m = SentenceTransformer(model)
    m.max_seq_length = 128
    L = m.encode(lab, normalize_embeddings=True, batch_size=128, show_progress_bar=True).astype(np.float16)
    E = Embedder().encode(items)                          # cùng vector với nút đồ thị (đã cache)
    out = {}
    for i in range(0, len(items), 512):
        sim = (E[i:i + 512].astype(np.float32) @ L.T.astype(np.float32))
        for t, s in zip(items[i:i + 512], sim):
            best = {}
            for j in np.argsort(-s)[:50]:                   # gom nhãn về khái niệm, giữ 3 khái niệm tốt nhất
                c = int(cid[j])
                if c not in best:
                    best[c] = (S.conceptUri[c], S.preferredLabel[c], round(float(s[j]), 4), lab[j], S.skillType[c])
                if len(best) == 3:
                    break
            out[t] = {"top": list(best.values())}
    json.dump(out, open(map_path(model), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("đã lưu", map_path(model), flush=True)
    return out


if __name__ == "__main__":
    from src.representation.req_graph import EMB_MODEL
    M = build(EMB_MODEL)
    s = np.array([v["top"][0][2] for v in M.values()])
    print("phân vị độ giống top-1:", {q: round(float(np.quantile(s, q)), 3) for q in (0.1, 0.25, 0.5, 0.75, 0.9)})
    for tau in (0.75, 0.8, 0.85, 0.9):
        print(f"ngưỡng {tau}: {np.mean(s >= tau):.1%} mục vượt ngưỡng, {np.mean([accept(v['top'][0], tau) for v in M.values()]):.1%} được thay (sau luật knowledge)")
