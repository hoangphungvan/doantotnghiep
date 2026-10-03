# Candidate-Job Matching

## 1. Mục tiêu hệ thống

Đây là hệ thống khớp CV với Job Description (JD) cho bài toán tuyển dụng IT tiếng Việt. Mục tiêu chính là xếp hạng các JD theo mức độ phù hợp với một CV, không phải chỉ phân loại một cặp CV-JD thành đúng hoặc sai.

Với một CV c và danh sách công việc J = {j1, j2, ..., jn}, hệ thống tính điểm:

$$
score(c, j_k)
$$

sau đó sắp xếp các JD theo điểm giảm dần.

Mỗi cặp CV-JD có thể có mức độ liên quan:

| Grade | Ý nghĩa |
|---:|---|
| 3 | Rất phù hợp |
| 2 | Phù hợp một phần |
| 1 | Có liên quan nhưng là hard negative |
| 0 | Không phù hợp |

Trong Recall@K và MRR, một JD được xem là `relevant` khi `grade >= 2`.
NDCG vẫn sử dụng đầy đủ graded relevance 0–3.

## 2. Mô hình kiến trúc tổng quát

Luồng chính của hệ thống:

~~~text
CV / JD thô
    ↓
Tiền xử lý văn bản
    ↓
Trích xuất entity
    ↓
Entity Cache
    ↓
Sentence-BERT embedding
    ↓
DeepSets pooling
    ↓
Xây dựng Candidate-Skill-Job graph
    ↓
GCN
    ↓
GCN Score
    ↓
Semantic Similarity
    ↓
Certification Bonus
    ↓
Hybrid Score
    ↓
Xếp hạng JD theo từng CV
    ↓
NDCG@K / Recall@K / MRR
~~~

Các module chính:

| Thành phần | File chính | Vai trò |
|---|---|---|
| Cấu hình | config.py | Entity types, trọng số, đường dẫn và hyperparameter |
| Trích xuất entity | src/extraction/entity_extractor.py | LLM extraction, chuẩn hóa và cache |
| Cache JD | src/data_collection/cache_jd_embeddings.py | Trích xuất và cache biểu diễn JD |
| Embedding | src/representation/embedding_generator.py | SBERT và DeepSets |
| Đồ thị | src/representation/graph_builder.py | Tạo PyTorch Geometric graph |
| Dataset | src/modeling/dataset.py | Nạp graph và chia dữ liệu |
| GCN | src/modeling/model.py | Học biểu diễn và điểm khớp graph |
| Huấn luyện | src/modeling/train.py | BCEWithLogitsLoss và ranking evaluation |
| Hybrid | src/evaluation/hybrid.py | Kết hợp GCN với semantic score |
| Inference | src/inference/predict.py | Dự đoán cho CV-JD mới |
| Chứng chỉ | src/evaluation/certification.py | Tính tỷ lệ khớp và certification bonus |

## 3. Tiếp nhận và tiền xử lý CV/JD

### 3.1. Dữ liệu đầu vào

Hệ thống có thể nhận:

- CV dạng văn bản hoặc PDF.
- JD từ file CSV hoặc văn bản.
- Dữ liệu đã được chuẩn hóa từ pipeline VietJobs.

Các bước tiền xử lý:

1. Đọc nội dung CV hoặc JD.
2. Chuẩn hóa khoảng trắng.
3. Bỏ trường rỗng hoặc giá trị không hợp lệ.
4. Giữ nguyên thuật ngữ kỹ thuật, tên công nghệ và tên chứng chỉ.
5. Chuyển văn bản sang cấu trúc entity có schema cố định.

### 3.2. Bảy nhóm entity

Hệ thống hiện sử dụng bảy nhóm:

~~~python
[
    "soft_skills",
    "hard_skills",
    "education",
    "field_of_education",
    "industry_sector",
    "role",
    "certifications",
]
~~~

certifications là nhóm được bổ sung. Entity bị thiếu được xử lý bằng danh sách rỗng, không làm hỏng pipeline.

Ví dụ kết quả trích xuất:

~~~json
{
  "role": ["Backend Developer"],
  "hard_skills": ["Python", "FastAPI", "PostgreSQL"],
  "soft_skills": ["Teamwork", "Communication"],
  "education": ["Bachelor"],
  "field_of_education": ["Computer Science"],
  "industry_sector": ["Fintech"],
  "certifications": ["AWS Certified Solutions Architect - Associate"]
}
~~~

## 4. Trích xuất và chuẩn hóa chứng chỉ

