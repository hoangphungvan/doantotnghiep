# Candidate-Job Matching (CJM): Graph Neural Network cho ghép CV – JD

Hệ thống chấm điểm mức độ phù hợp giữa một CV và một JD, **từng cặp một**, để backend sắp xếp các CV của mỗi JD theo điểm giảm dần (chiều có lợi cho nhà tuyển dụng). Xuất phát từ bài báo *Graph Neural Networks for Candidate-Job Matching: An Inductive Learning Approach*, hệ thống có hai engine:

| Engine | Mô hình | Vai trò |
|:---|:---|:---|
| **`req`** (mặc định) | **ReqGNN mức yêu cầu**: mỗi yêu cầu JD được đối chiếu với từng mục của CV, tính độ phủ có trọng số, trừ phạt khi thiếu cấp độ hoặc số năm | Chấm điểm và diễn giải lấy **từ cùng một mô hình** |
| `gcn` | Đồ thị 14 nút theo bài báo + Hybrid $S=\alpha\cdot s_{GCN}+(1-\alpha)\cdot s_{SBERT}$ | Baseline tái lập bài báo; dùng khi CV là PDF scan (đọc bằng Vision) |

LLM (Gemini) chỉ **trích xuất** thông tin có cấu trúc. Nó không tham gia tính điểm, và với engine `req` cũng không tham gia diễn giải.

---

## Workflow

### Huấn luyện (offline)

```
CV tổng hợp (104) + JD VietJobs (159) ─► pairs_labeled.csv (1664 cặp, mức 0–3, rubric)
        │
        ├─► [req] Gemini trích xuất TỪNG yêu cầu / mục (loại, bắt buộc/ưu tiên, số năm, cấp độ) → data/cache/req_cache.json
        │        ─► embedding BGE-M3 (cache data/cache/req_emb_*.npz) ─► đồ thị HeteroData mức yêu cầu
        │        ─► ReqGNN, loss xếp hạng pairwise theo JD
        │        ─► 5 fold theo JD: điểm out-of-fold → hiệu chỉnh 3 ngưỡng mức 0–3
        │        ─► huấn luyện lại trên toàn bộ → models/req_model.pt          (train_req.py final)
        │
        └─► [gcn] Gemini trích xuất 6 loại thực thể → embedding MiniLM + DeepSets → đồ thị 14 nút
                 ─► GCN (BCE, nhãn mềm grade/3) → Hybrid α = 0,3 → ngưỡng mức
                 ─► models/best_model.pt, hybrid.json, grade_thresholds.json
```

### Dự đoán (online, `CJMPredictor`)

```
CV + JD (text / PDF có text layer)
  ─► extract_requirements (Gemini, có cache)
  ─► build_pair_graph (BGE-M3) ─► ReqGNN ─► score = sigmoid(logit) ─► mức 0–3 (ngưỡng trong checkpoint)
  ─► requirement_details: với mỗi yêu cầu JD → độ phủ, trọng số attention, mục CV khớp nhất  (đọc từ chính mô hình)
  ─► recruiter_summary: kết luận + đáp ứng / chưa thấy + lưu ý số năm, cấp độ (song ngữ)
```

---

## Kiến trúc

### Engine `req`: đồ thị mức yêu cầu (`src/representation/req_graph.py`, `src/modeling/req_model.py`)

**Nút**
- `req`: mỗi yêu cầu của JD, gồm embedding, loại (one-hot 5 loại: hard_skill, soft_skill, education, role, industry), cờ bắt buộc/ưu tiên và số năm tối thiểu.
- `item`: mỗi mục ứng viên thực sự có trong CV, gồm embedding, loại và số năm.
- `spec`: 4 nút cố định (cấp độ JD, cấp độ CV, số năm JD, số năm CV).

**Cạnh**
- `req → item` cùng loại, giữ top-3 theo cosine; thuộc tính cạnh là giá trị cosine.
- `spec → spec`, thuộc tính là khoảng thiếu `max(0, JD − CV)`.

**Tính điểm**
1. Mỗi cạnh được chấm bằng một MLP trên [h_req, h_item, h_req ⊙ h_item, cos], cộng đường tắt cosine.
2. **Độ phủ của từng yêu cầu** là MAX điểm cạnh của yêu cầu đó.
3. Tổng hợp **có trọng số attention** (softmax trong từng JD, có biết cờ bắt buộc/ưu tiên).
4. **Phạt đơn điệu** khi CV thấp hơn JD về cấp độ hoặc số năm.

