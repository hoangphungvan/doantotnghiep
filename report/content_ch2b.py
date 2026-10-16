"""Chương 2, mục 2.4 – 2.6, tài liệu tham khảo và phụ lục."""

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
GITHUB = "https://github.com/hoangphungvan/doantotnghiep"


def c(x, n=3):
    return f"{x:.{n}f}".replace(".", ",")


def build(R):
    A = json.load(open(os.path.join(RES, "analysis.json"), encoding="utf-8"))
    EX, ER, IMP, CX = A["example"], A["errors"], A["importance"], A["complexity"]
    MR = json.load(open(os.path.join(RES, "main_results.json"), encoding="utf-8"))
    AB = json.load(open(os.path.join(RES, "ablation.json"), encoding="utf-8"))
    rows = {r["method"]: r for r in MR["rows"]}
    P, H, B = R.para, R.heading, R.bullet
    ref = lambda k: R.ref(k)

    # ================================================================== 2.4
    H("2.4. Huấn luyện mạng GCN (khối M4)", 2)
    P(r"Mục này trình bày mạng GCN theo bốn giai đoạn của một vòng huấn luyện: khởi tạo tham số, lan truyền xuôi, tính hàm mất mát và lan truyền ngược (Hình 2.4). "
      r"Đầu vào là đồ thị $G_{ik}$ ở mục 2.3 (ma trận $\mathbf{X}$ và các cạnh có trọng số), đầu ra là điểm đồ thị $s_{\mathrm{GCN}}\in(0,1)$.")
    R.figure("figures/fig_train.png", r"Quy trình huấn luyện GCN: khởi tạo, lan truyền xuôi, hàm mất mát, lan truyền ngược, cập nhật Adam và dừng sớm.", width_cm=15.5, label="fig_train")

    H("2.4.1. Khởi tạo tham số", 3)
    P(r"Mạng có 272.129 tham số học được (khoảng 1,1 MB). Các trọng số của lớp GCNConv được khởi tạo theo Glorot (Xavier) đồng nhất [26], các lớp tuyến tính theo khởi tạo mặc định của PyTorch "
      r"(Kaiming đồng nhất [27]), hệ số của LayerNorm [16] khởi tạo $\gamma=1$, $\beta=0$; hạt giống ngẫu nhiên cố định để tái lập. Bảng 2.%s thống kê kích thước các thành phần." % ref("t_params").split(".")[1])
    R.table(["Thành phần", "Kích thước (vào → ra)", "Số tham số"],
            [["Pre-aggregation: Linear + LayerNorm + ReLU", "1152 → 128", "147.840"],
             ["3 × [GCNConv + LayerNorm + ReLU + Dropout 0,3 + residual]", "128 → 128 (mỗi lớp)", "50.304"],
             ["Readout: ghép [$h_c$, $h_j$, $h_c-h_j$, $h_c\\odot h_j$]", "4 × 128 = 512", "0"],
             ["MLP cặp: Linear–ReLU–Dropout–Linear–ReLU–Dropout–Linear", "512 → 128 → 64 → 1", "73.985"],
             ["Tổng", "", "272.129"]],
            "Cấu trúc và số tham số của mạng GCN.", widths=[8.6, 4.4, 3.0], size=10.5, label="t_params", bold_rows=(4,))

    H("2.4.2. Lan truyền xuôi (forward propagation)", 3)
    P(r"**Pre-aggregation.** Do vector nhóm có 1152 chiều còn nhiều nút trống (bằng 0), trước hết chiếu mọi nút về không gian 128 chiều chung:")
    R.equation(r"\mathbf{H}^{(0)}=\mathrm{ReLU}\big(\mathrm{LN}(\mathbf{X}\mathbf{W}_0+\mathbf{b}_0)\big),\quad \mathbf{W}_0\in\mathbb{R}^{1152\times128}", "e_pre")
    R.where(['$\\mathbf{X}$: ma trận đặc trưng nút (14×1152); $\\mathbf{W}_0,\\mathbf{b}_0$: ma trận và vector độ lệch học được.', '$\\mathrm{LN}$: LayerNorm; $\\mathrm{ReLU}$: hàm kích hoạt; $\\mathbf{H}^{(0)}$: biểu diễn nút sau bước chiếu (14×128).'])
    P(r"trong đó LN là LayerNorm (chuẩn hóa từng nút theo 128 chiều) [16], ReLU$(z)=\max(0,z)$. Đầu ra $\mathbf{H}^{(0)}\in\mathbb{R}^{14\times128}$ là đầu vào của các lớp GCN.")
    P(r"**Lớp GCNConv.** Mỗi lớp cập nhật biểu diễn của nút bằng tổng có trọng số các biểu diễn của chính nó và các nút kề, theo công thức của Kipf và Welling [12] có dùng trọng số cạnh $w_{uv}$. "
      r"Thêm vòng lặp tự thân (trọng số 1) và chuẩn hóa đối xứng theo bậc:")
    R.equation(r"\hat{A}_{vu}=\frac{w_{uv}}{\sqrt{\tilde d_u\,\tilde d_v}},\qquad \hat{A}_{vv}=\frac{1}{\tilde d_v},\qquad \tilde d_v=1+\sum_{u}w_{uv}", "e_gcn_norm")
    R.where(['$w_{uv}$: trọng số cạnh $u\\to v$ ở mục 2.3; $\\hat{A}_{vu}$: hệ số mà nút $v$ nhận từ nút $u$.', '$\\tilde d_v$: tổng trọng số các cạnh đi vào nút $v$ cộng 1 (vòng lặp tự thân); chia cho $\\sqrt{\\tilde d_u\\tilde d_v}$ để nút nhiều cạnh không lấn át.'])
    R.equation(r"\mathbf{H}^{(l)}=\mathbf{H}^{(l-1)}+\mathrm{Drop}\Big(\mathrm{ReLU}\big(\mathrm{LN}(\hat{\mathbf{A}}\,\mathbf{H}^{(l-1)}\mathbf{W}_l+\mathbf{b}_l)\big)\Big),\qquad l=1,2,3", "e_layer")
    R.where(['$\\mathbf{H}^{(l)}$: biểu diễn các nút sau lớp $l$ ($\\mathbf{H}^{(l-1)}$: trước lớp đó); $\\hat{\\mathbf{A}}$: ma trận hệ số lan truyền.', '$\\mathbf{W}_l,\\mathbf{b}_l$: tham số học được; $\\mathrm{Drop}$: dropout; cộng $\\mathbf{H}^{(l-1)}$ là kết nối residual.'])
    P(r"Ý nghĩa: $\hat{\mathbf{A}}\mathbf{H}^{(l-1)}$ cho mỗi nút một trung bình có trọng số của các nút lân cận (lan truyền thông tin); $\mathbf{W}_l\in\mathbb{R}^{128\times128}$ là ma trận học được biến đổi đặc trưng; "
      r"LN và ReLU ổn định và phi tuyến hóa; Drop (xác suất 0,3) giảm quá khớp; số hạng $\mathbf{H}^{(l-1)}$ cộng thêm là kết nối residual giữ lại thông tin của lớp trước. "
      r"Sau 3 lớp, mỗi nút đã tổng hợp thông tin từ các nút cách tối đa 3 cạnh; vì đồ thị dày (mật độ cạnh " + c(EX["adj_density"], 2) + r"), thông tin của cả 14 nút đã ảnh hưởng đến nút trung tâm.")
    deg = {}
    for (s, d), w in zip(EX["edges"], EX["edge_w"]):
        deg[d] = deg.get(d, 0.0) + w
    dt = {v: 1 + x for v, x in deg.items()}
    coefs = []
    for (s, d), w in zip(EX["edges"], EX["edge_w"]):
        if d == 0:
            coefs.append((s, w / math.sqrt(dt[s] * dt[0])))
    coefs.append((0, 1 / dt[0]))
    coefs.sort(key=lambda t: -t[1])
    nm = {0: "chính nút 0 (CV)", 1: "nút 1 (JD)", 7: "nút 7 (role CV)", 13: "nút 13 (role JD)", 3: "nút 3 (hard CV)", 9: "nút 9 (hard JD)", 5: "nút 5 (field CV)", 11: "nút 11 (field JD)"}
    P(r"**Ví dụ (cặp ví dụ, nút trung tâm CV).** Hệ số lan truyền $\hat{A}_{0u}$ lớn nhất vào nút 0 lần lượt là: " +
      "; ".join(f"{nm.get(u, 'nút %d' % u)} {c(v, 3)}" for u, v in coefs[:5]) +
      r". Nghĩa là biểu diễn mới của nút CV chủ yếu đến từ chính nó, nút JD và các nhóm quan trọng (role, hard_skills), đúng với ý đồ đặt $\lambda_t$ cao cho các nhóm này.")
    P(r"**Readout và MLP cặp.** Lấy biểu diễn của hai nút trung tâm $\mathbf{h}_c=\mathbf{H}^{(3)}_{0}$ và $\mathbf{h}_j=\mathbf{H}^{(3)}_{1}$, ghép thêm hiệu và tích từng phần tử để mạng thấy trực tiếp sự khác nhau và giống nhau giữa CV và JD:")
    R.equation(r"\mathbf{r}=\big[\mathbf{h}_c\,\big\|\,\mathbf{h}_j\,\big\|\,\mathbf{h}_c-\mathbf{h}_j\,\big\|\,\mathbf{h}_c\odot\mathbf{h}_j\big]\in\mathbb{R}^{512}", "e_readout")
    R.where(['$\\mathbf{h}_c,\\mathbf{h}_j$: biểu diễn cuối của nút CV và nút JD; $\\mathbf{r}$: vector đầu vào MLP (512 chiều).', '$\\mathbf{h}_c-\\mathbf{h}_j$: sự khác nhau; $\\mathbf{h}_c\\odot\\mathbf{h}_j$: tích từng phần tử (sự giống nhau).'])
    R.equation(r"z=\mathbf{w}_3^{\top}\,\mathrm{ReLU}\big(\mathbf{W}_2\,\mathrm{ReLU}(\mathbf{W}_1\mathbf{r}+\mathbf{b}_1)+\mathbf{b}_2\big)+b_3,\qquad s_{\mathrm{GCN}}=\sigma(z)=\frac{1}{1+e^{-z}}", "e_mlp")
    R.where(['$\\mathbf{W}_1,\\mathbf{W}_2,\\mathbf{w}_3$ và $\\mathbf{b}_1,\\mathbf{b}_2,b_3$: tham số của MLP (512 → 128 → 64 → 1).', '$z$: logit; $\\sigma(z)$: hàm sigmoid đưa $z$ về $(0,1)$; $s_{\\mathrm{GCN}}$: điểm đồ thị.'])
    P(r"$z$ là logit, $\sigma$ là hàm sigmoid đưa về khoảng $(0,1)$. Với cặp ví dụ, mạng cho $s_{\mathrm{GCN}}=" + c(EX["result"]["gcn_score"]) + r"$.")

    H("2.4.3. Hàm mất mát", 3)
    P(r"Nhãn mức phù hợp $g\in\{0,1,2,3\}$ có thứ tự, nên thay vì phân loại cứng, đề tài dùng nhãn mềm $y=g/3\in\{0,\tfrac13,\tfrac23,1\}$ và hàm mất mát entropy chéo nhị phân trên logit (BCEWithLogits), "
      r"giúp điểm $s_{\mathrm{GCN}}$ tăng đơn điệu theo mức phù hợp và dùng trực tiếp để xếp hạng:")
    R.equation(r"y_b=\frac{g_b}{3}", "e_target")
    R.where(['$g_b$: nhãn mức (0–3) của đồ thị $b$; $y_b$: nhãn mềm trong $[0,1]$.'])
    R.equation(r"\mathcal{L}=-\frac{1}{B}\sum_{b=1}^{B}\Big[y_b\log\sigma(z_b)+(1-y_b)\log\big(1-\sigma(z_b)\big)\Big]", "e_loss")
    p = EX["result"]["gcn_score"]
    P(r"trong đó $B$ là số đồ thị của một lô (32), $z_b$ và $y_b$ là logit và nhãn mềm của đồ thị thứ $b$. **Ví dụ:** với $s_{\mathrm{GCN}}=" + c(p) + r"$ và nhãn mức 3 ($y=1$), "
      r"mất mát của cặp là $-\ln " + c(p) + r"=" + c(-math.log(p)) + r"$; nếu nhãn là mức 2 ($y=\tfrac23$) thì mất mát là $" + c(-(2 / 3 * math.log(p) + 1 / 3 * math.log(1 - p))) +
      r"$. Mất mát lớn hơn ở nhãn cao cho thấy mạng đang đánh giá thấp cặp này (điều mà bộ tổng hợp điểm ở mục 2.5 hiệu chỉnh).")

    H("2.4.4. Lan truyền ngược và cập nhật tham số", 3)
    P(r"Gradient của mất mát theo logit có dạng đơn giản nhờ kết hợp sigmoid với entropy chéo; sau đó quy tắc chuỗi lan truyền ngược qua MLP, readout, các lớp GCN (qua $\hat{\mathbf{A}}$, LayerNorm, ReLU, residual) "
      r"tới pre-aggregation (PyTorch autograd tính tự động):")
    R.equation(r"\frac{\partial\mathcal{L}}{\partial z_b}=\frac{1}{B}\big(\sigma(z_b)-y_b\big),\qquad \nabla_{\theta}\mathcal{L}=\sum_{b=1}^{B}\frac{\partial\mathcal{L}}{\partial z_b}\,\frac{\partial z_b}{\partial\theta}", "e_grad")
    R.where(['$\\partial\\mathcal{L}/\\partial z_b$: độ nhạy của mất mát theo logit của đồ thị $b$.', '$\\theta$: toàn bộ tham số mạng; $\\partial z_b/\\partial\\theta$: tính bằng quy tắc chuỗi (PyTorch autograd).'])
    P(r"Gradient được cắt theo chuẩn để tránh bùng nổ, rồi tham số được cập nhật bằng Adam [17] với phân rã trọng số (weight decay) $\lambda$ cộng vào gradient:")
    R.equation(r"\mathbf{g}\leftarrow\mathbf{g}\cdot\min\Big(1,\ \frac{1}{\lVert\mathbf{g}\rVert}\Big)", "e_clip")
    R.where(['$\\mathbf{g}$: vector gradient; nếu $\\lVert\\mathbf{g}\\rVert>1$ thì thu nhỏ về độ dài 1 để tránh cập nhật quá lớn.'])
    R.equation(r"\mathbf{g}_t=\nabla_{\theta}\mathcal{L}+\lambda\theta_{t-1},\quad \mathbf{m}_t=\beta_1\mathbf{m}_{t-1}+(1-\beta_1)\mathbf{g}_t,\quad \mathbf{v}_t=\beta_2\mathbf{v}_{t-1}+(1-\beta_2)\mathbf{g}_t^{2}", "e_adam1")
    R.where(['$\\lambda$: weight decay; $\\theta_{t-1}$: tham số ở bước trước; $\\mathbf{g}_t$: gradient đã cộng phân rã.', '$\\mathbf{m}_t,\\mathbf{v}_t$: trung bình trượt của gradient và của bình phương gradient; $\\beta_1,\\beta_2$: hệ số trượt.'])
    R.equation(r"\theta_t=\theta_{t-1}-\eta\,\frac{\mathbf{m}_t/(1-\beta_1^{t})}{\sqrt{\mathbf{v}_t/(1-\beta_2^{t})}+\epsilon}", "e_adam2")
    R.where(['$\\eta$: tốc độ học; $\\epsilon$: hằng số nhỏ tránh chia cho 0; $1-\\beta^{t}$: hiệu chỉnh độ lệch ở các bước đầu.'])
    P(r"Với $\eta=10^{-3}$ (giảm một nửa khi val loss đi ngang 5 epoch), $\lambda=10^{-4}$, $\beta_1=0,9$, $\beta_2=0,999$. Mỗi epoch duyệt hết tập huấn luyện theo lô 32 đồ thị rồi tính mất mát trên tập validation; "
      r"trạng thái tốt nhất được lưu và huấn luyện dừng nếu val loss không cải thiện sau 20 epoch (tối đa 100 epoch).")

    # ================================================================== 2.5
    H("2.5. Thiết kế công thức tính điểm tổng hợp (Hybrid Score) tối ưu theo NDCG và Recall", 2)
    P(r"Điểm đồ thị $s_{\mathrm{GCN}}$ phân biệt tốt chủ đề và vai trò nhưng yếu khi phân biệt các mức phù hợp sát nhau trong cùng vai trò (mục 2.6.3). Mục này trình bày hai cách tổng hợp: "
      r"công thức Hybrid tuyến tính đơn giản (2.5.1) và mô hình xếp chồng cuối cùng (2.5.2). Cả hai được tối ưu theo mục tiêu xếp hạng, không phải theo độ chính xác phân loại.")
    H("2.5.1. Hybrid tuyến tính và tối ưu hệ số trộn theo NDCG", 3)
    P(r"Hai điểm có thang đo khác nhau ($s_{\mathrm{GCN}}\in(0,1)$ còn cosine thường tập trung trong khoảng hẹp), nên điểm ngữ nghĩa được chuẩn hóa min–max về $[0,1]$ theo tập huấn luyện rồi trộn tuyến tính:")
    R.equation(r"\tilde{s}_{\mathrm{sem}}=\mathrm{clip}\Big(\frac{s_{\mathrm{sem}}-s_{\min}}{s_{\max}-s_{\min}},\,0,\,1\Big)", "e_norm")
    R.where(['$s_{\\mathrm{sem}}$: điểm ngữ nghĩa; $s_{\\min},s_{\\max}$: giá trị nhỏ nhất, lớn nhất trên tập huấn luyện; $\\tilde{s}_{\\mathrm{sem}}$: điểm sau chuẩn hóa về $[0,1]$.', '$\\mathrm{clip}(x,0,1)$: cắt $x$ vào đoạn $[0,1]$.'])
    R.equation(r"S_{\alpha}(c,j)=\alpha\,s_{\mathrm{GCN}}(c,j)+(1-\alpha)\,\tilde{s}_{\mathrm{sem}}(c,j),\qquad \alpha\in[0,1]", "e_hyb")
    R.where(['$S_{\\alpha}$: điểm Hybrid; $s_{\\mathrm{GCN}}$: điểm đồ thị; $\\tilde{s}_{\\mathrm{sem}}$: điểm ngữ nghĩa chuẩn hóa; $\\alpha$: hệ số trộn.'])
    P(r"Ý nghĩa: $\alpha$ là hệ số tin cậy dành cho tín hiệu cấu trúc đồ thị, $1-\alpha$ dành cho tín hiệu ngữ nghĩa toàn văn. Vì tiêu chí cuối cùng là chất lượng xếp hạng, $\alpha$ được chọn để tối đa NDCG@10 trung bình "
      r"trên tập huấn luyện $Q$ (lưới 0; 0,05; …; 1), không dùng dữ liệu của CV đang kiểm tra:")
    R.equation(r"\alpha^{*}=\argmax_{\alpha}\ \frac{1}{|Q|}\sum_{c\in Q}\mathrm{NDCG@10}\big(c;\,S_{\alpha}\big)", "e_alpha")
    R.where(['$Q$: tập các danh sách xếp hạng dùng để chọn $\\alpha$ (trên tập huấn luyện); $\\mathrm{NDCG@10}(\\cdot\\,;S_{\\alpha})$: NDCG@10 của danh sách xếp theo $S_{\\alpha}$.', '$\\alpha^{*}$: giá trị $\\alpha$ cho NDCG@10 trung bình cao nhất.'])
    P(r"NDCG@10 được chọn vì nó dùng nhãn có thứ bậc và nhấn mạnh các vị trí đầu danh sách, đồng thời Recall@K và MRR (mục 2.6.2.3) cũng cải thiện khi các mục phù hợp được đẩy lên đầu danh sách. "
      r"Trong thực nghiệm, $\alpha^{*}$ ở 5 lượt kiểm tra là " + ", ".join(c(a, 1) for a in MR["alphas"]) + r" (trung bình 0,68), nghĩa là điểm đồ thị được ưu tiên hơn nhưng điểm ngữ nghĩa vẫn đóng góp.")
    P(r"**Ghi chú về “mức thưởng tối đa 0,10” và công thức điểm đồ thị có thưởng chứng chỉ trong bản thảo trước.** Bản thảo trước có bước cộng thêm điểm thưởng chứng chỉ vào điểm đồ thị, với mức thưởng tối đa là hằng số 0,10 đặt thủ công. "
      r"Hằng số này không được xác định từ dữ liệu, và trong cài đặt hiện tại cơ chế chứng chỉ không còn (không có nút chứng chỉ, điều kiện cứng được LLM đánh giá riêng thành đặc trưng $\varphi_4$ ở dưới). "
      r"Vì vậy công thức điểm đồ thị có thưởng chứng chỉ được bỏ; việc cân đối giữa các tín hiệu nay do mô hình xếp chồng học từ dữ liệu thay cho các hằng số cố định.")
    H("2.5.2. Mô hình xếp chồng GCN + LLM + Gradient Boosting (điểm cuối)", 3)
    P(r"Điểm đồ thị bỏ sót hai tín hiệu quyết định nhãn: độ phủ yêu cầu bắt buộc và điều kiện cứng/cấp độ. Khối M5a gọi LLM một lần cho mỗi cặp (khi huấn luyện: một lần cho 15 JD của một CV) để đối chiếu từng yêu cầu, "
      r"rồi tạo sáu đặc trưng cặp: (1) $\varphi_1$ độ phủ = số yêu cầu bắt buộc đáp ứng / tổng số yêu cầu (0,5 nếu JD không nêu yêu cầu chuyên môn); (2) $\varphi_2$ số yêu cầu; "
      r"(3) $\varphi_3=\min(\max(0,a_j-a_c),6)/6$ với $a_j$ là số năm tối thiểu JD yêu cầu và $a_c$ số năm của CV; (4) $\varphi_4$ số điều kiện cứng (bằng cấp, chứng chỉ) chưa đáp ứng; "
      r"(5) $\varphi_5=1$ nếu công nghệ nêu trong chức danh JD không có trong CV; (6) $\varphi_6=1$ nếu phản hồi LLM hợp lệ. Vector đầu vào của bộ tổng hợp gồm 14 thành phần:")
    R.equation(r"\mathbf{z}_{ik}=\big[\varphi_1,\ldots,\varphi_6\ \big\|\ \kappa_0,\kappa_1,\ldots,\kappa_6\ \big\|\ s_{\mathrm{GCN}}\big]\in\mathbb{R}^{14}", "e_z")
    R.where(['$\\varphi_1,\\ldots,\\varphi_6$: sáu đặc trưng cặp do LLM đánh giá (độ phủ, số yêu cầu, lệch kinh nghiệm, điều kiện cứng chưa đáp ứng, công nghệ tiêu đề thiếu, hợp lệ).', '$\\kappa_0,\\ldots,\\kappa_6$: bảy cosine (toàn văn và sáu nhóm); $s_{\\mathrm{GCN}}$: điểm đồ thị out-of-fold.'])
    P(r"trong đó $\kappa_0=s_{\mathrm{sem}}$ (công thức 2." + ref("e_ssem").split(".")[1] + r") là cosine toàn văn, $\kappa_t$ ($t=1..6$) là cosine giữa hai vector trung bình nhóm loại $t$ của CV và JD, "
      r"và $s_{\mathrm{GCN}}$ là điểm GCN out-of-fold (tính trên dữ liệu mà GCN chưa huấn luyện, tránh rò rỉ). Mô hình Gradient Boosting [19][20] hồi quy trực tiếp mức phù hợp:")
    R.equation(r"s^{*}=F_M(\mathbf{z})=F_0+\nu\sum_{m=1}^{M}h_m(\mathbf{z}),\qquad \hat{y}=\min\big(3,\max(0,\mathrm{round}(s^{*}))\big)", "e_gbm")
    R.where(['$F_M$: mô hình Gradient Boosting gồm $M$ cây; $F_0$: giá trị khởi đầu (trung bình nhãn); $h_m$: cây thứ $m$; $\\nu$: tốc độ học.', '$s^{*}$: điểm cuối; $\\hat{y}$: mức phù hợp sau khi làm tròn và cắt vào $[0,3]$.'])
    P(r"$h_m$ là cây quyết định độ sâu 4 được thêm tuần tự để giảm sai số bình phương còn lại, $M=200$ cây, tốc độ học $\nu=0,05$. Đây là kỹ thuật xếp chồng (stacked generalization) [21]: tầng 1 gồm GCN và LLM, tầng 2 là bộ tổng hợp. "
      r"Điểm $s^{*}$ dùng để sắp xếp các CV của cùng một JD; $\hat{y}$ là mức đọc nhanh. Dù hàm mất mát là sai số bình phương, ta đánh giá và chọn cấu hình theo NDCG và Recall (mục 2.6) vì "
      r"mục tiêu cuối cùng là thứ tự JD.")
    ex = EX["pf_vector"]
    P(r"**Ví dụ.** Với cặp ví dụ, LLM đánh giá 5/5 yêu cầu bắt buộc được đáp ứng và điều kiện học vấn được đáp ứng: $\varphi=(1,0;\ 5;\ 0;\ 0;\ 0;\ 1)$ (CV có 3 năm, JD yêu cầu 2 năm nên $\varphi_3=0$); "
      r"bảy cosine là $(" + "; ".join(c(x, 2) for x in EX["topic_features"]) + r")$ và $s_{\mathrm{GCN}}=" + c(EX["result"]["gcn_score"]) + r"$. Bộ tổng hợp cho mức " + str(EX["result"]["grade"]) +
      r" (Phù hợp tốt): độ phủ đầy đủ kéo điểm lên dù điểm GCN riêng lẻ chỉ " + c(EX["result"]["gcn_score"], 2) + r".")
    H("2.5.3. Diễn giải cho nhà tuyển dụng (khối M7)", 3)
    P(r"Kết quả đối chiếu của M5a được dùng lại để sinh diễn giải, nên lời giải thích luôn nhất quán với mức điểm. Với cặp ví dụ, hệ thống trả về (tiếng Việt):")
    R.code(EX["explanation_vi"])
    P(r"Bản tiếng Anh có cùng nội dung (“Verdict: Strong match (level 3/3), worth interviewing …”). Phần so khớp thực thể kỹ thuật chi tiết được giữ riêng cho người dùng cần xem sâu.")

    H("2.5.4. Cách tích hợp với backend: chấm điểm từng cặp, xếp hạng ở bên ngoài", 3)
    P(r"Hệ thống chỉ xử lý **một cặp CV–JD mỗi lần gọi** (hàm predict_from_text của lớp CJMPredictor) và không tự trả danh sách xếp hạng. Danh sách CV của một JD được tạo ở ứng dụng gọi: "
      r"backend gửi lần lượt từng cặp $(c_i,j)$ cho hệ thống, nhận kết quả từng cặp, rồi sắp xếp các CV theo điểm giảm dần (công thức 1." + ref("e_rank").split(".")[1] + r"). Bảng " + ref("t_api") + r" liệt kê các trường kết quả của một cặp.")
    R.table(["Trường", "Ý nghĩa", "Dùng để"],
            [["score", "Điểm phù hợp của cặp, trong khoảng [0; 1] (ở chế độ stacker bằng $s^{*}/3$ cắt vào [0; 1])", "Sắp xếp CV"],
             ["grade, grade_label", "Mức phù hợp 0–3 và tên mức (Không phù hợp … Phù hợp tốt)", "Hiển thị nhãn nhanh"],
             ["explanation", "Diễn giải ngắn cho nhà tuyển dụng (tiếng Việt, tiếng Anh)", "Hiển thị lý do"],
             ["mode", "“stacker” (đầy đủ, có LLM) hoặc “gcn” (dự phòng khi không dùng được LLM)", "Kiểm tra tính so sánh được"],
             ["gcn_score", "Điểm riêng của mạng GCN", "Tiêu chí phụ khi hòa điểm"]],
            "Các trường kết quả chính của một cặp CV–JD.", widths=[3.2, 9.4, 3.4], size=10, label="t_api")
    P(r"**Cách dùng đúng.** Nhận định rằng backend gửi từng cặp rồi xếp hạng theo điểm là đúng với thiết kế hiện tại. Có ba lưu ý khi xếp hạng: (1) chỉ so sánh điểm cùng chế độ; "
      r"điểm ở chế độ “gcn” là sigmoid của GCN, khác thang với điểm “stacker”, nên một danh sách không nên trộn hai chế độ (nên gọi lại hoặc xếp riêng); (2) điểm bị cắt về tối đa 1,0 nên các CV rất phù hợp "
      r"($s^{*}\geq3$) có thể hòa, khi đó dùng gcn_score hoặc số yêu cầu đã đáp ứng làm tiêu chí phụ; (3) mỗi cặp tốn một lần gọi LLM cho đặc trưng cặp (việc trích xuất thực thể của mỗi CV và JD được lưu đệm nên chỉ gọi một lần), "
      r"vì vậy với $n$ CV cho một JD cần $n$ lần gọi và nên chạy song song hoặc hàng đợi.")

    # ================================================================== 2.6
    H("2.6. Kiểm thử phương pháp đề xuất", 2)
    H("2.6.1. Dữ liệu thực nghiệm", 3)
    P(r"**Bộ dữ liệu của đề tài.** Gồm 104 CV tổng hợp (13 nhóm nghề CNTT × 4 cấp độ Fresher/Junior/Middle/Senior × 2 CV, sinh bằng ChatGPT theo hồ sơ mẫu), 159 JD thật từ bộ VietJobs [23] lĩnh vực CNTT và 1664 cặp CV–JD "
      r"(mỗi CV được ghép với JD cùng nhóm, liền kề, khác khối CNTT và ngoài CNTT). Nhãn mức 0–3 gán theo rubric v1.2: người chấm ghi 4 đặc trưng (vai trò, độ phủ yêu cầu bắt buộc, lệch cấp độ, điều kiện cứng) rồi tính mức bằng bảng quyết định. "
      r"Phân bố nhãn: mức 0: 429; mức 1: 812; mức 2: 256; mức 3: 167. Kiểm chứng mù trên 36 cặp cho khớp chính xác 86,1% (31/36), trong ±1 mức 100%, kappa trọng số bình phương 0,94 [0,87–0,99] [29]; "
      r"hạn chế: chỉ một người chấm kiểm và mẫu cân bằng theo mức nên kappa cao hơn mẫu tự nhiên.")
    R.table(["Mức", "Tên", "Ý nghĩa", "Số cặp"],
            [["3", "Phù hợp tốt", "Cùng vai trò, đáp ứng phần lớn yêu cầu bắt buộc, đủ cấp độ", "167"],
             ["2", "Phù hợp một phần", "Đáng cân nhắc nhưng thiếu yêu cầu quan trọng hoặc lệch cấp", "256"],
             ["1", "Liên quan ngành", "Cùng ngành/vai trò nhưng thiếu phần lớn yêu cầu", "812"],
             ["0", "Không phù hợp", "Khác hẳn lĩnh vực", "429"]],
            "Thang nhãn mức phù hợp của bộ dữ liệu đề tài.", widths=[1.5, 3.5, 9.0, 2.0], size=10.5, label="t_labels")
    P(r"**Các bộ dữ liệu công khai liên quan.** Bảng " + ref("t_public") + r" mô tả các bộ dữ liệu công khai có thể dùng cho bài toán và đặc thù của từng bộ so với nhu cầu của đề tài.")
    R.table(["Bộ dữ liệu", "Nội dung và quy mô", "Đặc thù", "Vai trò với đề tài"],
            [["VietJobs [23] (Hugging Face)", "Tin tuyển dụng tiếng Việt nhiều ngành", "Văn bản JD thật, tiếng Việt xen thuật ngữ Anh; không có CV và nhãn ghép cặp", "Nguồn của 159 JD đã dùng"],
             ["JobBERT evaluation dataset [24] (Hugging Face)", "Hơn 10 nghìn tiêu đề tin tuyển dụng, mỗi tiêu đề gán một nghề ESCO v1.0.5; giấy phép MIT", "Tiếng Anh, chỉ có tiêu đề, bài toán chuẩn hóa chức danh nghề; không có CV", "Thực nghiệm bổ sung cho khối embedding (chưa chạy)"],
             ["Resume Dataset (Kaggle/Hugging Face) [25]", "Khoảng một nghìn hồ sơ tiếng Anh gán nhóm nghề", "Chỉ có CV và nhãn nhóm nghề; không có JD và nhãn ghép cặp", "Có thể kiểm tra riêng biểu diễn CV"],
             ["Job2CV (2024)", "Chưa xác định được nguồn công khai", "—", "Chưa thực nghiệm; cần liên kết từ giảng viên"]],
            "Các bộ dữ liệu công khai và đặc thù từng bộ.", widths=[3.6, 4.6, 4.6, 3.2], size=9.5, label="t_public")
    P(r"**Lưu ý trung thực.** Không bộ dữ liệu công khai nào ở trên chứa đồng thời CV, JD và nhãn mức phù hợp theo cặp, nên toàn bộ so sánh chính (mục 2.6.3) thực hiện trên bộ dữ liệu của đề tài. "
      r"Thực nghiệm trên JobBERT dataset và Job2CV theo yêu cầu **chưa được thực hiện** trong bản này: JobBERT dataset là bài toán chuẩn hóa chức danh (có thể dùng để so sánh SBERT với TF-IDF ở bước truy hồi nghề theo tiêu đề, chỉ kiểm tra khối embedding "
      r"chứ không kiểm tra GCN), còn Job2CV chưa tìm được nguồn dữ liệu. Giao thức dự kiến cho JobBERT dataset được nêu ở mục 2.6.3.6.")

    H("2.6.2. Môi trường và phương pháp thực nghiệm", 3)
    H("2.6.2.1. Môi trường thực nghiệm", 4)
    R.table(["Thành phần", "Cấu hình"],
            [["Phần cứng", "Intel Core i3-1115G4 (2 nhân, 4 luồng), RAM 12 GB, không GPU"],
             ["Hệ điều hành / ngôn ngữ", "Windows 11; Python 3.13"],
             ["Thư viện", "PyTorch 2.11.0 (CPU), PyTorch Geometric 2.7.0 [22], scikit-learn 1.8.0, sentence-transformers 5.4.1"],
             ["Embedding", "paraphrase-multilingual-MiniLM-L12-v2 (384 chiều, 117,65 triệu tham số)"],
             ["LLM (trích xuất, đặc trưng cặp)", "gemini-flash-lite-latest qua API tương thích OpenAI; kết quả được lưu đệm"],
             ["Mã nguồn", "%s (nhánh bang-branch); thư mục report/ chứa mã thực nghiệm của báo cáo" % "github.com/hoangphungvan/doantotnghiep"]],
            "Môi trường thực nghiệm.", widths=[4.4, 11.6], size=10.5, label="t_env")
    H("2.6.2.2. Chia dữ liệu và thiết lập siêu tham số", 4)
    P(r"Dữ liệu được chia theo CV: cross-validation 5 lượt (seed 42), mỗi CV nằm trong tập kiểm tra đúng một lần và mọi cặp của CV đó cùng ở tập kiểm tra, nên mô hình không thấy CV kiểm tra khi huấn luyện. "
      r"Trong phần huấn luyện của mỗi lượt, 15% số CV được tách làm tập validation để dừng sớm. Mô hình xếp chồng được đánh giá bằng cross-validation lồng nhau: điểm GCN dùng để huấn luyện bộ tổng hợp "
      r"là điểm out-of-fold của vòng trong. Mọi điểm số báo cáo ở mục 2.6.3 là điểm out-of-fold, tức dự đoán trên CV chưa từng dùng để huấn luyện, và không dùng tập kiểm tra giữ riêng thứ hai nên các siêu tham số ở Bảng " +
      ref("t_hyper") + r" được đặt cố định từ trước, không chỉnh theo kết quả kiểm tra. Khoảng tin cậy 95% lấy bằng bootstrap 500 lần lấy mẫu lại theo CV [28].")
    R.table(["Nhóm", "Tham số", "Giá trị"],
            [["GCN", "Chiều ẩn / số lớp GCNConv / dropout", "128 / 3 / 0,3"],
             ["GCN", "Tốc độ học $\\eta$ / weight decay $\\lambda$", "$10^{-3}$ / $10^{-4}$ (Adam)"],
             ["GCN", "Kích thước lô (batch size)", "32 đồ thị"],
             ["GCN", "Số epoch tối đa / dừng sớm", "100 / val loss không giảm sau 20 epoch"],
             ["GCN", "Lịch giảm tốc độ học", "ReduceLROnPlateau, hệ số 0,5, kiên nhẫn 5 epoch"],
             ["GCN", "Cắt gradient", "chuẩn tối đa 1,0"],
             ["Đồ thị", "k (k-NN) / p (sharpening)", "10 / 4,0"],
             ["Đồ thị", "$\\lambda_t$ (role, hard, field, industry, education, soft)", "3,0 / 2,5 / 2,0 / 1,5 / 1,5 / 1,0"],
             ["Bộ tổng hợp", "Gradient Boosting: số cây / độ sâu / tốc độ học", "200 / 4 / 0,05"],
             ["MLP (baseline)", "Kiến trúc / dropout / tối ưu", "[$u$; $v$; $|u-v|$; $u\\odot v$] 1536 → 256 → 64 → 1 / 0,3 / Adam như GCN (lô 32, tối đa 100 epoch)"],
             ["Ngưỡng ngữ nghĩa", "Cosine tối thiểu để coi hai mục khớp", "0,75"]],
            "Siêu tham số và thiết lập huấn luyện.", widths=[2.6, 7.0, 6.4], size=10, label="t_hyper")

    H("2.6.2.3. Độ đo thực nghiệm", 4)
    P(r"**Độ đo xếp hạng** được tính riêng cho từng JD (danh sách các CV có nhãn với JD đó, sắp theo điểm giảm dần) rồi lấy trung bình trên các JD. Gọi $g_r$ là nhãn của CV ở vị trí $r$:")
    R.equation(r"\mathrm{DCG@}K=\sum_{r=1}^{K}\frac{2^{g_r}-1}{\log_2(r+1)},\qquad \mathrm{NDCG@}K=\frac{\mathrm{DCG@}K}{\mathrm{IDCG@}K}", "e_ndcg")
    R.where(['$K$: số vị trí đầu xét; $g_r$: nhãn của CV ở vị trí $r$ trong danh sách của một JD (đã sắp theo điểm giảm dần).', '$2^{g_r}-1$: độ lợi (nhãn cao thì lợi nhiều); $\\log_2(r+1)$: hệ số giảm theo vị trí; $\\mathrm{IDCG@}K$: DCG của thứ tự lý tưởng.'])
    R.equation(r"\mathrm{Recall@}K=\frac{\big|\mathrm{Top}_K\cap\mathcal{R}\big|}{|\mathcal{R}|},\qquad \mathrm{MRR}=\frac{1}{|Q|}\sum_{j\in Q}\frac{1}{\mathrm{rank}_j}", "e_recall")
    R.where(['$\\mathrm{Top}_K$: $K$ CV đứng đầu danh sách của một JD; $\\mathcal{R}$: tập CV phù hợp (nhãn ≥ 2) của JD đó.', '$Q$: tập các JD dùng để đánh giá; $\\mathrm{rank}_j$: vị trí của CV phù hợp đầu tiên trong danh sách của JD $j$.'])
    P(r"Các giá trị $K\in\{1,3,5,10\}$. NDCG dùng nhãn có thứ bậc; Recall@K cho biết tỉ lệ CV phù hợp đã nằm trong $K$ vị trí đầu; MRR cho biết CV phù hợp đầu tiên nằm cao đến đâu. "
      r"Ngoài ra, để so sánh, báo cáo thêm góc nhìn ngược lại (mỗi CV xếp hạng các JD) ở Bảng " + ref("t_rank_cv") + r".")
    P(r"**Độ đo phân loại** xét bài toán nhị phân “phù hợp” (mức ≥ 2) với TP, FP, TN, FN là số dương thật, dương giả, âm thật, âm giả. Ngưỡng chia của mỗi lượt được chọn trên bốn lượt còn lại để tối đa F1 (cross-fit), không dùng nhãn lượt kiểm tra:")
    R.equation(r"\mathrm{Accuracy}=\frac{TP+TN}{TP+TN+FP+FN},\qquad \mathrm{Precision}=\frac{TP}{TP+FP}", "e_cls1")
    R.where(['$TP,TN,FP,FN$: số cặp dương thật, âm thật, dương giả, âm giả (dương là cặp phù hợp, nhãn ≥ 2).'])
    R.equation(r"\mathrm{Recall}=\frac{TP}{TP+FN},\qquad \mathrm{F1}=\frac{2\cdot\mathrm{Precision}\cdot\mathrm{Recall}}{\mathrm{Precision}+\mathrm{Recall}}", "e_cls2")
    R.where(['Precision: trong các cặp được báo là phù hợp, bao nhiêu cặp đúng; Recall: trong các cặp thật sự phù hợp, bao nhiêu cặp được tìm ra; F1: trung bình điều hòa của hai đại lượng.'])
    R.equation(r"\mathrm{AUC\text{-}ROC}=\frac{1}{|\mathcal{P}||\mathcal{N}|}\sum_{p\in\mathcal{P}}\sum_{n\in\mathcal{N}}\Big[\mathbb{1}(s_p>s_n)+\tfrac12\,\mathbb{1}(s_p=s_n)\Big]", "e_auc")
    R.where(['$\\mathcal{P},\\mathcal{N}$: tập cặp phù hợp và không phù hợp; $s_p,s_n$: điểm của một cặp thuộc mỗi tập; $\\mathbb{1}(\\cdot)$: bằng 1 nếu điều kiện đúng, 0 nếu sai.'])
    P(r"AUC-ROC là xác suất một cặp phù hợp ($\mathcal{P}$) có điểm cao hơn một cặp không phù hợp ($\mathcal{N}$), không phụ thuộc ngưỡng. Ngoài ra với dự đoán mức 0–3 báo cáo độ chính xác khớp chính xác và trong ±1 mức.")

    H("2.6.2.4. Các phương pháp cơ sở", 4)
    B("**TF-IDF + cosine** [1]: cosine giữa vector TF-IDF của văn bản thực thể CV và JD (không học).")
    B("**SBERT + cosine** [5][6]: điểm ngữ nghĩa $s_{\\mathrm{sem}}$ ở công thức 2." + ref("e_ssem").split(".")[1] + " (không học).")
    B("**MLP (SBERT)** (baseline học sâu): mạng nơ-ron truyền thẳng nhận vector SBERT của CV ($u$) và JD ($v$) dưới dạng $[u;v;|u-v|;u\\odot v]$, huấn luyện cùng nhãn mềm $y=g/3$ và cùng quy trình với GCN. Đây là đối chứng không dùng đồ thị. "
      "(Chưa có BiLSTM; MLP được chọn vì cùng đầu vào embedding nên so sánh công bằng với GCN.)")
    B("**GCN**: mạng đồ thị ở mục 2.4, chỉ dùng điểm đồ thị.")
    B("**Hybrid tuyến tính (GCN + SBERT)**: công thức 2." + ref("e_hyb").split(".")[1] + " với $\\alpha^{*}$ chọn theo NDCG@10.")
    B("**Mô hình đề xuất (GCN + LLM + GBM)**: công thức 2." + ref("e_gbm").split(".")[1] + ".")

    H("2.6.3. Đánh giá thực nghiệm và phân tích kết quả", 3)
    H("2.6.3.1. Kết quả độ chính xác", 4)
    JDR = json.load(open(os.path.join(RES, "by_jd.json"), encoding="utf-8"))
    jr = {r["method"]: r for r in JDR["rows"]}
    names = list(rows)
    PR = "Mô hình đề xuất (GCN + LLM + GBM)"

    def jv(n, k, nd=2):
        return c(jr[n][k], nd)

    def jci(n, k):
        return f'{c(jr[n][k][0], 2)}–{c(jr[n][k][1], 2)}'

    P(r"**Cách đánh giá.** Mỗi truy vấn là một JD: các CV có nhãn với JD đó được sắp xếp theo điểm giảm dần rồi so với nhãn thật. Trong 159 JD, giữ " + str(JDR["n_jd"]) +
      r" JD có ít nhất 2 CV và ít nhất một CV phù hợp (mức ≥ 2); đó là " + str(JDR["n_pairs"]) + r" cặp, trung bình " + c(JDR["mean_cv_per_jd"], 1) +
      r" CV mỗi JD. Điểm của mỗi cặp là điểm out-of-fold (CV của cặp chưa từng dùng để huấn luyện). Bảng " + ref("t_rank") + r" là độ đo xếp hạng, Bảng " + ref("t_cls") +
      r" là độ đo phân loại nhị phân “phù hợp” trên toàn bộ 1664 cặp; khoảng tin cậy 95% bootstrap theo JD (hoặc theo CV ở độ đo phân loại).")
    R.table(["Phương pháp", "NDCG@1", "NDCG@3", "NDCG@5", "NDCG@10", "Recall@5", "Recall@10", "MRR"],
            [[n, jv(n, "ndcg@1"), jv(n, "ndcg@3"), f'{jv(n, "ndcg@5")} [{jci(n, "ndcg@5_ci")}]', f'{jv(n, "ndcg@10")} [{jci(n, "ndcg@10_ci")}]',
              jv(n, "recall@5"), jv(n, "recall@10"), f'{jv(n, "mrr")} [{jci(n, "mrr_ci")}]'] for n in names],
            "Độ đo xếp hạng: với mỗi JD, xếp hạng các CV theo điểm giảm dần (" + str(JDR["n_jd"]) + " JD).", widths=[3.7, 1.3, 1.3, 2.4, 2.4, 1.5, 1.5, 2.4], size=8.5, label="t_rank", bold_rows=(5,))
    R.table(["Phương pháp", "Accuracy", "Precision", "Recall", "F1", "AUC-ROC"],
            [[n, c(rows[n]["accuracy"], 3), c(rows[n]["precision"], 3), c(rows[n]["recall"], 3), c(rows[n]["f1"], 3), c(rows[n]["auc_roc"], 3)] for n in names],
            "Độ đo phân loại nhị phân “phù hợp” (mức ≥ 2) trên 1664 cặp; ngưỡng chọn cross-fit theo F1, AUC-ROC không dùng ngưỡng.", widths=[5.6, 2.1, 2.1, 2.1, 2.1, 2.0], size=10, label="t_cls", bold_rows=(5,))
    R.figure("figures/fig_results.png", r"(a) NDCG@5, NDCG@10 và MRR kèm khoảng tin cậy 95% khi xếp hạng CV cho từng JD; (b) NDCG@K theo K.", width_cm=16.0, label="fig_results")
    s, g, m, t, sb, hy = (rows[n] for n in [PR, "GCN", "MLP (SBERT)", "TF-IDF + cosine", "SBERT + cosine", "Hybrid tuyến tính (GCN + SBERT)"])
    nov = [n for n in names[:5] if jr[PR]["ndcg@5_ci"][0] > jr[n]["ndcg@5_ci"][1]]
    P(r"**Nhận xét.** (1) Khi xếp hạng CV cho từng JD, mô hình đề xuất cao nhất ở mọi độ đo: NDCG@5 " + jv(PR, "ndcg@5") + r", NDCG@10 " + jv(PR, "ndcg@10") + r", MRR " + jv(PR, "mrr") + r", Recall@5 " + jv(PR, "recall@5") +
      r". Khoảng tin cậy NDCG@5 của nó không chồng lên khoảng của: " + (", ".join(nov) if nov else "không phương pháp nào") + r". Trên toàn bộ 1664 cặp, nó cũng có F1 " + c(s["f1"], 2) + r" và AUC-ROC " + c(s["auc_roc"], 2) + r" cao nhất. "
      r"(2) **Kết quả không đồng đều giữa các phương pháp học:** GCN đơn (NDCG@5 " + jv("GCN", "ndcg@5") + r") và MLP (" + jv("MLP (SBERT)", "ndcg@5") + r") thấp hơn cả SBERT + cosine (" + jv("SBERT + cosine", "ndcg@5") +
      r") và TF-IDF + cosine (" + jv("TF-IDF + cosine", "ndcg@5") + r"), dù ở bài toán ngược lại (mỗi CV xếp hạng các JD, Bảng " + ref("t_rank_cv") + r") GCN và MLP vượt hai phương pháp cosine. Một giải thích khả dĩ (chưa kiểm chứng riêng) là các mô hình học được huấn luyện trên danh sách "
      r"gồm nhiều JD khác ngành của cùng một CV, nên điểm của chúng thiên về việc phân biệt JD đúng ngành với JD khác ngành; còn để xếp các CV của cùng một JD cần phân biệt những ứng viên cùng ngành với nhau, "
      r"việc này phụ thuộc vào độ phủ yêu cầu mà đặc trưng LLM mô tả. (3) Khoảng tin cậy khá rộng vì chỉ có " + str(JDR["n_jd"]) + r" JD với khoảng " + c(JDR["mean_cv_per_jd"], 0) + r" CV mỗi JD, nên chênh lệch nhỏ giữa các phương pháp không đáng kể.")
    R.table(["Phương pháp", "NDCG@5", "NDCG@10", "MRR"],
            [[n, f'{c(rows[n]["ndcg@5"], 2)} [{c(rows[n]["ndcg@5_ci"][0], 2)}–{c(rows[n]["ndcg@5_ci"][1], 2)}]', f'{c(rows[n]["ndcg@10"], 2)} [{c(rows[n]["ndcg@10_ci"][0], 2)}–{c(rows[n]["ndcg@10_ci"][1], 2)}]',
              f'{c(rows[n]["mrr"], 2)} [{c(rows[n]["mrr_ci"][0], 2)}–{c(rows[n]["mrr_ci"][1], 2)}]'] for n in names],
            "Góc nhìn bổ sung: với mỗi CV, xếp hạng các JD (104 CV, cross-validation 5 lượt theo CV).", widths=[6.0, 3.4, 3.4, 3.2], size=9.5, label="t_rank_cv", bold_rows=(5,))
    P(r"Ở góc nhìn bổ sung này mô hình đề xuất vẫn cao nhất (NDCG@10 " + c(s["ndcg@10"], 2) + r"), GCN đơn (" + c(g["ndcg@10"], 2) + r") và MLP (" + c(m["ndcg@10"], 2) + r") vượt TF-IDF (" + c(t["ndcg@10"], 2) + r") và SBERT (" + c(sb["ndcg@10"], 2) +
      r"), MLP trên SBERT còn nhỉnh hơn GCN đơn với khoảng tin cậy chồng nhau. Về dự đoán mức 0–3, mô hình đề xuất khớp chính xác 71,3% và trong ±1 mức 99,0% trên 1664 cặp; GCN đơn (ngưỡng hiệu chỉnh) khớp chính xác 63,8%.")

    H("2.6.3.2. Phân tích đóng góp từng thành phần (ablation)", 4)
    ab = JDR["rows"][6:9]
    R.table(["Cấu hình", "NDCG@5", "NDCG@10", "MRR", "Recall@5"],
            [["Đầy đủ: GCN + LLM + cosine", jv(PR, "ndcg@5", 3), jv(PR, "ndcg@10", 3), jv(PR, "mrr", 3), jv(PR, "recall@5", 3)]] +
            [[a["method"].replace("GBM: ", "Bỏ thành phần – "), c(a["ndcg@5"], 3), c(a["ndcg@10"], 3), c(a["mrr"], 3), c(a["recall@5"], 3)] for a in ab],
            "Ablation khi xếp hạng CV cho từng JD (bỏ lần lượt GCN, cosine, đặc trưng LLM).", widths=[7.8, 2.0, 2.2, 1.8, 2.2], size=9.5, label="t_abl", bold_rows=(0,))
    a1, a2 = ab[1], ab[2]
    P(r"Bỏ GCN (chỉ LLM + cosine) gần như không làm giảm kết quả (NDCG@5 " + c(a1["ndcg@5"], 3) + r" so với " + jv(PR, "ndcg@5", 3) + r"; MRR " + c(a1["mrr"], 3) + r" so với " + jv(PR, "mrr", 3) +
      r"), còn bỏ đặc trưng LLM làm NDCG@5 giảm mạnh xuống " + c(a2["ndcg@5"], 3) + r". Vậy ở bài toán xếp hạng CV cho từng JD, đóng góp chính đến từ đặc trưng LLM; đóng góp riêng của GCN không đo được rõ. "
      r"(Với góc nhìn mỗi CV xếp hạng JD, GCN có đóng góp nhỏ: NDCG@5 từ " + c(AB[1]["ndcg@5"], 3) + r" lên " + c(rows[PR]["ndcg@5"], 3) + r".) Biến thể “không LLM” dùng điểm GCN out-of-fold một cấp nên có thể rò rỉ nhẹ; hai biến thể còn lại không bị.")

    H("2.6.3.3. Độ phức tạp tính toán và bộ nhớ", 4)
    P(r"**Lý thuyết.** Với đồ thị $N=14$ nút, $|E|\approx150$ cạnh, chiều ẩn $d_h=128$, chiều đầu vào $d=1152$, $L=3$ lớp: pre-aggregation $O(Nd\,d_h)$; mỗi lớp GCN $O(|E|d_h+Nd_h^{2})$; "
      r"dựng cạnh k-NN $O(N^{2}d)$. Mọi đại lượng này cố định theo cặp nên chi phí GCN là $O(1)$ theo cặp và tuyến tính theo số cặp. Chi phí chủ đạo là SBERT (Transformer 12 lớp, $O(\ell^{2}\,d_{\mathrm{model}})$ với độ dài $\ell$ của mỗi mục) "
      r"và hai lần gọi LLM. Bộ nhớ: ma trận đặc trưng một đồ thị $14\times1152\times4$ byte $\approx64,5$ KB; tham số GCN 1,1 MB.")
    R.table(["Chỉ số", "Giá trị đo được"],
            [["Số tham số: GCN / SBERT", f"{CX['params_gcn']:,} / {CX['params_sbert']:,}".replace(",", ".")],
             ["Tệp mô hình: GCN / stacker", f"{CX['file_mb']['best_model.pt']:.1f} MB / {CX['file_mb']['stacker.pkl']:.2f} MB".replace(".", ",")],
             ["Kích thước một tệp đồ thị / cả 1664 đồ thị", f"{CX['graph_file_kb']:.1f} KB / {CX['graph_total_mb']:.0f} MB".replace(".", ",")],
             ["Trung bình số cạnh mỗi đồ thị", f"{CX['avg_edges']:.0f}"],
             ["Mã hóa SBERT một cặp (≈35 mục)", f"{CX['ms_embed_pair']:.0f} ms".replace(".", ",")],
             ["Dựng đồ thị một cặp", f"{CX['ms_build_graph']:.2f} ms".replace(".", ",")],
             ["GCN suy luận một cặp / 1664 cặp", f"{CX['ms_gcn_forward']:.2f} ms / {CX['gcn_1664_pairs_s']:.2f} s".replace(".", ",")],
             ["Bộ tổng hợp (GBM) một cặp", f"{CX['ms_stacker']:.2f} ms".replace(".", ",")],
             ["Bộ nhớ RAM: sau khi nạp SBERT / đỉnh", f"{CX['rss_after_sbert_mb']:.0f} MB / {CX['peak_rss_mb']:.0f} MB"],
             ["Số lần gọi LLM khi suy luận", "1 lần/văn bản (trích xuất, có cache) + 1 lần/cặp (đặc trưng cặp)"]],
            "Đo thời gian và bộ nhớ (CPU i3-1115G4, không GPU).", widths=[7.6, 8.4], size=10, label="t_cx")
    P(r"Phần GCN và dựng đồ thị chỉ tốn vài mili-giây mỗi cặp; thời gian suy luận thực tế bị chi phối bởi mã hóa SBERT và độ trễ gọi LLM (không đo ở đây vì phụ thuộc mạng và nhà cung cấp). "
      r"Do mô hình nhỏ (1,1 MB), việc huấn luyện và suy luận trên CPU là khả thi.")

    H("2.6.3.4. Phân tích lỗi và khả năng diễn giải", 4)
    R.figure("figures/fig_confusion.png", r"Ma trận nhầm lẫn giữa mức thật và mức dự đoán của GCN đơn (trái) và mô hình đề xuất (phải); ô ghi số cặp và phần trăm theo hàng.", width_cm=14.0, label="fig_conf")
    cs = ER["confusion_stack"]
    P(r"Mô hình đề xuất nhận diện tốt mức 0 (79%) và 1 (80%), nhưng chỉ nhận đúng 57% ở mức 2 và 32% ở mức 3; lỗi chủ yếu là dự đoán thấp hơn một mức (" + str(cs[3][2]) + r"/" + str(sum(cs[3])) + r" cặp mức 3 bị dự đoán là mức 2). "
      r"Lỗi lệch từ hai mức trở lên rất hiếm (1,0% số cặp). "
      r"Mức 3 chiếm chỉ 10% dữ liệu nên mô hình hồi quy có xu hướng co dự đoán về giữa thang.")
    br = {x["role_match"]: x for x in ER["by_role_match"]}
    R.table(["Nhóm cặp", "Số cặp", "Độ chính xác mức", "Sai số tuyệt đối TB"],
            [["Khác hẳn vai trò (different)", int(br["different"]["n"]), c(br["different"]["acc"], 3), c(br["different"]["mean_abs_err"], 3)],
             ["Vai trò liền kề (adjacent)", int(br["adjacent"]["n"]), c(br["adjacent"]["acc"], 3), c(br["adjacent"]["mean_abs_err"], 3)],
             ["Cùng vai trò (same)", int(br["same"]["n"]), c(br["same"]["acc"], 3), c(br["same"]["mean_abs_err"], 3)]],
            "Lỗi của mô hình đề xuất theo mức độ giống vai trò giữa CV và JD.", widths=[6.2, 2.4, 3.6, 3.8], size=10.5, label="t_err")
    hq = ER["hard_req"]
    P(r"Lỗi tập trung ở các cặp cùng vai trò (độ chính xác " + c(br["same"]["acc"], 2) + r" so với " + c(br["different"]["acc"], 2) + r" khi khác vai trò): đây chính là nhóm cần phân biệt mức 2 và 3 dựa trên độ phủ yêu cầu. "
      r"Các cặp có điều kiện cứng chưa đáp ứng (" + str(hq["n_có"]) + r" cặp) cũng khó hơn (" + c(hq["có"], 2) + r" so với " + c(hq["không"], 2) + r"). Một số ví dụ sai nặng nhất:")
    wr = [w for w in ER["worst"][:4]]
    R.table(["CV – JD", "Nhãn / dự đoán", "Độ phủ LLM", "Lý do nhãn (rubric)"],
            [[f"{w['cv_id']} – {w['jd_id']}", f"{w['grade']} / {w['pred']}", f"{w['must_have_coverage_pct']}%", w["reason"]] for w in wr],
            "Các cặp bị dự đoán sai nhiều nhất.", widths=[3.8, 2.2, 2.2, 7.8], size=9.5, label="t_worst")
    P(r"Các lỗi này thường thuộc hai kiểu: nhãn đòi hỏi tri thức miền hẹp (ví dụ “ngân hàng” khác “bảo hiểm”) mà đặc trưng hiện có không mã hóa; hoặc LLM đánh giá độ phủ cao nhưng nhãn bị hạ vì lệch cấp độ. "
      r"Cả hai gợi ý hướng cải thiện ở mục 2.6.3.6.")
    R.figure("figures/fig_importance.png", r"Độ quan trọng của đặc trưng đầu vào bộ tổng hợp (permutation importance, trung bình 5 lượt). Màu đỏ: đặc trưng LLM; xanh dương: điểm GCN; xanh lá: cosine SBERT.", width_cm=13.0, label="fig_imp")
    P(r"Biểu đồ giải thích (Hình " + ref("fig_imp") + r") cho thấy điểm GCN là đặc trưng quan trọng nhất (" + c(IMP[0]["importance"], 3) + r"), tiếp theo là chênh lệch số năm kinh nghiệm (" + c(IMP[1]["importance"], 3) + r") và độ phủ yêu cầu bắt buộc (" +
      c(IMP[2]["importance"], 3) + r"); các cosine theo nhóm có đóng góp nhỏ. (Lưu ý: độ quan trọng hoán vị bị chia sẻ giữa các đặc trưng tương quan, nên điểm GCN, vốn đã chứa thông tin cosine, có thể hấp thụ phần đóng góp của chúng.) "
      r"Ở mức từng cặp, diễn giải cho nhà tuyển dụng ở mục 2.5.3 liệt kê các yêu cầu đáp ứng/chưa đáp ứng.")

    H("2.6.3.5. Vì sao mô hình lai cho kết quả tốt hơn", 4)
    B("**Lan truyền thông tin trên đồ thị.** Các cạnh sao, chéo và k-NN cho phép biểu diễn của nút CV/JD nhận thông tin từ từng nhóm thực thể, nên điểm đồ thị phản ánh đồng thời vai trò, kỹ năng và học vấn thay vì một vector toàn văn. "
      "Ở bài toán mỗi CV xếp hạng các JD, GCN đơn vượt TF-IDF và SBERT thuần ở NDCG@10 (" + c(g["ndcg@10"], 2) + " so với " + c(t["ndcg@10"], 2) + " và " + c(sb["ndcg@10"], 2) + "). Ở bài toán mỗi JD xếp hạng các CV thì lợi thế này không còn.")
    B("**Giảm mất mát ngữ nghĩa.** Embedding riêng từng nhóm thực thể và gộp bằng DeepSets giữ lại thông tin mà một vector toàn văn bị trung bình hóa (ví dụ khớp field hoàn toàn nhưng khớp soft skills yếu); cosine từng nhóm cũng được dùng trực tiếp làm đặc trưng.")
    B("**Tín hiệu bổ trợ.** Điểm đồ thị và cosine cho biết CV và JD có cùng vai trò/chủ đề không; đặc trưng LLM cho biết CV đáp ứng bao nhiêu yêu cầu bắt buộc và có lệch cấp độ không. Bộ tổng hợp kết hợp các nguồn nên vượt từng nguồn dùng riêng ở cả hai cách xếp hạng (Bảng " + ref("t_abl") + ").")
    P(r"Cần nói rõ giới hạn của lập luận: phần cải thiện lớn nhất đến từ đặc trưng LLM chứ không phải riêng GCN; ở xếp hạng CV cho từng JD, bỏ GCN không làm kết quả kém đi đáng kể. Kết luận hợp lý là mô hình lai tốt hơn các phương pháp đơn lẻ, "
      r"còn lợi thế riêng của đồ thị là nhỏ và chưa ổn định giữa hai cách xếp hạng trong thiết lập này.")

    H("2.6.3.6. Hạn chế và hướng mở rộng", 4)
    B("**Cách ghép cặp của dữ liệu:** các cặp được thiết kế cho từng CV (mỗi CV có khoảng 16 JD), nên danh sách CV của mỗi JD không được thiết kế mà chỉ gồm các CV tình cờ được ghép (trung bình khoảng 10 CV, " + str(JDR["n_jd"]) + " JD đủ điều kiện). Siêu tham số $\\alpha$ của Hybrid cũng chọn theo danh sách JD của từng CV. Cần bộ dữ liệu mà mọi CV ứng tuyển cùng một JD được gán nhãn để đánh giá đúng bài toán xếp hạng CV.")
    B("**Dữ liệu:** CV là dữ liệu tổng hợp, chỉ 104 CV và 159 JD; nhãn do một người chấm theo rubric nên mô hình học bắt chước rubric. Một JD xuất hiện ở nhiều CV nên chia theo CV chưa loại hết rò rỉ theo JD; mỗi danh sách có nhiều cặp rất dễ (ngoài ngành) nên chỉ nên so sánh tương đối giữa các phương pháp. Chưa có kiểm định thống kê ghép cặp.")
    B("**Chưa thực nghiệm trên dữ liệu công khai theo yêu cầu:** JobBERT dataset và Job2CV chưa được chạy. Giao thức đề xuất cho JobBERT dataset: mã hóa tiêu đề và tên nghề ESCO bằng SBERT và TF-IDF, đo độ chính xác Top-1/Top-5 khi gán nghề bằng cosine gần nhất; kết quả chỉ đánh giá khối embedding. Cần liên kết tới Job2CV để bổ sung.")
    B("**Chi phí và độ ổn định của LLM:** mô hình cuối cần một lần gọi LLM cho mỗi cặp khi suy luận; kết quả phụ thuộc mô hình LLM và có thể thay đổi giữa các lần gọi (giảm nhẹ bằng cache); đặc trưng huấn luyện tính theo lô 15 JD còn suy luận theo lô 1 JD.")
    B("**Điểm yếu của GCN:** phân biệt mức 2 và 3 trong cùng vai trò còn kém, trọng số cạnh và $\\lambda_t$ đặt thủ công. Hướng mở rộng: cho phép học trọng số cạnh (GAT hoặc $\\lambda_t$ học được), thêm đặc trưng tri thức miền (ví dụ lĩnh vực ngân hàng/bảo hiểm), thử JobBERT [7] cho nhóm role/field_of_education, thay LLM bằng mô hình mở chạy cục bộ để giảm chi phí.")
    B("**Đánh giá:** bổ sung nhiều người chấm để tính độ đồng thuận, thêm CV thật (đã ẩn danh) và đánh giá trên dữ liệu tương tác thực tế; tính kiểm định có ghép cặp.")