### 4.1. Vì sao không tính mọi chứng chỉ?

Không phải mọi dòng có chữ certificate trong CV đều chứng minh năng lực chuyên môn. Vì vậy hệ thống chỉ tính các chứng chỉ thuộc catalog được định nghĩa trong config.py.

Catalog đầy đủ được định nghĩa trực tiếp trong `config.CERTIFICATION_CATALOG`.
Catalog hiện bao phủ các nhóm chính như AWS/Azure/Google Cloud,
Kubernetes/HashiCorp, Red Hat/Linux, Cisco/CompTIA, cybersecurity, Java/.NET,
database/data engineering, Salesforce/SAP, testing, Agile/project management,
virtualization và governance. Tài liệu không coi một tên chứng chỉ là hợp lệ
nếu tên đó chưa có trong catalog.

Các alias như SAA-C03, AZ-104, CKA, CEH, PMP, Security+ được chuẩn hóa về tên canonical trước khi đưa vào graph.

### 4.2. Luồng xử lý chứng chỉ

~~~text
Toàn bộ văn bản CV/JD
    ↓
Chuẩn hóa Unicode và chữ thường
    ↓
Chuẩn hóa dấu gạch, dấu chấm và khoảng trắng
    ↓
So khớp tên canonical và alias trong catalog
    ↓
Loại chứng chỉ ngoài catalog
    ↓
Lưu danh sách certifications đã chuẩn hóa
~~~

Ví dụ:

~~~text
CV có:
  AWS SAA-C03, CKA, Coursera Certificate

Sau chuẩn hóa:
  AWS Certified Solutions Architect - Associate
  Certified Kubernetes Administrator

Coursera Certificate không được tính nếu không thuộc catalog.
~~~

Trích xuất chứng chỉ là deterministic post-processing. Sau khi LLM trả về entity, hệ thống vẫn quét lại toàn bộ văn bản để tránh bỏ sót mã chứng chỉ.

## 5. Semantic Embedding

### 5.1. Mô hình sử dụng

Mô hình hiện tại:

~~~text
paraphrase-multilingual-MiniLM-L12-v2
~~~

Đây là Sentence-BERT đa ngôn ngữ, phù hợp với văn bản tiếng Việt và thuật ngữ tiếng Anh trong CV/JD.

Kích thước vector đầu ra:

$$
d_{SBERT}=384
$$

### 5.2. Embedding từng entity

Ví dụ:

~~~text
hard_skills = ["Python", "FastAPI", "PostgreSQL"]
~~~

SBERT tạo ma trận:

$$
E=[e_1,e_2,e_3] \in R^{3 \times 384}
$$

Mỗi hàng là embedding 384 chiều của một entity.

### 5.3. DeepSets pooling

Với tập embedding E, hệ thống dùng ba phép pooling:

$$
e_{mean}=\frac{1}{N}\sum_{i=1}^{N}e_i
$$

$$
e_{sum}=\sum_{i=1}^{N}e_i
$$

$$
e_{max}[d]=\max_{i=1,...,N}e_i[d]
$$

Sau đó nối ba vector:

$$
h_{entity}=[e_{mean};e_{max};e_{sum}]
$$

Kích thước:

$$
384 \times 3=1152
$$

Ví dụ kích thước:

~~~text
SBERT hard_skills: [3, 384]
mean pooling:     [384]
max pooling:      [384]
sum pooling:      [384]
DeepSets output:  [1152]
~~~

Các nhóm entity được biểu diễn độc lập. certifications vẫn có vector 1152 để graph sử dụng khi chứng chỉ phù hợp.

Nhóm certifications không được nối vào central semantic text tổng quát. Chứng chỉ được xử lý riêng qua node graph và certification bonus, tránh việc thông tin chứng chỉ bị đếm trùng trong semantic score.

## 6. Biểu diễn đồ thị Candidate-Skill-Job

### 6.1. Kích thước graph

Mỗi cặp Candidate-JD hiện được biểu diễn bằng 16 nút:

~~~text
2 center nodes
+ 7 candidate entity nodes
+ 7 JD entity nodes
= 16 nodes
~~~

Thứ tự node cố định:

| Index | Node |
|---:|---|
| 0 | Candidate center |
| 1 | Candidate soft_skills |
| 2 | Candidate hard_skills |
| 3 | Candidate education |
| 4 | Candidate field_of_education |
| 5 | Candidate industry_sector |
| 6 | Candidate role |
| 7 | Candidate certifications |
| 8 | JD center |
| 9 | JD soft_skills |
| 10 | JD hard_skills |
| 11 | JD education |
| 12 | JD field_of_education |
| 13 | JD industry_sector |
| 14 | JD role |
| 15 | JD certifications |

