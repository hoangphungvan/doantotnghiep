"""Nội dung Chương 1 (viết lại theo góp ý giảng viên)."""

import docx

REFS_HINT = "Tài liệu tham khảo ở cuối báo cáo"


def build(R, orig_path):
    od = docx.Document(orig_path)
    ot = [p.text.strip() for p in od.paragraphs]
    P, H, B = R.para, R.heading, R.bullet

    R.new_chapter(1)
    H("CHƯƠNG 1. PHÂN TÍCH BÀI TOÁN KHỚP NỐI CV–JD TRONG TUYỂN DỤNG THÔNG MINH", 1)

    # ------------------------------------------------------------------ 1.1 (giữ nguyên)
    H("1.1. Bối cảnh và nhu cầu thực tế của bài toán tuyển dụng", 2)
    P(ot[19])
    P(ot[20])
    P(ot[21])
    for k in (22, 23):
        B(ot[k])
    B(ot[24])

    # ------------------------------------------------------------------ 1.2 Mô tả bài toán
    H("1.2. Mô tả bài toán khớp nối CV–JD", 2)
    P("Bài toán khớp nối CV–JD (resume–job matching, còn gọi là person–job fit) là bài toán xác định mức độ phù hợp giữa một hồ sơ ứng viên (CV) "
      "và một tin tuyển dụng (JD), từ đó giúp nhà tuyển dụng có danh sách các CV phù hợp nhất cho từng JD, xếp theo độ phù hợp giảm dần. Hệ thống chấm điểm từng cặp CV–JD, việc xếp hạng là bước sắp xếp các điểm của cùng một JD. Hình 1.1 mô tả luồng tổng quát "
      "Đầu vào – Xử lý – Đầu ra của bài toán; các mục 1.2.1–1.2.3 diễn giải từng khối. Mô tả trong mục này mang tính tổng quát, "
      "không phụ thuộc vào một mô hình cụ thể; cách giải quyết do đề tài đề xuất được trình bày ở Chương 2.")
    R.figure("figures/fig_ipo.png", "Luồng tổng quát Đầu vào – Xử lý – Đầu ra của bài toán khớp nối CV–JD (vẽ bằng matplotlib, xuất SVG vector).",
             width_cm=15.2, label="fig_ipo")

    H("1.2.1. Đầu vào (Input)", 3)
    P(r"Đầu vào của hệ thống tại mỗi lần xử lý là **một cặp gồm một CV và một JD**, không phải cả một tập tệp. Mỗi văn bản là dữ liệu phi cấu trúc hoặc bán cấu trúc, "
      r"có thể bằng tiếng Việt, tiếng Anh hoặc song ngữ (ví dụ CV tiếng Việt có xen các thuật ngữ kỹ thuật như “Spring Boot”, “CI/CD”). Dữ liệu của đề tài thuộc lĩnh vực "
      r"công nghệ thông tin (CNTT), nhưng cách mô tả bài toán không giới hạn ở một ngôn ngữ hay một ngành nghề.")
    R.equation(r"x=(c,\,j)", "e_pair")
    R.where([r"$c$: văn bản CV của một ứng viên (vị trí ứng tuyển, kỹ năng, học vấn, kinh nghiệm…).",
             r"$j$: văn bản JD của một vị trí cần tuyển (yêu cầu kỹ năng, học vấn, kinh nghiệm, lĩnh vực…)."])
    P(r"Khi cần có danh sách ứng viên cho một JD, ứng dụng bên ngoài (ví dụ backend của website tuyển dụng) lần lượt gửi từng cặp $(c_1,j),(c_2,j),\ldots,(c_n,j)$ "
      r"với cùng một JD $j$ và $n$ CV ứng tuyển, rồi nhận kết quả từng cặp. Hệ thống xử lý các cặp độc lập với nhau.")
    P(r"**Dữ liệu huấn luyện và đánh giá.** Riêng giai đoạn xây dựng mô hình, có tập CV, tập JD và nhãn mức phù hợp của từng cặp:")
    R.equation(r"\mathcal{C}=\{c_1,\ldots,c_N\},\qquad \mathcal{J}=\{j_1,\ldots,j_M\},\qquad y_{ik}\in\{0,1,2,3\}", "e_C")
    R.where([r"$\mathcal{C}$, $N$: tập CV và số CV; $\mathcal{J}$, $M$: tập JD và số JD.",
             r"$y_{ik}$: nhãn mức phù hợp của cặp $(c_i,j_k)$; $0$ là không phù hợp, các mức tiếp theo phù hợp tăng dần, $3$ là phù hợp tốt. "
             r"Nhãn chỉ dùng khi huấn luyện và đánh giá, không cần khi hệ thống chạy thực tế. Thang nhãn cụ thể ở mục 2.6.1."])

    H("1.2.2. Xử lý (Process)", 3)
    P("**Nguyên lý chung.** Một nhà tuyển dụng đánh giá mức độ phù hợp bằng cách (i) đọc hiểu CV và JD, rút ra những thông tin cốt lõi (vai trò, kỹ năng, "
      "trình độ, kinh nghiệm), (ii) so sánh yêu cầu của JD với năng lực của ứng viên không chỉ theo mặt chữ mà theo ý nghĩa, (iii) cho một kết luận về mức độ phù hợp và giải thích, "
      "và (iv) khi có nhiều ứng viên, xếp các ứng viên từ phù hợp nhất đến kém phù hợp nhất. Hệ thống tự động mô phỏng quy trình này theo năm bước tổng quát dưới đây (Hình 1.1).")
    P(r"**Mục tiêu của khối xử lý** là xây dựng một hàm chấm điểm cho một cặp, kèm ánh xạ sang mức phù hợp:")
    R.equation(r"s=s(c,j)\in\mathbb{R},\qquad \hat{y}=\phi(s)\in\{0,1,2,3\}", "e_s")
    R.where([r"$s(c,j)$: điểm phù hợp của cặp $(c,j)$; điểm càng cao thì CV càng phù hợp với JD.",
             r"$\phi$: phép quy điểm về mức phù hợp (ví dụ làm tròn); $\hat{y}$: mức phù hợp dự đoán của cặp."])
    P(r"Yêu cầu quan trọng nhất: với cùng một JD $j$, các CV thực sự phù hợp phải có điểm $s$ cao hơn các CV không phù hợp, để việc sắp xếp theo điểm đưa đúng ứng viên lên đầu danh sách.")
    B("**Bước 1 – Tiền xử lý và trích xuất thông tin có cấu trúc** (áp dụng cho CV $c$ và JD $j$ của cặp). Chuẩn hóa văn bản rồi tách ra các thông tin có "
      "ý nghĩa với bài toán: vị trí/vai trò, kỹ năng chuyên môn, kỹ năng mềm, học vấn, ngành đào tạo, lĩnh vực và yêu cầu kinh nghiệm. Mục đích: "
      "đưa văn bản tự do về các “mục” nhỏ, so sánh được với nhau.")
    B("**Bước 2 – Biểu diễn ngữ nghĩa.** Chuyển mỗi mục (hoặc cả văn bản) thành vector trong một không gian liên tục sao cho các khái niệm gần nghĩa "
      "(ví dụ “Golang” và “Go language”, hoặc “lập trình viên backend” và “Backend Developer”) nằm gần nhau, kể cả khi khác ngôn ngữ. Mục đích: "
      "khắc phục sai khác về cách diễn đạt mà khớp từ khóa không xử lý được.")
    B("**Bước 3 – Đối sánh và tính điểm phù hợp.** So khớp CV với JD theo từng khía cạnh (vai trò, kỹ năng, học vấn…) và tổng hợp thành điểm $s(c,j)$ của cặp. "
      "Mục đích: biến sự giống nhau về ngữ nghĩa và cấu trúc thành một con số liên tục.")
    B("**Bước 4 – Phân mức và sinh diễn giải.** Quy điểm về mức 0–3 để đọc nhanh; từ kết quả đối chiếu (yêu cầu nào của JD đã được đáp ứng, yêu cầu nào chưa thấy trong CV), "
      "tạo lời giải thích ngắn gọn cho nhà tuyển dụng. Đây là bước tạo ra đầu ra “thông tin diễn giải” ở mục 1.2.3.")
    B("**Bước 5 – Xếp hạng các CV của cùng một JD.** Khi đã có điểm của các cặp $(c_1,j),\\ldots,(c_n,j)$, sắp xếp các CV theo điểm giảm dần. Bước này chỉ cần phép sắp xếp, "
      "nên có thể thực hiện ở ứng dụng gọi hệ thống (backend) mà không cần chạy lại mô hình:")
    R.equation(r"\pi_j=\big(c_{(1)},\ldots,c_{(n)}\big)\ \ \text{sao cho}\ \ s\big(c_{(1)},j\big)\geq\cdots\geq s\big(c_{(n)},j\big)", "e_rank")
    R.where([r"$\pi_j$: danh sách các CV của JD $j$ sau khi sắp xếp.",
             r"$c_{(r)}$: CV đứng ở vị trí $r$ ($r=1$ là CV phù hợp nhất); $n$: số CV ứng tuyển cho JD $j$.",
             r"$s(c_{(r)},j)$: điểm phù hợp của CV đó với JD $j$."])
    P("Chương 2 trình bày một cách hiện thực hóa cụ thể các bước 1–4 bằng mô hình lai Semantic Embedding – Graph Neural Network, kèm công thức tính từng thành phần.")

    H("1.2.3. Đầu ra (Output)", 3)
    P("Đầu ra gồm hai phần. Với **mỗi cặp** $(c,j)$, hệ thống trả về:")
    B("**Điểm phù hợp** $s(c,j)$ của cặp.")
    B("**Mức phù hợp** $\\hat{y}\\in\\{0,1,2,3\\}$ để đọc nhanh (không phù hợp … phù hợp tốt).")
    B("**Thông tin diễn giải**: danh sách yêu cầu bắt buộc của JD mà CV đã đáp ứng/chưa thấy, kèm ghi chú về điều kiện cứng (bằng cấp, chứng chỉ) và số năm kinh nghiệm. "
      "Đầu ra này được sinh ở Bước 4.")
    P("Với **mỗi JD**, từ điểm của các cặp, danh sách CV được sắp xếp giảm dần theo điểm (công thức 1." + R.ref("e_rank").split(".")[1] + ", Bước 5), giúp nhà tuyển dụng xem trước các ứng viên phù hợp nhất.")

    # ------------------------------------------------------------------ 1.3 Hướng tiếp cận
    H("1.3. Các hướng tiếp cận giải quyết bài toán khớp nối CV–JD", 2)
    P("Căn cứ trên nguyên lý chung và mục tiêu ở mục 1.2.2, phần này điểm lại các hướng tiếp cận đã được nghiên cứu: cơ chế giải quyết, vấn đề mà mỗi hướng "
      "tập trung, và hạn chế còn tồn tại. Các số trong ngoặc vuông là tài liệu tham khảo ở cuối báo cáo.")

    H("1.3.1. Khớp từ khóa và thống kê (TF-IDF, BM25)", 3)
    P("Phần lớn các Hệ thống theo dõi ứng viên (Applicant Tracking System – ATS) vẫn vận hành dựa trên khớp từ khóa. Mỗi văn bản được biểu diễn dạng túi từ "
      "(Bag-of-Words); trọng số TF-IDF [1] đánh giá một từ quan trọng nếu xuất hiện nhiều trong văn bản nhưng hiếm trong toàn bộ tập văn bản, còn hàm xếp hạng "
      "BM25 [2] bổ sung chuẩn hóa theo độ dài văn bản và bão hòa tần suất từ. Điểm phù hợp thường là độ tương đồng cosine giữa hai vector từ. "
      "Hướng này tập trung vào việc truy hồi nhanh, đơn giản, không cần dữ liệu gán nhãn và dễ giải thích theo từ khóa. Tuy nhiên có các hạn chế sau:")
    B("**Bất đồng từ vựng (vocabulary mismatch).** Cùng một khái niệm có nhiều cách diễn đạt (“ReactJS” và “Frontend JavaScript Framework”, “Golang” và “Go language”). "
      "Không chia sẻ token chung nên điểm tương đồng gần bằng 0, khiến hệ thống loại oan ứng viên tiềm năng.")
    B("**Thiếu hiểu biết ngữ cảnh.** Chỉ đếm sự xuất hiện của từ, không phân biệt mức độ: “định hướng tìm hiểu Machine Learning” và “3 năm thiết kế hệ thống "
      "Machine Learning” nhận điểm gần như nhau; cụm phủ định như “chưa có kinh nghiệm với Java” vẫn có thể được tính là khớp.")
    B("**Bỏ qua cấu trúc quan hệ đa chiều.** Hồ sơ tuyển dụng là mạng quan hệ giữa vai trò, kỹ năng cứng, kỹ năng mềm, học vấn và lĩnh vực; vector từ phẳng làm mất "
      "thông tin này nên không phân biệt được ứng viên “giỏi kỹ năng nhưng sai vị trí” với ứng viên “phù hợp toàn diện”.")
    B("**Dễ bị đánh lừa và thiếu điểm liên tục có thể diễn giải.** Nhồi nhét từ khóa (keyword stuffing) làm tăng điểm mà năng lực thực tế không tương ứng; nhiều ATS "
      "chỉ trả kết quả nhị phân “khớp/không khớp” theo ngưỡng từ khóa tối thiểu.")

    H("1.3.2. Biểu diễn ngữ nghĩa bằng embedding", 3)
    P("Để khắc phục bất đồng từ vựng, các phương pháp embedding ánh xạ từ hoặc câu vào không gian vector liên tục, trong đó khoảng cách phản ánh độ gần về nghĩa. "
      "Word2vec [3] học vector từ từ ngữ cảnh xuất hiện nhưng mỗi từ chỉ có một vector, không phụ thuộc ngữ cảnh. BERT [4] sinh biểu diễn theo ngữ cảnh, nhưng việc "
      "so sánh hai câu phải đưa cả cặp vào mạng nên chi phí lớn khi cần so nhiều cặp. Sentence-BERT [5] huấn luyện mạng song sinh để mỗi câu có một vector cố định, "
      "so sánh bằng cosine, và bản đa ngữ [6] mở rộng sang hơn 50 ngôn ngữ (gồm tiếng Việt), phù hợp văn bản CV/JD trộn tiếng Việt – tiếng Anh. "
      "JobBERT [7] tinh chỉnh BERT trên tin tuyển dụng để chuẩn hóa chức danh nghề qua kỹ năng đi kèm; hướng này tập trung vào tầng chức danh nhưng huấn luyện trên dữ liệu "
      "tiếng Anh và chưa giải quyết việc so khớp toàn bộ CV với JD. Hạn chế chung của hướng embedding thuần: một vector cho cả văn bản gom mọi khía cạnh vào một điểm, nên "
      "khó phân biệt vai trò đúng với kỹ năng đúng; cosine giữa hai vector thể hiện sự giống nhau về chủ đề hơn là việc ứng viên có đáp ứng từng yêu cầu bắt buộc hay không.")

    H("1.3.3. Học sâu có giám sát cho Person–Job Fit", 3)
    P("Nhóm này huấn luyện mạng nơ-ron trực tiếp trên dữ liệu ghép cặp. Zhu và cộng sự [8] dùng mạng tích chập để học biểu diễn chung của JD và CV, "
      "với tín hiệu giám sát từ lịch sử ứng tuyển. Qin và cộng sự [9] dùng mạng hồi quy với cơ chế chú ý phân tầng để học “mức năng lực” mà JD yêu cầu và đối sánh với năng lực "
      "nêu trong CV, đồng thời cho phép xem phần văn bản nào được chú ý. Bian và cộng sự [10] đề xuất mạng đồng huấn luyện đa góc nhìn (nội dung văn bản và quan hệ tương tác) để giảm phụ "
      "thuộc vào dữ liệu tương tác thưa. Nhìn chung các mô hình này đạt kết quả tốt khi có lượng lớn dữ liệu tương tác, nhưng (i) cần nhãn quy mô lớn, thường là dữ liệu riêng của "
      "nền tảng tuyển dụng; (ii) biểu diễn văn bản dưới dạng chuỗi phẳng, chưa mô hình hóa tường minh quan hệ giữa các loại thông tin; (iii) khó giải thích khi đánh giá từng yêu cầu bắt buộc. "
      "Một số hệ thống thực tế dùng embedding cho ghép việc–ứng viên quy mô lớn [11], ưu tiên tốc độ truy hồi hơn độ chính xác ở mức từng yêu cầu.")

    H("1.3.4. Mô hình đồ thị (Graph Neural Network)", 3)
    P("Mạng nơ-ron đồ thị cho phép học trên dữ liệu có cấu trúc quan hệ. Mạng tích chập đồ thị GCN [12] cập nhật biểu diễn mỗi nút bằng trung bình có trọng số của các nút lân cận "
      "(lan truyền thông tin), qua đó mỗi nút “nhìn thấy” ngữ cảnh quanh nó. Áp dụng vào tuyển dụng, ứng viên, kỹ năng, vị trí và yêu cầu được xem là các nút nối với nhau bằng cạnh có trọng số. "
      "Hướng này tập trung vào khai thác cấu trúc quan hệ mà biểu diễn phẳng bỏ qua. Hạn chế: chất lượng phụ thuộc vào cách dựng đồ thị và chất lượng trích xuất thực thể đầu vào; "
      "với dữ liệu nhỏ, mô hình dễ phân biệt chủ đề (cùng/khác ngành) nhưng yếu ở việc phân biệt các mức phù hợp sát nhau trong cùng một vai trò (kết quả thực nghiệm ở mục 2.6).")

    H("1.3.5. Trích xuất và đánh giá bằng mô hình ngôn ngữ lớn (LLM)", 3)
    P("Mô hình ngôn ngữ lớn có khả năng đọc hiểu văn bản tự do và trả về thông tin có cấu trúc; nhiều nghiên cứu dùng LLM để trích xuất kỹ năng hoặc sinh dữ liệu huấn luyện cho tác vụ trích xuất kỹ năng [13]. "
      "Hướng này mạnh ở hiểu ngữ cảnh, phủ định và yêu cầu bắt buộc/ưu tiên, nhưng có chi phí gọi mô hình, độ trễ, kết quả có thể thay đổi giữa các lần gọi và phụ thuộc nhà cung cấp; "
      "vì vậy cần bộ nhớ đệm (cache) và không nên dùng LLM làm bộ chấm điểm duy nhất.")

    H("1.3.6. Tổng hợp và định vị hướng tiếp cận của đề tài", 3)
    R.table(["Hướng tiếp cận", "Cơ chế chính", "Tập trung giải quyết", "Hạn chế chính"],
            [["Khớp từ khóa (TF-IDF, BM25) [1][2]", "Vector từ, cosine/xếp hạng xác suất", "Truy hồi nhanh, đơn giản, giải thích theo từ khóa", "Bất đồng từ vựng, mù ngữ cảnh, không có cấu trúc"],
             ["Embedding câu (SBERT, đa ngữ, JobBERT) [4]–[7]", "Vector ngữ nghĩa, cosine", "Đồng nghĩa, đa ngôn ngữ", "Một vector gộp mọi khía cạnh; thiên về chủ đề"],
             ["Học sâu Person–Job Fit [8]–[10]", "CNN/RNN/attention trên cặp văn bản", "Học trực tiếp từ nhãn tương tác", "Cần nhiều dữ liệu; chuỗi phẳng; khó giải thích"],
             ["Mô hình đồ thị GCN [12]", "Lan truyền thông tin trên đồ thị", "Quan hệ giữa các loại thông tin", "Phụ thuộc cách dựng đồ thị; yếu ở mức phù hợp sát nhau"],
             ["LLM trích xuất/đánh giá [13]", "Đọc hiểu, trả thông tin có cấu trúc", "Ngữ cảnh, phủ định, yêu cầu bắt buộc", "Chi phí, độ trễ, không ổn định tuyệt đối"]],
            "Tổng hợp các hướng tiếp cận bài toán khớp nối CV–JD.", widths=[3.6, 3.7, 4.0, 4.7], size=10.5, label="t_approach")
    P("Mỗi hướng giải quyết tốt một phần của năm bước ở mục 1.2.2: LLM mạnh ở Bước 1, embedding mạnh ở Bước 2, đồ thị mạnh ở Bước 3 (quan hệ giữa các khía cạnh). "
      "Đề tài vì vậy đề xuất kết hợp các thành phần bổ trợ nhau thay vì dùng riêng lẻ: LLM để trích xuất thực thể, SBERT để biểu diễn ngữ nghĩa, GCN để đối sánh theo cấu trúc, "
      "và một bộ tổng hợp điểm để kết hợp tín hiệu đồ thị với đánh giá yêu cầu bắt buộc.")

    # ------------------------------------------------------------------ 1.4
    H("1.4. Xác định mục tiêu, phạm vi và hướng tiếp cận của đề tài", 2)
    P("**Mục tiêu.** Xây dựng và đánh giá một hệ thống khớp nối CV–JD trong lĩnh vực CNTT với bốn mục tiêu: (1) độ chính xác xếp hạng các CV của mỗi JD cao hơn các phương pháp cơ sở "
      "(TF-IDF, SBERT, học sâu đơn giản); (2) tận dụng cấu trúc quan hệ giữa các loại thực thể bằng mô hình đồ thị; (3) cho ra điểm liên tục và mức phù hợp 0–3; "
      "(4) cung cấp diễn giải dễ hiểu cho nhà tuyển dụng, hỗ trợ cả tiếng Việt và tiếng Anh.")
    P("**Phạm vi.** Dữ liệu gồm 104 CV tổng hợp (13 nhóm nghề CNTT × 4 cấp độ × 2 CV) và 159 JD thật lấy từ bộ VietJobs [23], tạo 1664 cặp có nhãn mức phù hợp 0–3 theo rubric thống nhất. "
      "Đề tài tập trung vào lĩnh vực CNTT, văn bản tiếng Việt có xen tiếng Anh; chưa xét dữ liệu tương tác thực tế (nhấp chuột, kết quả phỏng vấn) hay các ngành ngoài CNTT. "
      "Nhãn do một người chấm theo rubric (đã kiểm chứng mù trên 36 cặp), do đó kết quả thể hiện khả năng bắt chước rubric chứ không phải độ phù hợp tuyệt đối.")
    P("**Hướng tiếp cận.** (i) LLM trích xuất sáu loại thực thể từ CV và JD; (ii) SBERT đa ngữ + DeepSets biểu diễn từng nhóm thực thể; (iii) dựng một đồ thị 14 nút cho mỗi cặp CV–JD và dùng GCN "
      "tính điểm đồ thị; (iv) tổng hợp điểm đồ thị với độ tương đồng ngữ nghĩa và đặc trưng đánh giá yêu cầu bắt buộc bằng một mô hình xếp chồng (stacking); (v) sinh diễn giải từ kết quả đối chiếu yêu cầu. "
      "Hệ thống được đánh giá bằng cross-validation 5 lượt chia theo CV với các độ đo xếp hạng (NDCG@K, Recall@K, MRR) và độ đo phân loại, so với các phương pháp cơ sở.")
