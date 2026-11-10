"""
Baseline ConFit (nhận xét của cô): bi-encoder tinh chỉnh bằng học tương phản MultipleNegativesRankingLoss (InfoNCE) trên văn bản gốc (JD, CV).
 - Neo = JD, dương = CV có nhãn >= 2 với JD đó, âm khó = một CV nhãn 0 (nếu không có thì nhãn 1) của cùng JD, cộng mọi CV khác trong batch.
 - Batch không lặp JD/CV; các CV trong batch đã biết là phù hợp (nhãn >= 2) với JD neo bị che khỏi mẫu âm (tránh âm giả).
 - Cùng fold, cùng cách tách 15% JD làm validation, cùng seed với mô hình chính (src/modeling/train_req.py).
   Epoch tốt nhất (kể cả epoch 0 = chưa tinh chỉnh) chọn bằng NDCG@10 trên validation.
Chạy: python src/modeling/train_confit.py <jd|double|ext> [--seeds 5] [--epochs 3] [--maxlen 256] [--model ...]
      ext = resume-job-fit (cnamuangtoun), cùng fold với train_ext.py --protocol jd (gộp train+test, 5 fold theo JD)
      Trên GPU (Kaggle): notebooks/kaggle_confit.ipynb, dùng --maxlen 512
Ra:   report/results/confit_<protocol><tag>.csv (cv_id, jd_id, qid, seed, score), confit_<protocol><tag>_val.csv
"""
import argparse
import os
import sys
import time
from types import SimpleNamespace

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
import config
from src.data_collection.extract_requirements_all import load_texts
from src.evaluation.metrics import ndcg_at_k
from src.extraction import requirement_extractor as R
from src.modeling.train_req import splits

RES = os.path.join(ROOT, "report", "results")
os.makedirs(RES, exist_ok=True)  # report/ không nằm trong repo


def pairs_used():
    """Đúng tập cặp mà build_all() dùng (cả hai phía trích xuất được mục), để fold trùng khớp với mô hình chính."""
    cv, jd = load_texts()
    C = R._load()
    ok = lambda t, k: bool(C.get(R._key(t, k), {}).get("items"))
    P = pd.read_csv(os.path.join(config.DATA_RAW_DIR, "pairs_labeled.csv"))
    P = P[[ok(cv[c], "CV") and ok(jd[j], "JD") for c, j in zip(P.cv_id, P.jd_id)]]
    return [SimpleNamespace(cv_id=c, jd_id=j, grade=int(y)) for c, j, y in zip(P.cv_id, P.jd_id, P.grade)], cv, jd


def pairs_ext():
    """Đúng tập cặp của train_ext.py --protocol jd: train rồi test gốc, cả hai phía trích xuất được mục, cặp trùng giữ lần đầu."""
    from src.modeling.train_ext import load, sid
    d, C = load(), R._load()
    ok = lambda t, k: bool((C.get(R._key(t, k)) or {}).get("items"))
    gs, seen, cv, jd = [], set(), {}, {}
    for r in pd.concat([d["train"], d["test"]]).itertuples():
        if ok(r.resume_text, "CV") and ok(r.job_description_text, "JD") and (r.cv_id, r.jd_id) not in seen:
            seen.add((r.cv_id, r.jd_id))
            gs.append(SimpleNamespace(cv_id=r.cv_id, jd_id=r.jd_id, grade=int(r.grade)))
            cv[r.cv_id], jd[r.jd_id] = r.resume_text, r.job_description_text
    return gs, cv, jd


def batches(trip, bs, rng):
    """Chia bộ ba (jd, cv+, cv-) thành batch không lặp id nào (tránh JD/CV trùng gây âm giả trong batch)."""
    pend, out = list(rng.permutation(len(trip))), []
    while pend:
        cur, used, rest = [], set(), []
        for i in pend:
            ids = set(trip[i])
            if len(cur) < bs and not ids & used:
                cur.append(i)
                used |= ids
            else:
                rest.append(i)
        out.append([trip[i] for i in cur])
        pend = rest
    return out


def val_ndcg(scores, gs):
    by = {}
    for g in gs:
        by.setdefault(g.jd_id, []).append((g.grade, scores[(g.cv_id, g.jd_id)]))
    v = [ndcg_at_k([r for r, _ in x], [s for _, s in x], 10) for x in by.values() if len(x) >= 2 and max(r for r, _ in x) >= 2]
    return float(np.mean(v))