Ma trận đặc trưng node:

$$
X \in R^{16 \times 1152}
$$

### 6.2. Star edges

Candidate center nối đến bảy node entity của candidate. JD center nối đến bảy node entity của JD:

~~~text
0 ↔ 1, 2, 3, 4, 5, 6, 7
8 ↔ 9, 10, 11, 12, 13, 14, 15
~~~

Trọng số star edge được lấy theo độ quan trọng entity:

~~~text
role              : 3.0
hard_skills       : 2.5
field_of_education: 1.5
certifications    : 2.0
nhóm khác         : theo ENTITY_WEIGHTS
~~~

### 6.3. Cross edges giữa CV và JD

Với hai vector u và v, cosine similarity là:

$$
cos(u,v)=\frac{u \cdot v}{||u||_2||v||_2}
$$

Các nhóm cùng loại được kết nối, ví dụ:

~~~text
Candidate hard_skills ↔ JD hard_skills
Candidate role        ↔ JD role
Candidate education   ↔ JD education
Candidate certifications ↔ JD certifications
~~~

Trọng số cross edge:

$$
w_{cross}(t)=cos(h^C_t,h^J_t)\times\lambda_t
$$

Trong đó t là entity type và lambda là trọng số của nhóm đó.

Các semantic cross edge khác được tạo theo k-NN sharpening với:

~~~text
k=10
p=4.0
~~~

Một cách mô tả:

$$
w'_{ij}=
\frac{(max(0,cos(x_i,x_j)))^p}
{\sum_{l \in N_k(i)}(max(0,cos(x_i,x_l)))^p+\epsilon}
$$

Lũy thừa p làm nổi bật các cặp entity tương đồng và giảm ảnh hưởng của liên kết yếu.

### 6.4. Ví dụ tạo graph

Giả sử:

~~~text
CV:
  role = ["Backend Developer"]
  hard_skills = ["Python", "FastAPI"]
  certifications = ["AWS Certified Solutions Architect - Associate"]

JD:
  role = ["Backend Engineer"]
  hard_skills = ["Python", "AWS"]
  certifications = ["AWS Certified Solutions Architect - Associate"]
~~~

Các bước:

1. Mỗi nhóm được chuyển thành vector 1152 chiều.
2. Candidate center và JD center được tạo từ biểu diễn tổng hợp của mỗi phía.
3. Tạo 14 node entity thông thường và 2 node certification.
4. Tạo star edge giữa center và entity cùng phía.
5. Tạo cross edge giữa role, hard_skills và certifications.
6. Do chứng chỉ giao nhau, hai certification node được kích hoạt.
7. Tạo semantic k-NN edges nếu cosine similarity đạt điều kiện.
8. Lưu graph dưới dạng PyTorch Geometric Data.

## 7. Cơ chế chứng chỉ trong graph

### 7.1. Tỷ lệ khớp chứng chỉ

Gọi C_cert là tập chứng chỉ của candidate và J_cert là tập chứng chỉ của JD.

Tập giao:

$$
I=C_{cert}\cap J_{cert}
$$

Tỷ lệ khớp theo yêu cầu JD:

$$
r_{cert}=
\begin{cases}
\frac{|I|}{|J_{cert}|}, & |J_{cert}|>0 \\
0, & |J_{cert}|=0
\end{cases}
$$

Ví dụ:

~~~text
CV = {AWS SAA, CKA}
JD = {AWS SAA, PMP}

I = {AWS SAA}
r_cert = 1 / 2 = 0.5
~~~

### 7.2. Điều kiện kích hoạt certification node

- Nếu candidate có chứng chỉ phù hợp với JD, node certification được giữ lại, có feature embedding và tham gia star/cross/k-NN edges.
- Nếu candidate không có chứng chỉ chung với JD, hai certification node được zero feature, các certification edge bị bỏ qua và chúng không tham gia k-NN.
- Nếu JD không yêu cầu chứng chỉ, r_cert bằng 0 và không có điểm cộng.

Do đó, chứng chỉ không làm tăng điểm chỉ vì CV có chứa một chứng chỉ bất kỳ. Chứng chỉ chỉ có tác dụng khi liên quan đến yêu cầu JD.

### 7.3. Metadata chứng chỉ

Graph lưu thêm:

~~~python
data.certification_match
data.certification_match_ratio
~~~

