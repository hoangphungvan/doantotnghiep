# Hướng dẫn tạo và gán nhãn dữ liệu CV–JD (rubric v1)

Mục tiêu: có bộ cặp CV–JD với nhãn 0–3 tái lập được, đủ bằng chứng để bảo vệ trước hội đồng.

**Nguyên tắc bắt buộc**
1. Rubric này chốt trước khi chấm. Nếu sửa rubric, phải chấm lại toàn bộ và ghi số phiên bản (v1, v2...).
2. CV sinh **độc lập với JD** (Prompt A và B không được nhắc tới bất kỳ JD nào). Nếu không, nhãn bị "nướng" vào lúc sinh.
3. Nhãn dựa vào **nội dung** CV và JD, không dựa vào tên cụm trong `jd_clusters.csv` (cụm không đồng nhất, ví dụ cụm Java có lẫn JD quản lý dự án).
4. Lưu nguyên văn JSON ChatGPT trả về cho mọi lần chấm. Đó là bằng chứng.
5. Mở **chat mới cho mỗi CV** để các CV không ảnh hưởng lẫn nhau.

---

## 1. Rubric 0–3

Giữ nguyên tên 4 mức để khớp `config.GRADE_LABELS` trong code. Phần thay đổi là **định nghĩa có thể đo được**.

| Mức | Tên | Ý nghĩa thực tế |
|---|---|---|
| 3 | Phù hợp tốt | Có thể mời phỏng vấn ngay: đúng vai trò, đáp ứng phần lớn yêu cầu bắt buộc, đúng cấp độ |
| 2 | Phù hợp một phần | Đáng cân nhắc nhưng thiếu một số yêu cầu quan trọng, hoặc lệch cấp độ |
| 1 | Liên quan ngành | Cùng ngành CNTT hoặc cùng vai trò nhưng thiếu phần lớn yêu cầu; có thể chuyển đổi sau đào tạo |
| 0 | Không phù hợp | Khác hẳn lĩnh vực, không có kỹ năng liên quan |

### 1.1. Bốn đặc trưng cần xác định cho mỗi cặp

- **role_match**
  - `same`: cùng nhóm vai trò (xem 1.2).
  - `adjacent`: khác nhóm vai trò nhưng cùng khối nghề hoặc hay chuyển đổi cho nhau (xem 1.2).
  - `different`: khối nghề khác (ví dụ lập trình viên so với kinh doanh, CNC, thiết kế đồ họa).
- **must_have_coverage_pct** (0–100): tỉ lệ yêu cầu bắt buộc của JD mà CV có bằng chứng.
  - Must-have = kỹ năng, công nghệ, chứng chỉ, ngoại ngữ trong "Yêu cầu" và "Kỹ năng chuyên môn". **Bỏ qua** các ý ghi "ưu tiên", "là một lợi thế", "nice to have".
  - CV có bằng chứng = kỹ năng được nêu hoặc được dùng trong phần kinh nghiệm. Công nghệ tương đương rõ ràng được tính (MSSQL ≈ SQL Server). Không suy diễn kỹ năng CV không nhắc tới.
  - Ngưỡng: **high** ≥ 70, **medium** 40–69, **low** < 40.
- **seniority_gap** = cấp JD − cấp CV (số nguyên).
  - Cấp: Fresher = 0 (dưới 1 năm, kể cả thực tập), Junior = 1 (1–2 năm), Middle = 2 (3–4 năm), Senior = 3 (từ 5 năm).
  - Cấp JD lấy từ "Kinh nghiệm" và nội dung (có "Senior", "Lead", "Trưởng nhóm" thì tăng một cấp).
  - **level_mismatch** = `seniority_gap ≥ 2` (JD cao hơn CV từ 2 cấp) **hoặc** `seniority_gap ≤ −3` (CV cao hơn JD từ 3 cấp).
