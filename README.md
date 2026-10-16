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

1. **Trích xuất thực thể**: LLM trả JSON 6 loại thực thể. Với JD chỉ giữ yêu cầu **bắt buộc**; các ý "ưu tiên / lợi thế" tách riêng sang `preferred_skills` (không đưa vào đồ thị). Với CV chỉ giữ kỹ năng ứng viên **thực sự có**, bỏ câu phủ định ("chưa có kinh nghiệm frontend"). Cache theo SHA-256 của văn bản và phiên bản prompt (`ENTITY_PROMPT_VERSION`, `data/cache/entity_cache.json`, ghi qua tệp tạm).
2. **Embedding**: `paraphrase-multilingual-MiniLM-L12-v2` (384 chiều) + **DeepSets** (mean/sum/max → 1152 chiều mỗi nút).
3. **Đồ thị** 14 nút như trên.
4. **GCN**: pre-aggregation → 3 lớp `GCNConv` (hidden 128) → readout → MLP.
5. **Huấn luyện**: `BCEWithLogitsLoss` với target mềm = grade/3; chia train/val **theo nhóm CV** để không rò rỉ.
6. **Hybrid**: $\alpha \cdot \text{Score}_{GCN} + (1-\alpha)\cdot\text{Score}_{SBERT}$, α chọn trên tập val tối đa hóa NDCG@10.
7. **Đặc trưng LLM theo cặp** (`src/extraction/pair_features.py`): LLM đọc thẳng CV và JD, trả về các yêu cầu **bắt buộc** của JD mà CV đáp ứng (độ phủ), điều kiện cứng chưa đáp ứng, chênh lệch số năm kinh nghiệm, công nghệ trong tiêu đề JD có ở CV không. Khi huấn luyện, một lần gọi xử lý 1 CV với 15 JD.
8. **Mô hình xếp chồng** (`src/modeling/stacker.py`): gradient boosting trên [đặc trưng LLM, cosine SBERT toàn văn và theo từng loại thực thể, điểm GCN] hồi quy trực tiếp grade 0–3; mức = làm tròn. GCN giữ vai trò nắm chủ đề và vai trò, đặc trưng LLM bổ sung độ phủ yêu cầu.
9. **Đánh giá**: xếp hạng JD cho từng CV, NDCG@K, Recall@K, MRR; chia mức 0–3.

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
| TF-IDF + cosine | 0.62 | 0.72 | 0.79 | 0.62 | 0.78 |
| SBERT + cosine | 0.59 | 0.71 | 0.79 | 0.57 | 0.74 |
| GCN | 0.64 | 0.77 | 0.85 | 0.70 | 0.77 |
| Hybrid (GCN + SBERT) | 0.66 | 0.79 | 0.87 | 0.73 | 0.78 |

GCN vượt hai baseline ở NDCG@5 và NDCG@10 nhưng khoảng tin cậy chồng nhau ở NDCG@1 và MRR; Hybrid nhỉnh hơn GCN đơn nhưng nằm trong sai số. Huấn luyện có tính ngẫu nhiên: các lần chạy cross-validation liền nhau lệch tới ~0,04 ở NDCG@1, nên đừng diễn giải chênh lệch nhỏ hơn mức đó. (Bảng đầy đủ kèm các biến thể dùng đặc trưng LLM ở `cv_results.md`.)

### Mô hình xếp chồng (GCN + đặc trưng LLM) — kết quả cuối

Đánh giá bằng cross-validation **lồng nhau** (điểm GCN dùng để huấn luyện stacker là điểm out-of-fold của vòng trong, nên không rò rỉ; `python src/modeling/train.py --stack`), 104 CV:

| | NDCG@1 | NDCG@5 | NDCG@10 | MRR | Đúng chính xác mức 0–3 | Trong ±1 mức | Macro-F1 | Phân loại "phù hợp (≥ 2)" |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| GCN đơn | 0.67 | 0.75 | 0.85 | 0.76 | 64.2% | 91.8% | 0.54 | 74.3% |
| **Stacker** | **0.79** | **0.86** | **0.92** | **0.89** | **71.3%** | **99.0%** | **0.63** | **85.3%** |

