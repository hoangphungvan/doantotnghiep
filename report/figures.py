"""
Vẽ các hình của báo cáo bằng matplotlib (vector): lưu SVG + PNG vào report/figures/.
Chạy: python report/figures.py   (cần report/results/*.json đã có)
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
RES = os.path.join(HERE, "results")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "mathtext.fontset": "stix",
                     "svg.fonttype": "none", "axes.unicode_minus": False})

BLUE, GREEN, ORANGE, GREY, RED, PURPLE = "#DCE6F5", "#DDEFD9", "#FCE8C8", "#EDEDED", "#F6D5D5", "#E6DDF2"
EDGE = "#33415C"


def save(fig, name):
    for ext in ("svg", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def box(ax, x, y, w, h, text, fc=BLUE, fs=10, bold=False, ec=EDGE, lw=1.2, ls="-", align="center"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.6", fc=fc, ec=ec, lw=lw, ls=ls))
    ha = "center" if align == "center" else "left"
    tx = x + w / 2 if align == "center" else x + 0.8
    ax.text(tx, y + h / 2, text, ha=ha, va="center", fontsize=fs, fontweight="bold" if bold else "normal", linespacing=1.25)


def arrow(ax, p, q, text=None, fs=8.5, color=EDGE, rad=0.0, lw=1.4, off=(0, 0.9), ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=13, color=color, lw=lw, connectionstyle=f"arc3,rad={rad}", ls=ls))
    if text:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha="center", va="bottom", fontsize=fs, color=color)


def canvas(w, h, xmax, ymax):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.axis("off")
    return fig, ax


# ---------------------------------------------------------------------------
# Hình 1.1: Input – Process – Output tổng quát
# ---------------------------------------------------------------------------

def fig_ipo():
    fig, ax = canvas(11, 7.8, 110, 78)
    for x, w, t in ((1, 24, "ĐẦU VÀO (Input)"), (30, 46, "XỬ LÝ (Process)"), (81, 28, "ĐẦU RA (Output)")):
        ax.add_patch(FancyBboxPatch((x, 1), w, 72, boxstyle="round,pad=0.02,rounding_size=1.5", fc="white", ec="#7A869A", lw=1.2, ls="--"))
        ax.text(x + w / 2, 75, t, ha="center", fontsize=12, fontweight="bold")
    box(ax, 3, 40, 20, 24, "Một cặp (CV, JD)\n$(c,\\,j)$\n$c$: văn bản CV\n$j$: văn bản JD\n(tiếng Việt, tiếng Anh\nhoặc song ngữ)", BLUE, 9)
    box(ax, 3, 10, 20, 20, "Nhãn mức phù hợp\n$y\\in\\{0,1,2,3\\}$\n(tùy chọn, chỉ dùng\nkhi huấn luyện và\nđánh giá)", ORANGE, 9)
    steps = [("Bước 1. Tiền xử lý, trích xuất thông tin", "chuẩn hóa văn bản; tách vai trò, kỹ năng,\nhọc vấn, lĩnh vực, kinh nghiệm", BLUE),
             ("Bước 2. Biểu diễn ngữ nghĩa", "chuyển văn bản/thực thể thành vector\ntrong không gian liên tục, đa ngôn ngữ", BLUE),
             ("Bước 3. Đối sánh, tính điểm phù hợp", "so khớp CV–JD theo từng khía cạnh,\ntổng hợp thành điểm $s(c,j)$ của cặp", GREEN),
             ("Bước 4. Phân mức, sinh diễn giải", "quy điểm về mức 0–3; nêu yêu cầu\nđã đáp ứng / chưa thấy trong CV", ORANGE),
             ("Bước 5. Xếp hạng CV theo từng JD", "gom điểm các cặp cùng một JD,\nsắp xếp CV theo điểm giảm dần", GREEN)]
    for k, (a_, b_, col) in enumerate(steps):
        y = 58 - k * 13.5
        box(ax, 32, y, 42, 11, "", col, 9)
        ax.text(53, y + 8.3, a_, ha="center", va="center", fontsize=9.3, fontweight="bold")
        ax.text(53, y + 3.6, b_, ha="center", va="center", fontsize=8.3, linespacing=1.2)
        if k < 4:
            arrow(ax, (53, y), (53, y - 2.5), lw=1.3)
    arrow(ax, (23, 52), (32, 63), lw=1.1, color="#667")
    arrow(ax, (23, 20), (32, 20), lw=1.0, color="#889", ls="--")
    outs = [("Điểm phù hợp $s(c,j)$\ncủa cặp", BLUE, 53, 14), ("Mức phù hợp (0–3)\ncủa cặp", GREEN, 37, 13), ("Thông tin diễn giải\ncủa cặp", ORANGE, 21, 13),
            ("Danh sách CV của mỗi JD,\nxếp theo điểm giảm dần", PURPLE, 5, 13)]
    for t, c_, y, h in outs:
        box(ax, 83, y, 24, h, t, c_, 9)
    arrow(ax, (74, 36), (83, 58), lw=1.1, color="#667")
    arrow(ax, (74, 36), (83, 42), lw=1.1, color="#667")
    arrow(ax, (74, 23), (83, 26), lw=1.1, color="#667")
    arrow(ax, (74, 9), (83, 11), lw=1.1, color="#667")
    save(fig, "fig_ipo")


# ---------------------------------------------------------------------------
# Hình 2.1: kiến trúc tổng quát
# ---------------------------------------------------------------------------

def fig_arch():
    fig, ax = canvas(13, 7.6, 130, 76)
    ax.set_xlim(-4, 130)
    box(ax, 1, 56, 15, 14, "Văn bản\nCV và JD", GREY, 10, True)
    box(ax, 22, 52, 26, 22, "M1. Trích xuất thực thể\nLLM, 6 loại thực thể\n(+ yêu cầu ưu tiên)\nchuẩn hóa và cache", BLUE, 9.5, True)
    box(ax, 54, 52, 26, 22, "M2. Biểu diễn ngữ nghĩa\nSBERT (384 chiều)\nDeepSets: [mean | sum | max]\n→ 1152 chiều", GREEN, 9.5, True)
    box(ax, 86, 52, 26, 22, "M3. Dựng đồ thị cặp\n14 nút, cạnh sao / cầu /\nchéo / k-NN\ntrọng số cạnh $w_{uv}$", ORANGE, 9.5, True)
    box(ax, 86, 24, 26, 22, "M4. Mạng GCN\nPre-aggregation, 3 × GCNConv,\nreadout, MLP\n→ điểm đồ thị $s_{\\mathrm{GCN}}$", PURPLE, 9.5, True)
    box(ax, 54, 24, 26, 22, "M5. Điểm tổng hợp\nstacking (GBM) trên\n$s_{\\mathrm{GCN}}$ + 7 cosine\n+ 6 đặc trưng cặp LLM", RED, 9.5, True)
    box(ax, 22, 24, 26, 22, "M6. Xếp hạng và đánh giá\nmỗi JD: sắp xếp các CV\ntheo điểm giảm dần;\nNDCG@K, Recall@K, MRR", BLUE, 9.5, True)
    box(ax, 1, 24, 15, 22, "M7. Diễn giải\ntóm tắt cho\nnhà tuyển dụng\n(song ngữ)", GREEN, 9.5, True)
    box(ax, 54, 2, 26, 15, "M5a. Đánh giá cặp bằng LLM\nđộ phủ yêu cầu, lệch cấp,\nđiều kiện cứng chưa đáp ứng", ORANGE, 9, True)
    for a, b in (((16, 63), (22, 63)), ((48, 63), (54, 63)), ((80, 63), (86, 63)), ((99, 52), (99, 46)), ((86, 35), (80, 35)),
                 ((54, 35), (48, 35)), ((22, 35), (16, 35))):
        arrow(ax, a, b)
    arrow(ax, (67, 17), (67, 24))
    ax.plot([1, -2, -2, 50], [63, 63, 9.5, 9.5], color="#889", lw=1.2, ls="--")
    arrow(ax, (50, 9.5), (54, 9.5), color="#889", lw=1.2)
    ax.text(2, 11, "văn bản gốc của cặp CV–JD", fontsize=8.5, color="#556")
    arrow(ax, (67, 52), (67, 46), "cosine (SBERT)", off=(1, -3.2), fs=8)
    ax.text(65, 76, "KIẾN TRÚC TỔNG QUÁT CỦA HỆ THỐNG ĐỀ XUẤT", ha="center", fontsize=11, fontweight="bold")
    save(fig, "fig_arch")


# ---------------------------------------------------------------------------
# Hình 2.2: biểu diễn ngữ nghĩa (SBERT + DeepSets) với ví dụ
# ---------------------------------------------------------------------------

def fig_embed():
    fig, ax = canvas(13, 5.8, 130, 58)
    box(ax, 1, 16, 26, 36, "Nhóm hard_skills của CV\n$S=\\{s_1,\\ldots,s_n\\}$, $n=13$\n\nJava, Spring Boot,\nSpring Data JPA, RESTful API,\nMySQL, PostgreSQL, Redis,\nKafka, Docker, Git, Jenkins,\nJUnit, Tối ưu truy vấn", GREY, 9, align="center")
    box(ax, 34, 24, 20, 20, "SBERT\nparaphrase-multilingual-\nMiniLM-L12-v2\nmỗi mục → $\\mathbf{x}_i\\in\\mathbb{R}^{384}$", BLUE, 9, True)
    box(ax, 61, 24, 16, 20, "Ma trận\n$\\mathbf{X}\\in\\mathbb{R}^{13\\times384}$", GREEN, 10, True)
    for y, t in ((38, "mean"), (28, "sum"), (18, "max")):
        box(ax, 85, y, 17, 8, t, ORANGE, 10, True)
        arrow(ax, (77, 34), (85, y + 4), lw=1.1)
        arrow(ax, (102, y + 4), (108, 34), lw=1.1)
    box(ax, 108, 22, 20, 24, "Vector nhóm\n$\\mathbf{g}\\in\\mathbb{R}^{1152}$\n$=[\\mathbf{g}^{\\mathrm{mean}}\\,|\\,\\mathbf{g}^{\\mathrm{sum}}\\,|\\,\\mathbf{g}^{\\mathrm{max}}]$\n3 × 384", PURPLE, 9, True)
    arrow(ax, (27, 34), (34, 34))
    arrow(ax, (54, 34), (61, 34))
    ax.text(65, 55, "Đầu ra: một vector 1152 chiều cho mỗi nhóm thực thể → gán làm đặc trưng của nút tương ứng", ha="center", fontsize=9.5, style="italic")
    ax.text(65, 6, "Nhóm rỗng → vector 0 (1152 chiều); nút trung tâm CV/JD: SBERT của văn bản thực thể gộp, đặt vào 384 chiều đầu, 768 chiều còn lại = 0",
            ha="center", fontsize=8.5)
    save(fig, "fig_embed")


# ---------------------------------------------------------------------------
# Hình 2.3: xây dựng đồ thị theo từng bước (dữ liệu thật của cặp ví dụ)
# ---------------------------------------------------------------------------

TYPES = ["soft", "hard", "edu", "field", "ind.", "role"]
LAM = [1.0, 2.5, 1.5, 2.0, 1.5, 3.0]
COS = [0.690, 0.894, 0.602, 1.000, 0.662, 0.807]


def pos():
    ys = [7.2, 6.0, 4.8, 3.6, 2.4, 1.2]
    p = {0: (2.6, 9.2), 1: (7.4, 9.2)}
    for i, y in enumerate(ys):
        p[2 + i] = (1.0, y)
        p[8 + i] = (9.0, y)
    return p


def draw_nodes(ax, P, hl=()):
    for n, (x, y) in P.items():
        fc = "#9DB8E3" if n == 0 else "#9FD39A" if n == 1 else BLUE if n < 8 else GREEN
        ax.add_patch(Circle((x, y), 0.42 if n < 2 else 0.36, fc=fc, ec=EDGE, lw=1.2 if n not in hl else 2.4, zorder=3))
        ax.text(x, y, str(n), ha="center", va="center", fontsize=8.5, zorder=4, fontweight="bold")
    ax.text(P[0][0], P[0][1] + 0.7, "CV", ha="center", fontsize=9, fontweight="bold")
    ax.text(P[1][0], P[1][1] + 0.7, "JD", ha="center", fontsize=9, fontweight="bold")
    for i, t in enumerate(TYPES):
        ax.text(P[2 + i][0] - 0.55, P[2 + i][1], t, ha="right", va="center", fontsize=8)
        ax.text(P[8 + i][0] + 0.55, P[8 + i][1], t, ha="left", va="center", fontsize=8)


def line(ax, P, a, b, w, color="#555", alpha=0.9, lw_scale=1.0, ls="-"):
    ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]], color=color, lw=(0.5 + 1.0 * w) * lw_scale, alpha=alpha, zorder=1, ls=ls, solid_capstyle="round")


def panel(ax, title):
    ax.set_xlim(-1.2, 11.2)
    ax.set_ylim(0.2, 10.6)
    ax.axis("off")
    ax.set_title(title, fontsize=10.5, fontweight="bold", loc="left")


def fig_graph_steps():
    A = json.load(open(os.path.join(RES, "analysis.json"), encoding="utf-8"))["example"]
    P = pos()
    fig, axs = plt.subplots(2, 3, figsize=(15, 9.6))
    ax = axs[0, 0]; panel(ax, "(a) Nút: 2 nút trung tâm + 6 nút CV + 6 nút JD")
    draw_nodes(ax, P)
    ax.text(5, 0.3, "đặc trưng mỗi nút: vector 1152 chiều", ha="center", fontsize=8.5, style="italic")

    ax = axs[0, 1]; panel(ax, "(b) Cạnh sao và cạnh cầu (trọng số $\\lambda_t$)")
    for i in range(6):
        line(ax, P, 0, 2 + i, LAM[i], "#2F5597"); line(ax, P, 1, 8 + i, LAM[i], "#2E7D32")
        ax.text(P[2 + i][0] - 0.55, P[2 + i][1] - 0.38, f"$\lambda$={LAM[i]:g}".replace(".", ","), ha="right", va="center", fontsize=7.5, color="#2F5597")
        ax.text(P[8 + i][0] + 0.55, P[8 + i][1] - 0.38, f"$\lambda$={LAM[i]:g}".replace(".", ","), ha="left", va="center", fontsize=7.5, color="#2E7D32")
    line(ax, P, 0, 1, 1.0, "#C0392B"); ax.text(5, 9.4, "cầu 1,0", ha="center", fontsize=8, color="#C0392B")
    draw_nodes(ax, P)

    ax = axs[0, 2]; panel(ax, "(c) Cạnh chéo: $w=\\max(\\cos,0)\\cdot\\lambda_t$")
    for i in range(6):
        w = max(COS[i], 0) * LAM[i]
        line(ax, P, 2 + i, 8 + i, w, "#B9770E")
        ax.text(5, P[2 + i][1] + 0.22, f"cos {COS[i]:.2f} × {LAM[i]:g} = {w:.2f}", ha="center", fontsize=7.6, color="#7E5109", bbox=dict(fc="white", ec="none", pad=0.4))
    draw_nodes(ax, P)

    ax = axs[1, 0]; panel(ax, "(d) Cạnh k-NN của nút 7 (role CV), $k=10$, $p=4$")
    top = A["knn_role"]["top"]
    for (j, cs, w) in top:
        line(ax, P, 7, j, w * 4.5, "#7D3C98", alpha=0.85)
    draw_nodes(ax, P, hl=(7,))
    ax.text(5.0, 1.55, "nút 13: cos 0,807 → trọng số 0,906", ha="center", fontsize=8, color="#5B2C6F")
    ax.text(5.0, 0.85, "9 nút còn lại: cos 0,24–0,30 → mỗi cạnh ≈ 0,01", ha="center", fontsize=8, color="#5B2C6F")

    ax = axs[1, 1]; panel(ax, "(e) Hợp nhất: lấy trọng số lớn nhất (sao > chéo > k-NN)")
    E = A["edges"]; W = A["edge_w"]
    for (s, d), w in zip(E, W):
        if s < d and w < 0.6:
            line(ax, P, s, d, 0.1, "#BBB", alpha=0.5)
    for (s, d), w in zip(E, W):
        if s < d and w >= 0.6:
            line(ax, P, s, d, w, "#33415C", alpha=0.9)
    draw_nodes(ax, P)
    ax.text(5, 0.3, f"{A['n_nodes']} nút, {A['n_edges']} cạnh có hướng; đậm: trọng số ≥ 0,6", ha="center", fontsize=8.5, style="italic")

    ax = axs[1, 2]; ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    txt = ("Chú giải\n\n"
           "• Nút 0, 1: nút trung tâm của CV và JD.\n"
           "• Nút 2–7: nhóm thực thể của CV theo thứ tự\n  soft, hard, edu, field, industry, role.\n"
           "• Nút 8–13: nhóm thực thể tương ứng của JD.\n\n"
           "Độ dày nét tỉ lệ với trọng số cạnh.\n\n"
           "Cặp ví dụ: CV Backend Developer (3 năm)\nvà JD Java Backend Developer (2 năm).\n"
           "Cạnh quan trọng nhất: hard 2,23; role 2,42;\nfield 2,00 (cùng \"Công nghệ thông tin\").")
    ax.text(0.2, 9.6, txt, va="top", fontsize=9.6, linespacing=1.5)
    fig.tight_layout()
    save(fig, "fig_graph_steps")


# ---------------------------------------------------------------------------
# Hình 2.4: huấn luyện GCN
# ---------------------------------------------------------------------------

def fig_train():
    fig, ax = canvas(13, 5.6, 130, 56)
    box(ax, 1, 34, 20, 16, "Khởi tạo\n$\\theta$: Glorot (GCNConv),\nKaiming (Linear);\nLayerNorm: $\\gamma=1,\\beta=0$", GREY, 8.6, True)
    box(ax, 27, 34, 22, 16, "Lan truyền xuôi\npre-agg → 3×GCNConv\n→ readout → MLP\n→ logit $z$", BLUE, 8.6, True)
    box(ax, 55, 34, 22, 16, "Hàm mất mát\nBCEWithLogits\nmục tiêu $y=g/3$", ORANGE, 9, True)
    box(ax, 83, 34, 22, 16, "Lan truyền ngược\n$\\partial\\mathcal{L}/\\partial\\theta$\ncắt gradient $\\|\\nabla\\|\\leq1$", RED, 9, True)
    box(ax, 109, 34, 20, 16, "Cập nhật Adam\n$\\eta=10^{-3}$, wd $10^{-4}$", GREEN, 9, True)
    for a, b in (((21, 42), (27, 42)), ((49, 42), (55, 42)), ((77, 42), (83, 42)), ((105, 42), (109, 42))):
        arrow(ax, a, b)
    box(ax, 27, 8, 40, 16, "Mỗi epoch: đánh giá trên tập validation (15%)\nlưu trạng thái tốt nhất; ReduceLROnPlateau", GREY, 8.8)
    box(ax, 77, 8, 40, 16, "Dừng sớm: val loss không giảm\nsau 20 epoch (tối đa 100 epoch)", GREY, 8.8)
    arrow(ax, (119, 34), (97, 24), rad=0.0)
    arrow(ax, (77, 16), (67, 16))
    arrow(ax, (47, 24), (38, 34), "lặp theo lô 32 đồ thị", off=(-12, -1.5), fs=8.5, rad=0.2)
    ax.text(65, 54, "Quy trình huấn luyện GCN", ha="center", fontsize=11, fontweight="bold")
    save(fig, "fig_train")


# ---------------------------------------------------------------------------
# Hình kết quả
# ---------------------------------------------------------------------------

SHORT = ["TF-IDF", "SBERT", "MLP\n(SBERT)", "GCN", "Hybrid\ntuyến tính", "Đề xuất\n(GCN+LLM+GBM)"]


def fig_results():
    d = json.load(open(os.path.join(RES, "by_jd.json"), encoding="utf-8"))["rows"][:6]
    cols = ["#9AA5B1", "#7FA6D6", "#5B8FA8", "#E0A458", "#B2C77A", "#C0504D"]
    fig, axs = plt.subplots(1, 2, figsize=(14, 5.2))
    ax = axs[0]
    x = np.arange(len(d))
    wd = 0.27
    for k, (key, lab) in enumerate((("ndcg@5", "NDCG@5"), ("ndcg@10", "NDCG@10"), ("mrr", "MRR"))):
        v = np.array([r[key] for r in d])
        ci = np.array([r[key + "_ci"] for r in d])
        ax.bar(x + (k - 1) * wd, v, wd, yerr=[v - ci[:, 0], ci[:, 1] - v], capsize=2.5, label=lab,
               color=["#8FAADC", "#F4B183", "#A9D18E"][k], ec="#333", lw=0.6, error_kw=dict(lw=0.9))
    ax.set_xticks(x)
    ax.set_xticklabels(SHORT, fontsize=8.6)
    ax.set_ylim(0.4, 1.06)
    ax.set_ylabel("Giá trị độ đo", fontsize=10)
    ax.set_title("(a) NDCG@5, NDCG@10, MRR (khoảng tin cậy 95% bootstrap theo JD)", fontsize=10)
    ax.legend(loc="upper left", fontsize=9, ncol=3)
    ax.grid(axis="y", alpha=0.3)
    ax = axs[1]
    ks = [1, 3, 5, 10]
    for r, c, m in zip(d, cols, "osv^Dp"):
        ax.plot(ks, [r["ndcg@%d" % k] for k in ks], marker=m, color=c, lw=2 if r is d[-1] else 1.5, label=r["method"])
    ax.set_xticks(ks)
    ax.set_xlabel("K (số CV đứng đầu danh sách của một JD)", fontsize=10)
    ax.set_ylabel("NDCG@K", fontsize=10)
    ax.set_title("(b) NDCG@K theo K", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    save(fig, "fig_results")


def fig_confusion():
    A = json.load(open(os.path.join(RES, "analysis.json"), encoding="utf-8"))["errors"]
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, key, title in ((axs[0], "confusion_gcn", "GCN đơn (ngưỡng hiệu chỉnh)"), (axs[1], "confusion_stack", "Mô hình đề xuất (làm tròn)")):
        m = np.array(A[key], float)
        pct = m / m.sum(1, keepdims=True)
        ax.imshow(pct, cmap="Blues", vmin=0, vmax=1)
        for i in range(4):
            for j in range(4):
                ax.text(j, i, f"{int(m[i, j])}\n({pct[i, j] * 100:.0f}%)", ha="center", va="center", fontsize=9, color="white" if pct[i, j] > 0.55 else "black")
        ax.set_xticks(range(4)); ax.set_yticks(range(4))
        ax.set_xlabel("Mức dự đoán", fontsize=10); ax.set_ylabel("Mức thật", fontsize=10)
        ax.set_title(title, fontsize=10.5)
    fig.tight_layout()
    save(fig, "fig_confusion")


def fig_importance():
    imp = json.load(open(os.path.join(RES, "analysis.json"), encoding="utf-8"))["importance"]
    imp = sorted(imp, key=lambda r: r["importance"])
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    vals = [r["importance"] for r in imp]
    ax.barh([r["feature"] for r in imp], vals, color=["#C0504D" if "LLM" in r["feature"] else "#4F81BD" if "GCN" in r["feature"] else "#9BBB59" for r in imp], ec="#333", lw=0.5)
    for i, v in enumerate(vals):
        ax.text(max(v, 0) + 0.005, i, f"{v:.3f}", va="center", fontsize=8)
    ax.set_xlabel("Mức tăng MSE của điểm dự đoán khi hoán vị đặc trưng (permutation importance)", fontsize=9.5)
    ax.grid(axis="x", alpha=0.3)
    ax.tick_params(axis="y", labelsize=8.6)
    fig.tight_layout()
    save(fig, "fig_importance")


if __name__ == "__main__":
    for f in (fig_ipo, fig_arch, fig_embed, fig_graph_steps, fig_train, fig_results, fig_confusion, fig_importance):
        f()
        print("ok", f.__name__)