- **hard_requirement_missing** (true/false): JD ghi **bắt buộc** một điều kiện cứng (bằng cấp, chứng chỉ, ngoại ngữ như tiếng Nhật N2, quyền làm việc) mà CV không có.

### 1.2. Nhóm vai trò

| Khối nghề | Nhóm vai trò (cùng nhóm = `same`) |
|---|---|
| Phát triển phần mềm | Backend · Frontend · Fullstack · Mobile |
| Hạ tầng và vận hành | DevOps/Cloud · Sysadmin/Network/Security · IT Support |
| Chất lượng | QA/Tester |
| Dữ liệu | Data Analyst · Data Engineer/ML-AI |
| Phân tích và quản lý | Business Analyst · PM/Product Owner |
| Thiết kế | UI/UX và Graphic Designer |

- Khác nhóm nhưng cùng khối nghề → `adjacent`.
- Cặp thường chuyển đổi cho nhau cũng là `adjacent`: QA ↔ Phát triển phần mềm, BA ↔ PM, Data Analyst ↔ Data Engineer.
- Còn lại → `different`.

### 1.3. Bảng quyết định (áp dụng theo thứ tự)

Ký hiệu: `M` = level_mismatch, `H` = hard_requirement_missing.

| role_match | coverage | Điều kiện | Mức |
|---|---|---|---|
| different | low | | 0 |
| different | medium / high | | 1 |
| same | high | không M, không H | **3** |
| same | high | có M hoặc có H | 2 |
| same | medium | không M, không H | 2 |
| same | medium | có M hoặc có H | 1 |
| same | low | | 1 |
| adjacent | high | không M, không H | 2 |
| adjacent | còn lại | | 1 |

**Khi phân vân giữa hai mức, chọn mức thấp hơn** (để chống xu hướng chấm dễ dãi của mô hình).

### 1.4. Ví dụ minh họa (không phải dữ liệu thật)

- CV Backend Java Middle (Spring Boot, Oracle, REST, Git) với JD Java Developer cần Spring Boot, Oracle, REST API, Docker, 3 năm: role `same`, coverage 3/4 = 75% (thiếu Docker), gap 0, không H → **3**. (Nếu JD chỉ có 3 must-have thì thiếu Docker còn 67% = medium → mức 2; luôn đếm đúng số must-have.)
- CV Frontend React Junior với JD Java Backend: role `adjacent`, coverage khoảng 10% → **1**.
- CV Data Analyst Junior với JD Nhân viên kinh doanh yêu cầu tiếng Nhật N2: role `different`, coverage thấp → **0**.
- CV Backend Java Fresher với JD Java Senior 5 năm: role `same`, coverage cao nhưng gap = 3 (có M) → **2**.

---

## 2. Cơ cấu CV cần sinh

13 nhóm vai trò × 4 cấp độ × 2 CV = **104 CV**.

| Mã | Nhóm vai trò | | Mã | Nhóm vai trò |
|---|---|---|---|---|
| BE | Backend | | QA | QA/Tester |
| FE | Frontend | | DA | Data Analyst |
| FS | Fullstack | | DE | Data Engineer/ML-AI |
| MOB | Mobile | | BA | Business Analyst |
| DEVOPS | DevOps/Cloud | | PM | PM/Product Owner |
| SYS | Sysadmin/Network/Security | | DES | UI/UX và Graphic Designer |
| SUP | IT Support | | | |

Mã cấp: `FRE` (Fresher), `JUN`, `MID`, `SEN`. Ví dụ `BE_JUN_01`.

Chạy Prompt A **13 lần** (mỗi nhóm một lần, 8 hồ sơ: 2 cho mỗi cấp).

---

## 3. Prompt A: sinh hồ sơ ứng viên (chưa phải CV)

Thay `{ROLE_FAMILY}` và `{CODE}`. Dán vào chat mới.

````text
Bạn đang giúp tôi xây dựng bộ dữ liệu hồ sơ ứng viên CNTT tại Việt Nam cho một đồ án nghiên cứu.

