# Candidate-Job Matching (CJM) bằng Graph Convolutional Network (GCN)

Hệ thống xếp hạng mức độ phù hợp giữa Ứng viên (CV) và Bản mô tả công việc (JD) bằng **Graph Convolutional Network** (PyTorch Geometric), trích xuất thực thể bằng LLM (API tương thích OpenAI) và embedding đa ngôn ngữ **Sentence-BERT**.

---

## Kiến trúc hệ thống

### 1. Đồ thị bipartite 14 nút

Mỗi cặp (CV, JD) là một đồ thị 14 nút:

```
        [Soft Skills]──┐                  ┌──[Soft Skills]
       [Hard Skills]───┤                  ├───[Hard Skills]
         [Education]───┤                  ├───[Education]
  [Field of Education]─┼──[Candidate]────[JD]──┼─[Field of Education]
    [Industry Sector]──┤                  ├──[Industry Sector]
              [Role]───┘                  └───[Role]
```

- **2 nút trung tâm**: ứng viên và việc làm. **12 nút thực thể**: 6 loại mỗi bên (`role`, `hard_skills`, `field_of_education`, `industry_sector`, `education`, `soft_skills`).
- **Cạnh**: star (nút trung tâm ↔ thực thể của mình), cross-edge giữa các thực thể cùng loại (trọng số theo cosine và `ENTITY_WEIGHTS`), k-NN sharpening ($k=10$, $p=4$).

### 2. Pipeline

1. **Trích xuất thực thể**: LLM trả JSON 6 loại thực thể; cache theo SHA-256 của văn bản (`data/cache/entity_cache.json`, ghi qua tệp tạm).
2. **Embedding**: `paraphrase-multilingual-MiniLM-L12-v2` (384 chiều) + **DeepSets** (mean/sum/max → 1152 chiều mỗi nút).
3. **Đồ thị** 14 nút như trên.
4. **GCN**: pre-aggregation → 3 lớp `GCNConv` (hidden 128) → readout → MLP.
5. **Huấn luyện**: `BCEWithLogitsLoss` với target mềm = grade/3; chia train/val **theo nhóm CV** để không rò rỉ.
6. **Hybrid**: $\alpha \cdot \text{Score}_{GCN} + (1-\alpha)\cdot\text{Score}_{SBERT}$, α chọn trên tập val tối đa hóa NDCG@10.
7. **Đánh giá**: xếp hạng JD cho từng CV, NDCG@K, Recall@K, MRR.

---

## Bộ dữ liệu

