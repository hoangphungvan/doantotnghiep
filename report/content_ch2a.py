"""Chương 2, mục 2.1 – 2.3 (kiến trúc, embedding, đồ thị)."""

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def build(R):
    A = json.load(open(os.path.join(HERE, "results", "analysis.json"), encoding="utf-8"))["example"]
    P, H, B = R.para, R.heading, R.bullet
    R.new_chapter(2)
    H("CHƯƠNG 2. ĐỀ XUẤT MÔ HÌNH LAI SEMANTIC EMBEDDING – GRAPH NEURAL NETWORKS CHO KHỚP NỐI CV–JD", 1)

    # ================================================================== 2.1
    H("2.1. Mô hình kiến trúc tổng quát", 2)
    P(r"Chương này hiện thực hóa năm bước tổng quát ở mục 1.2.2 bằng một mô hình lai: LLM trích xuất thực thể, SBERT cùng DeepSets biểu diễn ngữ nghĩa, "
      r"mạng đồ thị GCN đối sánh theo cấu trúc, và một bộ tổng hợp điểm kết hợp tín hiệu đồ thị với độ tương đồng ngữ nghĩa và đặc trưng đánh giá yêu cầu bắt buộc. "
      r"Luồng xử lý của hệ thống như sau:")
    P(r"Văn bản CV/JD → trích xuất thực thể bằng LLM (6 loại) → chuẩn hóa và lưu đệm (cache) thực thể → SBERT (vector 384 chiều cho mỗi mục) → "
      r"DeepSets (vector 1152 chiều cho mỗi nhóm thực thể) → đồ thị 14 nút cho mỗi cặp CV–JD → lớp pre-aggregation → 3 lớp GCNConv → readout và MLP cặp → điểm đồ thị "
      r"→ tổng hợp với cosine ngữ nghĩa và đặc trưng LLM (stacking) → điểm, mức phù hợp và diễn giải của cặp → sắp xếp các CV của cùng một JD theo điểm giảm dần → NDCG@K, Recall@K, MRR.", indent=False, italic=True)
    R.figure("figures/fig_arch.png", r"Kiến trúc tổng quát của hệ thống đề xuất. Các khối M1–M4 tạo điểm đồ thị; M5 tổng hợp điểm cuối; M6, M7 là xếp hạng–đánh giá và diễn giải.",
             width_cm=15.5, label="fig_arch")
    P(r"**Đơn vị xử lý.** Hệ thống nhận một cặp CV–JD mỗi lần gọi và trả điểm, mức phù hợp và diễn giải của cặp đó. Danh sách CV xếp hạng cho một JD do ứng dụng gọi (backend) tạo bằng cách chấm điểm từng cặp rồi sắp xếp (mục 2.5.4).")
    P(r"Bảng 2.1 liệt kê các khối xử lý theo đúng thứ tự trong Hình 2.1, kèm đầu vào, đầu ra và mục trình bày chi tiết. Đầu ra của khối trước là đầu vào của khối sau.")
    R.table(["Khối", "Đầu vào", "Xử lý chính", "Đầu ra", "Mục"],
            [["M1. Trích xuất thực thể", "Văn bản CV hoặc JD", "LLM tách 6 loại thực thể (cùng yêu cầu ưu tiên của JD); chuẩn hóa, lưu đệm theo SHA-256 của văn bản", "Từ điển 6 nhóm mục", "2.2.2"],
             ["M2. Biểu diễn ngữ nghĩa", "Các mục thực thể", "SBERT mã hóa từng mục (384 chiều); DeepSets gộp [mean | sum | max] theo nhóm", "Vector 1152 chiều cho mỗi nhóm; vector 384 chiều cho toàn văn", "2.2.3–2.2.5"],
             ["M3. Dựng đồ thị cặp", "Vector nhóm của CV và JD", "Tạo 14 nút; cạnh sao, cầu, chéo, k-NN; hợp nhất trọng số", "Đồ thị $G_{ik}$ (14 nút, ≈150 cạnh)", "2.3"],
             ["M4. Mạng GCN", "Đồ thị $G_{ik}$", "Pre-aggregation, 3 lớp GCNConv có residual, readout, MLP cặp", "Điểm đồ thị $s_{\\mathrm{GCN}}\\in(0,1)$", "2.4"],
             ["M5a. Đánh giá cặp bằng LLM", "Văn bản CV và JD", "LLM đối chiếu từng yêu cầu bắt buộc, số năm kinh nghiệm, điều kiện cứng", "6 đặc trưng cặp", "2.5.2"],
             ["M5. Điểm tổng hợp", "$s_{\\mathrm{GCN}}$, 7 cosine, 6 đặc trưng cặp", "Mô hình xếp chồng (Gradient Boosting) hồi quy mức phù hợp", "Điểm cuối $s^{*}\\in[0,3]$", "2.5"],
             ["M6. Xếp hạng và đánh giá", "Điểm cuối của các cặp cùng một JD", "Với mỗi JD sắp xếp các CV theo điểm giảm dần; tính NDCG@K, Recall@K, MRR", "Danh sách CV xếp hạng; độ đo", "2.6"],
             ["M7. Diễn giải", "Kết quả đánh giá yêu cầu của M5a", "Tóm tắt yêu cầu đáp ứng/chưa thấy (tiếng Việt, tiếng Anh)", "Văn bản diễn giải", "2.5.3"]],
            "Các khối xử lý của hệ thống và mối liên hệ đầu vào – đầu ra.", widths=[3.0, 3.0, 5.2, 3.4, 1.4], size=10, label="t_modules")
    P(r"**Vai trò từng khối.** M1 chuyển văn bản tự do thành các mục có nhãn loại, làm cơ sở so sánh có chủ đích (kỹ năng với kỹ năng, vai trò với vai trò). "
      r"M2 biến mỗi mục thành vector để so sánh theo ý nghĩa thay vì mặt chữ. M3 gom các vector của một cặp CV–JD vào một đồ thị nhỏ, trong đó cạnh thể hiện quan hệ cần so sánh. "
      r"M4 lan truyền thông tin trên đồ thị để rút ra một điểm cho cả cặp. M5 hiệu chỉnh điểm đồ thị bằng các tín hiệu bổ sung mà đồ thị mô tả yếu (độ phủ yêu cầu bắt buộc, lệch cấp độ). "
      r"M6 và M7 tạo kết quả cuối cùng: danh sách CV xếp hạng cho từng JD và lời diễn giải.")
    P(r"**Ví dụ chạy xuyên suốt.** Các mục sau dùng chung một cặp: JD “Java Backend Developer” (yêu cầu tối thiểu 2 năm; Java, Spring Boot, RESTful API, MySQL/PostgreSQL, Git; "
      r"ưu tiên Docker, Kafka, AWS) và một CV Backend Developer có 3 năm kinh nghiệm trong bộ dữ liệu. Mọi con số trong ví dụ là kết quả chạy thật của mã nguồn (tệp report/analysis.py).")
    R.table(["Ký hiệu", "Ý nghĩa"],
            [[r"$t$, $T$", "Loại thực thể và số loại; $T=6$ (soft_skills, hard_skills, education, field_of_education, industry_sector, role)"],
             [r"$E_t(d)$, $n_t$", "Tập mục thực thể loại $t$ của văn bản $d$ (CV hoặc JD) và số mục"],
             [r"$\mathbf{x}_s\in\mathbb{R}^{384}$", "Vector SBERT của một mục (chuỗi) $s$"],
             [r"$\mathbf{g}^{d}_t\in\mathbb{R}^{1152}$", "Vector DeepSets của nhóm loại $t$ của văn bản $d$ ($d=c$ cho CV, $d=j$ cho JD)"],
             [r"$G_{ik}=(V,E,\mathbf{X},w)$", "Đồ thị của cặp CV $c_i$ – JD $j_k$: tập nút, tập cạnh, ma trận đặc trưng nút, trọng số cạnh"],
             [r"$\lambda_t$", "Trọng số nghiệp vụ của loại thực thể $t$ (role 3,0; hard_skills 2,5; field 2,0; industry 1,5; education 1,5; soft_skills 1,0)"],
             [r"$w_{uv}$", "Trọng số cạnh từ nút $u$ đến nút $v$"],
             [r"$\mathbf{h}^{(l)}_v$", "Biểu diễn nút $v$ sau lớp GCN thứ $l$ (128 chiều)"],
             [r"$s_{\mathrm{GCN}}$, $s_{\mathrm{sem}}$, $s^{*}$", "Điểm đồ thị, điểm ngữ nghĩa (cosine toàn văn), điểm cuối"]],
            "Các ký hiệu chính dùng trong Chương 2.", widths=[4.2, 11.8], size=10.5, label="t_symbols")

    # ================================================================== 2.2
    H("2.2. Phương pháp Semantic Embedding để biểu diễn ngữ nghĩa của CV và JD", 2)
    H("2.2.1. Lựa chọn mô hình embedding", 3)
    P(r"Yêu cầu đối với mô hình embedding của đề tài: (i) hiểu tiếng Việt và tiếng Anh cùng lúc, vì CV/JD Việt Nam trộn hai ngôn ngữ; (ii) cho vector cố định cho mỗi câu/cụm từ để so sánh bằng cosine "
      r"với chi phí thấp; (iii) đủ nhẹ để chạy trên CPU; (iv) có sẵn, không cần dữ liệu huấn luyện lớn. Bảng " + R.ref("t_embed") + r" so sánh các lựa chọn.")
    R.table(["Phương án", "Ưu điểm", "Hạn chế đối với bài toán này"],
            [["TF-IDF/BM25 [1][2]", "Nhanh, không cần huấn luyện", "Không hiểu đồng nghĩa; không liên ngôn ngữ"],
             ["Word2vec/fastText [3]", "Nhẹ, có vector từ", "Vector tĩnh theo từ, không có vector cho cụm từ/câu; cần ghép thêm"],
             ["BERT nguyên bản [4]", "Biểu diễn theo ngữ cảnh", "Không tối ưu cho so sánh câu bằng cosine; so cặp tốn chi phí"],
             ["JobBERT [7]", "Hiểu chức danh nghề theo kỹ năng", "Huấn luyện trên dữ liệu tiếng Anh, mức chức danh; không phục vụ so khớp tiếng Việt"],
             ["SBERT đa ngữ (paraphrase-multilingual-MiniLM-L12-v2) [5][6][14]", "Hỗ trợ hơn 50 ngôn ngữ gồm tiếng Việt; vector 384 chiều; 117,7 triệu tham số; chạy được trên CPU", "Không chuyên biệt cho tuyển dụng; câu dài bị cắt theo giới hạn độ dài"]],
            "So sánh các lựa chọn mô hình biểu diễn văn bản.", widths=[4.4, 5.0, 6.6], size=10.5, label="t_embed")
    P(r"Đề tài chọn SBERT đa ngữ vì đáp ứng cả bốn yêu cầu. JobBERT không được chọn vì dữ liệu huấn luyện là tiếng Anh và mục tiêu là chuẩn hóa chức danh, trong khi đề tài cần so khớp nhiều loại thực thể tiếng Việt; "
      r"tuy vậy JobBERT là hướng mở rộng hợp lý cho nhóm role/field (mục 2.6.3). Mô hình được đóng băng (không tinh chỉnh) nhằm giữ nguyên khả năng đa ngữ và tránh quá khớp trên 104 CV.")

    H("2.2.2. Trích xuất, chuẩn hóa và lưu đệm thực thể (khối M1)", 3)
    P(r"Đây là bước đầu của pipeline. Với mỗi văn bản $d$ (CV hoặc JD), LLM (gemini-flash-lite) nhận văn bản và một lời nhắc (prompt) cố định rồi trả về JSON gồm sáu nhóm mục:")
    R.equation(r"E(d)=\big\{E_t(d)\big\}_{t=1}^{T},\qquad E_t(d)=\{s_{t,1},\ldots,s_{t,n_t}\}", "e_E")
    R.where(['$E(d)$: kết quả trích xuất của văn bản $d$ (CV hoặc JD).', '$E_t(d)$: tập các mục thuộc loại $t$ (ví dụ các kỹ năng chuyên môn); $s_{t,i}$: mục thứ $i$ (một chuỗi chữ); $n_t$: số mục của loại $t$.', '$T=6$: số loại thực thể.'])
    P(r"Quy tắc trích xuất (phiên bản prompt v2): với JD chỉ giữ yêu cầu bắt buộc trong các nhóm chính, còn kỹ năng “ưu tiên/có thì tốt” được tách sang nhóm riêng preferred_skills (không đưa vào đồ thị); "
      r"với CV bỏ các kỹ năng bị phủ định (ví dụ “chưa có kinh nghiệm với Java”). Kết quả được chuẩn hóa (cắt khoảng trắng, loại mục trùng) và lưu đệm theo khóa gồm phiên bản prompt "
      r"và mã băm SHA-256 của văn bản, nên cùng một văn bản không phải gọi LLM lần hai.")
    P(r"**Ví dụ.** Với CV và JD của ví dụ, kết quả như Bảng " + R.ref("t_entities") + r" (rút gọn). Đây là đầu ra của M1 và là đầu vào của bước SBERT.")
    cv, jd = A["cv_entities"], A["jd_entities"]
    labels = [("role", "role"), ("hard_skills", "hard_skills"), ("field_of_education", "field_of_education"), ("industry_sector", "industry_sector"),
              ("education", "education"), ("soft_skills", "soft_skills")]
    R.table(["Nhóm", "CV (đầu ra M1)", "JD (đầu ra M1)"],
            [[r"%s" % lab, "; ".join(cv[k]), "; ".join(jd[k])] for k, lab in labels] + [["preferred_skills", "—", "; ".join(jd["preferred_skills"]) + " (không vào đồ thị)"]],
            "Thực thể trích xuất cho cặp ví dụ.", widths=[3.4, 6.6, 6.0], size=9.5, label="t_entities")

    H("2.2.3. Mã hóa từng mục bằng SBERT (khối M2, bước 1)", 3)
    P(r"Đầu vào: từng mục $s$ trong các nhóm $E_t(d)$. SBERT đưa chuỗi qua mạng Transformer rút gọn (MiniLM [14]) rồi lấy trung bình các vector token (mean pooling) để được một vector cố định:")
    R.equation(r"\mathbf{x}_s=\frac{1}{L}\sum_{l=1}^{L}\mathbf{h}_l\in\mathbb{R}^{384}", "e_sbert")
    R.where(['$s$: một mục (chuỗi chữ) cần mã hóa; $L$: số token của $s$.', '$\\mathbf{h}_l$: vector đầu ra của Transformer tại token $l$ (384 chiều); $\\mathbf{x}_s$: vector SBERT của mục $s$.'])
    P(r"trong đó $L$ là số token của chuỗi $s$ và $\mathbf{h}_l\in\mathbb{R}^{384}$ là vector đầu ra của Transformer tại token $l$. Hai chuỗi gần nghĩa cho hai vector có độ tương đồng cosine cao:")
    R.equation(r"\cos(\mathbf{u},\mathbf{v})=\frac{\mathbf{u}^{\top}\mathbf{v}}{\lVert\mathbf{u}\rVert\,\lVert\mathbf{v}\rVert}", "e_cos")
    R.where(['$\\mathbf{u},\\mathbf{v}$: hai vector cần so sánh; $\\mathbf{u}^{\\top}\\mathbf{v}$: tích vô hướng; $\\lVert\\cdot\\rVert$: độ dài vector.', 'Kết quả nằm trong $[-1,1]$; càng gần 1 thì hai mục càng gần nghĩa.'])
    P(r"**Ví dụ.** Nhóm hard_skills của CV có $n=13$ mục nên cho ma trận $\mathbf{X}\in\mathbb{R}^{13\times384}$; nhóm của JD có $n=7$ mục. Bảng " + R.ref("t_xs") + r" là ba chiều đầu của vector từng mục của CV.")
    it = A["items"]["cv_hard_skills"]
    R.table(["Mục (CV, hard_skills)", r"$x_1$", r"$x_2$", r"$x_3$"],
            [[name] + [f"{v:+.3f}".replace(".", ",") for v in vec] for name, vec in zip(it["items"], it["first3"])],
            r"Ba chiều đầu của vector SBERT từng mục hard_skills của CV ($\mathbf{x}_s\in\mathbb{R}^{384}$).", widths=[7.0, 3.0, 3.0, 3.0], size=10, label="t_xs")
    R.figure("figures/fig_embed.png", r"Từ nhóm thực thể đến vector nhóm 1152 chiều (SBERT rồi DeepSets), minh họa bằng nhóm hard_skills của CV ví dụ.", width_cm=15.5, label="fig_embed")

    H("2.2.4. Gộp các mục của một nhóm bằng DeepSets (khối M2, bước 2)", 3)
    P(r"Số mục $n_t$ của mỗi nhóm khác nhau giữa các văn bản và thứ tự các mục không có ý nghĩa, nên cần một phép gộp bất biến với hoán vị. "
      r"DeepSets [15] đưa ra dạng tổng quát cho hàm tập hợp bất biến hoán vị; đề tài dùng ba phép gộp cơ bản và ghép lại để giữ nhiều loại thông tin: trung bình (mức tổng thể), "
      r"tổng (độ nhiều/độ phủ của số mục) và cực đại theo từng chiều (đặc trưng nổi bật nhất). Với $\mathbf{X}_t=[\mathbf{x}_1;\ldots;\mathbf{x}_n]$:")
    R.equation(r"\mathbf{g}^{\mathrm{mean}}_t=\frac{1}{n}\sum_{i=1}^{n}\mathbf{x}_i", "e_mean")
    R.where(['$n$: số mục của nhóm; $\\mathbf{x}_i$: vector SBERT của mục $i$; $\\mathbf{g}^{\\mathrm{mean}}_t$: vector trung bình của nhóm loại $t$ (384 chiều).'])
    R.equation(r"\mathbf{g}^{\mathrm{sum}}_t=\sum_{i=1}^{n}\mathbf{x}_i", "e_sum")
    R.where(['$\\mathbf{g}^{\\mathrm{sum}}_t$: tổng các vector của nhóm (384 chiều); nhóm có nhiều mục thì tổng lớn hơn.'])
    R.equation(r"g^{\mathrm{max}}_{t,m}=\max_{1\leq i\leq n}x_{i,m},\qquad m=1,\ldots,384", "e_max")
    R.where(['$x_{i,m}$: thành phần thứ $m$ của $\\mathbf{x}_i$; $g^{\\mathrm{max}}_{t,m}$: giá trị lớn nhất của thành phần $m$ trên mọi mục của nhóm.'])
    R.equation(r"\mathbf{g}_t=\big[\mathbf{g}^{\mathrm{mean}}_t\,\big\|\,\mathbf{g}^{\mathrm{sum}}_t\,\big\|\,\mathbf{g}^{\mathrm{max}}_t\big]\in\mathbb{R}^{1152}", "e_deepsets")
    R.where(['Ký hiệu ‖: ghép nối tiếp các vector; $\\mathbf{g}_t$: vector nhóm cuối cùng của loại $t$ (3 × 384 = 1152 chiều).'])
    P(r"Nhóm rỗng (văn bản không có mục loại đó) cho $\mathbf{g}_t=\mathbf{0}$. Phép gộp [mean | sum | max] không có tham số học được nên giữ nguyên ngữ nghĩa SBERT.")
    hc = A["items"]["cv_hard_skills"]
    hj = A["items"]["jd_hard_skills"]
    f = lambda v: "[" + "; ".join(f"{x:+.3f}".replace(".", ",") for x in v) + "]"
    P(r"**Ví dụ (ba chiều đầu).** Với 13 mục hard_skills của CV: $\mathbf{g}^{\mathrm{mean}}=$ " + f(hc["mean3"]) + r", $\mathbf{g}^{\mathrm{sum}}=$ " + f(hc["sum3"]) + r", $\mathbf{g}^{\mathrm{max}}=$ " + f(hc["max3"]) +
      r". Với 7 mục của JD: $\mathbf{g}^{\mathrm{mean}}=$ " + f(hj["mean3"]) + r", $\mathbf{g}^{\mathrm{sum}}=$ " + f(hj["sum3"]) + r", $\mathbf{g}^{\mathrm{max}}=$ " + f(hj["max3"]) +
      r". Vì CV có nhiều mục hơn nên tổng lớn hơn (độ phủ rộng hơn), còn cực đại bằng nhau ở hai chiều đầu do hai bên cùng chứa các mục Java và Spring Boot.")
    M = A["hard_cos"]["matrix"]
    cvi, jdi = A["hard_cos"]["cv_items"], A["hard_cos"]["jd_items"]
    best = []
    for c in range(len(jdi)):
        col = [M[r][c] for r in range(len(cvi))]
        r = max(range(len(cvi)), key=lambda q: col[q])
        best.append((jdi[c], cvi[r], col[r]))
    R.table(["Yêu cầu hard_skills của JD", "Mục gần nhất trong CV", "Cosine", "Khớp (≥ 0,75)"],
            [[a, b, f"{c:.2f}".replace(".", ","), "có" if c >= 0.75 else "không"] for a, b, c in best],
            "Độ gần ngữ nghĩa của từng yêu cầu hard_skills của JD với CV (cosine SBERT, ngưỡng khớp 0,75).", widths=[5.4, 5.4, 2.4, 2.8], size=10, label="t_match")
    P(r"Sáu yêu cầu được đáp ứng đúng nghĩa (cosine 1,00); yêu cầu “Tiếng Anh” không có mục tương ứng (cosine cao nhất chỉ 0,42), phù hợp với thực tế CV không nêu ngoại ngữ.")

    H("2.2.5. Biểu diễn tổng thể của văn bản và điểm ngữ nghĩa (khối M2, bước 3)", 3)
    P(r"Ngoài sáu vector nhóm, mỗi văn bản có một vector toàn văn để làm nút trung tâm trong đồ thị. Gộp tất cả mục của sáu nhóm thành một chuỗi $\mathrm{text}(d)$ (các mục nối bằng dấu cách), "
      r"mã hóa bằng SBERT và đặt vào 384 chiều đầu của vector 1152 chiều (768 chiều còn lại bằng 0) để cùng kích thước với vector nhóm:")
    R.equation(r"\mathbf{f}_d=\big[\mathbf{x}_{\mathrm{text}(d)}\,\big\|\,\mathbf{0}_{768}\big]\in\mathbb{R}^{1152}", "e_center")
    R.where(['$\\mathbf{f}_d$: vector đặc trưng của nút trung tâm của văn bản $d$ (1152 chiều).', '$\\mathbf{x}_{\\mathrm{text}(d)}$: vector SBERT của chuỗi gộp mọi mục của $d$ (384 chiều); $\\mathbf{0}_{768}$: 768 số 0 đệm cho đủ kích thước.'])
    P(r"Điểm ngữ nghĩa của cặp là cosine giữa hai vector toàn văn:")
    R.equation(r"s_{\mathrm{sem}}(c,j)=\cos\big(\mathbf{x}_{\mathrm{text}(c)},\,\mathbf{x}_{\mathrm{text}(j)}\big)", "e_ssem")
    R.where(['$c,j$: văn bản CV và JD của cặp; $s_{\\mathrm{sem}}$: điểm ngữ nghĩa, càng gần 1 càng cùng chủ đề.'])
    P(r"Ý nghĩa các thành phần: $\mathbf{x}_{\mathrm{text}(c)}$ và $\mathbf{x}_{\mathrm{text}(j)}$ là vector của toàn bộ thông tin trích xuất của CV và JD; cosine đo góc giữa hai vector nên chỉ phụ thuộc hướng, "
      r"không phụ thuộc độ dài văn bản; giá trị gần 1 nghĩa là cùng chủ đề. Đây là điểm baseline “SBERT + cosine” ở mục 2.6 và cũng là một đặc trưng của bộ tổng hợp điểm. "
      r"Khi dùng riêng điểm này, ta thu được độ tương đồng chủ đề, không phân biệt được ứng viên đáp ứng đủ hay thiếu yêu cầu bắt buộc, vì vậy cần các khối tiếp theo.")
    P(r"**Ví dụ.** $s_{\mathrm{sem}}=" + f"{A['main_cos']:.3f}".replace(".", ",") + r"$ cho cặp ví dụ. Các cosine theo từng nhóm (trên 384 chiều đầu) là: " +
      "; ".join(f"{n} {v:.3f}".replace(".", ",") for n, v in zip(["soft", "hard", "edu", "field", "industry", "role"], A["topic_features"][1:])) + ".")

    # ================================================================== 2.3
    H("2.3. Biểu diễn đồ thị tuyển dụng Candidate–Skill–Job dựa trên GCN", 2)
    H("2.3.1. Đồ thị theo từng cặp và lý do có 14 nút", 3)
    P(r"**Đồ thị theo từng cặp là gì.** Với mỗi cặp $(c_i,j_k)$, hệ thống dựng một đồ thị nhỏ $G_{ik}$ chứa đúng thông tin của cặp đó: các nhóm thực thể của CV, các nhóm thực thể của JD, "
      r"và các cạnh nối những phần cần so sánh. Mạng GCN lan truyền thông tin trên $G_{ik}$ để rút ra một điểm duy nhất cho cặp (bài toán hồi quy mức đồ thị). "
      r"Cách làm này có ba ý nghĩa: (1) nhãn $y_{ik}$ gắn trực tiếp với một đồ thị nên có thể huấn luyện có giám sát; (2) mỗi cặp chỉ có 14 nút nên xây dựng rất nhẹ (khoảng 1,2 ms) và xử lý theo lô; "
      r"(3) quan hệ so sánh được mã hóa trong cấu trúc đồ thị thay vì để mạng tự suy ra từ hai vector phẳng.")
    P(r"**Vì sao đúng 14 nút.** Mỗi bên (CV, JD) có một nút trung tâm đại diện toàn văn và $T=6$ nút đại diện sáu nhóm thực thể:")
    R.equation(r"N=2+2T=2+2\times6=14", "e_N")
    R.where(['$N$: số nút của đồ thị một cặp; số 2 là hai nút trung tâm (CV và JD); $T=6$ là số loại thực thể; $2T$ là sáu nhóm của CV cộng sáu nhóm của JD.'])
    P(r"Số nút cố định cho mọi cặp (kể cả khi một nhóm rỗng, nút đó mang vector 0) nên các đồ thị có cùng kích thước, ghép được thành lô và thứ tự nút có ý nghĩa cố định: "
      r"nút 0 là CV, nút 1 là JD, nút 2–7 là các nhóm của CV, nút 8–13 là các nhóm của JD theo thứ tự soft_skills, hard_skills, education, field_of_education, industry_sector, role. "
      r"Nhờ vậy nút $2+t$ luôn so sánh được với nút $8+t$ cùng loại. (Ghi chú: bản thảo trước của báo cáo mô tả đồ thị 16 nút do có thêm hai nút chứng chỉ; phiên bản cài đặt hiện tại "
      r"không còn nút chứng chỉ, nên số nút là 14 và báo cáo được cập nhật tương ứng.)")
    H("2.3.2. Nút và đặc trưng khởi tạo", 3)
    P(r"Tập nút gồm hai nút trung tâm $v_c,v_j$ và $2T$ nút thực thể $u^{c}_t,u^{j}_t$. Đặc trưng khởi tạo của nút lấy trực tiếp từ đầu ra khối M2: nút trung tâm dùng $\mathbf{f}_c,\mathbf{f}_j$ (công thức 2.%s), "
      r"nút thực thể dùng vector nhóm $\mathbf{g}^{c}_t,\mathbf{g}^{j}_t$ (công thức 2.%s). Ma trận đặc trưng của toàn đồ thị:" % (R.ref("e_center").split(".")[1], R.ref("e_deepsets").split(".")[1]))
    R.equation(r"\mathbf{X}=\big[\mathbf{f}_c;\ \mathbf{f}_j;\ \mathbf{g}^{c}_1;\ldots;\mathbf{g}^{c}_T;\ \mathbf{g}^{j}_1;\ldots;\mathbf{g}^{j}_T\big]\in\mathbb{R}^{14\times1152}", "e_X")
    R.where(['$\\mathbf{X}$: ma trận đặc trưng, mỗi hàng là vector 1152 chiều của một nút (14 hàng).', '$\\mathbf{f}_c,\\mathbf{f}_j$: nút trung tâm CV, JD; $\\mathbf{g}^{c}_t,\\mathbf{g}^{j}_t$: nút nhóm loại $t$ của CV, JD.'])
    P(r"Hình 2.3(a) minh họa 14 nút của cặp ví dụ. Các nút chưa có cạnh; các mục tiếp theo bổ sung từng loại cạnh.")
    R.figure("figures/fig_graph_steps.png", r"Quá trình dựng đồ thị cho cặp ví dụ: (a) nút; (b) cạnh sao và cầu; (c) cạnh chéo; (d) cạnh k-NN của nút role CV; (e) hợp nhất. Số liệu là kết quả chạy thật.",
             width_cm=16.0, label="fig_graph")
    H("2.3.3. Cạnh sao và cạnh cầu (khởi tạo trọng số theo nghiệp vụ)", 3)
    P(r"**Cạnh sao** nối nút trung tâm với từng nút thực thể cùng bên, cho phép nút trung tâm thu thập thông tin của mọi nhóm. Trọng số là hệ số nghiệp vụ $\lambda_t$ theo mức độ quyết định của loại thực thể "
      r"(vai trò sai cấp độ là lỗi nghiêm trọng nhất, kỹ năng mềm gần như JD nào cũng yêu cầu):")
    R.equation(r"w(v_c,u^{c}_t)=w(u^{c}_t,v_c)=w(v_j,u^{j}_t)=w(u^{j}_t,v_j)=\lambda_t", "e_star")
    R.where(['$v_c,v_j$: nút trung tâm của CV, JD; $u^{c}_t,u^{j}_t$: nút nhóm loại $t$ của CV, JD.', '$w(a,b)$: trọng số cạnh từ nút $a$ đến nút $b$ (cạnh hai chiều nên hai hướng cùng giá trị); $\\lambda_t$: hệ số nghiệp vụ của loại $t$ (loại càng quan trọng càng lớn).'])
    P(r"**Cạnh cầu** nối trực tiếp hai nút trung tâm để so sánh toàn văn:")
    R.equation(r"w(v_c,v_j)=w(v_j,v_c)=1", "e_bridge")
    R.where(['Cạnh nối hai nút trung tâm có trọng số cố định bằng 1.'])
    P(r"Các hệ số $\lambda_t$ là siêu tham số đặt theo nghiệp vụ (role 3,0; hard_skills 2,5; field_of_education 2,0; industry_sector 1,5; education 1,5; soft_skills 1,0), không học trong huấn luyện. "
      r"Hình 2.3(b) cho thấy các cạnh sao từ role dày nhất.")
    H("2.3.4. Cạnh chéo giữa các nhóm cùng loại", 3)
    P(r"Cạnh chéo nối nút thực thể của CV với nút cùng loại của JD, giúp mạng thấy trực tiếp “role của CV có giống role của JD không”. Trọng số bằng độ tương đồng cosine nhân hệ số nghiệp vụ; "
      r"chỉ giữ phần dương và chỉ tạo cạnh khi trọng số dương:")
    R.equation(r"w(u^{c}_t,u^{j}_t)=w(u^{j}_t,u^{c}_t)=\max\big(\cos(\mathbf{g}^{c}_t,\mathbf{g}^{j}_t),\,0\big)\cdot\lambda_t", "e_cross")
    R.where(['$\\cos(\\mathbf{g}^{c}_t,\\mathbf{g}^{j}_t)$: độ gần ngữ nghĩa giữa nhóm loại $t$ của CV và của JD; $\\max(\\cdot,0)$: chỉ lấy phần dương.', '$\\lambda_t$: hệ số nghiệp vụ. Hai nhóm càng giống nhau thì cạnh càng nặng.'])
    cr = A["cross"]
    P(r"**Ví dụ (Hình 2.3(c)).** " + "; ".join(f"{n}: {cr[k]['cosine']:.2f}×{cr[k]['lambda']:g} = {cr[k]['weight']:.2f}".replace(".", ",") for n, k in
      [("soft", "soft_skills"), ("hard", "hard_skills"), ("education", "education"), ("field", "field_of_education"), ("industry", "industry_sector"), ("role", "role")]) +
      r". Nhóm field_of_education có cosine 1,00 vì cả hai cùng là “Công nghệ thông tin”.")
    H("2.3.5. Cạnh k-NN và tham số làm sắc nét p", 3)
    P(r"Ngoài các quan hệ có chủ đích ở trên, đồ thị còn có cạnh k-NN nối mỗi nút với $k=10$ nút giống nó nhất trong 13 nút còn lại, để bắt những quan hệ không dự kiến trước (ví dụ nhóm hard_skills của CV giống nhóm industry_sector của JD). "
      r"Gọi $\mathcal{N}_k(i)$ là tập $k$ nút có cosine lớn nhất với nút $i$ (cosine tính trên vector 1152 chiều của nút). Trọng số của cạnh $i\to l$ được tính theo hai bước: nâng lũy thừa $p$ rồi chuẩn hóa theo hàng:")
    R.equation(r"w_{il}=\frac{\max(\cos_{il},0)^{p}}{\sum_{m\in\mathcal{N}_k(i)}\max(\cos_{im},0)^{p}},\qquad l\in\mathcal{N}_k(i)", "e_knn")
    R.where(['$\\cos_{il}$: cosine giữa vector của nút $i$ và nút $l$; $\\mathcal{N}_k(i)$: $k$ nút giống nút $i$ nhất; $w_{il}$: trọng số cạnh từ $i$ đến $l$.', '$p$: số mũ làm sắc nét (giải thích bên dưới); mẫu số là tổng để các trọng số đi ra từ nút $i$ cộng lại bằng 1.'])
    P(r"**Ý nghĩa của tham số p.** Tham số $p$ (cài đặt $p=4$) là số mũ làm sắc nét (sharpening). Khi $p=1$ trọng số tỉ lệ thẳng với cosine nên các nút chỉ hơi giống nhau vẫn nhận phần đáng kể; khi $p$ lớn, "
      r"phép lũy thừa khuếch đại chênh lệch, nên trọng số dồn vào các hàng xóm thực sự giống và triệt tiêu nhiễu. Chuẩn hóa theo hàng làm tổng trọng số các cạnh ra khỏi một nút bằng 1, "
      r"tránh việc các cạnh k-NN lấn át cạnh sao/chéo (có trọng số lớn hơn 1).")
    top = A["knn_role"]["top"]
    cs = [t[1] for t in top]
    raw4 = [c ** 4 for c in cs]
    w4 = raw4[0] / sum(raw4)
    w1 = cs[0] / sum(cs)
    P(r"**Ví dụ (nút 7, role của CV – Hình 2.3(d)).** Hàng xóm gần nhất là nút 13 (role của JD) với cosine " + f"{cs[0]:.3f}".replace(".", ",") +
      r"; chín hàng xóm còn lại có cosine " + f"{min(cs[1:]):.2f}–{max(cs[1:]):.2f}".replace(".", ",") + r". Với $p=4$: $" + f"{cs[0]:.3f}".replace(".", ",") + r"^{4}=" + f"{raw4[0]:.3f}".replace(".", ",") +
      r"$, tổng lũy thừa của mười hàng xóm là $" + f"{sum(raw4):.3f}".replace(".", ",") + r"$ nên $w_{7\to13}=" + f"{w4:.3f}".replace(".", ",") + r"$, trong khi mỗi hàng xóm còn lại chỉ nhận khoảng 0,01. "
      r"Nếu $p=1$ thì $w_{7\to13}=" + f"{w1:.3f}".replace(".", ",") + r"$, nghĩa là quan hệ role–role bị pha loãng bởi chín nút không liên quan.")
    H("2.3.6. Hợp nhất cạnh và trọng số sau cùng", 3)
    P(r"Ba nguồn cạnh có thể cùng nối một cặp nút (ví dụ nút 7–13 vừa có cạnh chéo vừa có cạnh k-NN). Khi trùng, lấy trọng số lớn nhất, nên các quan hệ có chủ đích (sao, chéo) luôn được giữ nguyên giá trị:")
    R.equation(r"w_{uv}=\max\big(w^{\mathrm{star/bridge}}_{uv},\ w^{\mathrm{cross}}_{uv},\ w^{\mathrm{knn}}_{uv}\big)", "e_merge")
    R.where(['$w_{uv}$: trọng số cuối cùng của cạnh $u\\to v$; ba số trong $\\max$ lần lượt là trọng số từ cạnh sao/cầu, cạnh chéo và cạnh k-NN (bằng 0 nếu không có loại cạnh đó).'])
    deg = {}
    for (s, d), w in zip(A["edges"], A["edge_w"]):
        deg[d] = deg.get(d, 0.0) + w
    d7, d13 = 1 + deg[7], 1 + deg[13]
    w713 = [w for (s, d), w in zip(A["edges"], A["edge_w"]) if (s, d) == (7, 13)][0]
    P(r"Kết quả cho cặp ví dụ: " + f"{A['n_nodes']} nút và {A['n_edges']} cạnh có hướng (Hình 2.3(e)); mật độ cạnh {A['adj_density']:.2f}".replace(".", ",") + r".")
    P(r"**Trọng số cạnh được cập nhật như thế nào.** Cần phân biệt hai việc. (1) Trọng số $w_{uv}$ được tính một lần khi dựng đồ thị từ embedding (công thức 2.%s–2.%s) và cố định, không phải tham số huấn luyện; "
      r"vì vậy việc “cập nhật” duy nhất khi dựng đồ thị là chọn trọng số lớn nhất khi trùng cạnh. (2) Trong mỗi lớp GCN, trọng số được chuẩn hóa theo bậc của nút (công thức 2.%s ở mục 2.4.2) để nút nhiều cạnh không lấn át. "
      r"Ví dụ: tổng trọng số vào nút 7 cộng 1 (vòng lặp tự thân) là $\tilde d_7=%s$, vào nút 13 là $\tilde d_{13}=%s$, nên cạnh 7→13 có trọng số $w_{7\to13}=%s$ được chuẩn hóa thành $%s/\sqrt{%s\cdot%s}=%s$. "
      r"Điều được học trong huấn luyện là ma trận trọng số $\mathbf{W}^{(l)}$ biến đổi đặc trưng nút, không phải trọng số cạnh." %
      (R.ref("e_star").split(".")[1], R.ref("e_merge").split(".")[1], R.ref("e_gcn_norm").split(".")[1], *[f"{v:.3f}".replace(".", ",") if i in (2, 3, 6) else f"{v:.2f}".replace(".", ",") for i, v in enumerate((d7, d13, w713, w713, d7, d13, w713 / math.sqrt(d7 * d13)))]))
    H("2.3.7. Tổ chức lưu trữ đồ thị", 3)
    P(r"Mỗi đồ thị được lưu thành một tệp PyTorch Geometric (graph_NNNNNN.pt trong data/processed/graphs/), gồm các trường: **x** (ma trận $14\times1152$, kiểu float32), "
      r"**edge_index** (hai hàng chỉ số nút nguồn – nút đích), **edge_attr** (trọng số mỗi cạnh), **y** (nhãn mức phù hợp, sau đó quy về $y/3$ khi huấn luyện), cùng mã nguồn cv_source, jd_source để truy vết cặp. "
      r"Bộ dữ liệu gồm 1664 tệp, trung bình khoảng 71,5 KB mỗi tệp (tổng cộng khoảng 119 MB), mỗi tệp có trung bình 150 cạnh. Khi huấn luyện, các đồ thị được ghép thành lô (batch) bằng DataLoader của PyG [22]. "
      r"Thực thể trích xuất và vector embedding được lưu đệm riêng (data/cache/) để không phải gọi lại LLM và SBERT khi dựng lại đồ thị.")