Các trường này phục vụ inference và evaluation. Chúng không thay thế node graph mà cung cấp tín hiệu rõ ràng cho lớp scoring.

## 8. GCN và điểm graph

### 8.1. Luồng tensor

~~~text
X: [16, 1152]
    ↓ Pre-Aggregation
[16, 128]
    ↓ GCNConv layer 1
[16, 128]
    ↓ GCNConv layer 2
[16, 128]
    ↓ GCNConv layer 3
[16, 128]
    ↓ Global readout
Graph representation
    ↓ MLP
GCN logit
~~~

Mô hình dùng ba lớp GCN với hidden dimension 128. Một lớp GCN có thể mô tả:

$$
H^{(l+1)}=
\sigma\left(
\tilde{D}^{-\frac{1}{2}}\tilde{A}
\tilde{D}^{-\frac{1}{2}}H^{(l)}W^{(l)}
\right)
$$

Trong đó:

- A là ma trận kề có trọng số.
- I được cộng vào để tạo self-loop.
- D là ma trận bậc.
- W là tham số học được.
- sigma là hàm kích hoạt.

Sau message passing, graph readout tạo biểu diễn candidate và JD. Vector cặp có thể mô tả:

$$
h_{pair}=[h_{CV};h_{JD};|h_{CV}-h_{JD}|;h_{CV}\odot h_{JD}]
$$

MLP trả về GCN logit:

$$
s_{GCN}=MLP(h_{pair})
$$

Khi cần chuyển sang xác suất:

$$
p_{GCN}=\sigma(s_{GCN})
$$

## 9. Huấn luyện mô hình

### 9.1. Nhãn và loss

Nhãn grade được chuẩn hóa:

$$
y_{target}=\frac{grade}{3}
$$

| Grade | Target |
|---:|---:|
| 0 | 0.00 |
| 1 | 0.33 |
| 2 | 0.67 |
| 3 | 1.00 |

Loss hiện tại là BCEWithLogitsLoss.

Không nhầm lẫn giữa relevance grade, normalized target, GCN logit, sigmoid probability và final ranking score.

### 9.2. Chia dữ liệu

Dữ liệu được chia theo query/CV, không chia ngẫu nhiên từng dòng. Các cặp:

~~~text
CV_A → JD_1
CV_A → JD_2
CV_A → JD_3
~~~

phải được giữ cùng một nhóm train, validation hoặc test để tránh rò rỉ thông tin.

## 10. Hybrid Score

### 10.1. Semantic score

Semantic score đo độ tương đồng giữa biểu diễn semantic của CV và JD:

$$
s_{semantic}=cos(h_{CV}^{semantic},h_{JD}^{semantic})
$$

Score được chuẩn hóa về thang phù hợp trước khi kết hợp.

### 10.2. Certification bonus

Sau khi có điểm graph cơ sở:

$$
s_{base}=p_{GCN}
$$

Điểm sau chứng chỉ:

$$
s_{GCN}^{cert}=min(1,\ s_{base}+\beta r_{cert})
$$

Trong code hiện tại:

$$
\beta=0.10
$$

Ví dụ có chứng chỉ liên quan:

~~~text
base score = 0.70
r_cert = 0.50

bonus = 0.10 × 0.50 = 0.05
score sau chứng chỉ = 0.75
~~~

Ví dụ chứng chỉ không liên quan:

~~~text
base score = 0.70
r_cert = 0
score sau chứng chỉ = 0.70
~~~

Như vậy chứng chỉ liên quan thì tăng điểm, chứng chỉ không liên quan thì giữ nguyên điểm cơ sở.

### 10.3. Hybrid Score cuối cùng

$$
HybridScore=
\alpha s_{GCN}^{cert}
+(1-\alpha)s_{semantic}
$$

alpha được cung cấp hoặc tuning trên validation set. Không tuning alpha bằng test set.

Ví dụ:

~~~text
s_GCN sau certification = 0.75
s_semantic = 0.80
alpha = 0.60

HybridScore = 0.60 × 0.75 + 0.40 × 0.80
            = 0.45 + 0.32
            = 0.77
~~~

## 11. Luồng huấn luyện từ đầu đến cuối

Pipeline dữ liệu hiện tại:

~~~text
VietJobs.csv
    ↓
Lọc JD IT bằng extract_vietjobs_it.py
    ↓
Khoảng 1,906 JD theo cấu hình hiện tại
    ↓
Trích xuất entity và tạo SBERT/DeepSets cache
    ↓
