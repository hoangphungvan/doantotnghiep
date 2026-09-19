# Candidate-Job Matching (CJM) bằng GCN

Hệ thống đánh giá mức độ phù hợp giữa Ứng viên (CV) và Mô tả công việc (JD) sử dụng **Graph Convolutional Network (GCN)** trên nền tảng PyTorch Geometric.

## Kiến trúc

### Cấu trúc Đồ thị (Bipartite Graph - 14 nút)

```
        [Soft Skills]──┐                  ┌──[Soft Skills]
       [Hard Skills]───┤                  ├───[Hard Skills]
         [Education]───┤                  ├───[Education]
  [Field of Education]─┼──[Candidate]────[JD]──┼─[Field of Education]
    [Industry Sector]──┤                  ├──[Industry Sector]
              [Role]───┘                  └───[Role]
```

- **2 nút chính**: Candidate (v_c) và Job Description (v_jd)
- **12 nút thực thể**: 6 loại cho mỗi bên
- **Kết nối**: Star Topology + k-NN cross-edges

### Pipeline xử lý

1. **Trích xuất thực thể** (LLM API - OpenRouter/Gemini)
2. **Tạo Embedding** (sentence-transformers đa ngôn ngữ + DeepSets pooling)
3. **Xây dựng đồ thị** (14 nút, edge weights với k-NN sharpening)
4. **GCN Model** (Pre-aggregation → GCNConv → Readout → Classifier)

### Nhãn mức độ phù hợp (graded relevance 0-3)

| Grade | Ý nghĩa |
|-------|---------|
| 0 | Không phù hợp |
| 1 | Liên quan ngành |
| 2 | Phù hợp một phần |
| 3 | Phù hợp tốt |

Model output sigmoid ∈ [0,1] (target = grade/3), dùng để **xếp hạng** JD cho từng CV.
Đánh giá bằng **NDCG@K, MRR, Recall@K** (module `metrics.py`) — mỗi CV là một query,
các JD của cùng một CV được group qua thuộc tính `cv_source`/`cv_path`.

### Mô hình lai (Hybrid Score)

Kết hợp 2 tín hiệu — semantic embedding (SBERT) và graph-based matching (GCN):

```
Hybrid Score = α · graph_score + (1 − α) · semantic_score
```

- `graph_score`    : sigmoid output của GCN (khai thác cấu trúc đồ thị) ∈ [0,1]
- `semantic_score` : cosine similarity giữa SBERT embedding của CV và JD
                     (đọc trực tiếp từ main-node trong đồ thị), chuẩn hóa min-max
- `α`              : tune trên tập validation tối đa hóa NDCG@K (grid 0..1, bước 0.05)

Baseline để so sánh: **TF-IDF + cosine**, **SBERT + cosine** (semantic thuần) —
module `baselines.py`. Tất cả đánh giá bằng cùng bộ ranking metrics trên cùng
tập validation (split theo nhóm CV).

```bash
python src/evaluation/hybrid.py      # Hybrid + baseline trên dữ liệu thật đã chuẩn bị
python src/evaluation/hybrid.py --alpha 0.7   # α cố định thay vì tune
python src/evaluation/baselines.py   # chỉ chạy baseline
python main.py --mode hybrid         # demo end-to-end (không cần API key)
```

## Cài đặt

```bash
pip install -r requirements.txt
```

## Cách sử dụng

### 1. Demo nhanh (không cần API key)
```bash
python main.py --mode demo
```

### 2. Test trích xuất thực thể (cần API key)
```bash
python main.py --mode extract
```

### 3. Full pipeline với LLM
```bash
python main.py --mode pipeline
```

### 4. Huấn luyện từ CSV
```bash
python main.py --mode train
```

CSV format:
```csv
cv_path,jd_path,label
data/raw/cvs/cv001.pdf,data/raw/jds/jd001.txt,3
data/raw/cvs/cv001.pdf,data/raw/jds/jd002.txt,0
data/raw/cvs/cv002.pdf,data/raw/jds/jd001.txt,1
```

(`label` = mức phù hợp 0-3; ghép MỘT CV với NHIỀU JD để đánh giá xếp hạng được)

### 5. Dự đoán tương tác
```bash
python main.py --mode predict
```

## Cấu trúc Project

Tổ chức theo flow xử lý — mỗi thư mục trong `src/` là một giai đoạn:

```
doantotnghiep/
├── main.py                          # Entry point — chọn mode chạy toàn bộ flow
├── config.py                        # Cấu hình chung (API, embedding, hyperparams, paths)
├── requirements.txt
├── src/
│   ├── data_collection/             # Bước 0 — Thu thập & gán nhãn dữ liệu (grade 0-3)
│   │   └── prepare_training_data.py
│   ├── extraction/                  # Bước 1 — Trích xuất thực thể bằng LLM
│   │   └── entity_extractor.py
│   ├── representation/              # Bước 2-3 — Embedding + Đồ thị
│   │   ├── embedding_generator.py   #   SBERT đa ngôn ngữ + DeepSets pooling
│   │   └── graph_builder.py         #   Đồ thị bipartite 14 nút
│   ├── modeling/                    # Bước 4-5 — Dataset + GCN + Huấn luyện
│   │   ├── dataset.py               #   CJMDataset, sample dataset theo nhóm CV
│   │   ├── model.py                 #   GCN Model + soft-label loss
│   │   └── train.py                 #   Train/val split theo CV, early stopping
│   ├── evaluation/                  # Bước 6 — Đánh giá xếp hạng & mô hình lai
│   │   ├── metrics.py               #   NDCG@K, MRR, Recall@K
│   │   ├── hybrid.py                #   Hybrid Score (GCN + SBERT) + tune α
│   │   └── baselines.py             #   Baseline TF-IDF / SBERT-cosine
│   └── inference/                   # Bước 7 — Dự đoán
│       └── predict.py
├── data/
│   ├── raw/cvs/                     # CV files (PDF/TXT)
│   ├── raw/jds/                     # JD files (PDF/TXT)
│   └── processed/
│       ├── graphs/                  # Pre-processed graphs (.pt)
│       └── training_pairs.csv
└── models/                          # best_model.pt
```


## Thông số kỹ thuật

| Thông số | Giá trị |
|----------|---------|
| Số nút / đồ thị | 14 |
| Embedding model | paraphrase-multilingual-MiniLM-L12-v2 (đa ngôn ngữ, hỗ trợ tiếng Việt) |
| Embedding dim | 384 |
| Feature dim (sau DeepSets) | 1152 (384 × 3) |
| Hidden dim | 128 |
| GCN layers | 3 |
| k-NN k | 10 |
| Sharpening p | 4.0 |
| Loss function | BCEWithLogitsLoss trên soft target = grade/3 |
| Thang nhãn | 0-3 (graded relevance) |
| Ranking metrics | NDCG@K, MRR, Recall@K (K = 1, 3, 5, 10) |
