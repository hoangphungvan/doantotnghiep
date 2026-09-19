# Candidate-Job Matching (CJM) bằng Graph Convolutional Network (GCN)

Hệ thống đánh giá và xếp hạng mức độ phù hợp giữa Ứng viên (CV) và Bản mô tả công việc (JD) sử dụng **Graph Convolutional Network (GCN)** trên nền tảng PyTorch Geometric, kết hợp trích xuất thực thể bằng LLM (**Groq API**) và mô hình đa ngôn ngữ **Sentence-BERT**.

---

## Kiến trúc Hệ thống

### 1. Cấu trúc Đồ thị Bipartite (14 nút)

Mỗi cặp (CV, JD) được mô hình hóa thành một đồ thị dị thể (bipartite graph) gồm 14 nút:

```
        [Soft Skills]──┐                  ┌──[Soft Skills]
       [Hard Skills]───┤                  ├───[Hard Skills]
         [Education]───┤                  ├───[Education]
  [Field of Education]─┼──[Candidate]────[JD]──┼─[Field of Education]
    [Industry Sector]──┤                  ├──[Industry Sector]
              [Role]───┘                  └───[Role]
```

- **2 nút trung tâm**: Ứng viên ($v_c$) và Việc làm ($v_{jd}$).
- **12 nút thực thể**: 6 loại cho mỗi bên (`role`, `hard_skills`, `field_of_education`, `industry_sector`, `education`, `soft_skills`).
- **Topology kết nối**:
  - *Star Topology*: Nút trung tâm kết nối với các nút thực thể tương ứng của mình.
  - *Cross-edges*: Kết nối giữa các nút thực thể cùng loại giữa CV và JD với trọng số $w_e$ dựa trên độ tương đồng Cosine kết hợp hàm k-NN sharpening ($p=4.0$).

### 2. Pipeline Xử lý 7 Bước

1. **Trích xuất thực thể**: Sử dụng **Groq API** (`qwen/qwen3.8-27b`) trích xuất 6 loại thực thể từ văn bản thô, tích hợp cơ chế **2-Layer Entity Cache** (SHA-256 + đường dẫn file).
2. **Tạo Embedding**: Mô hình `paraphrase-multilingual-MiniLM-L12-v2` (dim 384, hỗ trợ tiếng Việt) kết hợp cơ chế gom cụm **DeepSets** (Mean, Max, Sum pooling → 1152 chiều).
3. **Xây dựng Đồ thị**: Khởi tạo 14 nút với feature DeepSets, tính toán trọng số cạnh có định hướng mức độ ưu tiên thực thể (`role` > `hard_skills` > `field_of_education` > ...).
4. **Mô hình GCN**: Pre-aggregation $\rightarrow$ 3 lớp `GCNConv` $\rightarrow$ Global Readout $\rightarrow$ Classifier MLP.
5. **Huấn luyện**: Hàm mất mát `BCEWithLogitsLoss` trên mục tiêu liên tục ($\text{target} = \text{grade} / 3$), chia tập train/val theo cơ chế **Query-aware Split** (tách theo nhóm CV để tránh data leakage).
6. **Mô hình lai (Hybrid)**: Kết hợp điểm đồ thị và tương đồng ngữ nghĩa:
   $$\text{Score}_{\text{Hybrid}} = \alpha \cdot \text{Score}_{\text{GCN}} + (1 - \alpha) \cdot \text{Score}_{\text{Semantic}}$$
7. **Đánh giá & Suy luận**: Xếp hạng JD cho từng ứng viên bằng **NDCG@K, Recall@K, MRR**.

---

## Thang nhãn Mức độ Phù hợp (Graded Relevance 0–3)

| Grade | Tên nhãn | Định nghĩa | Target Train ($\text{grade}/3$) |
|:---:|:---|:---|:---:|
| **3** | Phù hợp tốt | Khớp chuyên môn, role, kỹ năng cốt lõi và ngành nghề | `1.00` |
| **2** | Phù hợp một phần | Cùng nhóm chuyên môn nhưng lệch seniority hoặc thiếu công nghệ phụ | `0.67` |
| **1** | Liên quan ngành | Hard Negative: Cùng thuộc CNTT nhưng khác domain (vd: Java Backend vs Mobile iOS) | `0.33` |
| **0** | Không phù hợp | Easy Negative: Khác biệt hoàn toàn chuyên môn (vd: IT Helpdesk vs Software Sales/UI-UX) | `0.00` |

---

## Dữ liệu Huấn luyện từ VietJobs (Ngành CNTT)