KMeans với K = 20
    ↓
Chọn JD đại diện và tạo negative samples
    ↓
Tạo các profile CV kỹ thuật
    ↓
Sinh các cặp CV-JD có grade 0/1/2/3
    ↓
Chuẩn bị 16-node PyG graph
    ↓
Query-aware train/validation/test split
    ↓
Huấn luyện GCN
    ↓
Đánh giá ranking
~~~

Trong cấu hình thí nghiệm hiện tại, dữ liệu mẫu gồm 24 profile CV và 120 cặp CV-JD. Mỗi CV được ghép với các JD thuộc cùng cụm, cụm gần và cụm xa để tạo đủ bốn mức grade 0/1/2/3.

## 12. Lưu trữ graph và cache

### 12.1. Entity cache

~~~text
data/cache/entity_cache_v4_certification_catalog_expanded.json
~~~

Cache lưu entity đã trích xuất và version schema. Cache được version hóa vì việc thêm certifications làm thay đổi schema cũ.

### 12.2. JD embedding cache

~~~text
data/cache/jd_embeddings_cache_v4_certification_catalog_expanded.pt
~~~

Cache lưu structured entity, embedding và DeepSets representation của JD.

### 12.3. Graph cache

~~~text
data/processed/graphs_v4_certification_catalog_expanded/
~~~

Mỗi file graph PyTorch Geometric thường chứa:

~~~python
Data(
    x=[16, 1152],
    edge_index=[2, num_edges],
    edge_attr=[num_edges],
    y=...,
    certification_match=...,
    certification_match_ratio=...
)
~~~

### 12.4. Model checkpoint

~~~text
models/best_model_v4_certification_catalog_expanded.pt
~~~

Không dùng cache graph 14-node cũ với model 16-node mới. Nếu thay đổi entity schema, node ordering, embedding dimension hoặc topology, phải tạo cache phiên bản mới.

## 13. Luồng inference chi tiết

Khi người dùng đưa vào một CV:

1. Đọc nội dung CV.
2. Trích xuất bảy nhóm entity.
3. Chuẩn hóa chứng chỉ theo catalog.
4. Tạo embedding 384 chiều cho entity.
5. Pooling thành vector 1152 chiều.
6. Với từng JD ứng viên, lấy entity và embedding đã cache.
7. Xây một graph 16 node cho cặp CV-JD.
8. Đưa graph qua GCN để lấy base_score.
9. Tính certification_match_ratio.
10. Cộng certification bonus nếu có giao nhau.
11. Tính semantic score.
12. Kết hợp thành Hybrid Score.
13. Sắp xếp tất cả JD của CV theo Hybrid Score giảm dần.

Kết quả inference có thể gồm:

~~~json
{
  "score": 0.77,
  "base_score": 0.72,
  "certification_match_ratio": 0.5
}
~~~

score là điểm sau khi áp dụng tín hiệu chứng chỉ và được dùng cho ranking.

## 14. Kiểm thử và đánh giá thực nghiệm

### 14.1. Baseline

Các phương pháp cần so sánh:

1. TF-IDF + cosine similarity.
2. Sentence-BERT + cosine similarity.
3. GCN score.
4. Hybrid GCN + semantic.
5. Hybrid có thêm certification bonus.

Baseline phải được giữ nguyên khi báo cáo để kết quả so sánh công bằng.

### 14.2. NDCG@K

NDCG đánh giá chất lượng thứ tự xếp hạng có xét mức độ liên quan:

$$
DCG@K=
\sum_{i=1}^{K}
\frac{2^{rel_i}-1}{\log_2(i+1)}
$$

$$
NDCG@K=\frac{DCG@K}{IDCG@K}
$$

Giá trị càng gần 1 càng tốt.

### 14.3. Recall@K