**Cấu hình triển khai** `main_pairbce` dùng kiến trúc `pair_skip_mlp_specfeat` (lớp truyền tin = 0, tốt nhất trên validation), huấn luyện bằng loss **pairwise + BCE**. Thêm 1–3 lớp GATv2 (`abl_L1..3`) không cải thiện, nên tín hiệu chính đến từ **cấu trúc khớp yêu cầu – mục** chứ không từ truyền tin nhiều bước. Báo cáo cần nêu rõ điều này.

### Engine `gcn`: đồ thị 14 nút theo bài báo (`graph_builder.py`, `model.py`)

```
        [Soft Skills]──┐                  ┌──[Soft Skills]
       [Hard Skills]───┤                  ├───[Hard Skills]
         [Education]───┤                  ├───[Education]
  [Field of Education]─┼──[Candidate]────[JD]──┼─[Field of Education]
    [Industry Sector]──┤                  ├──[Industry Sector]
              [Role]───┘                  └───[Role]
```

- **Nút:** 2 nút trung tâm và 12 nút thực thể. Mỗi nút thực thể gộp một nhóm bằng DeepSets (mean/sum/max của embedding MiniLM, 1152 chiều).
- **Cạnh:** star (trọng số `ENTITY_WEIGHTS`), cầu, cạnh chéo giữa thực thể cùng loại, và k-NN ($k=10$, $p=4$).
- **Mô hình:** 3 lớp `GCNConv` có residual, readout [h_c, h_jd, h_c − h_jd, h_c ⊙ h_jd], rồi MLP.
- **Hybrid:** $\tilde s_{SBERT}$ là cosine giữa embedding **chuỗi thực thể ghép** của CV và JD (nút 0 và 1, không phải toàn văn), chuẩn hóa min–max; **α = 0,3**.

**Yếu điểm đã biết** (và là lý do chuyển sang engine `req`):
- Gộp mỗi loại thành một vector nên mất độ phủ từng yêu cầu.
- Với $k=10$ trên 14 nút, đồ thị gần như đầy đủ.
- Không thấy số năm và cấp độ.
- Diễn giải tách khỏi điểm.

---

## Cách backend dùng

```python
from src.inference.predict import CJMPredictor

predictor = CJMPredictor()                     # engine "req" nếu có models/req_model.pt, ngược lại "gcn"
results = [(cv["id"], predictor.predict_from_text(cv["text"], jd_text)) for cv in cv_list]
ranked = sorted(results, key=lambda t: t[1]["score"], reverse=True)
```

**Khóa kết quả chung:** `score` (0–1, dùng để xếp hạng), `grade` / `grade_label` (0–3), `label` (MATCH nếu mức ≥ 2), `explanation` (`{"vi", "en"}`), `engine`.

- **Engine `req`:**
  - `requirements`: danh sách {`text`, `type`, `required`, `met`, `coverage`, `weight`, `best_match`}, khớp với điểm vì cùng lấy từ mô hình.
  - `cv_requirements`, `jd_requirements`: kết quả trích xuất.
  - Không tốn lời gọi LLM nào ngoài trích xuất (mỗi văn bản một lần nhờ cache).
- **Engine `gcn`:** `gcn_score`, `semantic_score`, `llm_requirements`, `llm_conditions`, `explanation_detail`, `entity_match`, `gcn_attribution`. Diễn giải tốn 1 lời gọi Gemini cho mỗi cặp.

**PDF scan:** engine `req` cần văn bản, nên báo lỗi với PDF scan. Khi đó dùng `CJMPredictor(engine="gcn")`, engine này đọc được bằng Gemini Vision.

---

## Bộ dữ liệu