| Thành phần | Nguồn | Quy mô |
|:---|:---|:---|
| **CV** | Tổng hợp bằng ChatGPT, 13 nhóm nghề × 4 cấp (Fresher/Junior/Middle/Senior) × 2 CV | 104 CV (`data/raw/cvs_synth/`) |
| **JD** | Thật, lấy từ [VietJobs](https://huggingface.co/datasets/dinhieufam/VietJobs) ngành CNTT, chọn xác định (không ngẫu nhiên) theo cụm và nhóm nghề | 159 JD dùng trong nhãn (`data/raw/selected_jds.csv`) |
| **Cặp CV–JD** | 15 JD cho mỗi CV: cùng nhóm, liền kề, khác khối CNTT, ngoài CNTT (`data/raw/pairs_design.csv`) | 1664 cặp |
| **Nhãn** | Claude chấm theo rubric v1.2, ghi lại 4 đặc trưng (vai trò, độ phủ yêu cầu bắt buộc, lệch cấp, điều kiện cứng) rồi **tính điểm bằng bảng quyết định** (`data/raw/judgments/`) | 0: 429 · 1: 812 · 2: 256 · 3: 167 |

Thang nhãn (chi tiết, ví dụ và các quyết định đã chốt: [docs/labeling_guide.md](docs/labeling_guide.md)):

| Grade | Tên | Ý nghĩa | Target (grade/3) |
|:---:|:---|:---|:---:|
| 3 | Phù hợp tốt | Cùng vai trò, đáp ứng phần lớn yêu cầu bắt buộc, đủ cấp độ | 1.00 |
| 2 | Phù hợp một phần | Đáng cân nhắc nhưng thiếu yêu cầu quan trọng hoặc lệch cấp | 0.67 |
| 1 | Liên quan ngành | Cùng ngành/vai trò nhưng thiếu phần lớn yêu cầu | 0.33 |
| 0 | Không phù hợp | Khác hẳn lĩnh vực | 0.00 |

Nhãn đo **năng lực làm được việc**: ứng viên dư kinh nghiệm không bị trừ điểm.

### Kiểm chứng nhãn (chấm mù)

Vòng chính thức: 36 cặp khác nhau, một người chấm độc lập chưa xem nhãn của Claude.

- Khớp chính xác **86,1%** (31/36), trong ±1 mức **100%**, không cặp nào lệch ≥ 2 mức.
- Kappa trọng số bình phương **0,94** [0,87–0,99]; nhị phân (mức ≥ 2) khớp 97,2%.
- Hạn chế: một người chấm (chưa có độ đồng thuận giữa người với người); mẫu cân bằng theo mức điểm nên kappa cao hơn mẫu tự nhiên.

Chi tiết các vòng kiểm chứng: [data/raw/validation/rounds_summary.md](data/raw/validation/rounds_summary.md). Phiếu chấm mù và khóa đáp án nằm cùng thư mục (khóa là `_KEY_DO_NOT_OPEN_*.csv`; đừng đưa cho người chấm).

---

## Kết quả (5-fold cross-validation theo CV)

104 CV, mỗi CV nằm ở tập test đúng một lần; ô là trung bình [khoảng tin cậy 95% bootstrap theo CV]. Bảng đầy đủ: [data/processed/cv_results.md](data/processed/cv_results.md).

| Phương pháp | NDCG@1 | NDCG@5 | NDCG@10 | Recall@5 | MRR |
|:---|:---:|:---:|:---:|:---:|:---:|
| Random | 0.39 | 0.45 | 0.56 | 0.32 | 0.52 |
| TF-IDF + cosine | 0.65 | 0.72 | 0.78 | 0.62 | 0.79 |
| SBERT + cosine | 0.60 | 0.70 | 0.79 | 0.59 | 0.74 |
| GCN | 0.69 | 0.78 | 0.87 | 0.68 | 0.80 |
| Hybrid (GCN + SBERT) | **0.70** | **0.80** | **0.88** | **0.70** | **0.81** |

GCN vượt rõ hai baseline ở NDCG@10; ở NDCG@1, NDCG@5 và MRR khoảng tin cậy chồng nhau với TF-IDF. Hybrid cao nhất ở hầu hết chỉ số nhưng chênh lệch với GCN nằm trong khoảng tin cậy. Huấn luyện có tính ngẫu nhiên: hai lần chạy cross-validation liền nhau lệch tới ~0,04 ở NDCG@1, nên đừng diễn giải chênh lệch nhỏ hơn mức đó. Mô hình cuối (`models/best_model.pt`) huấn luyện trên toàn bộ 104 CV (84 train / 20 val để dừng sớm); các chỉ số trên tập val của nó bị lạc quan nên không dùng để báo cáo.

### Chuyển điểm sang mức 0–3

Cách cũ `round(score×3)` khiến dự đoán dồn về mức 1–2 (chỉ dự đoán 64 cặp mức 3, trong khi nhãn thật có 167). Ngưỡng nay được hiệu chỉnh trên điểm out-of-fold (`python src/evaluation/calibrate_thresholds.py`, lưu ở `models/grade_thresholds.json`), tối đa hóa macro-F1. Đánh giá cross-fit (ngưỡng mỗi fold tìm trên 4 fold còn lại):

| | Khớp chính xác | ±1 mức | Macro-F1 | F1 theo mức (0/1/2/3) | Số dự đoán (0/1/2/3) |
|:---|:---:|:---:|:---:|:---:|:---:|
| Cách cũ | 70,0% | 94,8% | 0,556 | 0,93 / 0,77 / 0,30 / 0,23 | 444 / 907 / 249 / 64 |
| Ngưỡng hiệu chỉnh | 67,8% | 93,0% | 0,570 | 0,92 / 0,74 / 0,25 / 0,37 | 431 / 838 / 221 / 174 |
| Nhãn thật | | | | | 429 / 812 / 256 / 167 |

Hiệu chỉnh làm phân bố dự đoán khớp phân bố thật và tăng nhận diện mức 3, nhưng cải thiện chỉ nhỏ và độ chính xác tổng giảm nhẹ: điểm GCN phân tách yếu giữa mức 2 và 3, ngưỡng chỉ dịch chuyển lỗi chứ không loại bỏ được. Với xếp hạng nên dùng điểm liên tục; mức 0–3 chỉ để đọc nhanh.

### Hạn chế cần nêu khi báo cáo

- Nhãn do một người chấm theo rubric (đã kiểm mù); mô hình học bắt chước rubric này, không phải "độ phù hợp" tuyệt đối.
- Mỗi JD xuất hiện ở nhiều CV nên JD ở tập train có thể gặp lại ở tập test (chia theo CV chưa loại hết).
- Mỗi danh sách 15 JD có sẵn nhiều cặp rất dễ phân biệt (ngoài ngành): chỉ nên so sánh tương đối giữa các phương pháp.
- Nhãn 3 chỉ chiếm 10%; chưa dùng trọng số lớp. GCN có xu hướng dồn dự đoán về mức giữa.
- Chưa có kiểm định có ghép cặp (paired) giữa GCN và baseline.

---

## Cài đặt & cấu hình

Yêu cầu Python 3.10+ (đã chạy trên Python 3.13, Windows).

```bash
pip install -r requirements.txt
```

Tạo `.env` ở thư mục gốc. Mặc định trong `config.py` là **Groq** (`qwen/qwen3.8-27b`); `.env` ghi đè được để dùng nhà cung cấp khác có API tương thích OpenAI. Bộ dữ liệu hiện tại được trích xuất thực thể bằng `gemini-3.1-flash-lite` (xem lưu ý bên dưới):

```env
LLM_API_KEY=<khóa API>
OPENAI_BASE_URL=<endpoint tương thích OpenAI>
LLM_MODEL=<tên model>
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
```

> **Lưu ý khi đổi LLM**: cache thực thể khóa theo nội dung văn bản, không theo model. CV/JD đã có trong `entity_cache.json` luôn dùng kết quả cũ (Gemini); văn bản mới mới gọi LLM đang cấu hình. Đổi nhà cung cấp rồi suy luận trên CV/JD mới có thể cho thực thể hơi khác phân phối lúc huấn luyện; muốn đồng nhất hoàn toàn thì xóa cache và chạy lại `--mode prepare` rồi huấn luyện lại.

> Trên Windows nên chạy `python -X utf8 ...` để tránh lỗi hiển thị tiếng Việt.

---

## Hướng dẫn chạy

```bash
# 1. Dựng đồ thị từ nhãn + CV + JD (gọi LLM, có cache; ~vài phút lần đầu)
python -X utf8 main.py --mode prepare

# 2. Cross-validation 5 fold theo CV, so sánh với baseline (ghi data/processed/cv_results.*)
python -X utf8 src/modeling/train.py --cv 5

# 3. Hiệu chỉnh ngưỡng điểm → mức 0-3 (dùng điểm out-of-fold của bước 2)
python -X utf8 src/evaluation/calibrate_thresholds.py

# 3b. Huấn luyện mô hình cuối (lưu models/best_model.pt)
python -X utf8 src/modeling/train.py --patience 20

# 4. Dự đoán cho một cặp CV–JD
python -X utf8 main.py --mode predict

# Kiểm tra
python -X utf8 tests/test_dataset_labels.py
python -X utf8 tests/test_explain.py
```

Tạo lại dữ liệu JD từ đầu (chỉ khi cần; cần file VietJobs gốc ngoài repo): `src/data_collection/extract_vietjobs_it.py` → `cache_jd_embeddings.py` → `cluster_jds.py` → `select_jds.py`.

### Diễn giải kết quả

`src/inference/explain.py` giải thích mức khớp giữa CV và JD (khớp thực thể, khớp ngữ nghĩa SBERT, đóng góp của từng nút theo occlusion), xuất song ngữ Việt/Anh.

---

## Cấu trúc thư mục

```
├── main.py                       # Điều hướng các chế độ chạy
├── config.py                     # Tham số mô hình, đường dẫn, API
├── docs/labeling_guide.md        # Rubric v1.2, prompt sinh CV, quy trình gán nhãn
├── src/
│   ├── data_collection/
│   │   ├── select_jds.py         # Chọn JD thật có kiểm soát (không ngẫu nhiên)
│   │   ├── prepare_training_data.py  # Dựng đồ thị từ nhãn + CV + JD
│   │   └── extract_vietjobs_it.py, cache_jd_embeddings.py, cluster_jds.py
│   ├── extraction/entity_extractor.py   # LLM extractor + cache
│   ├── representation/           # Embedding + DeepSets, xây đồ thị 14 nút
│   ├── modeling/                 # model.py, train.py (có --cv)
│   ├── evaluation/               # metrics, baselines, hybrid, calibrate_thresholds
│   └── inference/                # predict.py, explain.py
├── data/
│   ├── raw/                      # cvs_synth, profiles, judgments, selected_jds.csv, pairs_design.csv, validation/
│   ├── processed/                # dataset_manifest.csv, cv_results.*, jd_clusters.csv, graphs/ (sinh ra, không commit)
│   └── cache/                    # entity_cache.json, jd_embeddings_cache.pt
├── models/best_model.pt          # Mô hình cuối
└── tests/                        # test_dataset_labels, test_explain, test_select_jds
```

## Thông số kỹ thuật

| Thông số | Giá trị |
|:---|:---|
| Số nút đồ thị | 14 (2 trung tâm + 12 thực thể) |
| Embedding | `paraphrase-multilingual-MiniLM-L12-v2`, 384 chiều; DeepSets → 1152 chiều |
| GCN | 3 lớp `GCNConv`, hidden 128, dropout 0.3 |
| k-NN / sharpening | $k=10$, $p=4.0$ |
| Loss | `BCEWithLogitsLoss`, target = grade/3 |
| Tối ưu | Adam, lr 1e-3, weight decay 1e-4, early stopping theo val loss |
| Ngưỡng ngữ nghĩa (diễn giải) | cosine ≥ 0.75 |
| Metrics xếp hạng | NDCG@K, Recall@K, MRR với K ∈ {1, 3, 5, 10} |
