"""
Phân tích cho báo cáo (mục 2.6.3): độ phức tạp tính toán, phân tích lỗi, độ quan trọng đặc trưng, và ví dụ minh họa
xuyên suốt (một cặp CV-JD đi qua từng bước của pipeline với số liệu thật).

Chạy sau report/experiments.py:  python report/analysis.py
Kết quả: report/results/analysis.json
"""

import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import psutil
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import config
from src.data_collection.prepare_training_data import load_all_graphs
from src.extraction.entity_extractor import extract_entities
from src.extraction.pair_features import extract_pair_features, to_vector, FEATURE_NAMES
from src.inference.predict import CJMPredictor
from src.modeling.stacker import build_features, make_stacker, predict_grade, topic_features, STACKER_FILE
from src.modeling.train import attach_pair_features, get_query_id
from src.representation.embedding_generator import EmbeddingGenerator
from src.representation.graph_builder import build_graph, build_cross_entity_edges, build_knn_edges, build_star_edges

RES = os.path.join(ROOT, "report", "results")
OUT = {}


def proc_mb():
    return psutil.Process(os.getpid()).memory_info().rss / 1e6


# ---------------------------------------------------------------------------
# 1. Ví dụ xuyên suốt
# ---------------------------------------------------------------------------

def worked_example():
    cv_text = open(os.path.join(ROOT, "demo", "cv_04_backend_java.txt"), encoding="utf-8").read()
    jd_text = open(os.path.join(ROOT, "report", "example", "jd_example.txt"), encoding="utf-8").read()
    ce, je = extract_entities(cv_text), extract_entities(jd_text)
    gen = EmbeddingGenerator()
    d = gen.embedding_dim
    ex = {"cv_entities": ce, "jd_entities": je, "dim": d}

    # embedding từng item (3 chiều đầu để minh họa) + DeepSets
    items = {}
    for side, ents in (("cv", ce), ("jd", je)):
        for t in ["hard_skills"]:
            E = gen.encode(ents[t])
            items[f"{side}_{t}"] = {"items": ents[t], "first3": np.round(E[:, :3], 3).tolist(),
                                    "mean3": np.round(E.mean(0)[:3], 3).tolist(), "sum3": np.round(E.sum(0)[:3], 3).tolist(),
                                    "max3": np.round(E.max(0)[:3], 3).tolist(), "norms": np.round(np.linalg.norm(E, axis=1), 3).tolist()}
    ex["items"] = items
    # cosine giữa các item hard_skills CV x JD
    ec, ej = gen.encode(ce["hard_skills"]), gen.encode(je["hard_skills"])
    cos = (ec / np.linalg.norm(ec, axis=1, keepdims=True)) @ (ej / np.linalg.norm(ej, axis=1, keepdims=True)).T
    ex["hard_cos"] = {"cv_items": ce["hard_skills"], "jd_items": je["hard_skills"], "matrix": np.round(cos, 3).tolist()}

    cm, cf = gen.build_node_features(ce)
    jm, jf = gen.build_node_features(je)
    data = build_graph(cm, cf, jm, jf)
    ex["main_cos"] = float(torch.nn.functional.cosine_similarity(data.x[0, :d], data.x[1, :d], dim=0))
    # trọng số cạnh cross theo từng loại
    xn = data.x / data.x.norm(dim=1, keepdim=True).clamp(min=1e-8)
    ex["cross"] = {}
    for i, t in enumerate(config.ENTITY_TYPES):
        c = float(torch.dot(xn[config.CANDIDATE_ENTITY_START + i], xn[config.JD_ENTITY_START + i]).clamp(min=0))
        ex["cross"][t] = {"cosine": round(c, 3), "lambda": config.ENTITY_WEIGHTS[t], "weight": round(c * config.ENTITY_WEIGHTS[t], 3)}
    # k-NN của nút role CV (node 7)
    sim = xn @ xn.t()
    node = config.CANDIDATE_ENTITY_START + config.ENTITY_TYPES.index("role")
    s = sim[node].clone(); s[node] = -1
    v, ix = torch.topk(s, config.KNN_K)
    sharp = v.clamp(min=0) ** config.SHARPENING_P
    ex["knn_role"] = {"top": [(int(i), round(float(a), 3), round(float(b), 3)) for i, a, b in zip(ix, v, sharp / sharp.sum())]}
    ex["n_nodes"], ex["n_edges"] = int(data.num_nodes), int(data.edge_index.shape[1])
    ex["edges"] = data.edge_index.t().tolist()
    ex["edge_w"] = [round(float(x), 4) for x in data.edge_attr]
    ex["adj_density"] = ex["n_edges"] / (data.num_nodes * (data.num_nodes - 1))

    # GCN + LLM + stacker
    pred = CJMPredictor()
    res = pred.predict_from_text(cv_text, jd_text)
    ex["result"] = {k: res[k] for k in ["score", "mode", "gcn_score", "grade", "grade_label", "label"]}
    ex["llm_requirements"], ex["llm_conditions"] = res["llm_requirements"], res["llm_conditions"]
    raw = extract_pair_features(cv_text, jd_text)
    ex["llm_raw"] = {k: raw.get(k) for k in ["jd_min_years", "cv_years", "title_tech_in_cv"]}
    ex["pf_vector"] = {k: round(float(v), 3) for k, v in to_vector(raw).items()}
    ex["explanation_vi"], ex["explanation_en"] = res["explanation"]["vi"], res["explanation"]["en"]
    ex["topic_features"] = np.round(topic_features([data])[0], 3).tolist()
    return ex