| Thành phần | Nguồn | Quy mô |
|:---|:---|:---|
| **CV** (`data/raw/cvs_synth/`) | Tổng hợp bằng ChatGPT: 13 nhóm nghề × 4 cấp (Fresher/Junior/Middle/Senior) × 2 CV | 104 |
| **JD** (`data/raw/selected_jds.csv`) | Thật, từ [VietJobs](https://huggingface.co/datasets/dinhieufam/VietJobs) ngành CNTT, chọn theo cụm và nhóm nghề (cột `jd_brief`) | 159 |
| **Cặp và nhãn** (`data/raw/pairs_labeled.csv`) | Mỗi CV ghép với khoảng 16 JD (cùng nhóm, liền kề, khác khối CNTT, ngoài CNTT); nhãn theo rubric 4 đặc trưng (vai trò, độ phủ yêu cầu bắt buộc, lệch cấp, điều kiện cứng) | 1664 cặp: mức 0: 429 · 1: 812 · 2: 256 · 3: 167 |

| Mức | Tên | Ý nghĩa |
|:---:|:---|:---|
| 3 | Phù hợp tốt | Cùng vai trò, đáp ứng phần lớn yêu cầu bắt buộc, đủ cấp độ |
| 2 | Phù hợp một phần | Đáng cân nhắc nhưng thiếu yêu cầu quan trọng hoặc lệch cấp |
| 1 | Liên quan ngành | Cùng ngành/vai trò nhưng thiếu phần lớn yêu cầu |
| 0 | Không phù hợp | Khác hẳn lĩnh vực |

Nhãn đo **năng lực làm được việc**: ứng viên dư kinh nghiệm không bị trừ điểm. Kiểm chứng mù trên 36 cặp (một người chấm độc lập) cho kết quả:
- khớp chính xác 86,1%, trong phạm vi ±1 mức 100%;
- kappa trọng số bình phương 0,94 [0,87–0,99].

---

## Kết quả

Chiều chính là **mỗi JD xếp hạng các CV**. Cách chia dữ liệu quyết định độ lạc quan của kết quả, nên báo cáo ba cách chia (điểm out-of-fold, bootstrap theo truy vấn):

| Cách chia | CV mới? | JD mới? | NDCG@5 Hybrid (α = 0,3) | NDCG@5 SBERT cosine |
|:---|:---:|:---:|:---:|:---:|
| Theo CV | có | không | 0,82 | 0,83 |
| Theo JD | không | có | 0,85 | 0,83 |
| **Loại trừ cả hai** | có | có | 0,89 | 0,89 |

**Cách chia loại trừ cả hai** (187 truy vấn, GCN 3 seed) đại diện cho triển khai thật: ứng viên mới, tin tuyển dụng mới. Mỗi lượt chỉ huấn luyện trên khoảng 666 cặp, và danh sách ngắn (khoảng 5 CV) nên NDCG cao hơn các bảng khác; chỉ so sánh trong cùng bảng:

| Phương pháp | NDCG@5 | NDCG@10 | MRR | AUC |
|:---|:---:|:---:|:---:|:---:|
| TF-IDF + cosine | 0,877 | 0,901 | 0,835 | 0,778 |
| SBERT + cosine | **0,889** | **0,910** | **0,854** | 0,783 |
| MLP trên SBERT | 0,861 | 0,886 | 0,822 | 0,774 |
| GCN đơn | 0,832 | 0,864 | 0,781 | 0,722 |
| Hybrid (α chọn theo validation, TB 0,54) | 0,881 | 0,904 | 0,849 | 0,784 |
| **Hybrid (α = 0,3, engine `gcn`)** | **0,890** | **0,911** | **0,857** | **0,802** |

**Engine `req`** (`train_req.py final`, 5 fold theo JD, 1 seed, chấm trên tập kiểm tra):

| Hàm mất mát (cùng kiến trúc) | NDCG@10 | Mức 0–3 macro-F1 | Khớp chính xác |
|:---|:---:|:---:|:---:|
| Pairwise (RankNet) | 0,889 | 0,337 | 39,8% |
| BCE | 0,880 | 0,383 | 44,2% |
| **Pairwise + BCE (triển khai, `main_pairbce`)** | **0,887–0,891** | **0,423** | **49,6%** |

- Hai dòng đầu fit ngưỡng trên tập validation của từng mô hình. Dòng cuối fit ngưỡng trên điểm out-of-fold gộp, cross-fit theo fold.
- Loss pairwise chỉ so sánh CV **trong cùng một JD**, nên điểm của hai JD khác nhau không cùng thang. Vì vậy xếp hạng tốt nhưng quy ra mức 0–3 (thang tuyệt đối) lại kém. Thêm BCE neo thang điểm chung mà không làm giảm NDCG.
- Không so trực tiếp macro-F1 này với 0,535 của engine `gcn`: con số đó dùng cách chia theo CV, dễ hơn vì JD đã được thấy lúc huấn luyện.
- Bảng đầy đủ theo seed và ablation: `python src/modeling/train_req.py jd|double --seeds 5` (ghi vào `report/results/`).

**Chiều ứng viên** (mỗi CV xếp hạng các JD, chia theo CV, 104 CV; chiều phụ):
- NDCG@10: TF-IDF 0,79 · SBERT 0,79 · MLP 0,89 · GCN 0,85 · Hybrid 0,85.
- Phân loại "phù hợp" (mức ≥ 2): F1 Hybrid 0,60 (GCN 0,58, SBERT 0,55); AUC 0,84 (GCN 0,82, SBERT 0,78).

**Đọc kết quả thận trọng**
- Với ứng viên và JD mới, engine `gcn` **chỉ ngang** SBERT cosine thuần (NDCG@5 0,890 so với 0,889), còn GCN đơn kém hơn (0,832); khoảng tin cậy chồng nhau.
- Điểm Hybrid chỉ giải thích khoảng 54% biến thiên của nhãn, trong khi 7 đặc trưng rubric giải thích 99%. Trong cùng vai trò, tách mức 3 khỏi mức 2 bằng độ phủ yêu cầu thật đạt AUC 0,94, còn Hybrid chỉ đạt 0,64. Thông tin còn thiếu là độ phủ yêu cầu và lệch cấp độ, nên mới có engine `req`.
- Dao động giữa các lần huấn luyện khoảng ±0,01 NDCG và ±0,015 AUC; không nên diễn giải các chênh lệch nhỏ hơn mức này.

### Hạn chế

- Nhãn do một người chấm theo rubric (đã kiểm mù), nên mô hình học bắt chước rubric. Engine `req` mô hình hóa đúng các đặc trưng của rubric, vì vậy cần **kiểm định ngoài** với nhãn độc lập (`train_ext.py`, các bộ dữ liệu công khai) trước khi khẳng định khả năng tổng quát.
- CV là dữ liệu tổng hợp; mỗi JD xuất hiện ở nhiều CV. Danh sách CV của mỗi JD không được thiết kế (trung bình khoảng 10 CV).
- Engine `req`: một yêu cầu được coi là "đáp ứng" khi độ phủ > 0,5, nhưng ngưỡng này chưa được hiệu chỉnh trên nhãn của từng yêu cầu. Kết quả thử còn khớp nhầm, ví dụ "Có laptop" ↔ "User Story". Cần gán nhãn đáp ứng/không cho một mẫu yêu cầu rồi fit ngưỡng.
- Attention của ReqGNN thường dồn trọng số vào yêu cầu *ưu tiên* hơn là *bắt buộc*: mô hình học theo nhãn, không theo ý nghĩa nghiệp vụ. Nên thử ràng buộc trọng số bắt buộc ≥ ưu tiên.
- Mức 0–3 của engine `req` (khớp chính xác khoảng 50%) chỉ để đọc nhanh; xếp hạng nên dùng `score`.

### Hướng cải tiến tiếp theo

1. Kiểm định ngoài trên dữ liệu thật (resume-job-description-fit, vacancy-resume-matching); thêm người chấm thứ hai; gán nhãn đủ mọi CV cho một số JD.
2. Lọc nhanh bằng embedding toàn văn rồi chấm kỹ top-N bằng ReqGNN (retrieve → rerank) khi số CV lớn.
3. Gộp các đặc trưng (ReqGNN, SBERT, độ phủ, lệch cấp, lệch số năm) bằng bộ xếp hạng LambdaMART; thay ngưỡng bằng hồi quy thứ bậc.
4. Nếu cần đóng góp "truyền tin" thật: dựng đồ thị toàn cục CV – kỹ năng – JD có taxonomy kỹ năng (ESCO/O*NET) với GraphSAGE/HGT inductive.
5. Kiểm tra thiên lệch: đổi tên, giới tính, trường học và đo xem điểm có thay đổi không.

---

## Cài đặt và cấu hình

Yêu cầu Python 3.10+ (đã chạy trên Python 3.12/3.13, Windows).

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

> **Lưu ý về cache**
> - Cache trích xuất (`entity_cache.json`, `req_cache.json`) khóa theo nội dung văn bản và phiên bản prompt, **không theo model**. Vì vậy văn bản đã có trong cache luôn dùng kết quả cũ.
> - Lần chạy đầu sẽ tải MiniLM và BGE-M3 (khoảng 2,2 GB) từ Hugging Face.
> - Trên Windows nên chạy `python -X utf8 ...`.

---

## Hướng dẫn chạy

```bash
# Engine req (mặc định). Kết quả trích xuất cho bộ dữ liệu đã có sẵn trong data/cache/req_cache.json,
# nên không cần khóa API để huấn luyện.
python -X utf8 src/modeling/train_req.py final                       # → models/req_model.pt (kèm ngưỡng mức 0–3)
python -X utf8 src/modeling/train_req.py jd --seeds 5 --configs pair_skip_mlp_specfeat   # đánh giá; "double" = loại trừ cả CV và JD
python -X utf8 src/modeling/train_ext.py --protocol jd --configs pair_skip_mlp_specfeat  # bộ ngoài (cần data/raw/cnamuangtoun/)

# Engine gcn (baseline theo bài báo)
python -X utf8 main.py --mode prepare                    # dựng đồ thị 14 nút (gọi Gemini, có cache)
python -X utf8 src/modeling/train.py --cv 5              # CV 5 fold theo CV, baseline, điểm out-of-fold
python -X utf8 src/modeling/train.py --patience 20       # GCN cuối → models/best_model.pt
python -X utf8 src/evaluation/fit_hybrid.py --alpha 0.3  # Hybrid + ngưỡng mức

# Dự đoán một cặp
python -X utf8 src/inference/predict.py --cv examples/cv_example.txt --jd examples/jd_example.txt [--engine gcn]
python -X utf8 main.py --mode predict                    # chế độ tương tác

# Kiểm tra
python -X utf8 tests/test_dataset_labels.py
python -X utf8 tests/test_pair_features.py
python -X utf8 tests/test_entity_extractor.py
python -X utf8 tests/test_explain.py
```

### Chạy trên Kaggle

Dùng notebook [`kaggle/cjm_kaggle.ipynb`](kaggle/cjm_kaggle.ipynb):
1. Push code lên GitHub, kể cả `models/req_model.pt`.
2. Trên Kaggle chọn *Create → Notebook → File → Import Notebook* rồi tải file này lên.
3. Bật *GPU T4* và *Internet*.
4. Sửa `BRANCH` trong cell đầu cho đúng nhánh, rồi chọn *Run All*.

Notebook tự clone repo vào `/kaggle/working`, cài `torch_geometric`, tải hai bộ dữ liệu ngoài vào đúng đường dẫn mà code cần, sau đó chạy `final`, đánh giá `jd`/`double` và kiểm định ngoài. Kết quả được gom vào `cjm_outputs.zip` ở tab *Output*. Không cần khóa Gemini, vì kết quả trích xuất của mọi bộ dữ liệu đã có trong `req_cache.json`. Repo private thì thêm secret `GITHUB_TOKEN`.

### Ví dụ diễn giải (`result["explanation"]["vi"]`)

```
Kết luận: Phù hợp một phần (mức 2/3), đáng cân nhắc, cần làm rõ các điểm còn thiếu.
Đáp ứng (5/8 yêu cầu bắt buộc): Unity, C#, OOP, data structures, algorithms.
Chưa thấy trong CV: multiplayer technologies, Game performance optimization, ...
Cần lưu ý: JD yêu cầu tối thiểu 1 năm kinh nghiệm, CV chưa có kinh nghiệm liên quan; JD tuyển cấp junior, CV ở cấp fresher.
```

Với engine `req`, danh sách đáp ứng và chưa thấy lấy từ độ phủ từng yêu cầu của chính ReqGNN, nên **khớp với điểm**. Bản kỹ thuật in bằng `--engine req`: mỗi yêu cầu kèm độ phủ, trọng số và mục CV khớp nhất.

---

## Cấu trúc thư mục

```
├── main.py                       # Điều hướng các chế độ chạy
├── config.py                     # Tham số mô hình, đường dẫn, Gemini
├── src/
│   ├── data_collection/          # prepare_training_data.py (đồ thị 14 nút), extract_requirements_all.py, extract_external.py
│   ├── extraction/               # entity_extractor.py (6 loại thực thể), requirement_extractor.py (mức yêu cầu), pair_features.py
│   ├── representation/           # graph_builder.py + embedding_generator.py (14 nút), req_graph.py (mức yêu cầu, BGE-M3)
│   ├── modeling/                 # model.py + train.py (GCN), req_model.py + train_req.py (ReqGNN), train_ext.py, train_vk.py
│   ├── evaluation/               # metrics, baselines, hybrid, fit_hybrid, calibrate_thresholds
│   └── inference/                # predict.py (CJMPredictor, 2 engine), explain.py
├── data/
│   ├── raw/                      # cvs_synth/, selected_jds.csv, pairs_labeled.csv
│   ├── processed/                # cv_oof_predictions.csv, graphs/ (sinh ra, không commit)
│   └── cache/                    # entity_cache.json, req_cache.json, req_emb_*.npz (không commit)
├── models/                       # req_model.pt, best_model.pt, hybrid.json, grade_thresholds.json
├── examples/                     # cv_example.txt, jd_example.txt
└── tests/
```