F1 theo mức (0/1/2/3): GCN đơn 0,90 / 0,70 / 0,26 / 0,29; stacker 0,86 / 0,79 / 0,45 / 0,42. Mức 2 vẫn là mức khó nhất. Khoảng tin cậy chưa tính cho bảng này (cross-validation lồng nhau tốn khoảng 40 phút). Stacker chia mức bằng cách làm tròn; GCN đơn dùng ngưỡng hiệu chỉnh cross-fit.

**Về việc sửa prompt trích xuất.** Các con số trên đo sau khi sửa prompt (JD chỉ giữ yêu cầu bắt buộc, CV bỏ câu phủ định). Trước khi sửa, cùng quy trình cho stacker NDCG@5 0,88, đúng chính xác 75,4%, phân loại ≥ 2 là 87,0%; GCN đơn NDCG@5 0,78. Mức giảm sau khi sửa (khoảng 0,02 NDCG@5 và 3–4 điểm phần trăm độ chính xác) nằm trong mức nhiễu giữa các lần huấn luyện và lẫn với một thay đổi khác: lần trích xuất lại dùng `gemini-flash-lite-latest` thay cho `gemini-3.1-flash-lite`, nên không tách được ảnh hưởng riêng của prompt. Bản sửa được giữ vì đúng về nghiệp vụ (không tính mục "ưu tiên" là yêu cầu, không coi kỹ năng bị phủ định là có).

**Vì sao GCN đơn yếu ở mức 2–3 (chẩn đoán).** Nhãn 3 là "cùng nghề + độ phủ yêu cầu bắt buộc cao + không vướng cấp độ/điều kiện cứng"; 70% nhãn 2 là "cùng nghề + độ phủ vừa". Nghĩa là phân biệt 2/3 gần như chỉ cần **độ phủ yêu cầu bắt buộc**. (Số đo ở đoạn này lấy trước khi sửa prompt trích xuất.) Độ phủ tính qua thực thể LLM rồi khớp cosine tương quan chỉ 0,38 với độ phủ chuẩn (0,15 trong cùng nghề) và AUC tách 3 khỏi 2 trong cùng nghề chỉ 0,50–0,66, vì danh sách thực thể lẫn cả mục "ưu tiên" (trung bình 11,9 mục/JD so với 8,3 yêu cầu bắt buộc), kỹ năng bị gộp vào một nút, và cosine không tách được "cùng nghĩa" khỏi "giống bề ngoài". Khi LLM đọc thẳng cặp CV–JD, tương quan đạt 0,66 (mẫu 105 cặp). GCN vẫn phân biệt chủ đề rất tốt (AUC 0,98 giữa khác nghề và cùng nghề), nên được giữ làm một thành phần của stacker.

**Lưu ý:** (1) Stacker cần 1 lần gọi LLM cho mỗi cặp lúc suy luận; không có LLM hoặc PDF scan thì tự lùi về GCN đơn. (2) Đặc trưng lúc huấn luyện tính theo lô 15 JD/CV, lúc suy luận theo lô 1 JD cùng prompt; đã so lô với từng cặp (prompt cũ) trên 45 cặp thấy độ phủ tương quan 0,86, nhưng chưa so trực tiếp lô 15 với lô 1 cùng prompt. (3) Đặc trưng LLM do `gemini-flash-lite-latest` sinh; đổi LLM thì kết quả đặc trưng đổi (cache khóa theo tên model) và nên tính lại + huấn luyện lại stacker.

### Chuyển điểm sang mức 0–3 (GCN đơn)

Cách cũ `round(score×3)` khiến dự đoán dồn về mức 1–2 (chỉ dự đoán 61 cặp mức 3, trong khi nhãn thật có 167). Ngưỡng nay được hiệu chỉnh trên điểm out-of-fold (`python src/evaluation/calibrate_thresholds.py`, lưu ở `models/grade_thresholds.json`), tối đa hóa macro-F1. Đánh giá cross-fit (ngưỡng mỗi fold tìm trên 4 fold còn lại):