# ---------------------------------------------------------------------------
# 2. Độ phức tạp tính toán
# ---------------------------------------------------------------------------

def complexity():
    r = {}
    base = proc_mb()
    t = time.time(); gen = EmbeddingGenerator(); r["sbert_load_s"] = round(time.time() - t, 2)
    r["rss_after_sbert_mb"] = round(proc_mb(), 0)
    pred = CJMPredictor()
    r["rss_after_all_mb"] = round(proc_mb(), 0)
    r["params_gcn"] = int(sum(p.numel() for p in pred.model.parameters()))
    r["params_sbert"] = int(sum(p.numel() for p in gen.model.parameters()))
    r["file_mb"] = {"best_model.pt": round(os.path.getsize(os.path.join(config.MODEL_DIR, "best_model.pt")) / 1e6, 2),
                    "stacker.pkl": round(os.path.getsize(STACKER_FILE) / 1e6, 2)}
    gl = glob.glob(os.path.join(config.GRAPH_DIR, "graph_*.pt"))
    r["graph_file_kb"] = round(np.mean([os.path.getsize(f) for f in gl[:200]]) / 1e3, 1)
    r["graph_total_mb"] = round(sum(os.path.getsize(f) for f in gl) / 1e6, 0)

    graphs = load_all_graphs()
    r["avg_edges"] = float(np.mean([g.edge_index.shape[1] for g in graphs]))
    r["avg_items_per_pair"] = None

    # thời gian từng khâu trên một cặp (CPU, 2 luồng), trung bình nhiều lần
    cv_text = open(os.path.join(ROOT, "demo", "cv_04_backend_java.txt"), encoding="utf-8").read()
    jd_text = open(os.path.join(ROOT, "report", "example", "jd_example.txt"), encoding="utf-8").read()
    ce, je = extract_entities(cv_text), extract_entities(jd_text)
    n_items = sum(len(ce[t]) for t in config.ENTITY_TYPES) + sum(len(je[t]) for t in config.ENTITY_TYPES)
    r["items_example"] = n_items

    def avg(fn, n=20):
        fn()
        t = time.perf_counter()
        for _ in range(n):
            fn()
        return (time.perf_counter() - t) / n * 1000

    r["ms_embed_pair"] = round(avg(lambda: (gen.build_node_features(ce), gen.build_node_features(je))), 1)
    cm, cf = gen.build_node_features(ce); jm, jf = gen.build_node_features(je)
    r["ms_build_graph"] = round(avg(lambda: build_graph(cm, cf, jm, jf)), 2)
    g = build_graph(cm, cf, jm, jf)
    pred.model.eval()
    with torch.no_grad():
        r["ms_gcn_forward"] = round(avg(lambda: pred.model(g)), 2)
    attach = g.clone(); attach.g_feat = torch.zeros(1, len(FEATURE_NAMES))
    if pred.stacker is not None:
        r["ms_stacker"] = round(avg(lambda: pred.stacker.predict(build_features([attach], [0.5]))), 2)
    # batch 1664 cặp qua GCN
    from torch_geometric.loader import DataLoader
    loader = DataLoader(graphs, batch_size=64)
    t = time.perf_counter()
    with torch.no_grad():
        for b in loader:
            pred.model(b)
    r["gcn_1664_pairs_s"] = round(time.perf_counter() - t, 2)
    r["peak_rss_mb"] = round(proc_mb(), 0)
    return r


# ---------------------------------------------------------------------------
# 3. Phân tích lỗi + độ quan trọng đặc trưng
# ---------------------------------------------------------------------------

