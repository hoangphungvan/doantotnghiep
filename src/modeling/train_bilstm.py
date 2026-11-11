"""
Baseline BiLSTM (nhận xét của cô: "MLP và BiLSTM"): bộ so khớp văn bản siamese kiểu PJFNN/APJFNN rút gọn, học từ đầu trên văn bản gốc.
 - Token hóa bằng tokenizer đa ngữ của MiniLM (paraphrase-multilingual-MiniLM-L12-v2), embedding từ (word-piece) lấy từ lớp vào của
   MiniLM và ĐÓNG BĂNG (dữ liệu quá ít để học embedding; không dùng phần Transformer -> khác SBERT/ConFit).
 - Một BiLSTM chung mã hóa CV và JD (tối đa --maxlen token), max-pool theo thời gian -> u, v;
   điểm = MLP([u, v, |u - v|, u * v]).
 - Loss xếp hạng RankNet theo từng JD (pair_loss, cùng loss với mô hình chính), AdamW lr 1e-3, batch = 2 JD, tối đa 20 epoch.
 - Cùng tập cặp, fold, cách tách 15% JD validation, seed như mô hình chính / ConFit; epoch tốt nhất chọn bằng NDCG@10 validation.
Chạy: python src/modeling/train_bilstm.py <jd|double|ext> [--seeds 5] [--epochs 20]   (GPU Kaggle: notebooks/kaggle_bilstm.ipynb)
Ra:   report/results/bilstm_<protocol><tag>.csv (cv_id, jd_id, qid, seed, score), bilstm_<protocol><tag>_val.csv
"""
import argparse
import os
import sys
import time
from types import SimpleNamespace

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence, pad_sequence

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from src.modeling.train_confit import RES, pairs_ext, pairs_used, val_ndcg
from src.modeling.train_req import pair_loss, splits


class BiLSTM(nn.Module):
    def __init__(self, emb, pad, h=128, drop=0.2):
        super().__init__()
        self.emb = nn.Embedding.from_pretrained(emb, freeze=True, padding_idx=pad)
        self.lstm = nn.LSTM(emb.shape[1], h, batch_first=True, bidirectional=True)
        self.drop = nn.Dropout(drop)
        self.head = nn.Sequential(nn.Linear(8 * h, h), nn.ReLU(), nn.Dropout(drop), nn.Linear(h, 1))
        self.pad = pad

    def enc(self, seqs):
        """seqs: list tensor id (độ dài khác nhau) -> (n, 2h), max-pool trên các vị trí thật."""
        dev = self.emb.weight.device
        lens = torch.tensor([len(s) for s in seqs])
        x = self.drop(self.emb(pad_sequence(seqs, batch_first=True, padding_value=self.pad).to(dev)))
        out, _ = self.lstm(pack_padded_sequence(x, lens, batch_first=True, enforce_sorted=False))
        out, _ = pad_packed_sequence(out, batch_first=True)
        mask = (torch.arange(out.shape[1])[None, :] < lens[:, None]).to(dev)
        return out.masked_fill(~mask[..., None], -1e4).max(1).values

    def score(self, u, v):
        return self.head(torch.cat([u, v, (u - v).abs(), u * v], -1)).squeeze(-1)


def load_tok(model, maxlen, texts):
    from transformers import AutoModel, AutoTokenizer
    tk = AutoTokenizer.from_pretrained(model)
    emb = AutoModel.from_pretrained(model).get_input_embeddings().weight.detach().clone()
    ids = {k: torch.tensor(tk(t, truncation=True, max_length=maxlen, add_special_tokens=False)["input_ids"][:maxlen] or [tk.unk_token_id])
           for k, t in texts.items()}
    return emb, tk.pad_token_id, ids


def encode_all(m, keys, ids, bs=64):
    out = {}
    with torch.no_grad():
        for i in range(0, len(keys), bs):
            out.update(zip(keys[i:i + bs], m.enc([ids[k] for k in keys[i:i + bs]])))
    return out


def predict(m, gs, ids):
    m.eval()
    e = encode_all(m, sorted({"C" + g.cv_id for g in gs} | {"J" + g.jd_id for g in gs}), ids)
    with torch.no_grad():
        s = m.score(torch.stack([e["C" + g.cv_id] for g in gs]), torch.stack([e["J" + g.jd_id] for g in gs]))
    return dict(zip(((g.cv_id, g.jd_id) for g in gs), s.tolist()))