def score(m, gs, cv, jd):
    cs, js = sorted({g.cv_id for g in gs}), sorted({g.jd_id for g in gs})
    with torch.no_grad():
        ec = dict(zip(cs, m.encode([cv[c] for c in cs], batch_size=16, normalize_embeddings=True, convert_to_tensor=True)))
        ej = dict(zip(js, m.encode([jd[j] for j in js], batch_size=16, normalize_embeddings=True, convert_to_tensor=True)))
    return {(g.cv_id, g.jd_id): float(ec[g.cv_id] @ ej[g.jd_id]) for g in gs}


def train_fold(tr, va, test, cv, jd, a, seed):
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.util import batch_to_device
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    m = SentenceTransformer(a.model, device=a.device)
    m.max_seq_length = a.maxlen
    lab = {(g.cv_id, g.jd_id): g.grade for g in tr}
    by = {}
    for g in tr:
        by.setdefault(g.jd_id, {}).setdefault(g.grade, []).append(g.cv_id)
    opt = torch.optim.AdamW(m.parameters(), lr=a.lr)
    amp = a.device.startswith("cuda")                                   # fp16 trên GPU cho nhanh; CPU giữ fp32
    scaler = torch.amp.GradScaler("cuda", enabled=amp)
    tok = lambda t: batch_to_device(m.tokenize(t), m.device)
    best = (val_ndcg(score(m, va, cv, jd), va), 0, score(m, test, cv, jd))       # epoch 0 = chưa tinh chỉnh
    print(f"    epoch 0 val={best[0]:.4f}", flush=True)
    for ep in range(1, a.epochs + 1):
        trip = []
        for j, d in by.items():
            negs = d.get(0) or d.get(1)
            for y in (2, 3):
                for c in d.get(y, []):
                    trip.append(("J" + j, "C" + c, "C" + (negs[rng.integers(len(negs))] if negs else rng.choice(sorted(set(cv) - {c})))))
        m.train()
        t0 = time.time()
        for b in batches(trip, a.bs, rng):
            q = [jd[j[1:]] for j, _, _ in b]
            cand = [x for k in (1, 2) for x in (t[k] for t in b)]          # B dương rồi B âm khó
            with torch.autocast("cuda", dtype=torch.float16, enabled=amp):
                eq = F.normalize(m(tok(q))["sentence_embedding"].float(), dim=-1)
                ec = F.normalize(m(tok([cv[c[1:]] for c in cand]))["sentence_embedding"].float(), dim=-1)
            S = a.scale * eq @ ec.T
            mask = torch.tensor([[k != i and lab.get((c[1:], j[1:]), 0) >= 2 for k, c in enumerate(cand)] for i, (j, _, _) in enumerate(b)], device=S.device)
            loss = F.cross_entropy(S.masked_fill(mask, -1e4), torch.arange(len(b), device=S.device))
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            opt.zero_grad()
        m.eval()
        v = val_ndcg(score(m, va, cv, jd), va)
        print(f"    epoch {ep} val={v:.4f}  loss={loss.item():.3f}  {time.time() - t0:.0f}s", flush=True)
        if v > best[0]:
            best = (v, ep, score(m, test, cv, jd))
    return best


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("protocol", choices=["jd", "double", "ext"])
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--maxlen", type=int, default=256)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--scale", type=float, default=20.0)              # 1/nhiệt độ, mặc định của MultipleNegativesRankingLoss
    ap.add_argument("--model", default="paraphrase-multilingual-MiniLM-L12-v2")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    gs, cv, jd = pairs_ext() if a.protocol == "ext" else pairs_used()
    folds, qf = splits(gs, "jd" if a.protocol == "ext" else a.protocol)
    print(len(gs), "cặp", flush=True)
    rows, vrows = [], []
    for seed in range(a.seeds):
        for f, pool, test in folds:
            js = sorted({g.jd_id for g in pool})
            vj = set(np.random.default_rng(seed).choice(js, size=max(1, int(0.15 * len(js))), replace=False))
            v, ep, sc = train_fold([g for g in pool if g.jd_id not in vj], [g for g in pool if g.jd_id in vj], test, cv, jd, a, seed)
            vrows.append((seed, f, v, ep))
            rows += [(g.cv_id, g.jd_id, qf(g), seed, sc[(g.cv_id, g.jd_id)]) for g in test]
            print(f"  seed {seed} fold {f}: val={v:.4f} (epoch {ep})", flush=True)
            out = os.path.join(RES, f"confit_{a.protocol}{a.tag}")       # ghi sau mỗi fold để dừng giữa chừng không mất kết quả
            pd.DataFrame(rows, columns=["cv_id", "jd_id", "qid", "seed", "score"]).to_csv(out + ".csv", index=False)
            pd.DataFrame(vrows, columns=["seed", "fold", "val_ndcg10", "epoch"]).to_csv(out + "_val.csv", index=False)
    print("xong")