def appendix_and_refs(R):
    P, H, B = R.para, R.heading, R.bullet
    H("TÀI LIỆU THAM KHẢO", 1)
    refs = [
        ("G. Salton, C. Buckley, “Term-weighting approaches in automatic text retrieval”, Information Processing & Management, 24(5), 513–523, 1988.", "https://doi.org/10.1016/0306-4573(88)90021-0"),
        ("S. Robertson, H. Zaragoza, “The Probabilistic Relevance Framework: BM25 and Beyond”, Foundations and Trends in Information Retrieval, 3(4), 333–389, 2009.", "https://doi.org/10.1561/1500000019"),
        ("T. Mikolov, K. Chen, G. Corrado, J. Dean, “Efficient Estimation of Word Representations in Vector Space”, arXiv:1301.3781, 2013.", "https://arxiv.org/abs/1301.3781"),
        ("J. Devlin, M.-W. Chang, K. Lee, K. Toutanova, “BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding”, NAACL-HLT, 2019.", "https://arxiv.org/abs/1810.04805"),
        ("N. Reimers, I. Gurevych, “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks”, EMNLP-IJCNLP, 2019.", "https://arxiv.org/abs/1908.10084"),
        ("N. Reimers, I. Gurevych, “Making Monolingual Sentence Embeddings Multilingual using Knowledge Distillation”, EMNLP, 2020.", "https://arxiv.org/abs/2004.09813"),
        ("J.-J. Decorte, J. Van Hautte, T. Demeester, C. Develder, “JobBERT: Understanding Job Titles through Skills”, FEAST Workshop, ECML-PKDD, 2021.", "https://arxiv.org/abs/2109.09605"),
        ("C. Zhu et al., “Person-Job Fit: Adapting the Right Talent for the Right Job with Joint Representation Learning”, ACM Transactions on Management Information Systems, 2018.", "https://arxiv.org/abs/1810.04040"),
        ("C. Qin et al., “Enhancing Person-Job Fit for Talent Recruitment: An Ability-aware Neural Network Approach”, SIGIR, 2018.", "https://arxiv.org/abs/1812.08947"),
        ("S. Bian et al., “Learning to Match Jobs with Resumes from Sparse Interaction Data using Multi-View Co-Teaching Network”, CIKM, 2020.", "https://arxiv.org/abs/2009.13299"),
        ("“Embedding-based Recommender System for Job to Candidate Matching on Scale”, arXiv:2107.00221, 2021.", "https://arxiv.org/abs/2107.00221"),
        ("T. N. Kipf, M. Welling, “Semi-Supervised Classification with Graph Convolutional Networks”, ICLR, 2017.", "https://arxiv.org/abs/1609.02907"),
        ("J.-J. Decorte et al., “Extreme Multi-Label Skill Extraction Training using Large Language Models”, arXiv:2307.10778, 2023.", "https://arxiv.org/abs/2307.10778"),
        ("W. Wang et al., “MiniLM: Deep Self-Attention Distillation for Task-Agnostic Compression of Pre-Trained Transformers”, NeurIPS, 2020.", "https://arxiv.org/abs/2002.10957"),
        ("M. Zaheer et al., “Deep Sets”, NeurIPS, 2017.", "https://arxiv.org/abs/1703.06114"),
        ("J. L. Ba, J. R. Kiros, G. E. Hinton, “Layer Normalization”, arXiv:1607.06450, 2016.", "https://arxiv.org/abs/1607.06450"),
        ("D. P. Kingma, J. Ba, “Adam: A Method for Stochastic Optimization”, ICLR, 2015.", "https://arxiv.org/abs/1412.6980"),
        ("K. Järvelin, J. Kekäläinen, “Cumulated gain-based evaluation of IR techniques”, ACM Transactions on Information Systems, 20(4), 422–446, 2002.", "https://doi.org/10.1145/582415.582418"),
        ("J. H. Friedman, “Greedy function approximation: A gradient boosting machine”, The Annals of Statistics, 29(5), 1189–1232, 2001.", "https://doi.org/10.1214/aos/1013203451"),
        ("F. Pedregosa et al., “Scikit-learn: Machine Learning in Python”, Journal of Machine Learning Research, 12, 2825–2830, 2011.", "https://jmlr.org/papers/v12/pedregosa11a.html"),
        ("D. H. Wolpert, “Stacked generalization”, Neural Networks, 5(2), 241–259, 1992.", "https://doi.org/10.1016/S0893-6080(05)80023-1"),
        ("M. Fey, J. E. Lenssen, “Fast Graph Representation Learning with PyTorch Geometric”, ICLR Workshop, 2019.", "https://arxiv.org/abs/1903.02428"),
        ("VietJobs – bộ dữ liệu tin tuyển dụng tiếng Việt (Hugging Face, dinhieufam/VietJobs).", "https://huggingface.co/datasets/dinhieufam/VietJobs"),
        ("TechWolf, JobBERT evaluation dataset (Hugging Face).", "https://huggingface.co/datasets/TechWolf/JobBERT-evaluation-dataset"),
        ("Resume Dataset (Hugging Face, Sachinkelenjaguri/Resume_dataset).", "https://huggingface.co/datasets/Sachinkelenjaguri/Resume_dataset"),
        ("X. Glorot, Y. Bengio, “Understanding the difficulty of training deep feedforward neural networks”, AISTATS, 2010.", "https://proceedings.mlr.press/v9/glorot10a.html"),
        ("K. He, X. Zhang, S. Ren, J. Sun, “Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification”, ICCV, 2015.", "https://arxiv.org/abs/1502.01852"),
        ("B. Efron, “Bootstrap methods: another look at the jackknife”, The Annals of Statistics, 7(1), 1–26, 1979.", "https://doi.org/10.1214/aos/1176344552"),
        ("J. Cohen, “Weighted kappa: Nominal scale agreement with provision for scaled disagreement or partial credit”, Psychological Bulletin, 70(4), 213–220, 1968.", "https://doi.org/10.1037/h0026256"),
    ]
    for i, (t, u) in enumerate(refs, 1):
        p = R.para(f"[{i}] {t} {u}", align=0, indent=False, size=12, after=3, left=0.9)
        p.paragraph_format.first_line_indent = __import__("docx").shared.Cm(-0.9)
    R.page_break()
    H("PHỤ LỤC A. CÀI ĐẶT VÀ THỰC THI THỰC NGHIỆM", 1)
    P(r"Toàn bộ mã nguồn, dữ liệu nhãn và mã thực nghiệm của báo cáo nằm trong kho mã: " + GITHUB + r" (nhánh bang-branch). Thư mục report/ chứa mã tạo các số liệu, hình trong Chương 2 (cần được đẩy lên kho trước khi nộp).", indent=False)
    H("A.1. Cài đặt", 3)
    P(r"Yêu cầu Python 3.10 trở lên (đã chạy trên Python 3.13, Windows 11, CPU). Cài thư viện và cấu hình LLM:", indent=False)
    R.code("pip install -r requirements.txt\n\n# Tạo tệp .env ở thư mục gốc (KHÔNG đưa lên kho mã)\nLLM_API_KEY=<khóa API>\nOPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/\nLLM_MODEL=gemini-flash-lite-latest\nEMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2")
    H("A.2. Huấn luyện và đánh giá", 3)
    R.code("# 1. Dựng đồ thị từ nhãn + CV + JD (gọi LLM, có cache)\npython -X utf8 main.py --mode prepare\n\n"
           "# 2. Cross-validation 5 lượt theo CV, so sánh baseline\npython -X utf8 src/modeling/train.py --cv 5\n\n"
           "# 3. Đặc trưng cặp từ LLM (mỗi CV một lần gọi cho 15 JD)\npython -X utf8 src/extraction/pair_features.py --workers 3\n\n"
           "# 4. Đánh giá mô hình xếp chồng (cross-validation lồng nhau, khoảng 40 phút)\npython -X utf8 src/modeling/train.py --stack\n\n"
           "# 5. Huấn luyện mô hình cuối: GCN rồi stacker\npython -X utf8 src/modeling/train.py --patience 20\npython -X utf8 src/modeling/stacker.py")
    H("A.3. Tái tạo số liệu và hình của báo cáo", 3)
    R.code("python -X utf8 report/experiments.py   # baseline MLP, độ đo phân loại, khoảng tin cậy -> report/results/main_results.json\n"
           "python -X utf8 report/ablation.py      # ablation -> report/results/ablation.json\n"
           "python -X utf8 report/analysis.py      # ví dụ thật, độ phức tạp, phân tích lỗi, độ quan trọng đặc trưng\n"
           "python -X utf8 report/figures.py       # vẽ hình (SVG + PNG) -> report/figures/")
    H("A.4. Dự đoán cho một cặp CV–JD, xếp hạng CV cho một JD và chạy thử", 3)
    P(r"Ví dụ cách backend dùng hệ thống: chấm điểm từng cặp rồi sắp xếp các CV của cùng một JD (ưu tiên chế độ stacker, sau đó điểm, sau đó gcn_score):", indent=False)
    R.code("from src.inference.predict import CJMPredictor\n\npredictor = CJMPredictor()\nresults = []\nfor cv in cv_list:                      # các CV ứng tuyển cùng một JD\n"
           "    r = predictor.predict_from_text(cv['text'], jd_text)\n    results.append((cv['id'], r))\n\n"
           "ranked = sorted(results, reverse=True,\n                key=lambda t: (t[1]['mode'] == 'stacker', t[1]['score'], t[1]['gcn_score']))\n"
           "for cv_id, r in ranked:\n    print(cv_id, r['score'], r['grade_label'], r['explanation'])")
    R.code("python -X utf8 main.py --mode predict      # nhập CV, JD và nhận điểm + diễn giải\npython -X utf8 demo/run_demo.py             # demo 4 cặp CV–JD mới\npython -X utf8 tests/test_pair_features.py   # kiểm tra đơn vị")
    P(r"Ghi chú: nhiều kết quả có tính ngẫu nhiên (huấn luyện mạng); các lần chạy cross-validation liền nhau có thể lệch khoảng 0,04 ở NDCG@1, nên không nên diễn giải chênh lệch nhỏ hơn mức đó.", indent=False)