| | Khớp chính xác | ±1 mức | Macro-F1 | Số dự đoán (0/1/2/3) |
|:---|:---:|:---:|:---:|:---:|
| Cách cũ | 63,4% | 96,0% | 0,529 | 379 / 788 / 436 / 61 |
| Ngưỡng hiệu chỉnh (0,22 / 0,49 / 0,64) | 64,0% | 94,1% | 0,559 | 420 / 733 / 353 / 158 |
| Nhãn thật | | | | 429 / 812 / 256 / 167 |

Hiệu chỉnh làm phân bố dự đoán gần phân bố thật và tăng nhận diện mức 3, nhưng cải thiện chỉ nhỏ và độ chính xác ±1 giảm: điểm GCN phân tách yếu giữa mức 2 và 3, ngưỡng chỉ dịch chuyển lỗi chứ không loại bỏ được. Với xếp hạng nên dùng điểm liên tục; mức 0–3 chỉ để đọc nhanh.

### Hạn chế cần nêu khi báo cáo

- Nhãn do một người chấm theo rubric (đã kiểm mù); mô hình học bắt chước rubric này, không phải "độ phù hợp" tuyệt đối.
- Mỗi JD xuất hiện ở nhiều CV nên JD ở tập train có thể gặp lại ở tập test (chia theo CV chưa loại hết).
- Mỗi danh sách 15 JD có sẵn nhiều cặp rất dễ phân biệt (ngoài ngành): chỉ nên so sánh tương đối giữa các phương pháp.
- Nhãn 3 chỉ chiếm 10%; chưa dùng trọng số lớp. GCN có xu hướng dồn dự đoán về mức giữa.
- Chưa có kiểm định có ghép cặp (paired) giữa GCN/stacker và baseline.
- Stacker phụ thuộc đặc trưng do một LLM cụ thể sinh ra (xem lưu ý ở trên) và cần LLM lúc suy luận.

---

## Cài đặt & cấu hình

Yêu cầu Python 3.10+ (đã chạy trên Python 3.13, Windows).

```bash
pip install -r requirements.txt
```

Tạo `.env` ở thư mục gốc. Mặc định trong `config.py` là **Groq** (`qwen/qwen3.8-27b`); `.env` ghi đè được để dùng nhà cung cấp khác có API tương thích OpenAI. Cấu hình đã dùng để tạo kết quả trong README là **`gemini-flash-lite-latest`** cho đặc trưng LLM theo cặp (thực thể CV/JD cũng được trích xuất lại bằng `gemini-flash-lite-latest` với prompt v2). Gói miễn phí Gemini giới hạn **500 lượt/ngày/model** (đặc trưng theo cặp gộp 15 JD/lần gọi nên cả bộ chỉ cần 104 lần gọi); Groq miễn phí chậm hơn nhiều (vài chục giây đến vài phút mỗi lần gọi lô lớn):

```env
LLM_API_KEY=<khóa API>
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_MODEL=gemini-flash-lite-latest
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
```

> **Lưu ý khi đổi LLM**: cache thực thể khóa theo nội dung văn bản và phiên bản prompt, **không theo model**. CV/JD đã có trong `entity_cache.json` luôn dùng kết quả cũ; văn bản mới mới gọi LLM đang cấu hình. Đổi nhà cung cấp rồi suy luận trên văn bản mới có thể cho thực thể hơi khác phân phối lúc huấn luyện; muốn đồng nhất hoàn toàn thì xóa các khóa `v2:` trong cache rồi chạy lại `--mode prepare` và huấn luyện lại. (Cache đặc trưng theo cặp `pair_features.jsonl` thì khóa theo cả tên model.)

> Trên Windows nên chạy `python -X utf8 ...` để tránh lỗi hiển thị tiếng Việt.

---

## Hướng dẫn chạy