Hãy tạo 8 hồ sơ ứng viên (chưa phải CV) cho nhóm vai trò: {ROLE_FAMILY}, mã nhóm {CODE}.
Phân bổ: 2 Fresher (FRE), 2 Junior (JUN), 2 Middle (MID), 2 Senior (SEN).

Quy tắc:
- Số năm kinh nghiệm phải khớp cấp độ: Fresher dưới 1 năm (kể cả thực tập), Junior 1-2 năm, Middle 3-4 năm, Senior từ 5 năm.
- Phản ánh thị trường Việt Nam. Mỗi hồ sơ dùng bộ công nghệ khác nhau; không lặp cùng một bộ công nghệ quá 2 lần.
- Mỗi hồ sơ có 1-3 khoảng trống kỹ năng thực tế (ví dụ chưa dùng cloud, chưa có chứng chỉ). Không ai biết đủ mọi thứ.
- Khoảng 2/8 hồ sơ là người chuyển ngành hoặc đi lên từ vai trò khác. Khoảng 2/8 hồ sơ có kinh nghiệm thực tế mỏng so với cấp độ.
- KHÔNG nhắm tới bất kỳ tin tuyển dụng cụ thể nào và không nhắc tới JD.
- Dùng tên hư cấu; không dùng thông tin cá nhân thật.

Chỉ trả về MỘT mảng JSON, không thêm lời dẫn. Mỗi phần tử có đúng các khóa:
{
  "profile_id": "{CODE}_<FRE|JUN|MID|SEN>_<01|02>",
  "role_family": "{ROLE_FAMILY}",
  "target_title": "chức danh ứng viên đang hướng tới",
  "seniority": "Fresher|Junior|Middle|Senior",
  "years_experience": <số>,
  "education": "bậc học, ngành, loại trường (không cần tên trường thật)",
  "core_skills": ["5-10 kỹ năng chính"],
  "secondary_skills": ["2-6 kỹ năng phụ"],
  "known_gaps": ["1-3 kỹ năng còn thiếu"],
  "languages": ["ngoại ngữ và mức độ"],
  "industries": ["lĩnh vực đã làm"],
  "career_note": "một câu về lộ trình (chuyển ngành, thăng tiến, ...)",
  "cv_style": "chuẩn|ngắn gọn|dài dòng|lẫn Anh-Việt|có lỗi chính tả nhẹ"
}
````

Lưu mỗi kết quả thành `data/raw/profiles/{CODE}.json` (giữ nguyên văn).

---

## 4. Prompt B: sinh CV từ hồ sơ

Mỗi lần dán 3 hồ sơ (một phần tử mảng JSON mỗi hồ sơ). Dán vào chat mới.

````text
Dựa trên các hồ sơ JSON bên dưới, hãy viết CV dạng văn bản thuần như một ứng viên Việt Nam thật sự tự viết. Mỗi hồ sơ viết thành một CV.

Quy tắc:
- Cấu trúc: THÔNG TIN LIÊN HỆ (tên hư cấu, email dạng ten@example.com, thành phố), MỤC TIÊU NGHỀ NGHIỆP, HỌC VẤN, KỸ NĂNG CHUYÊN MÔN, KỸ NĂNG MỀM, KINH NGHIỆM LÀM VIỆC (công ty hư cấu hoặc phổ biến, thời gian, 2-4 gạch đầu dòng mô tả việc làm có kết quả cụ thể), DỰ ÁN (nếu có), CHỨNG CHỈ (nếu có).
- Độ dài 250-450 từ. Văn phong theo trường cv_style. Giữ thuật ngữ kỹ thuật bằng tiếng Anh như CV Việt Nam thật.
- CHỈ dùng thông tin trong hồ sơ. Không bịa thêm kỹ năng ngoài core_skills và secondary_skills.
- known_gaps: KHÔNG nhắc tới các kỹ năng này, cũng không viết "chưa biết".
- Tổng thời gian các công việc phải khớp years_experience.
- KHÔNG ghi CV phù hợp vị trí nào, không nhắc tới tin tuyển dụng, không thêm nhận xét của AI.

