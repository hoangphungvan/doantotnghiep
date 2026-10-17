# Candidate-Job Matching (CJM): mô hình lai Semantic Embedding + Graph Neural Network

Hệ thống chấm điểm mức độ phù hợp giữa một CV và một JD, **từng cặp một**, để backend sắp xếp các CV của mỗi JD theo điểm giảm dần (chiều có lợi cho nhà tuyển dụng). Điểm là **Hybrid Score** kết hợp điểm của **Graph Convolutional Network** (PyTorch Geometric) với độ tương đồng ngữ nghĩa **Sentence-BERT**. LLM (Gemini) chỉ trích xuất thực thể và viết diễn giải, không tham gia tính điểm.

---

## Kiến trúc

### 1. Đồ thị 14 nút cho mỗi cặp (CV, JD)

```
        [Soft Skills]──┐                  ┌──[Soft Skills]
       [Hard Skills]───┤                  ├───[Hard Skills]
         [Education]───┤                  ├───[Education]
  [Field of Education]─┼──[Candidate]────[JD]──┼─[Field of Education]
    [Industry Sector]──┤                  ├──[Industry Sector]
              [Role]───┘                  └───[Role]
```

- 2 nút trung tâm (ứng viên, việc làm) và 12 nút thực thể (6 loại mỗi bên: `role`, `hard_skills`, `field_of_education`, `industry_sector`, `education`, `soft_skills`).
- Cạnh: star (trung tâm ↔ thực thể của mình, trọng số `ENTITY_WEIGHTS`), cầu (trung tâm CV ↔ trung tâm JD), cạnh chéo giữa thực thể cùng loại (cosine × trọng số), k-NN làm sắc nét ($k=10$, $p=4$).

### 2. Pipeline

1. **Trích xuất thực thể (Gemini)**: JSON 6 loại thực thể. JD chỉ giữ yêu cầu **bắt buộc** (ý "ưu tiên" tách sang `preferred_skills`, không vào đồ thị); CV bỏ kỹ năng bị phủ định. Cache theo SHA-256 của văn bản và phiên bản prompt.
2. **Embedding**: `paraphrase-multilingual-MiniLM-L12-v2` (384 chiều) + **DeepSets** (mean/sum/max → 1152 chiều mỗi nút).
3. **GCN**: pre-aggregation → 3 lớp `GCNConv` (hidden 128, residual) → readout → MLP → điểm đồ thị $s_{GCN}\in(0,1)$. Huấn luyện bằng `BCEWithLogitsLoss` với nhãn mềm = grade/3, chia train/val theo nhóm CV.
4. **Hybrid Score**: $S=\alpha\cdot s_{GCN}+(1-\alpha)\cdot\tilde s_{SBERT}$, $\tilde s_{SBERT}$ là cosine SBERT toàn văn CV–JD chuẩn hóa min–max; **α = 0,3** (`models/hybrid.json`).
5. **Quy mức 0–3**: so $S$ với 3 ngưỡng hiệu chỉnh trên điểm out-of-fold (`models/grade_thresholds.json`, tối đa macro-F1).
6. **Diễn giải (Gemini)**: đối chiếu từng yêu cầu **bắt buộc** của JD với CV (đáp ứng / chưa thấy), điều kiện cứng, số năm kinh nghiệm; chỉ để giải thích, không đổi điểm. Không có LLM thì dùng đối chiếu thực thể.

### 3. Cách backend dùng

```python
from src.inference.predict import CJMPredictor

predictor = CJMPredictor()
results = [(cv["id"], predictor.predict_from_text(cv["text"], jd_text)) for cv in cv_list]   # các CV ứng tuyển cùng một JD
ranked = sorted(results, key=lambda t: t[1]["score"], reverse=True)                          # CV phù hợp nhất trước
```

Mỗi kết quả có `score` (Hybrid, 0–1), `gcn_score`, `semantic_score`, `grade` / `grade_label` (0–3), `label` (MATCH nếu mức ≥ 2), `explanation` (tiếng Việt và tiếng Anh), `llm_requirements`, `llm_conditions`. Điểm được cắt ở 0 và 1 nên các cặp ở hai đầu có thể hòa; mỗi cặp tốn một lần gọi Gemini cho phần diễn giải (trích xuất thực thể của mỗi văn bản chỉ gọi một lần nhờ cache). Hệ thống nhận cả PDF (có text layer hoặc PDF scan qua Vision).