def error_analysis():
    df = pd.read_csv(os.path.join(RES, "oof_all_methods.csv"))
    lab = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(config.DATA_RAW_DIR, "judgments", "claude_b0*_part*.csv"))])
    df = df.merge(lab[["cv_id", "jd_id", "role_match", "must_have_coverage_pct", "seniority_gap", "hard_requirement_missing",
                       "core_tech_missing", "reason"]], on=["cv_id", "jd_id"])
    df["pred"] = np.clip(np.rint(df.stack_score), 0, 3).astype(int)
    from src.evaluation.calibrate_thresholds import apply, fit_thresholds
    fold = df.fold.values
    gp = np.zeros(len(df), int)
    for f in range(5):
        th, _ = fit_thresholds(df.gcn_score.values[fold != f], df.grade.values[fold != f])
        gp[fold == f] = apply(df.gcn_score.values[fold == f], th)
    df["pred_gcn"] = gp
    out = {"confusion_stack": pd.crosstab(df.grade, df.pred).reindex(index=range(4), columns=range(4), fill_value=0).values.tolist(),
           "confusion_gcn": pd.crosstab(df.grade, df.pred_gcn).reindex(index=range(4), columns=range(4), fill_value=0).values.tolist()}
    out["acc_stack"], out["acc_gcn"] = float((df.pred == df.grade).mean()), float((df.pred_gcn == df.grade).mean())
    out["within1_stack"] = float((abs(df.pred - df.grade) <= 1).mean())
    by = df.groupby("role_match").apply(lambda g: pd.Series({"n": len(g), "acc": (g.pred == g.grade).mean(),
                                                            "mean_abs_err": abs(g.pred - g.grade).mean()}))
    out["by_role_match"] = by.round(3).reset_index().to_dict("records")
    df["gap_group"] = pd.cut(df.seniority_gap, [-4, -1, 0, 1, 4], labels=["CV cao hơn JD", "ngang cấp", "JD cao hơn 1 cấp", "JD cao hơn từ 2 cấp"])
    out["by_gap"] = df.groupby("gap_group", observed=True).apply(lambda g: pd.Series({"n": len(g), "acc": (g.pred == g.grade).mean()})).round(3).reset_index().astype({"gap_group": str}).to_dict("records")
    out["hard_req"] = {"có": float((df[df.hard_requirement_missing == 1].pred == df[df.hard_requirement_missing == 1].grade).mean()),
                       "không": float((df[df.hard_requirement_missing == 0].pred == df[df.hard_requirement_missing == 0].grade).mean()),
                       "n_có": int((df.hard_requirement_missing == 1).sum())}
    # lỗi nặng nhất
    df["err"] = df.pred - df.grade
    worst = df.reindex(df.err.abs().sort_values(ascending=False).index).head(40)
    out["worst"] = worst[["cv_id", "jd_id", "grade", "pred", "stack_score", "role_match", "must_have_coverage_pct", "seniority_gap",
                          "hard_requirement_missing", "core_tech_missing", "reason"]].round(3).to_dict("records")
    out["over_pred_share"] = float((df.err > 0).mean()); out["under_pred_share"] = float((df.err < 0).mean())
    out["n_err2plus"] = int((df.err.abs() >= 2).sum())
    return out


def importance():
    from sklearn.inspection import permutation_importance
    from src.modeling.train import split_by_query  # noqa
    graphs = load_all_graphs()
    attach_pair_features(graphs)
    oof = pd.read_csv(os.path.join(config.DATA_PROCESSED_DIR, "cv_oof_predictions.csv")).set_index(["cv_id", "jd_id"]).gcn_score
    gs = np.array([oof[(g.cv_source, g.jd_source)] for g in graphs])
    X = build_features(graphs, gs)
    y = np.array([g.y.item() for g in graphs])
    cvs = np.array([g.cv_source for g in graphs])
    names = ["Độ phủ yêu cầu bắt buộc (LLM)", "Số yêu cầu (LLM)", "Chênh lệch số năm kinh nghiệm (LLM)",
             "Số điều kiện cứng chưa đáp ứng (LLM)", "Công nghệ tiêu đề JD thiếu ở CV (LLM)", "Hợp lệ (LLM)",
             "Cosine toàn văn CV–JD"] + [f"Cosine nhóm {t}" for t in config.ENTITY_TYPES] + ["Điểm GCN (out-of-fold)"]
    uq = np.array(sorted(set(cvs))); np.random.default_rng(42).shuffle(uq)
    imps = np.zeros(X.shape[1]); n = 0
    for te in np.array_split(uq, 5):
        m = np.isin(cvs, te)
        model = make_stacker().fit(X[~m], y[~m])
        r = permutation_importance(model, X[m], y[m], scoring="neg_mean_squared_error", n_repeats=10, random_state=0)
        imps += r.importances_mean; n += 1
    imps /= n
    order = np.argsort(-imps)
    return [{"feature": names[i], "importance": float(imps[i])} for i in order]


def main():
    OUT["example"] = worked_example()
    print("ví dụ xong", flush=True)
    OUT["errors"] = error_analysis()
    print("lỗi xong", flush=True)
    OUT["importance"] = importance()
    print("importance xong", flush=True)
    OUT["complexity"] = complexity()
    json.dump(OUT, open(os.path.join(RES, "analysis.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("xong")


if __name__ == "__main__":
    main()