$$
Recall@K=
\frac{\#\{JD liên quan trong top K\}}
{\#\{JD liên quan\}}
$$

Có thể báo cáo Recall@1, Recall@3, Recall@5 và Recall@10.

### 14.4. MRR

MRR tập trung vào vị trí của JD liên quan đầu tiên:

$$
MRR=\frac{1}{|Q|}
\sum_{q=1}^{|Q|}
\frac{1}{rank_q}
$$

MRR phù hợp với bối cảnh nhà tuyển dụng quan tâm những kết quả tốt nhất ở đầu danh sách.

### 14.5. Hiệu năng kỹ thuật

Ngoài độ chính xác, cần đo:

- Thời gian trích xuất entity.
- Thời gian tạo embedding.
- Thời gian xây graph.
- Thời gian inference mỗi cặp CV-JD.
- Throughput khi xử lý nhiều JD.
- Bộ nhớ sử dụng của cache và model.
- Khả năng xử lý khi entity hoặc chứng chỉ bị thiếu.

## 15. Các lệnh chạy chính

Chạy bằng Python UTF-8 trên Windows:

~~~powershell
python -X utf8 src/data_collection/cache_jd_embeddings.py
python -X utf8 src/data_collection/prepare_training_data.py
python -X utf8 src/modeling/train.py --epochs 60 --batch 16 --lr 0.001 --patience 15
python -X utf8 src/evaluation/hybrid.py
python -X utf8 src/evaluation/baselines.py
python -X utf8 main.py --mode demo
~~~

### 15.1. FastAPI AI Service

Khởi động service từ thư mục gốc:

~~~powershell
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
~~~

Swagger UI: `http://localhost:8000/docs`.

| Method | Endpoint | Mục đích |
|---|---|---|
| GET | `/health/live` | Kiểm tra process đang hoạt động |
| GET | `/health/ready` | Kiểm tra checkpoint có tồn tại |
| GET | `/v1/meta` | Trả về schema entity, dimension và artifact version |
| POST | `/v1/entities/extract` | Trích xuất entity từ text |
| POST | `/v1/match` | Chấm điểm một CV với một JD |
| POST | `/v1/rank` | Xếp hạng tối đa 100 JD cho một CV |
| POST | `/v1/match/files` | Chấm điểm từ file PDF/TXT multipart |

Ví dụ request `/v1/rank`:

~~~json
{
  "cv_text": "Backend Developer, Python, FastAPI, PostgreSQL",
  "jobs": [
    {"job_id": "job-001", "jd_text": "Backend Engineer, Python, FastAPI"},
    {"job_id": "job-002", "jd_text": "iOS Developer, Swift, UIKit"}
  ]
}
~~~

Response được sắp xếp theo `rank` và mỗi phần tử có các trường chính:
`hybrid_score`, `graph_score`, `semantic_score`, `hybrid_alpha`,
`certification_match_ratio`, `grade`, `grade_label` và `explanation`.

Service dùng `HYBRID_ALPHA` làm alpha mặc định, hiện mặc định là `0.2`. Có
thể ghi đè alpha trong từng request trong khoảng `[0, 1]`. Model và
Sentence-BERT chỉ được load khi có request matching đầu tiên, trừ khi bật
`AI_SERVICE_EAGER_LOAD=true`.

Trước khi huấn luyện đầy đủ, cần kiểm tra:

~~~text
data.x.shape              = [16, 1152]
data.edge_index.shape     = [2, num_edges]
data.edge_attr.shape      = [num_edges]
data.y                    = nhãn hợp lệ
certification_match_ratio = số hữu hạn trong [0, 1]
~~~

## 16. Nguyên tắc quan trọng

- Hệ thống là bài toán ranking, không kết luận bằng classification accuracy.
- Mỗi CV phải được ranking độc lập trên danh sách JD của chính nó.
- Không để cùng một CV rò rỉ giữa train, validation và test.
- Không cộng điểm cho chứng chỉ ngoài catalog.
- Chứng chỉ không liên quan phải giữ nguyên điểm cơ sở.
- Không dùng test set để tuning alpha.
- Không trộn graph 14-node cũ với graph 16-node mới.
- Khi thay đổi entity schema hoặc embedding dimension phải version hóa cache.
- Semantic score nền không bao gồm `certifications`; chứng chỉ chỉ tác động qua graph và bonus có điều kiện.
- Không hard-code API key.
- Không tự động biến dữ liệu trích xuất lỗi thành dữ liệu huấn luyện hợp lệ.

## 17. Tóm tắt đóng góp của phần chứng chỉ

Việc bổ sung certifications mở rộng graph từ 14 lên 16 node và tạo thêm tín hiệu khớp chuyên biệt:

~~~text
14 node cũ
    ↓
thêm Candidate certifications và JD certifications
    ↓
16 node
    ↓
semantic certification edges khi có liên quan
    ↓
certification_match_ratio
    ↓
bonus tối đa 0.10
    ↓
Hybrid Score cuối
~~~

Cách thiết kế này giúp chứng chỉ nâng thứ hạng khi đáp ứng yêu cầu của JD, nhưng không làm sai lệch kết quả khi chứng chỉ chỉ xuất hiện trong CV mà không liên quan đến công việc.