Mỗi CV bắt đầu bằng đúng một dòng:
=== CV: <profile_id> ===
rồi tới nội dung CV. Không có lời dẫn hay kết luận.

HỒ SƠ:
<dán 3 hồ sơ JSON ở đây>
````

Lưu mỗi CV thành `data/raw/cvs_synth/<profile_id>.txt`.

---

## 5. Prompt C: chấm mức phù hợp (trả JSON)

Mở chat mới cho **mỗi CV**. Dán 10-12 JD mỗi lần (cột `jd_brief` trong `data/raw/selected_jds.csv`, kèm `jd_id`). Lần chấm thứ hai trên mẫu kiểm tra: **đảo thứ tự JD**.

````text
Bạn là chuyên viên tuyển dụng CNTT tại Việt Nam. Hãy đánh giá mức độ phù hợp của MỘT CV với TỪNG JD trong danh sách, theo rubric v1 dưới đây. Đánh giá từng JD độc lập; không so sánh các JD với nhau.

RUBRIC v1
Mức: 3 = Phù hợp tốt | 2 = Phù hợp một phần | 1 = Liên quan ngành | 0 = Không phù hợp.

Với MỖI JD, làm đúng theo thứ tự:
1. Xác định must-have: kỹ năng, công nghệ, chứng chỉ, ngoại ngữ trong "Yêu cầu" và "Kỹ năng chuyên môn". BỎ QUA các ý ghi "ưu tiên", "là một lợi thế", "nice to have".
2. role_match:
   - same: cùng nhóm vai trò. Nhóm: Backend; Frontend; Fullstack; Mobile; DevOps/Cloud; Sysadmin/Network/Security; IT Support; QA/Tester; Data Analyst; Data Engineer/ML-AI; Business Analyst; PM/Product Owner; UI/UX-Graphic Designer.
   - adjacent: khác nhóm nhưng cùng khối nghề (Phát triển phần mềm; Hạ tầng và vận hành; Dữ liệu; Phân tích và quản lý; Thiết kế), hoặc cặp hay chuyển đổi: QA <-> lập trình, BA <-> PM, Data Analyst <-> Data Engineer.
   - different: còn lại.
3. must_have_coverage_pct (0-100): tỉ lệ must-have mà CV CÓ BẰNG CHỨNG (nêu trong kỹ năng hoặc dùng trong kinh nghiệm). Công nghệ tương đương rõ ràng được tính (MSSQL ~ SQL Server). Không suy diễn kỹ năng CV không nhắc tới. high >= 70, medium 40-69, low < 40.
4. cv_level và jd_level: Fresher (dưới 1 năm), Junior (1-2 năm), Middle (3-4 năm), Senior (từ 5 năm). Cấp JD lấy từ "Kinh nghiệm" và nội dung (có Senior/Lead/Trưởng nhóm thì tăng một cấp). seniority_gap = số cấp của JD trừ số cấp của CV (Fresher=0, Junior=1, Middle=2, Senior=3).
   level_mismatch = (seniority_gap >= 2) HOẶC (seniority_gap <= -3).
5. hard_requirement_missing: true nếu JD ghi BẮT BUỘC một điều kiện cứng (bằng cấp, chứng chỉ, ngoại ngữ như tiếng Nhật N2...) mà CV không có.
6. grade theo bảng, áp dụng theo thứ tự:
   - different + coverage low -> 0
   - different + coverage medium/high -> 1
   - same + high + không mismatch + không hard_missing -> 3
   - same + high + (mismatch hoặc hard_missing) -> 2
   - same + medium + không mismatch + không hard_missing -> 2
   - same + medium + (mismatch hoặc hard_missing) -> 1
   - same + low -> 1
   - adjacent + high + không mismatch + không hard_missing -> 2
   - adjacent + các trường hợp còn lại -> 1
   Khi phân vân giữa hai mức, chọn mức THẤP hơn.