---

## Bộ dữ liệu

| Thành phần | Nguồn | Quy mô |
|:---|:---|:---|
| **CV** (`data/raw/cvs_synth/`) | Tổng hợp bằng ChatGPT: 13 nhóm nghề × 4 cấp (Fresher/Junior/Middle/Senior) × 2 CV | 104 |
| **JD** (`data/raw/selected_jds.csv`) | Thật, từ [VietJobs](https://huggingface.co/datasets/dinhieufam/VietJobs) ngành CNTT, chọn xác định theo cụm và nhóm nghề (cột `jd_brief`) | 159 |
| **Cặp và nhãn** (`data/raw/pairs_labeled.csv`) | Mỗi CV ghép với khoảng 16 JD (cùng nhóm, liền kề, khác khối CNTT, ngoài CNTT); nhãn tính theo rubric từ 4 đặc trưng (vai trò, độ phủ yêu cầu bắt buộc, lệch cấp, điều kiện cứng) | 1664 cặp: mức 0: 429 · 1: 812 · 2: 256 · 3: 167 |

| Mức | Tên | Ý nghĩa |
|:---:|:---|:---|
| 3 | Phù hợp tốt | Cùng vai trò, đáp ứng phần lớn yêu cầu bắt buộc, đủ cấp độ |
| 2 | Phù hợp một phần | Đáng cân nhắc nhưng thiếu yêu cầu quan trọng hoặc lệch cấp |
| 1 | Liên quan ngành | Cùng ngành/vai trò nhưng thiếu phần lớn yêu cầu |
| 0 | Không phù hợp | Khác hẳn lĩnh vực |

Nhãn đo **năng lực làm được việc**: ứng viên dư kinh nghiệm không bị trừ điểm. Kiểm chứng mù trên 36 cặp (một người chấm độc lập): khớp chính xác 86,1%, trong ±1 mức 100%, kappa trọng số bình phương 0,94 [0,87–0,99]; hạn chế là chỉ một người chấm và mẫu cân bằng theo mức.

---

## Kết quả

Chiều chính là **mỗi JD xếp hạng các CV**. Cách chia dữ liệu quyết định độ lạc quan của kết quả, nên báo cáo ba cách chia (điểm out-of-fold, bootstrap theo truy vấn):

| Cách chia | CV mới? | JD mới? | NDCG@5 Hybrid (α = 0,3) | NDCG@5 SBERT cosine |
|:---|:---:|:---:|:---:|:---:|
| Theo CV | có | không | 0,82 | 0,83 |
| Theo JD | không | có | 0,85 | 0,83 |
| **Loại trừ cả hai** | có | có | 0,89 | 0,89 |

**Cách chia loại trừ cả hai** (đại diện cho triển khai thật: ứng viên mới, tin tuyển dụng mới; 187 truy vấn, GCN 3 seed). Mỗi lượt chỉ huấn luyện trên khoảng 666 cặp nên mô hình học yếu hơn; danh sách ngắn (khoảng 5 CV) nên NDCG cao hơn các bảng khác, chỉ so sánh trong cùng bảng:

| Phương pháp | NDCG@5 | NDCG@10 | MRR | AUC |
|:---|:---:|:---:|:---:|:---:|
| TF-IDF + cosine | 0,877 | 0,901 | 0,835 | 0,778 |
| SBERT + cosine | **0,889** | **0,910** | **0,854** | 0,783 |
| MLP trên SBERT | 0,861 | 0,886 | 0,822 | 0,774 |
| GCN đơn | 0,832 | 0,864 | 0,781 | 0,722 |
| Hybrid (α chọn theo validation, TB 0,54) | 0,881 | 0,904 | 0,849 | 0,784 |
| **Hybrid (α = 0,3, hệ thống)** | **0,890** | **0,911** | **0,857** | **0,802** |

**Chiều ứng viên** (mỗi CV xếp hạng các JD, chia theo CV, 104 CV; chiều phụ): NDCG@10 TF-IDF 0,79 · SBERT 0,79 · MLP 0,89 · GCN 0,85 · Hybrid (α = 0,3) 0,85; phân loại "phù hợp" (mức ≥ 2): F1 Hybrid 0,60 (GCN 0,58, SBERT 0,55), AUC 0,84 (GCN 0,82, SBERT 0,78).

**Đọc kết quả thận trọng.**
- Với ứng viên và JD mới, Hybrid (α = 0,3) **chỉ ngang** SBERT cosine thuần (NDCG@5 0,890 so với 0,889), GCN đơn kém hơn (0,832); khoảng tin cậy chồng nhau. Ở chuẩn này NDCG@10 gần như phẳng với α từ 0 đến 0,6. Hybrid có lợi rõ khi mô hình đã thấy CV hoặc JD lúc huấn luyện hoặc ở chiều ứng viên.
- Chẩn đoán: điểm Hybrid chỉ giải thích khoảng 54% biến thiên của nhãn, trong khi 7 đặc trưng của rubric giải thích 99%; trong cùng vai trò, tách mức 3 khỏi mức 2 bằng độ phủ yêu cầu thật đạt AUC 0,94, còn điểm Hybrid chỉ 0,64. Thông tin còn thiếu là độ phủ yêu cầu bắt buộc và lệch cấp độ. Thêm dữ liệu có lợi (AUC GCN 0,73 → 0,83 khi dữ liệu huấn luyện tăng 25% → 100%) nhưng chưa đủ.
- α = 0,3 là lựa chọn trung gian: với CV mới, chọn α theo NDCG@10 theo JD cho α = 0 (SBERT thuần); α = 0,3 chỉ kém 0,011 NDCG@10 ở tình huống đó và được lợi ở các tình huống còn lại.
- Dao động giữa các lần huấn luyện GCN khoảng ±0,01 NDCG, ±0,015 AUC; không diễn giải chênh lệch nhỏ hơn.

### Chuyển điểm Hybrid sang mức 0–3

Ba ngưỡng (0,34 / 0,58 / 0,70) tối đa macro-F1 trên điểm Hybrid out-of-fold; khớp chính xác cross-fit 61,5%, macro-F1 0,535. Mức 2 và 3 trong cùng vai trò là phần khó nhất. Với xếp hạng nên dùng điểm liên tục; mức 0–3 chỉ để đọc nhanh.

### Hạn chế

- Nhãn do một người chấm theo rubric (đã kiểm mù); mô hình học bắt chước rubric.
- Các cặp được thiết kế theo từng CV, nên danh sách CV của mỗi JD không được thiết kế (trung bình khoảng 10 CV); khoảng tin cậy ở chiều nhà tuyển dụng rộng. Cần dữ liệu mà mọi CV ứng tuyển cùng một JD đều được gán nhãn.
- CV là dữ liệu tổng hợp; mỗi JD xuất hiện ở nhiều CV.
- GCN chưa mô hình hóa độ phủ yêu cầu bắt buộc, lệch cấp độ và điều kiện cứng, nên yếu khi phân biệt các CV cùng vai trò.
- Diễn giải LLM tách khỏi điểm nên có thể không khớp mức (ví dụ đáp ứng đủ yêu cầu nhưng điểm thấp).

---

## Cài đặt và cấu hình

Yêu cầu Python 3.10+ (đã chạy trên Python 3.13, Windows).

```bash
pip install -r requirements.txt
```

Tạo `.env` ở thư mục gốc (không commit):

```env
LLM_API_KEY=<khóa Gemini>
# Tùy chọn, mặc định đã là Gemini:
# OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
# LLM_MODEL=gemini-flash-lite-latest
```

> Cache thực thể khóa theo nội dung văn bản và phiên bản prompt, **không theo model**: CV/JD đã có trong `data/cache/entity_cache.json` luôn dùng kết quả cũ. Lần đầu chạy cần tải model SBERT từ Hugging Face. Trên Windows nên chạy `python -X utf8 ...`.

---

## Hướng dẫn chạy

```bash
# 1. Dựng đồ thị từ nhãn + CV + JD (gọi Gemini, có cache; vài phút lần đầu)
python -X utf8 main.py --mode prepare

# 2. Cross-validation 5 fold theo CV, so sánh baseline; ghi điểm GCN out-of-fold (data/processed/cv_oof_predictions.csv)
python -X utf8 src/modeling/train.py --cv 5

# 3. Huấn luyện mô hình cuối: GCN (models/best_model.pt)
python -X utf8 src/modeling/train.py --patience 20

# 4. Hybrid: tính lại min/max SBERT, hiệu chỉnh ngưỡng mức 0-3 (models/hybrid.json, grade_thresholds.json)
python -X utf8 src/evaluation/fit_hybrid.py --alpha 0.3     # bỏ --alpha để chọn α theo NDCG@10

# 5. Dự đoán cho một cặp CV–JD
python -X utf8 main.py --mode predict

# Kiểm tra
python -X utf8 tests/test_dataset_labels.py
python -X utf8 tests/test_pair_features.py
python -X utf8 tests/test_entity_extractor.py
python -X utf8 tests/test_explain.py
```

### Diễn giải kết quả

`result["explanation"]` (`recruiter_summary` trong `src/inference/explain.py`) là bản ngắn gọn, song ngữ Việt/Anh cho nhà tuyển dụng, ví dụ:

```
Kết luận: Phù hợp một phần (mức 2/3), đáng cân nhắc, cần làm rõ các điểm còn thiếu.
Đáp ứng (5/8 yêu cầu bắt buộc): Unity, C#, OOP, data structures, algorithms.
Chưa thấy trong CV: multiplayer technologies, Game performance optimization, ...
Cần lưu ý: JD yêu cầu tối thiểu 1 năm kinh nghiệm, CV chưa có kinh nghiệm liên quan.
```

Kết luận (mức) lấy từ Hybrid, danh sách đáp ứng lấy từ đánh giá của LLM nên hai phần có thể chưa khớp. Khi không có LLM (hoặc PDF scan không đọc được), điểm và mức không đổi, bản tóm tắt chỉ liệt kê kỹ năng chuyên môn khớp/thiếu. Bản kỹ thuật (khớp thực thể theo cosine, đóng góp của từng nút GCN) có ở `result["explanation_detail"]`.

---

## Cấu trúc thư mục

```
├── main.py                       # Điều hướng các chế độ chạy
├── config.py                     # Tham số mô hình, đường dẫn, Gemini
├── src/
│   ├── data_collection/prepare_training_data.py   # Dựng đồ thị từ nhãn + CV + JD
│   ├── extraction/               # entity_extractor.py (thực thể + cache), pair_features.py (LLM đối chiếu yêu cầu để diễn giải)
│   ├── representation/           # Embedding + DeepSets, đồ thị 14 nút
│   ├── modeling/                 # model.py (GCN), train.py (--cv)
│   ├── evaluation/               # metrics, baselines, hybrid, fit_hybrid, calibrate_thresholds
│   └── inference/                # predict.py, explain.py
├── data/
│   ├── raw/                      # cvs_synth/, selected_jds.csv, pairs_labeled.csv
│   ├── processed/                # cv_oof_predictions.csv, graphs/ (sinh ra, không commit)
│   └── cache/                    # entity_cache.json
├── models/                       # best_model.pt, hybrid.json, grade_thresholds.json
├── examples/                     # cv_example.txt, jd_example.txt: một cặp CV–JD để chạy thử
└── tests/
```

## Thông số kỹ thuật

| Thông số | Giá trị |
|:---|:---|
| Số nút đồ thị | 14 (2 trung tâm + 12 thực thể) |
| Embedding | `paraphrase-multilingual-MiniLM-L12-v2`, 384 chiều; DeepSets → 1152 chiều |
| GCN | 3 lớp `GCNConv`, hidden 128, dropout 0.3, residual; 272.129 tham số |
| k-NN / sharpening | $k=10$, $p=4.0$ |
| Loss | `BCEWithLogitsLoss`, target = grade/3 |
| Tối ưu | Adam, lr 1e-3, weight decay 1e-4, batch 32, tối đa 100 epoch, dừng sớm 20 epoch |
| Hybrid | α = 0,3 |
| Ngưỡng ngữ nghĩa (diễn giải) | cosine ≥ 0.75 (precision ~0,74, recall ~0,40 trên 178 cặp gán nhãn tay) |
| Metrics xếp hạng | NDCG@K, Recall@K, MRR với K ∈ {1, 3, 5, 10}; phân loại: Accuracy, Precision, Recall, F1, AUC-ROC |
