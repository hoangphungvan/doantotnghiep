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
2. **Tạo Embedding** (sentence-transformers + DeepSets pooling)
3. **Xây dựng đồ thị** (14 nút, edge weights với k-NN sharpening)
4. **GCN Model** (Pre-aggregation → GCNConv → Readout → Classifier)

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
data/raw/cvs/cv001.pdf,data/raw/jds/jd001.txt,1
data/raw/cvs/cv002.pdf,data/raw/jds/jd001.txt,0
```

### 5. Dự đoán tương tác
```bash
python main.py --mode predict
```

## Cấu trúc Project

```
AI GCN/
├── .env                    # API keys
├── config.py               # Cấu hình hệ thống
├── entity_extractor.py     # Trích xuất thực thể bằng LLM
├── embedding_generator.py  # Tạo embeddings + DeepSets
├── graph_builder.py        # Xây dựng đồ thị PyG
├── dataset.py              # CJMDataset class
├── model.py                # GCN Model
├── train.py                # Pipeline huấn luyện
├── predict.py              # Pipeline dự đoán
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── data/
│   ├── raw/cvs/            # CV files (PDF/TXT)
│   ├── raw/jds/            # JD files (PDF/TXT)
│   └── processed/graphs/   # Pre-processed graphs
└── models/                 # Saved models
```

## Cấu hình (.env)

```env
OPENAI_API_KEY=sk-or-v1-xxx        # OpenRouter API key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=google/gemini-2.0-flash-exp:free
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## Thông số kỹ thuật

| Thông số | Giá trị |
|----------|---------|
| Số nút / đồ thị | 14 |
| Embedding dim | 384 (all-MiniLM-L6-v2) |
| Feature dim (sau DeepSets) | 1152 (384 × 3) |
| Hidden dim | 128 |
| GCN layers | 3 |
| k-NN k | 10 |
| Sharpening p | 4.0 |
| pos_weight | 10.0 |
| Loss function | BCEWithLogitsLoss |