7. reason: tối đa 25 từ, nêu cụ thể kỹ năng đã khớp hoặc còn thiếu.

BỎ QUA: tên, giới tính, tuổi, độ dài hay văn phong của CV, tên trường và tên công ty.

ĐẦU RA: chỉ trả MỘT mảng JSON, mỗi JD một phần tử, giữ nguyên jd_id, không có chữ nào ngoài JSON:
[
  {
    "jd_id": "jd_0105",
    "role_match": "same|adjacent|different",
    "must_have_coverage_pct": 0,
    "cv_level": "Fresher|Junior|Middle|Senior",
    "jd_level": "Fresher|Junior|Middle|Senior",
    "seniority_gap": 0,
    "hard_requirement_missing": false,
    "grade": 0,
    "reason": "..."
  }
]

CV:
<dán nội dung CV>

DANH SÁCH JD:
[jd_id: jd_xxxx]
<dán jd_brief>

[jd_id: jd_yyyy]
<dán jd_brief>
...
````

Lưu mỗi kết quả thành `data/raw/judgments/<profile_id>_run1.json` (và `_run2.json` cho lần chấm thứ hai).

---

## 6. Quy trình và kiểm chứng

1. Sinh 104 hồ sơ (Prompt A) → 104 CV (Prompt B). Đọc lướt vài CV để chắc không lộ tên vị trí hoặc "nhận xét AI".
2. JD: `python src/data_collection/select_jds.py` (180 JD thật, 9 JD mỗi cụm).
3. Ghép mỗi CV với khoảng 15 JD gồm: vài JD cùng nhóm, vài JD khác cấp độ, vài JD nhóm liền kề, vài JD khác khối nghề. Kế hoạch ghép sẽ được làm thành script ở bước tiếp theo.
4. Chấm bằng Prompt C. Chạy lần hai (đảo thứ tự JD) trên khoảng 25% số CV để đo độ nhất quán của chính ChatGPT.
5. **Kiểm chứng bằng người** (bắt buộc): chấm mù 60-100 cặp phân tầng theo mức, chưa xem nhãn AI. Tính kappa có trọng số giữa bạn và ChatGPT; từ khoảng 0,6 trở lên là chấp nhận được.
6. Kiểm tra ngược: từ các đặc trưng ChatGPT trả về, tính lại mức theo bảng 1.3 và đếm số cặp ChatGPT tự mâu thuẫn với bảng. Cặp mâu thuẫn cần xem lại bằng tay.
7. Ghi vào luận văn: phiên bản rubric, số cặp, kappa, tỉ lệ nhãn bị sửa, và giới hạn (CV tổng hợp, nhãn do LLM chấm có kiểm chứng).

### Gợi ý ngành cho 20 cụm JD

Tên cụm trong `jd_clusters.csv` do thuật toán tự đặt nên bị cắt lệch. Bảng dưới là gợi ý của tôi suy từ tên cụm, **chưa kiểm tra từng JD**; hãy xem tiêu đề JD trong `selected_jds.csv` trước khi dựa vào.

| Cụm | Gợi ý nhóm | | Cụm | Gợi ý nhóm |
|---|---|---|---|---|
| 0 | Kinh doanh | | 10 | QA/Tester |
| 1 | CNC/cơ khí | | 11 | Sysadmin/VoIP |
| 2 | Backend/DevOps (Python, Docker, K8s) | | 12 | Kinh doanh/hành chính |
| 3 | Thiết kế đồ họa | | 13 | 3D/Game art |
| 4 | Kinh doanh | | 14 | Data Analyst |
| 5 | IT Support | | 15 | Mobile |
| 6 | Backend Java | | 16 | Marketing/Ads |
| 7 | Dựng video/audio | | 17 | Sysadmin/Network/Storage |
| 8 | Frontend | | 18 | BA/Product |
| 9 | UI/UX và Graphic | | 19 | PM/BA |