Dự án tích hợp bộ dữ liệu thực tế từ [dinhieufam/VietJobs](https://huggingface.co/datasets/dinhieufam/VietJobs) với quy trình trích xuất và phân cụm tối ưu:

### Quy trình chuẩn bị dữ liệu (Data Pipeline)

```
[VietJobs.csv (48k JDs)]
         │
         ▼ (src/data_collection/extract_vietjobs_it.py)
[1,906 JD CNTT (VietJobs_cntt.csv)]
         │
         ▼ (src/data_collection/cache_jd_embeddings.py)
[Entity Cache + DeepSets Embeddings Cache (100% Cache Hit)]
         │
         ▼ (src/data_collection/cluster_jds.py)
[KMeans K=20 Cụm + Ma trận Tương đồng + Hướng dẫn Negative Sampling]
         │
         ▼ (src/data_collection/generate_training_data.py)
[12 CV Chuyên ngành + 60 Cặp Huấn luyện Cân bằng (pairs_it.csv)]
         │
         ▼ (src/data_collection/prepare_training_data.py)
[60 Đồ thị PyG Huấn luyện (data/processed/graphs/*.pt)]
```

---

## Cài đặt & Cấu hình

### 1. Cài đặt môi trường

Yêu cầu Python 3.10+ (đã kiểm thử trên Python 3.12 Windows).

```bash
pip install -r requirements.txt
```

### 2. Cấu hình biến môi trường (`.env`)

Tạo file `.env` tại thư mục gốc của dự án:

```env
# Cấu hình Groq API (Khuyên dùng: tốc độ cao, độ trễ <1s)
LLM_API_KEY=gsk_your_groq_api_key_here
GROQ_API_KEY=gsk_your_groq_api_key_here
OPENAI_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=qwen/qwen3.8-27b
```

> **Lưu ý trên Windows**: Để tránh lỗi hiển thị bảng mã ký tự tiếng Việt trên terminal, luôn thêm tham số `-X utf8` khi chạy lệnh: `python -X utf8 ...`

---

## Hướng dẫn Chạy Hệ thống

### 1. Chạy nhanh Suy luận / Demo

```bash
# Demo end-to-end với dữ liệu mẫu (không cần gọi LLM ngoài)
python -X utf8 main.py --mode demo

# Đánh giá tương tác giữa 1 CV và 1 JD bất kỳ
python -X utf8 main.py --mode predict
```

### 2. Tái tạo Toàn bộ Dữ liệu từ VietJobs

```bash
# Bước 1: Lọc 1.906 JD ngành CNTT từ file VietJobs.csv
python -X utf8 src/data_collection/extract_vietjobs_it.py

# Bước 2: Trích xuất thực thể và tính trước DeepSets embedding cho 1.906 JD
python -X utf8 src/data_collection/cache_jd_embeddings.py

# Bước 3: Phân 1.906 JD thành 20 cụm việc làm và tạo hướng dẫn ghép Hard/Easy Negative
python -X utf8 src/data_collection/cluster_jds.py

# Bước 4: Tự động sinh 12 profile CV kỹ thuật và tạo 60 cặp huấn luyện cân bằng
python -X utf8 src/data_collection/generate_training_data.py

# Bước 5: Chuyển đổi các cặp sang đồ thị PyG huấn luyện
python -X utf8 src/data_collection/prepare_training_data.py --mode file --csv data/raw/pairs_it.csv
```

### 3. Huấn luyện Mô hình GCN

```bash
python -X utf8 src/modeling/train.py --epochs 60 --batch 16 --lr 0.001 --patience 15
```

Mô hình tốt nhất được lưu tự động tại `models/best_model.pt`.

### 4. Đánh giá Xếp hạng & Mô hình Lai (Hybrid Evaluation)

```bash
# Đánh giá mô hình lai (tự động tune alpha tối ưu hóa NDCG@5)
python -X utf8 src/evaluation/hybrid.py

# Đánh giá với alpha cố định
python -X utf8 src/evaluation/hybrid.py --alpha 0.7

# So sánh với các baseline truyền thống (TF-IDF + Cosine, SBERT thuần)
python -X utf8 src/evaluation/baselines.py
```

---

## Cấu trúc Thư mục Dự án

```
doantotnghiep/
├── main.py                          # Entry point điều hướng các chế độ chạy
├── config.py                        # Cấu hình tham số mô hình, đường dẫn, API
├── requirements.txt                 # Danh sách thư viện phụ thuộc
├── .env                             # Biến môi trường (API Key, model config)
│
├── src/
│   ├── data_collection/             # Thu thập, phân cụm và chuẩn bị dữ liệu
│   │   ├── extract_vietjobs_it.py   # Lọc JD CNTT từ VietJobs
│   │   ├── cache_jd_embeddings.py   # Trích xuất và cache embedding cho JD
│   │   ├── cluster_jds.py           # Phân cụm KMeans K=20 & Negative sampling guide
│   │   ├── generate_training_data.py# Sinh CV và cặp huấn luyện (pairs_it.csv)
│   │   └── prepare_training_data.py # Chuyển đổi cặp ghép sang đồ thị PyG (.pt)
│   │
│   ├── extraction/                  # Trích xuất thực thể
│   │   └── entity_extractor.py      # LLM Groq extractor + 2-layer cache
│   │
│   ├── representation/              # Biểu diễn vector và đồ thị
│   │   ├── embedding_generator.py   # SBERT đa ngôn ngữ + DeepSets pooling (1152-d)
│   │   └── graph_builder.py         # Xây dựng đồ thị 14 nút và k-NN cross-edges
│   │
│   ├── modeling/                    # Kiến trúc GCN & Huấn luyện
│   │   ├── dataset.py               # Dataset loader & query-aware splitting
│   │   ├── model.py                 # GCNModel (Pre-aggregation + GCNConv + MLP)
│   │   └── train.py                 # Vòng lặp huấn luyện, early stopping, checkpoint
│   │
│   ├── evaluation/                  # Đánh giá chất lượng xếp hạng
│   │   ├── metrics.py               # NDCG@K, MRR, Recall@K, MAE, AUC-ROC
│   │   ├── hybrid.py                # Mô hình kết hợp GCN + SBERT Semantic
│   │   └── baselines.py             # Baselines TF-IDF và SBERT Cosine
│   │
│   └── inference/                   # Suy luận và phục vụ người dùng
│       └── predict.py               # CJMPredictor (predict_from_files / predict_from_text)
│
├── data/
│   ├── cache/                       # Cache hệ thống (tăng tốc xử lý)
│   │   ├── entity_cache.json        # Cache thực thể theo SHA-256
│   │   └── jd_embeddings_cache.pt   # Cache vector DeepSets của 1.906 JD
│   ├── raw/
│   │   ├── cvs/                     # File văn bản hồ sơ CV
│   │   ├── jds/cntt/                # File văn bản mô tả công việc (JD)
│   │   ├── VietJobs_cntt.csv        # Bảng dữ liệu 1.906 JD CNTT
│   │   └── pairs_it.csv             # Bảng 60 cặp huấn luyện (cv_path, jd_path, label)
│   └── processed/
│       ├── graphs/                  # Đồ thị PyG đã tiền xử lý (.pt)
│       ├── training_pairs.csv       # Metadata danh sách cặp đồ thị
│       ├── jd_clusters.csv          # Bảng gán cụm cho 1.906 JD
│       ├── representative_jds.csv   # 40 JD đại diện cho 20 cụm
│       ├── cluster_similarity_matrix.csv # Ma trận Cosine giữa các tâm cụm
│       └── cluster_negative_sampling_guide.json # Hướng dẫn chọn Hard/Easy Negative
│
└── models/
    └── best_model.pt                # Checkpoint mô hình GCN tốt nhất
```

---

## Bảng Thông số Kỹ thuật

| Thông số | Giá trị cấu hình | Mô tả |
|:---|:---|:---|
| **Số nút đồ thị** | 14 nút | 2 nút trung tâm + 12 nút thực thể (6 loại mỗi bên) |
| **Embedding Model** | `paraphrase-multilingual-MiniLM-L12-v2` | Sentence-BERT 384 chiều, hỗ trợ tiếng Việt |
| **Feature Pooling** | DeepSets (Mean + Max + Sum) | $384 \times 3 = 1152$ chiều mỗi nút |
| **Số lớp GCN** | 3 lớp `GCNConv` | Kích thước ẩn (Hidden dimension) = 128 |
| **k-NN & Sharpening** | $k=10$, $p=4.0$ | Tăng cường độ phân biệt của các cạnh tương đồng |
| **Loss Function** | `BCEWithLogitsLoss` | Soft target continuous: $\text{target} = \text{grade}/3$ |
| **LLM Extractor** | `qwen/qwen3.8-27b` (Groq) | Trích xuất JSON thực thể với độ trễ thấp |
| **Ranking Metrics** | NDCG@K, Recall@K, MRR | Đánh giá tại $K \in \{1, 3, 5, 10\}$ theo từng CV query |