def train_fold(tr, va, test, emb, pad, ids, a, seed):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    m = BiLSTM(emb, pad, a.hidden).to(a.device)
    opt = torch.optim.AdamW([p for p in m.parameters() if p.requires_grad], lr=a.lr, weight_decay=1e-4)
    by = {}
    for g in tr:
        by.setdefault(g.jd_id, []).append(g)
    js = sorted(by)
    best = (-1.0, 0, None)
    for ep in range(1, a.epochs + 1):
        m.train()
        t0 = time.time()
        order = rng.permutation(len(js))
        for i in range(0, len(order), a.jd_per_batch):
            b = [g for k in order[i:i + a.jd_per_batch] for g in by[js[k]]]
            if len({g.grade for g in b}) < 2:
                continue
            keys = sorted({"C" + g.cv_id for g in b} | {"J" + g.jd_id for g in b})
            e = dict(zip(keys, m.enc([ids[k] for k in keys])))
            s = m.score(torch.stack([e["C" + g.cv_id] for g in b]), torch.stack([e["J" + g.jd_id] for g in b]))
            loss = pair_loss(s.cpu(), SimpleNamespace(y=torch.tensor([float(g.grade) for g in b]), jd_id=[g.jd_id for g in b]))
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(m.parameters(), 1.0)
            opt.step()
        v = val_ndcg(predict(m, va, ids), va)
        print(f"    epoch {ep} val={v:.4f}  loss={loss.item():.3f}  {time.time() - t0:.0f}s", flush=True)
        if v > best[0]:
            best = (v, ep, predict(m, test, ids))
    return best


# tự kiểm tra: max-pool bỏ qua phần đệm, điểm không phụ thuộc thứ tự trong batch
_m = BiLSTM(torch.randn(10, 4), pad=0, h=3).eval()
_a, _b = torch.tensor([1, 2, 3]), torch.tensor([4, 5])
assert torch.allclose(_m.enc([_a, _b])[1], _m.enc([_b])[0], atol=1e-5)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("protocol", choices=["jd", "double", "ext"])
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--seed0", type=int, default=0)
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--maxlen", type=int, default=512)
    ap.add_argument("--hidden", type=int, default=128)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--jd-per-batch", type=int, default=2)   # 8 JD/batch chỉ ~12 bước/epoch: không học kịp (thử trên fold 0)
    ap.add_argument("--model", default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--tag", default="")
    ap.add_argument("--max-folds", type=int, default=0, help="chỉ để chạy thử nhanh")
    a = ap.parse_args()
    gs, cv, jd = pairs_ext() if a.protocol == "ext" else pairs_used()
    folds, qf = splits(gs, "jd" if a.protocol == "ext" else a.protocol)
    emb, pad, ids = load_tok(a.model, a.maxlen, {**{"C" + k: v for k, v in cv.items()}, **{"J" + k: v for k, v in jd.items()}})
    print(len(gs), "cặp;", a.device, flush=True)
    rows, vrows = [], []
    for seed in range(a.seed0, a.seed0 + a.seeds):
        for f, pool, test in folds[:a.max_folds or None]:
            js = sorted({g.jd_id for g in pool})
            vj = set(np.random.default_rng(seed).choice(js, size=max(1, int(0.15 * len(js))), replace=False))
            v, ep, sc = train_fold([g for g in pool if g.jd_id not in vj], [g for g in pool if g.jd_id in vj], test, emb, pad, ids, a, seed)
            vrows.append((seed, f, v, ep))
            rows += [(g.cv_id, g.jd_id, qf(g), seed, sc[(g.cv_id, g.jd_id)]) for g in test]
            print(f"  seed {seed} fold {f}: val={v:.4f} (epoch {ep})", flush=True)
            out = os.path.join(RES, f"bilstm_{a.protocol}{a.tag}")       # ghi sau mỗi fold
            pd.DataFrame(rows, columns=["cv_id", "jd_id", "qid", "seed", "score"]).to_csv(out + ".csv", index=False)
            pd.DataFrame(vrows, columns=["seed", "fold", "val_ndcg10", "epoch"]).to_csv(out + "_val.csv", index=False)
    print("xong")