```bash
# 1. Dựng đồ thị từ nhãn + CV + JD (gọi LLM, có cache; ~vài phút lần đầu)
python -X utf8 main.py --mode prepare

# 2. Cross-validation 5 fold theo CV, so sánh với baseline (ghi data/processed/cv_results.*)
python -X utf8 src/modeling/train.py --cv 5

# 1b. Đặc trưng LLM theo cặp: mỗi CV một lần gọi cho 15 JD (104 lần gọi, vài phút)
python -X utf8 src/extraction/pair_features.py --workers 3

# 2b. Đánh giá mô hình xếp chồng bằng cross-validation lồng nhau (~40 phút, không gọi LLM)
python -X utf8 src/modeling/train.py --stack

# 3. Hiệu chỉnh ngưỡng điểm → mức 0-3 cho GCN đơn (dùng điểm out-of-fold của bước 2)
python -X utf8 src/evaluation/calibrate_thresholds.py

# 3b. Huấn luyện mô hình cuối: GCN (models/best_model.pt) rồi stacker (models/stacker.pkl)
python -X utf8 src/modeling/train.py --patience 20
python -X utf8 src/modeling/stacker.py

# 4. Dự đoán cho một cặp CV–JD
python -X utf8 main.py --mode predict

# Kiểm tra
python -X utf8 tests/test_dataset_labels.py
python -X utf8 tests/test_pair_features.py
python -X utf8 tests/test_entity_extractor.py
python -X utf8 tests/test_explain.py
```

Tạo lại dữ liệu JD từ đầu (chỉ khi cần; cần file VietJobs gốc ngoài repo): `src/data_collection/extract_vietjobs_it.py` → `cache_jd_embeddings.py` → `cluster_jds.py` → `select_jds.py`.

### Diễn giải kết quả

`result["explanation"]` (`recruiter_summary` trong `src/inference/explain.py`) là bản **ngắn gọn cho nhà tuyển dụng**, song ngữ Việt/Anh, không thuật ngữ: kết luận theo mức (Rất phù hợp / Phù hợp một phần / Ít phù hợp / Không phù hợp), các yêu cầu bắt buộc của JD mà CV đáp ứng, các yêu cầu chưa thấy trong CV, và điều cần lưu ý (điều kiện cứng chưa đáp ứng, thiếu số năm kinh nghiệm, công nghệ trong tiêu đề JD chưa có ở CV). Ví dụ:

```
Kết luận: Phù hợp một phần (mức 2/3), đáng cân nhắc, cần làm rõ các điểm còn thiếu.
Đáp ứng (5/8 yêu cầu bắt buộc): Unity, C#, OOP, data structures, algorithms.
Chưa thấy trong CV: multiplayer technologies, Game performance optimization, ...
Cần lưu ý: JD yêu cầu tối thiểu 1 năm kinh nghiệm, CV chưa có kinh nghiệm liên quan.
```

Nội dung lấy từ đánh giá của LLM về từng yêu cầu (cùng nguồn với đặc trưng của stacker nên nhất quán với mức điểm). Khi không có LLM (hoặc PDF scan), mô hình chạy GCN đơn và bản tóm tắt chỉ liệt kê kỹ năng chuyên môn khớp/thiếu, có ghi chú là ước lượng nhanh. Bản **kỹ thuật** (khớp từng loại thực thể theo cosine, đóng góp của từng nút GCN) vẫn có ở `result["explanation_detail"]` và trong chế độ tương tác của `main.py --mode predict`; độ tin cậy của phần khớp ngữ nghĩa bị giới hạn như đã nêu ở trên (precision ~0,74 tại ngưỡng 0,75, kỹ năng mềm ~0,60), nên không dùng cho nhà tuyển dụng.

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
│   ├── extraction/               # entity_extractor.py (thực thể + cache), pair_features.py (đặc trưng LLM theo cặp)
│   ├── representation/           # Embedding + DeepSets, xây đồ thị 14 nút
│   ├── modeling/                 # model.py, train.py (--cv, --stack), stacker.py
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
| Ngưỡng ngữ nghĩa (diễn giải) | cosine ≥ 0.75 (precision ~0,74, recall ~0,40 trên 178 cặp gán nhãn tay) |
| Metrics xếp hạng | NDCG@K, Recall@K, MRR với K ∈ {1, 3, 5, 10} |
