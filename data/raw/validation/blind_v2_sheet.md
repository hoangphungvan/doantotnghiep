# Phiếu chấm mù v2 — kiểm chứng chính thức

**Cách chấm (rubric v1.2)** — với mỗi cặp CV–JD, xác định 4 điều rồi tra bảng; chấm độc lập, không trao đổi với người khác:

1. **Vai trò**: *cùng nhóm* (vd Backend với Backend) / *liền kề* (cùng khối nghề: Backend-Frontend-Fullstack-Mobile-QA; DevOps-Sysadmin-IT Support; Data Analyst-Data Engineer; BA-PM; UI/UX-đồ họa) / *khác khối*.
2. **Độ phủ yêu cầu bắt buộc** của JD (bỏ qua ý "ưu tiên/là lợi thế"): *cao* ≥ 70% · *vừa* 40–69% · *thấp* < 40%. Sát ngưỡng thì chọn phía thấp. Chỉ tính kỹ năng CV có bằng chứng.
3. **Lệch cấp độ**: Fresher (<1 năm) · Junior (1–2) · Middle (3–4) · Senior (≥5). **Chỉ tính là lệch khi JD cao hơn CV từ 2 cấp** (CV thiếu kinh nghiệm). CV cao hơn JD (thừa kinh nghiệm) **không bị hạ điểm**: nhãn đo năng lực làm được việc, không đoán khả năng ứng viên bỏ đi.
4. **Điều kiện cứng** JD ghi bắt buộc mà CV không có (bằng cấp, chứng chỉ, ngoại ngữ có mức cụ thể, tình trạng sinh viên, yêu cầu gửi CV tiếng Anh, ...; không tính tuổi/giới tính), và **công nghệ trong tiêu đề JD** mà CV hoàn toàn không có.

| Vai trò | Độ phủ | Điểm |
|---|---|---|
| khác khối | thấp | **0** |
| khác khối | vừa/cao | **1** |
| cùng nhóm | cao, không lệch cấp, không thiếu điều kiện cứng | **3** |
| cùng nhóm | cao nhưng lệch cấp hoặc thiếu điều kiện cứng; hoặc vừa và ổn | **2** |
| cùng nhóm | vừa nhưng lệch cấp/thiếu điều kiện cứng; hoặc thấp | **1** |
| liền kề | cao, ổn | **2** |
| liền kề | các trường hợp còn lại | **1** |

Nếu JD có công nghệ trong tiêu đề mà CV không có thì **hạ 1 mức** (không dưới 1 với cùng nhóm/liền kề). Phân vân giữa hai mức thì chọn mức thấp hơn. Bỏ qua tên, tuổi, giới tính, văn phong CV.

Điền điểm vào file `blind_v2_labels.csv` (cột `human_grade`). Đừng xem thư mục `data/raw/judgments/` hay file `_KEY_*.csv`.


Có 40 cặp. Mỗi cặp độc lập; cùng một CV hoặc JD có thể xuất hiện lại, hãy đọc kỹ từng cặp, không lục lại các cặp trước. Đọc đầy đủ CV và JD trước khi chấm.


---

## P01

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi tốt nghiệp ngành Thống kê kinh tế và có 8 tháng thực tập phân tích dữ liệu Digital Marketing tại agency quảng cáo. Tôi muốn phát triển chuyên môn về Marketing Analytics, đặc biệt trong việc theo dõi hiệu quả chiến dịch, phân tích marketing funnel và trực quan hóa dữ liệu. Mục tiêu của tôi là nâng cao khả năng sử dụng SQL, BigQuery và Looker Studio để hỗ trợ việc đánh giá hoạt động marketing dựa trên số liệu.

HỌC VẤN

Cử nhân Thống kê kinh tế
Đại học công lập khối kinh tế.

Có nền tảng kiến thức về thống kê, xử lý và phân tích số liệu kinh tế.

KỸ NĂNG CHUYÊN MÔN

- Google Sheets, Microsoft Excel: Tổng hợp và xử lý bảng dữ liệu.
- SQL cơ bản, Google BigQuery cơ bản: Truy vấn dữ liệu phục vụ báo cáo.
- Looker Studio: Xây dựng dashboard trực quan.
- Google Analytics 4: Theo dõi dữ liệu marketing ở mức cơ bản.
- Marketing Funnel Analysis: Phân tích các giai đoạn trong phễu marketing.
- Data Cleaning, Data Visualization.
- Google Tag Manager cơ bản, Python pandas cơ bản.
- Canva; kiến thức lý thuyết về A/B Testing.

KỸ NĂNG MỀM

- Tổng hợp và trình bày thông tin marketing theo yêu cầu báo cáo.
- Phối hợp trong quá trình chuẩn bị dữ liệu đánh giá chiến dịch.
- Tiếng Việt: Bản ngữ.
- Tiếng Anh: B2, đọc hiểu tài liệu và giao tiếp công việc.

KINH NGHIỆM LÀM VIỆC

Marketing Data Analyst Intern
Công ty TNHH Truyền thông BlueWave
02/2026 – 10/2026 (8 tháng)

- Thu thập và tổng hợp dữ liệu từ các nền tảng marketing vào Google Sheets, tạo bảng dữ liệu phục vụ theo dõi chiến dịch.
- Hỗ trợ làm sạch và kiểm tra dữ liệu quảng cáo trước khi lập báo cáo.
- Sử dụng Looker Studio để trực quan hóa số liệu, hỗ trợ nhóm marketing đánh giá hiệu quả chiến dịch.
- Hỗ trợ tổng hợp thông tin theo marketing funnel và chuẩn bị báo cáo định kỳ cho người phụ trách.

DỰ ÁN

Báo cáo hiệu quả chiến dịch Digital Marketing

Tham gia nhóm tổng hợp dữ liệu quảng cáo từ nhiều nền tảng. Sử dụng Google Sheets để xử lý dữ liệu và Looker Studio để thể hiện kết quả. Công việc tập trung vào chuẩn bị dữ liệu, cập nhật báo cáo và hỗ trợ phân tích hiệu quả chiến dịch theo yêu cầu của nhóm.
```

### JD

```
Vị trí: Lập Trình Viên PHP Laravel Backend
Kinh nghiệm: 2 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: PHP, Laravel, MySQL, PostgreSQL, MongoDB, HTML, CSS, JavaScript, Git
Yêu cầu: Tối thiểu 2 năm kinh nghiệm làm việc với PHP, đặc biệt là Laravel Framework. Hiểu biết sâu về các kiến trúc RESTful API và cách triển khai chúng. Kinh nghiệm làm việc với hệ quản trị cơ sở dữ liệu (MySQL, PostgreSQL, hoặc MongoDB). Thành thạo HTML, CSS, JavaScript (ưu tiên có kinh nghiệm làm việc với các framework như Vue.js, ReactJS, React Native là điểm cộng). Hiểu biết về các công cụ quản lý mã nguồn như Git. Có khả năng phân tích, xử lý vấn đề và làm việc độc lập hoặc theo nhóm. Kỹ năng giao tiếp tốt, sẵn sàng học hỏi và tiếp thu công nghệ mới.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P02

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Có khoảng 1,6 năm kinh nghiệm DevOps tại công ty phát triển sản phẩm SaaS. Đã tham gia duy trì GitLab CI/CD pipeline, triển khai dịch vụ bằng Docker và Amazon ECS. Mong muốn tiếp tục phát triển chuyên môn về tự động hóa triển khai, quản lý hạ tầng AWS và tối ưu quy trình vận hành ứng dụng.

HỌC VẤN

Đại học tư thục tại TP. Hồ Chí Minh
Chuyên ngành: Kỹ thuật phần mềm
Trình độ: Đại học

KỸ NĂNG CHUYÊN MÔN

- Hệ thống: Linux Administration.
- CI/CD: GitLab CI/CD, Git.
- Container: Docker, Amazon ECS, AWS ECR.
- Infrastructure: Terraform.
- AWS: IAM, CloudWatch, Application Load Balancer, Secrets Manager.
- Scripting: Python Scripting, Shell Scripting.
- Database: MySQL.
- Ngoại ngữ: Tiếng Anh B2, đọc viết tài liệu kỹ thuật tốt, giao tiếp công việc cơ bản.

KỸ NĂNG MỀM

- Phối hợp với kỹ sư cấp cao trong việc thay đổi hạ tầng.
- Làm việc theo kế hoạch và tài liệu thiết kế có sẵn.
- Chủ động kiểm tra kết quả sau khi triển khai.
- Trao đổi các vấn đề kỹ thuật với thành viên trong nhóm.

KINH NGHIỆM LÀM VIỆC

Công ty TNHH Công nghệ CloudVista
Vị trí: DevOps Engineer
Thời gian: 03/2025 - 10/2026 (1 năm 7 tháng, xấp xỉ 1,6 năm)

- Duy trì GitLab CI/CD pipeline cho các dịch vụ SaaS, hỗ trợ tự động hóa quá trình build và triển khai ứng dụng.
- Đóng gói ứng dụng bằng Docker, quản lý image trên AWS ECR và hỗ trợ triển khai các service lên Amazon ECS.
- Sử dụng Terraform để thực hiện thay đổi tài nguyên AWS theo thiết kế được kỹ sư cấp cao phê duyệt.
- Theo dõi log và thông tin vận hành bằng Amazon CloudWatch, kiểm tra trạng thái dịch vụ sau mỗi lần cập nhật.

DỰ ÁN

Duy trì hạ tầng AWS cho ứng dụng SaaS

- Tham gia vận hành các service container trên Amazon ECS.
- Hỗ trợ cấu hình AWS IAM, Application Load Balancer và quản lý thông tin ứng dụng qua AWS Secrets Manager.
- Sử dụng Python và Shell Scripting để hỗ trợ các thao tác vận hành lặp lại.
- Kết quả: Duy trì quy trình triển khai cho các dịch vụ được phân công, thực hiện các thay đổi hạ tầng theo thiết kế và kiểm tra kết quả sau triển khai.
```

### JD

```
Vị trí: Chuyên Viên Vận Hành Hệ Thống Microsoft Exchange Hybrid
Kinh nghiệm: 2 năm
Học vấn: College degree or bachelor degree in IT
Kỹ năng chuyên môn: Microsoft Exchange, Azure AD, SharePoint, Teams, email protocols, Cloud platforms, Azure, Azure DevOps, Docker, Kubernetes, CI/CD tools, Jenkins, GitLab
Yêu cầu: College degree or bachelor degree in IT. Minimum 2 years of experience operating Microsoft Exchange hybrid or on-premises systems. In-depth knowledge of Microsoft Exchange, Azure AD, SharePoint, Teams, and email protocols. Strong troubleshooting, analytical, and teamwork skills. Nice to have: Experience with Cloud platforms, especially Azure and Azure DevOps. Familiarity with Docker, Kubernetes, and CI/CD tools (Jenkins, GitLab, etc.). Good English communication skills.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P03

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi xuất phát từ background Graphic Design và chuyển sang Frontend Development sau khi hoàn thành khóa đào tạo lập trình web. Với 1,8 năm kinh nghiệm làm React Developer trong lĩnh vực thương mại điện tử, tôi muốn tiếp tục phát triển theo hướng xây dựng các sản phẩm web có giao diện tốt và trải nghiệm người dùng nhất quán. Thế mạnh của tôi là kết hợp tư duy thiết kế với khả năng implement UI bằng ReactJS, giúp chuyển thiết kế thành giao diện thực tế.

HỌC VẤN

Tốt nghiệp Đại học ngành Thiết kế đồ họa

Trường đại học tư thục

Đã hoàn thành khóa đào tạo lập trình Frontend, tập trung vào HTML5, CSS3, JavaScript ES6+ và ReactJS.

KỸ NĂNG CHUYÊN MÔN

- Frontend: HTML5, CSS3, JavaScript ES6+, ReactJS, React Hooks.
- Styling: Tailwind CSS, Responsive Web Design.
- UI Implementation: Chuyển thiết kế Figma thành giao diện web.
- Design tools: Figma nâng cao, Adobe Photoshop.
- Animation: Framer Motion cơ bản.
- Tools: Git, Axios, Vercel.
- Kiến thức bổ trợ: SEO cơ bản.

KỸ NĂNG MỀM

- Có khả năng phối hợp với team UI/UX trong quá trình phát triển giao diện.
- Trao đổi yêu cầu thiết kế và chuyển đổi thành các công việc implementation.
- Tiếng Anh B1, có thể đọc documentation và trao đổi các yêu cầu liên quan đến UI.

KINH NGHIỆM LÀM VIỆC

React Developer

Công ty Giải pháp Website Hưng Thịnh

Thời gian: 1,8 năm

Lĩnh vực: E-commerce, Digital Marketing, website doanh nghiệp

- Develop và maintain giao diện các website thương mại điện tử bằng ReactJS, JavaScript ES6+ và Tailwind CSS.
- Implement UI từ Figma design, sử dụng kiến thức Graphic Design để đảm bảo bố cục, khoảng cách và các thành phần giao diện bám sát thiết kế.
- Phối hợp cùng team UI/UX để điều chỉnh giao diện website, cải thiện cách hiển thị trên desktop và mobile thông qua Responsive Web Design.
- Sử dụng React Hooks và Axios trong quá trình phát triển giao diện, kết hợp Git để quản lý source code.

DỰ ÁN

Website thương mại điện tử

Tech stack: ReactJS, JavaScript ES6+, Tailwind CSS, Axios, Vercel.

Tham gia phát triển các phần giao diện cho website thương mại điện tử. Responsible for UI implementation, chỉnh sửa React components và đảm bảo giao diện hiển thị phù hợp với bản thiết kế.

Website giới thiệu doanh nghiệp

Tech stack: ReactJS, HTML5, CSS3, Figma, Framer Motion.

Tham gia xây dựng giao diện website doanh nghiệp, tập trung vào responsive layout, tính thẩm mỹ và việc thể hiện nội dung theo thiết kế. Vận dụng kiến thức SEO cơ bản khi triển khai nội dung giao diện.
```

### JD

```
Vị trí: Nhân Viên Kinh Doanh Phần Mềm - Website (Sales)
Kinh nghiệm: 1 năm
Học vấn: Cao Đẳng trở lên
Kỹ năng chuyên môn: Tin học văn phòng
Yêu cầu: Tối thiểu 6 tháng kinh nghiệm sales phần mềm, website hoặc các lĩnh vực khác liên quan. Năng động, nhiệt tình trong công việc. Khả năng giao tiếp, xây dựng quan hệ. Có laptop cá nhân. Thành thạo tin học văn phòng. Chủ động, ham học hỏi, lăn sả, máu chiến. Muốn thử thách bản thân với các nhiệm vụ khó.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P04

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có khoảng 1,6 năm kinh nghiệm làm Data Analysis trong lĩnh vực logistics và giao hàng. Công việc chính của tôi là xử lý dữ liệu vận hành, theo dõi delivery success rate, delivery time và xây dựng các báo cáo hỗ trợ đánh giá hoạt động giao nhận. Tôi muốn tiếp tục phát triển theo hướng Data Analytics, tập trung vào SQL, Python và Exploratory Data Analysis để khai thác dữ liệu hiệu quả hơn, đồng thời cải thiện chất lượng của các báo cáo vận hành.

HỌC VẤN

Cử nhân Công nghệ thông tin – Đại học tư thục.

Có kiến thức nền tảng về lập trình, cơ sở dữ liệu và xử lý thông tin.

KỸ NĂNG CHUYÊN MÔN

- Database: PostgreSQL.
- SQL: Sử dụng CTE, Window Functions để truy vấn, tổng hợp và phân tích dữ liệu.
- Python: pandas, NumPy để xử lý dữ liệu và thực hiện các bước phân tích.
- Data Visualization: Matplotlib, Seaborn, Metabase.
- Exploratory Data Analysis (EDA): Khám phá dữ liệu, tìm kiếm xu hướng và các điểm bất thường.
- Data Quality Validation: Kiểm tra tính hợp lệ và nhất quán của dữ liệu.
- Công cụ khác: Jupyter Notebook, Microsoft Excel, Git.
- REST API cơ bản, Basic Statistical Testing.

KỸ NĂNG MỀM

- Trình bày kết quả phân tích thông qua dashboard và biểu đồ.
- Chủ động xây dựng báo cáo vận hành theo các chỉ số được giao.
- Tiếng Việt: Bản ngữ.
- Tiếng Anh: B1, có khả năng đọc hiểu tài liệu kỹ thuật tốt hơn giao tiếp.

KINH NGHIỆM LÀM VIỆC

Data Analyst
Công ty TNHH Logistics Đông Nam
03/2025 – 10/2026 (1 năm 7 tháng)

- Phân tích dữ liệu giao nhận từ PostgreSQL, xây dựng SQL queries để tổng hợp delivery success rate và delivery time.
- Tự xây dựng báo cáo theo dõi tỷ lệ giao hàng thành công và thời gian giao nhận, cung cấp thông tin cho việc đánh giá hoạt động vận hành.
- Sử dụng Metabase để trình bày các chỉ số dưới dạng dashboard, giúp việc theo dõi dữ liệu thuận tiện hơn.
- Áp dụng Python pandas và NumPy cho một phần công việc Data Cleaning và tổng hợp dữ liệu, thay thế các thao tác xử lý thủ công trước đây.

DỰ ÁN

Delivery Performance Analytics

Thực hiện phân tích dữ liệu hiệu suất giao hàng, tập trung vào hai nhóm chỉ số: delivery success rate và delivery time.

Tôi sử dụng PostgreSQL và SQL để truy vấn dữ liệu, Python pandas để xử lý và Metabase để xây dựng dashboard. Bên cạnh đó, tôi thực hiện EDA bằng Matplotlib, Seaborn nhằm trực quan hóa kết quả phân tích.

Đầu ra là các báo cáo vận hành giúp theo dõi tỷ lệ giao thành công và thời gian giao nhận theo dữ liệu thực tế.
```

### JD

```
Vị trí: Chuyên gia phân tích hoạt động
Kinh nghiệm: 2 năm
Học vấn: Tốt nghiệp Đại học chuyên ngành Phân tích dữ liệu, Hệ thống thông tin, Toán thống kê, Kinh tế, hoặc các ngành liên quan
Kỹ năng chuyên môn: SQL, BigQuery, Metabase, Google Sheets, Python, R
Yêu cầu: Tốt nghiệp Đại học chuyên ngành Phân tích dữ liệu, Hệ thống thông tin, Toán thống kê, Kinh tế, hoặc các ngành liên quan. Tối thiểu 2 năm kinh nghiệm trong phân tích dữ liệu, xây dựng hệ thống báo cáo. Thành thạo SQL và các công cụ phân tích như BigQuery, Metabase, Google Sheets, Python hoặc R là lợi thế. Có kinh nghiệm làm việc với Data Warehouse, Data-mart và luồng ETL. Hiểu biết tốt về thử nghiệm A/B, causal inference, mô hình đánh giá hiệu quả. Có khả năng trình bày, trực quan hóa dữ liệu rõ ràng, dễ hiểu. Kỹ năng quản lý tài liệu, chia sẻ tri thức và truyền đạt quy trình một cách logic, dễ tiếp cận. Có tư duy hệ thống, chú ý chi tiết và tinh thần cải tiến liên tục. Chủ động, có khả năng phối hợp đa phòng ban và quản lý nhiều dự án cùng lúc. Thành thạo tiếng Anh là một lợi thế.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P05

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi tốt nghiệp ngành Quản trị kinh doanh, có background về Customer Service trong lĩnh vực ngân hàng bán lẻ và đã tham gia các hoạt động Business Analysis liên quan đến quy trình nội bộ. Tôi muốn phát triển theo hướng Business Analyst, tận dụng hiểu biết về banking operations và trải nghiệm làm việc với người dùng nội bộ để cải thiện quy trình vận hành, đặc biệt trong mảng chăm sóc khách hàng.

HỌC VẤN

Cử nhân Quản trị kinh doanh
Đại học tư thục khối kinh tế

KỸ NĂNG CHUYÊN MÔN

- Business Process Analysis: Phân tích quy trình chăm sóc khách hàng và các vấn đề phát sinh trong vận hành.
- Requirement Gathering: Thu thập yêu cầu từ Internal Users.
- Business Requirement: Viết và tổng hợp yêu cầu nghiệp vụ cơ bản.
- Process Mapping: Mô tả As-Is và To-Be Process.
- Lucidchart: Vẽ Flowchart để trình bày các bước xử lý nghiệp vụ.
- Google Sheets để tổng hợp thông tin và theo dõi vấn đề.
- CRM Operations, Notion và Google Docs phục vụ công việc.
- Figma cơ bản để thể hiện ý tưởng giao diện.

KỸ NĂNG MỀM

- Giao tiếp với người dùng nội bộ để ghi nhận các khó khăn trong quá trình làm việc.
- Có khả năng quan sát và phân tích vấn đề từ góc nhìn vận hành thực tế.
- Tổng hợp phản hồi và trình bày lại thông tin theo từng bước xử lý.
- Tiếng Anh B1, giao tiếp công việc ở mức cơ bản.

KINH NGHIỆM LÀM VIỆC

Customer Service / Business Operations Support
Ngân hàng TMCP Phát triển An Việt
Thời gian: 0,7 năm (khoảng 8 tháng)

- Thực hiện công việc liên quan đến Customer Service, tiếp nhận thông tin và các vấn đề từ khách hàng.
- Trong 7 tháng tham gia cải tiến quy trình nội bộ, hỗ trợ thu thập feedback từ người dùng hệ thống tiếp nhận yêu cầu và xử lý khiếu nại.
- Phân tích các bước xử lý hiện tại, xây dựng As-Is Flow và đề xuất To-Be Flow bằng Lucidchart.
- Tổng hợp Business Requirements trên Google Docs, quản lý các vấn đề nghiệp vụ bằng Google Sheets và Notion.

DỰ ÁN

Internal Customer Complaint Process Improvement

Tham gia hoạt động cải tiến quy trình tiếp nhận yêu cầu và xử lý khiếu nại trong ngân hàng bán lẻ.

Tôi phụ trách hỗ trợ mô tả business flow, ghi nhận các điểm gây khó khăn cho bộ phận vận hành và tổng hợp yêu cầu điều chỉnh. Kết quả công việc là bộ mô tả As-Is, To-Be Process cùng danh sách yêu cầu nghiệp vụ để nhóm phụ trách hệ thống nội bộ tham khảo.
```

### JD

```
Vị trí: Chuyên Viên Chuyển Đổi Số
Kinh nghiệm: 1 năm
Học vấn: Cao Đẳng trở lên
Kỹ năng chuyên môn: CRM, ERP, Google Workspace, Trello, ClickUp, Notion
Yêu cầu: Giới tính: Nam, Độ tuổi: Từ 25 đến 35 tuổi, Kinh nghiệm: Tối thiểu 1 năm kinh nghiệm trong các vị trí liên quan đến quản lý hệ thống, chuyển đổi số, triển khai phần mềm doanh nghiệp. Tư duy hệ thống, logic, phân tích tốt. Có kiến thức nền tảng về quản trị doanh nghiệp & phần mềm quản lý. Ưu tiên ứng viên có kinh nghiệm triển khai phần mềm CRM, ERP, hệ thống POS, quản lý kho. Kỹ năng giao tiếp, đào tạo, truyền đạt dễ hiểu cho người không rành công nghệ.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P06

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi đã có gần 4 năm làm việc trong lĩnh vực phát triển phần mềm doanh nghiệp, chủ yếu tham gia xây dựng các hệ thống quản lý bán hàng, kho hàng và đơn hàng. Công nghệ tôi sử dụng thường xuyên là Java, Spring Boot, Vue.js 2 và MySQL. Trong quá trình làm việc, tôi đã có cơ hội tham gia phát triển nhiều module nghiệp vụ, từ việc xử lý dữ liệu phía Backend đến xây dựng giao diện phục vụ người sử dụng.

Tôi mong muốn tiếp tục phát triển chuyên môn Fullstack, đặc biệt là xây dựng ứng dụng quản lý doanh nghiệp có quy trình nghiệp vụ rõ ràng, ổn định và thuận tiện cho việc bảo trì lâu dài.

HỌC VẤN

Tốt nghiệp Đại học chuyên ngành Công nghệ thông tin tại một trường đại học tư thục.

KỸ NĂNG CHUYÊN MÔN

- Backend: Java, Spring Boot, Spring Data JPA, Spring Security cơ bản.
- Frontend: Vue.js 2, JavaScript, Element UI.
- Database: MySQL.
- API: RESTful API, Postman.
- Công cụ phát triển: Maven, Git, Jenkins cơ bản.
- Testing: JUnit cơ bản.

KỸ NĂNG MỀM

- Có khả năng chủ động triển khai và hoàn thiện các tính năng nghiệp vụ được giao.
- Có kinh nghiệm trao đổi yêu cầu và phối hợp trong quá trình phát triển phần mềm doanh nghiệp.
- Đọc hiểu tốt tài liệu kỹ thuật tiếng Anh, trình độ B1.

KINH NGHIỆM LÀM VIỆC

Công ty TNHH Enterprise Solutions Việt Nam
Fullstack Developer | 05/2024 - 10/2026

- Tham gia phát triển và bảo trì hệ thống quản lý đơn hàng, kho hàng và báo cáo phục vụ hoạt động của doanh nghiệp.
- Sử dụng Java, Spring Boot, Spring Data JPA và MySQL để xây dựng chức năng xử lý nghiệp vụ, truy vấn và cập nhật dữ liệu.
- Xây dựng giao diện quản lý bằng Vue.js 2 kết hợp Element UI, tích hợp RESTful API giữa Frontend và Backend.
- Đảm nhận độc lập nhiều module quản lý đơn hàng và báo cáo, hoàn thiện các chức năng theo yêu cầu sử dụng thực tế.

Công ty CP Mekong Software
Java Developer | 11/2022 - 05/2024

- Tham gia phát triển các chức năng Backend cho phần mềm quản lý bán hàng và logistics bằng Java, Spring Boot.
- Xây dựng RESTful API phục vụ thao tác dữ liệu đơn hàng và quản lý thông tin kho.
- Sử dụng Maven để quản lý dự án, Postman để kiểm tra API và Git để quản lý mã nguồn.

DỰ ÁN

Hệ thống quản lý kho và đơn hàng doanh nghiệp

Dự án tập trung vào việc quản lý thông tin hàng hóa, đơn hàng và báo cáo nghiệp vụ. Tôi tham gia cả phần Backend bằng Spring Boot, MySQL và phần giao diện Vue.js 2. Công việc chính là xây dựng chức năng, tích hợp API và xử lý các yêu cầu thay đổi trong quá trình sử dụng.

NGOẠI NGỮ

Tiếng Anh B1, đọc tài liệu kỹ thuật tốt, giao tiếp ở mức cơ bản.
```

### JD

```
Vị trí: Nhà phát triển FullStack (PHP/ReactJS)
Kinh nghiệm: 3 năm
Học vấn: Cao Đẳng trở lên
Kỹ năng chuyên môn: PHP, React.js, HTML, CSS, JavaScript, TypeScript, MySQL, PostgreSQL, MongoDB, AWS
Yêu cầu: • Có kiến thức nền tảng tốt về lập trình (OOP, cấu trúc dữ liệu và giải thuật…).
• Có kiến thức nền tảng tốt về cơ sở dữ liệu quan hệ (thiết kế, sử dụng…).
• Có kiến thức nền tảng tốt về hệ điều hành linux, cấu hình, triển khai web server.
• Từ 3 năm kinh nghiệm lập trình sử dụng ngôn ngữ PHP trên các FrameWork như Laravel, Cake....
• Từ 3 năm kinh nghiệm lập trình Frontend sử dụng HTML/CSS/Javascript, TypeScript trên các framework như Reactjs, Vuejs…
• Có trên 1 năm lập trình trên môi trường cloud đặc biệt là AWS (Ec2, lambda…).
• Có khả năng tìm hiểu, thích ứng tốt với công nghệ mới.
• Có kinh nghiệm đảm nhiệm các vị trí project team leader là điểm cộng.
• Nhiệt tình, teamwork tốt, sẵn sàng học hỏi các công nghệ mới để đáp ứng công việc.
• Có tư duy hệ thống, tư duy logic tốt, có khả năn
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P07

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có 8 năm kinh nghiệm trong frontend engineering, từ Angular Developer đến Senior Frontend Engineer. Tôi muốn tiếp tục tập trung vào frontend system design cho các enterprise applications, đặc biệt là những hệ thống cần nhiều team phát triển song song. Điểm tôi quan tâm là maintainability, component reuse và hiệu năng thực tế, thay vì chỉ hoàn thành từng màn hình riêng lẻ.

HỌC VẤN

Tốt nghiệp đại học ngành Khoa học máy tính tại một trường đại học công lập. Kiến thức nền được tôi vận dụng trong việc đánh giá giải pháp kiến trúc và tổ chức các ứng dụng doanh nghiệp có nhiều phân hệ.

KỸ NĂNG CHUYÊN MÔN

Core stack: TypeScript, Angular, RxJS, NgRx, Angular Signals, SCSS. Có kinh nghiệm với Micro Frontends, Module Federation, Frontend System Design và Web Performance Optimization. Supporting tools: Nx Monorepo, Jasmine, Karma, Docker và Azure DevOps. Technical Leadership là một phần công việc thường xuyên của tôi.

KỸ NĂNG MỀM

Từng dẫn dắt team 6 developers, review định hướng kỹ thuật và phối hợp chuẩn hóa cách triển khai giữa các module. Tiếng Anh C1; có thể trình bày technical solutions, trao đổi trực tiếp với khách hàng quốc tế và giải thích các trade-off về kiến trúc.

KINH NGHIỆM LÀM VIỆC

Angular Developer → Senior Frontend Engineer – Công ty Cổ phần Giải pháp Số Nam Việt
10/2018 – 10/2026 (8 năm)

- Phát triển các frontend modules cho hệ thống ngân hàng, bảo hiểm và enterprise software bằng Angular, TypeScript, RxJS và NgRx.
- Lead team 6 developers, định hướng frontend system design và chuẩn hóa cách phối hợp khi nhiều nhóm cùng phát triển sản phẩm.
- Thiết kế kiến trúc Micro Frontends với Module Federation; tổ chức mã nguồn theo Nx Monorepo để các phân hệ có thể dùng chung những thành phần cần thiết.
- Xây dựng shared component library, ứng dụng Angular Signals và SCSS; thực hiện web performance optimization, kiểm thử với Jasmine, Karma và hỗ trợ quy trình bằng Azure DevOps.

DỰ ÁN

Enterprise frontend platform: Tham gia chuẩn hóa Micro Frontends và xây dựng thư viện UI components dùng chung cho các hệ thống phục vụ chuyển đổi số. Tôi phụ trách technical direction, trao đổi với các bên liên quan và hỗ trợ nhóm duy trì kiến trúc đã thống nhất.
```

### JD

```
Vị trí: Lập Trình Viên Front End (WEB)
Kinh nghiệm: 2 năm
Học vấn: Đại học trở lên chuyên ngành máy tính, phát triển phần mềm và các chuyên ngành liên quan
Kỹ năng chuyên môn: HTML5, CSS3, JavaScript, Ajax, JSON, Fetch, jQuery, Bootstrap, Echart, uni-app, Vue, Python, Node, Java, PHP, MySQL
Yêu cầu: Có hơn 2 năm kinh nghiệm phát triển front-end WEB, tốt nghiệp đại học trở lên chuyên ngành máy tính, phát triển phần mềm và các chuyên ngành liên quan khác, ưu tiên ứng viên đã từng sử dụng WeChat Pay và Alipay; Thành thạo các công nghệ cốt lõi của ngôn ngữ JavaScript như Ajax.JSON.Fetch, thành thạo sử dụng các thư viện/khung giao diện người dùng JavaScript phổ biến như jQuery.Boottrap.echart; Thành thạo viết mã HTML cho bố cục HTML/DIV+CSS/JavaScript, có phong cách và thói quen lập trình tốt; Thành thạo uni-app, vue và có thể tự mình hoàn thành việc phát triển H5 với sự hợp tác của backend; Thành thạo nhiều ngôn ngữ phát triển backend (như Python.Node/Java.PHP), nhiều cơ sở dữ liệu (như MySql) và có kinh nghiệm dự án liên quan; Có tinh thần cầu tiến mạnh mẽ, tinh thần trách nhiệm cao, tin
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P08

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi tốt nghiệp ngành Ứng dụng phần mềm và có kinh nghiệm thực tập Frontend với Vue 3. Mong muốn tiếp tục phát triển kỹ năng xây dựng giao diện web, làm việc với Vue Router, Pinia và các công cụ hỗ trợ phát triển Frontend. Định hướng trở thành lập trình viên có khả năng thực hiện các tính năng giao diện một cách độc lập và đáp ứng yêu cầu thực tế của sản phẩm.

HỌC VẤN

Tốt nghiệp Cao đẳng ngành Ứng dụng phần mềm

Trường cao đẳng kỹ thuật

Có kiến thức về lập trình web, HTML5, CSS3, JavaScript và phát triển ứng dụng giao diện người dùng.

KỸ NĂNG CHUYÊN MÔN

- HTML5, CSS3, JavaScript.
- Vue 3, Vue Router, Pinia cơ bản.
- Tailwind CSS, Figma.
- Axios, Vite, Git.
- Firebase Hosting, Chrome DevTools.

KỸ NĂNG MỀM

- Có khả năng phối hợp trong nhóm phát triển phần mềm.
- Tiếp nhận yêu cầu chỉnh sửa giao diện trong quá trình thực tập.
- Tiếng Anh A2, đọc hiểu tài liệu kỹ thuật đơn giản.

KINH NGHIỆM LÀM VIỆC

Frontend Developer Intern

Công ty Công nghệ An Việt

Thời gian: 0,7 năm

Lĩnh vực: Gia công phần mềm, bán lẻ và dịch vụ đặt lịch

- Tham gia phát triển giao diện quản lý sản phẩm bằng Vue 3, HTML5 và CSS3, hoàn thiện các phần giao diện được phân công.
- Xây dựng giao diện hệ thống đặt lịch dịch vụ, sử dụng Vue Router để tổ chức điều hướng giữa các trang.
- Sử dụng Tailwind CSS để chỉnh sửa bố cục và các thành phần giao diện theo thiết kế Figma.
- Sử dụng Git để quản lý mã nguồn và Chrome DevTools để kiểm tra, xử lý các vấn đề hiển thị.

DỰ ÁN

Hệ thống quản lý sản phẩm và đặt lịch dịch vụ

Công nghệ: Vue 3, JavaScript, Vue Router, Tailwind CSS, Axios, Vite.

Tham gia xây dựng các màn hình quản lý sản phẩm và giao diện đặt lịch trong thời gian thực tập. Công việc chủ yếu là phát triển các phần giao diện theo yêu cầu và chỉnh sửa để đảm bảo hiển thị phù hợp với thiết kế.
```

### JD

```
Vị trí: Thực Tập Sinh Lập Trình Web
Kinh nghiệm: Không yêu cầu
Học vấn: Sinh viên năm cuối hoặc mới tốt nghiệp khối ngành CNTT (Kỹ thuật phần mềm/Công nghệ phần mềm)
Kỹ năng chuyên môn: lập trình web, web server, database, html, css, javascript, PHP, Nodejs, Java, Golang, ReactJs, NextJS, Git
Yêu cầu: Yêu cầu ứng viên: Sinh viên năm cuối hoặc mới tốt nghiệp khối ngành CNTT (Kỹ thuật phần mềm/Công nghệ phần mềm). Nắm vững kiến thức cơ bản của lập trình web (web server, database, html, css, javascript ...) và các khái niệm của lập trình hướng đối tượng. Có kinh nghiệm thực tiễn qua các dự án cá nhân hoặc các khóa học lập trình ứng dụng. Đã từng làm việc với PHP, Nodejs, Java, Golang hoặc ReactJs, NextJS là một lợi thế. Hiểu về quá trình thiết kế và chuẩn hóa DB Schema. Có kiến thức về Git. Ưu tiên các bạn có khả năng đọc hiểu, tự học hỏi tốt từ các tài liệu bằng tiếng anh. Năng động, nhiệt tình, ham học hỏi và trách nhiệm trong công việc. Có laptop cá nhân.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P09

### CV

```
MỤC TIÊU NGHỀ NGHIỆP
Tôi có hơn 5 năm kinh nghiệm làm việc trong lĩnh vực phân tích dữ liệu và xây dựng hệ thống báo cáo nội bộ, chủ yếu tại doanh nghiệp bảo hiểm và dịch vụ tài chính. Trong quá trình làm việc, tôi tập trung vào việc phát triển, vận hành và bảo trì các báo cáo phục vụ hoạt động quản lý, theo dõi chỉ số kinh doanh và đối chiếu dữ liệu giữa các nguồn. Tôi mong muốn tiếp tục phát huy kinh nghiệm về SQL Server, Enterprise Reporting và Reporting Automation để xây dựng hệ thống báo cáo ổn định, đáp ứng các nhu cầu khai thác dữ liệu của doanh nghiệp.

HỌC VẤN
Cử nhân Hệ thống thông tin
Đại học công lập
Có nền tảng kiến thức về hệ thống thông tin, quản lý và khai thác dữ liệu trong doanh nghiệp.

KỸ NĂNG CHUYÊN MÔN
- Microsoft SQL Server, T-SQL.
- Stored Procedures, SQL Server Agent.
- SQL Server Reporting Services (SSRS).
- Microsoft Excel VBA.
- Power BI, DAX.
- Enterprise Reporting.
- KPI Dashboard Development.
- Data Reconciliation.
- Reporting Automation.
- Data Governance cơ bản.
- Business Requirement Gathering.
- Microsoft PowerPoint.

KỸ NĂNG MỀM
- Thu thập và làm rõ yêu cầu báo cáo từ các bộ phận nghiệp vụ.
- Có khả năng hướng dẫn nhân viên phân tích mới trong công việc xây dựng và kiểm tra báo cáo.
- Chú trọng sự chính xác, nhất quán của dữ liệu và tính ổn định của hệ thống báo cáo.
- Trình bày các chỉ số và nội dung báo cáo phục vụ hoạt động quản lý.
- Tiếng Anh B1, đọc tài liệu kỹ thuật và viết email công việc.

KINH NGHIỆM LÀM VIỆC
Công ty Cổ phần Bảo hiểm An Phúc
Senior Reporting Data Analyst
03/2021 - 10/2026 (5 năm 7 tháng)

- Phụ trách xây dựng, bảo trì và cập nhật các báo cáo nội bộ phục vụ hoạt động kinh doanh và quản lý nghiệp vụ bảo hiểm, sử dụng Microsoft SQL Server, T-SQL và SSRS.
- Phát triển các Stored Procedures để tổng hợp dữ liệu, sử dụng SQL Server Agent và Excel VBA nhằm tự động hóa các công việc báo cáo định kỳ, hạn chế thao tác tổng hợp thủ công.
- Thiết kế dashboard bằng Power BI, sử dụng DAX để xây dựng các chỉ số KPI, giúp bộ phận quản lý theo dõi kết quả hoạt động trên cùng một hệ thống báo cáo.
- Thực hiện Data Reconciliation để đối chiếu số liệu giữa các nguồn, đồng thời hướng dẫn nhân viên phân tích mới về quy trình kiểm tra dữ liệu và bảo trì báo cáo.

DỰ ÁN
Xây dựng và tự động hóa hệ thống báo cáo quản trị bảo hiểm

Trong quá trình làm việc, tôi tham gia phát triển hệ thống báo cáo tổng hợp phục vụ nhu cầu theo dõi các chỉ số kinh doanh của doanh nghiệp. Công việc bao gồm tiếp nhận yêu cầu từ bộ phận nghiệp vụ, thiết kế truy vấn dữ liệu bằng T-SQL, xây dựng báo cáo SSRS và sử dụng SQL Server Agent để lên lịch thực hiện các tác vụ báo cáo.

Bên cạnh đó, tôi sử dụng Power BI và DAX để phát triển các dashboard KPI, thực hiện đối chiếu dữ liệu trước khi cung cấp báo cáo cho bộ phận quản lý. Kết quả là hệ thống có các báo cáo định kỳ được chuẩn hóa, hỗ trợ việc tổng hợp và kiểm tra số liệu thuận tiện hơn.
```

### JD

```
Vị trí: Chuyên Viên Phân Tích Dữ Liệu
Kinh nghiệm: 3 năm
Học vấn: Tốt nghiệp đại học chuyên ngành quản trị kinh tế, công nghệ thông tin, tài chính ngân hàng, Có các chứng chỉ quốc tế như CFA, CAAC là 1 lợi thế
Kỹ năng chuyên môn: Kỹ năng phân tích, Kỹ năng giao tiếp và thuyết trình, Sử dụng thành thạo các công cụ phân tích dữ liệu, Kỹ năng viết tài liệu phân tích, Kỹ năng thu thập, xử lý dữ liệu, Kỹ năng sử dụng các công cụ thiết kế và mô hình hóa tài liệu, Kỹ năng về phân tích các bài toán nghiệp vụ ngành tài chính, Kỹ năng sử dụng các tool visualize dữ liệu, Kỹ năng hiểu biết về data governance, Kỹ năng quản trị dự án và quản lý sự thay đổi, Kỹ năng sử dụng AI và big data
Yêu cầu: 1. Trình độ học vấn/Chứng chỉ: Tốt nghiệp đại học chuyên ngành quản trị kinh tế, công nghệ thông tin, tài chính ngân hàng, có các chứng chỉ quốc tế như CFA, CAAC là 1 lợi thế. 2. Kinh nghiệm làm việc: Ít nhất 3-5 năm kinh nghiệm trong lĩnh vực phân tích nghiệp vụ, ưu tiên ứng viên có kinh nghiệm trong ngành tài chính, chứng khoán, bảo hiểm. 3. Kiến thức/Năng lực chuyên môn/Kỹ năng: Kỹ năng phân tích, tư duy phản biện và giải quyết vấn đề xuất sắc. Kỹ năng giao tiếp và thuyết trình tốt. Sử dụng thành thạo các công cụ phân tích dữ liệu và phần mềm quản lý dự án. Kỹ năng viết tài liệu phân tích rõ ràng, logic, đảm bảo đủ tính năng phát triển. Kỹ năng thu thập, xử lý dữ và sử dụng dữ liệu cho mục tiêu phân tích (Áp dụng mô hình DIKW). Kỹ năng sử dụng các công cụ thiết kế và mô hình hóa tài liệ
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P10

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi tốt nghiệp chuyên ngành Kế toán – Hệ thống thông tin và có khoảng 3,7 năm kinh nghiệm làm Business Analyst trong lĩnh vực ERP, chủ yếu với hệ thống Odoo tại doanh nghiệp phân phối. Công việc của tôi tập trung vào phân tích quy trình mua hàng, quản lý kho, kiểm soát dữ liệu và hỗ trợ người dùng vận hành hệ thống. Tôi mong muốn tiếp tục phát triển theo hướng BA nghiệp vụ doanh nghiệp, đặc biệt trong việc cải thiện quy trình quản lý mua hàng và tồn kho thông qua các giải pháp ERP phù hợp với hoạt động thực tế.

HỌC VẤN

Cử nhân Kế toán – Hệ thống thông tin
Trường đại học công lập khối kinh tế.

KỸ NĂNG CHUYÊN MÔN

- Phân tích quy trình mua hàng, nhập kho, xuất kho và quản lý tồn kho.
- Odoo ERP Functional Analysis, thực hiện Gap Analysis giữa quy trình thực tế và chức năng hệ thống.
- Xây dựng Functional Requirement cho các yêu cầu điều chỉnh trên Odoo.
- Microsoft Excel PivotTable phục vụ tổng hợp, đối chiếu dữ liệu mua hàng và kho.
- Quản lý Master Data, thực hiện Data Mapping trong quá trình chuẩn hóa dữ liệu.
- Microsoft Visio để vẽ quy trình nghiệp vụ.
- Microsoft Power BI và Odoo Studio ở mức cơ bản.
- Google Workspace phục vụ quản lý và trao đổi tài liệu.

KỸ NĂNG MỀM

- Trao đổi với người dùng để ghi nhận các vấn đề phát sinh trong quá trình vận hành.
- User Training, hướng dẫn nhân viên sử dụng các chức năng ERP theo quy trình.
- Tiếng Anh B1, đọc hiểu tài liệu Odoo ERP và giao tiếp nội bộ.

KINH NGHIỆM LÀM VIỆC

Business Analyst – Công ty TNHH Phân phối Hưng Phát
02/2023 – 10/2026 (3 năm 8 tháng)

- Phụ trách phân tích yêu cầu và hỗ trợ duy trì hệ thống Odoo ERP đang được sử dụng trong doanh nghiệp phân phối quy mô nhỏ, tập trung vào các hoạt động mua hàng và quản lý tồn kho.
- Làm việc với bộ phận mua hàng và kho để tìm hiểu cách xử lý nghiệp vụ thực tế, sau đó thực hiện Gap Analysis nhằm xác định những điểm cần điều chỉnh trên hệ thống Odoo.
- Viết Functional Requirement, sử dụng Microsoft Visio mô tả quy trình và phối hợp thực hiện các tùy chỉnh cơ bản bằng Odoo Studio, giúp yêu cầu nghiệp vụ được thể hiện rõ trước khi áp dụng.
- Sử dụng Excel PivotTable để đối chiếu dữ liệu, hỗ trợ quản lý Master Data, thực hiện Data Mapping và hướng dẫn nhân viên thao tác trên ERP, góp phần hạn chế sự không thống nhất trong dữ liệu vận hành.

DỰ ÁN

Duy trì và tùy chỉnh hệ thống Odoo ERP cho doanh nghiệp phân phối

Tôi tham gia hỗ trợ triển khai và duy trì các chức năng liên quan đến mua hàng, quản lý kho và dữ liệu hàng hóa. Công việc bao gồm tiếp nhận yêu cầu, phân tích sự khác biệt giữa quy trình thực tế với hệ thống, chuẩn bị tài liệu chức năng và hỗ trợ người dùng sau khi điều chỉnh. Phần lớn kinh nghiệm của tôi được tích lũy trong quá trình làm việc lâu dài với cùng một hệ thống ERP.
```

### JD

```
Vị trí: Chuyên Viên Phân Tích Nghiệp Vụ
Kinh nghiệm: 2 năm
Học vấn: Đại học các ngành: Công nghệ thông tin, Hệ thống thông tin quản lý
Kỹ năng chuyên môn: Visio, Figma, Draw.io, Jira, Confluence, BPMN tools
Yêu cầu: Tốt nghiệp Đại học các ngành: Công nghệ thông tin, Hệ thống thông tin quản lý. Có ít nhất 1–3 năm kinh nghiệm làm BA/Test trong lĩnh vực phần mềm, ưu tiên ứng viên từng làm với khách hàng là ngân hàng hoặc tổ chức tài chính. Hiểu biết tốt về các nghiệp vụ ngân hàng: tín dụng, tài sản đảm bảo, định giá, thanh toán, huy động vốn, v.v. Có khả năng viết tài liệu rõ ràng, logic, và kỹ năng giao tiếp tốt với cả kỹ thuật lẫn nghiệp vụ. Thành thạo các công cụ phân tích nghiệp vụ: Visio, Figma, Draw.io, Jira, Confluence, BPMN tools,... Kỹ năng làm việc nhóm và làm việc độc lập tốt. Ưu tiên có chứng chỉ liên quan như: CBAP, CCBA, PMI-PBA hoặc từng học qua các khóa đào tạo BA chuyên sâu. Có kinh nghiệm Agile/Scrum là một lợi thế.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P11

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Senior iOS Developer với 6,4 năm kinh nghiệm trong native iOS development, từng tham gia các sản phẩm thuộc healthcare, insurance và utility applications.

Tôi có kinh nghiệm làm việc với cả Objective-C và Swift, tham gia chuyển đổi legacy code sang Swift và đảm nhiệm vai trò technical owner cho ứng dụng chăm sóc sức khỏe. Định hướng tiếp theo là tiếp tục phát triển các ứng dụng iOS có cấu trúc dễ bảo trì, quy trình release ổn định và chú trọng chất lượng code. Tôi cũng mong muốn đóng góp nhiều hơn vào technical mentoring và code review trong nhóm phát triển.

HỌC VẤN

Tốt nghiệp Đại học – Ngành Công nghệ thông tin
Hệ đào tạo: Chính quy, trường đại học tư thục.

KỸ NĂNG CHUYÊN MÔN

- Programming Languages: Swift nâng cao, Objective-C.
- UI Development: SwiftUI.
- Reactive Programming: Combine.
- Concurrency: Swift Concurrency.
- Architecture: MVVM-C.
- Local Persistence: Core Data.
- Dependency Management: Swift Package Manager.
- Testing: XCTest, XCUITest.
- Build và Release: Fastlane, App Store Connect.
- Notification và Security: APNs, Keychain Services.
- Performance Analysis: Instruments.
- Engineering Practices: Technical Documentation, Code Review.

KỸ NĂNG MỀM

- Technical mentoring cho junior developers.
- Có kinh nghiệm hướng dẫn, review code và trao đổi giải pháp kỹ thuật trong nhóm.
- Giao tiếp tiếng Anh tốt trong môi trường nhóm quốc tế, đọc viết technical documentation thành thạo.

KINH NGHIỆM LÀM VIỆC

Senior iOS Developer
Công ty Giải pháp Y tế An Tâm
05/2023 – 10/2026 (3 năm 5 tháng)

- Đảm nhiệm vai trò kỹ thuật chính trong quá trình phát triển và duy trì healthcare application, tham gia xử lý các quyết định kỹ thuật liên quan đến phần iOS.
- Phát triển tính năng bằng Swift, SwiftUI, Combine và Swift Concurrency; sử dụng MVVM-C để tổ chức các thành phần và luồng điều hướng ứng dụng.
- Tham gia migration một phần codebase từ Objective-C sang Swift, đồng thời thực hiện Code Review và hỗ trợ junior developers trong quá trình triển khai.
- Quản lý release workflow với Fastlane, App Store Connect và thực hiện kiểm thử bằng XCTest, XCUITest trước các đợt phát hành.

iOS Developer
Công ty Công nghệ Bảo hiểm Đông Phương
05/2020 – 05/2023 (3 năm)

- Tham gia phát triển các chức năng iOS cho sản phẩm bảo hiểm và ứng dụng tiện ích sử dụng Swift, Objective-C.
- Làm việc với Core Data để lưu trữ dữ liệu, APNs cho notifications và Keychain Services trong các chức năng cần lưu trữ thông tin an toàn.
- Sử dụng Instruments để phân tích hoạt động ứng dụng, Swift Package Manager để quản lý package và tham gia kiểm thử trước khi phát hành.

DỰ ÁN

Healthcare Mobile Application

Vai trò: Senior iOS Developer / Technical Owner.

Tech stack: Swift, SwiftUI, Combine, Swift Concurrency, MVVM-C, Core Data, XCTest, XCUITest, Fastlane.

Phụ trách phần kỹ thuật iOS của ứng dụng, tham gia code migration, duy trì chất lượng source code, mentoring junior developers và điều phối các công việc liên quan đến app release.
```

### JD

```
Vị trí: Giám đốc phát triển kinh doanh
Kinh nghiệm: 5 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: Am hiểu sâu sắc thị trường B2B, Kỹ năng trình bày giải pháp theo hướng insight-driven, Khả năng phối hợp đa phòng ban
Yêu cầu: Tối thiểu 5 năm kinh nghiệm trong vai trò Business Development đặc biệt trong phân khúc Enterprise.
Ưu tiên ứng viên từng làm trong lĩnh vực Agency/Consulting cho client Enterprise hoặc MarTech, AdTech, SaaS.
Am hiểu sâu sắc thị trường B2B, đặc biệt trong ngành hàng Consumer Brands, FMCG, Retail, Fashion,...
Tự tin trong giao tiếp và đàm phán với các C-level/ Director/ Head trong doanh nghiệp lớn.
Kỹ năng trình bày giải pháp theo hướng insight-driven, có tư duy hệ thống và khả năng phối hợp đa phòng ban (cross-functional).
Thái độ cầu tiến, trách nhiệm, chuyên nghiệp trong công việc.
Tinh thần trách nhiệm cao, chuyên nghiệp, cầu tiến và sẵn sàng đồng hành dài hạn trong giai đoạn scale-up của Metric.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P12

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có gần 4 năm kinh nghiệm trong lĩnh vực phát triển phần mềm và DevOps, bắt đầu từ Java Backend trước khi chuyển sang Platform Engineering. Mong muốn tiếp tục phát triển chuyên môn về Kubernetes, GitOps và tự động hóa quy trình triển khai, đồng thời xây dựng nền tảng vận hành ổn định cho các nhóm phát triển sản phẩm.

HỌC VẤN

Tốt nghiệp Đại học chuyên ngành Công nghệ thông tin tại một trường đại học kỹ thuật công lập ở Hà Nội.

KỸ NĂNG CHUYÊN MÔN

- Container & Orchestration: Docker, Kubernetes, Helm, Kustomize.
- CI/CD & GitOps: GitLab CI/CD, Argo CD.
- Monitoring: Prometheus, Grafana, OpenTelemetry cơ bản.
- Hệ điều hành và Automation: Linux, Shell Scripting.
- Backend & Database: Java Spring Boot, PostgreSQL, Redis, RESTful API.

KỸ NĂNG MỀM

- Có kinh nghiệm phối hợp với nhóm phát triển sản phẩm trong quá trình triển khai và vận hành hệ thống.
- Chủ động phân tích vấn đề kỹ thuật và cải tiến quy trình làm việc.
- Tiếng Anh B2, có thể trao đổi các vấn đề kỹ thuật và đọc hiểu tài liệu chuyên ngành.

KINH NGHIỆM LÀM VIỆC

Platform Engineer – Công ty Công nghệ Tài chính Minh Phát
02/2024 – 10/2026 (2 năm 8 tháng)

- Triển khai và quản lý các ứng dụng container trên Kubernetes, sử dụng Helm và Kustomize để quản lý cấu hình.
- Xây dựng quy trình GitOps với Argo CD kết hợp GitLab CI/CD, giúp nhóm phát triển quản lý việc cập nhật và triển khai dịch vụ thống nhất hơn.
- Thiết lập Prometheus và Grafana để theo dõi tình trạng hoạt động của các dịch vụ, hỗ trợ phát hiện và phân tích sự cố.
- Sử dụng Shell Scripting để tự động hóa những tác vụ vận hành lặp lại trên Linux.

Java Backend Developer – Công ty Phần mềm Đông Á
02/2023 – 02/2024 (1 năm)

- Phát triển các chức năng Backend bằng Java Spring Boot và xây dựng RESTful API.
- Làm việc với PostgreSQL và Redis để phục vụ các chức năng xử lý và truy xuất dữ liệu.
- Tham gia container hóa dịch vụ bằng Docker, tạo tiền đề cho việc chuyển sang công việc DevOps.

DỰ ÁN

Xây dựng quy trình GitOps cho nền tảng Fintech

Tham gia chuẩn hóa cấu hình triển khai dịch vụ trên Kubernetes bằng Helm và Kustomize. Kết hợp Argo CD với GitLab CI/CD để đồng bộ quá trình phát hành ứng dụng, đồng thời sử dụng Prometheus, Grafana và OpenTelemetry ở mức cơ bản để hỗ trợ quan sát hệ thống.
```

### JD

```
Vị trí: Kỹ sư độ tin cậy trang web của Junior (SRE)
Kinh nghiệm: 1 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: Kubernetes, Docker, Terraform, Ansible, PostgreSQL, MongoDB, AWS, GitLab CI/CD, GitHub Actions
Yêu cầu: At least 1 year of experience in SRE/DevOps roles, preferably with international software projects. Hands-on experience with Docker and Kubernetes. Experience with Terraform, Ansible. Experience with api gateway such as APISIX and Nginx is a strong advantage. Experience with CI/CD tools such as Jenkins, GitLab CI/CD, or GitHub Actions. Familiarity with Grafana for monitor log and log analysis. Basic understanding of networking concepts (TCP/IP, DNS, firewalls, load balancers). Willingness to be on-call during weekends for production issue resolution. Knowledge of AWS architecture and services. Good verbal and written English communication skills.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P13

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có 4 năm kinh nghiệm làm DevOps và quản trị hệ thống hạ tầng CNTT, tập trung vào môi trường máy chủ on-premise. Công việc chủ yếu liên quan đến vận hành hệ thống nội bộ, triển khai ứng dụng và tự động hóa các tác vụ quản trị. Tôi muốn tiếp tục phát triển theo hướng Infrastructure DevOps, nâng cao chất lượng vận hành và khả năng đáp ứng của hệ thống doanh nghiệp.

HỌC VẤN

Tốt nghiệp Đại học chuyên ngành Mạng máy tính và Truyền thông dữ liệu tại một trường đại học công lập ở miền Nam.

KỸ NĂNG CHUYÊN MÔN

- Virtualization: VMware vSphere, Proxmox VE.
- CI/CD và Automation: Jenkins, Ansible, Shell Scripting, Git.
- Container: Docker Swarm.
- Hệ điều hành: CentOS Stream.
- Network và Load Balancing: HAProxy, SSH, NFS, Network Troubleshooting.
- Monitoring: Zabbix.
- Database: MariaDB.

KỸ NĂNG MỀM

- Có khả năng phối hợp với các bộ phận sử dụng hệ thống nội bộ để xác định và xử lý vấn đề phát sinh.
- Chủ động kiểm tra, theo dõi tình trạng máy chủ trong quá trình vận hành.
- Tiếng Anh B1, đọc hiểu tài liệu quản trị hệ thống và hướng dẫn kỹ thuật.

KINH NGHIỆM LÀM VIỆC

DevOps Engineer – Công ty Giải pháp Hạ tầng Thành Nam
10/2024 – 10/2026 (2 năm)

- Quản lý các máy chủ ảo hóa trên VMware vSphere và hỗ trợ vận hành Proxmox VE cho hệ thống nội bộ của khách hàng.
- Duy trì Jenkins pipeline để tự động hóa quá trình build và triển khai các ứng dụng doanh nghiệp.
- Sử dụng Ansible và Shell Scripting để thực hiện cấu hình máy chủ, giảm thao tác thủ công trong quá trình quản trị.
- Thiết lập Zabbix theo dõi tài nguyên máy chủ, hỗ trợ phát hiện sớm những vấn đề trong quá trình vận hành.

System & DevOps Engineer – Công ty Sản xuất Phú Hưng
10/2022 – 10/2024 (2 năm)

- Vận hành máy chủ CentOS Stream, quản lý kết nối SSH và chia sẻ dữ liệu qua NFS.
- Cấu hình HAProxy cho các ứng dụng quản trị nội bộ, hỗ trợ phân phối lưu lượng giữa các dịch vụ.
- Tham gia triễn khai ứng dụng bằng Docker Swarm và quản lý source code với Git.
- Kiểm tra kết nối mạng, xử lý lỗi truy cập dịch vụ và hỗ trợ vận hành MariaDB.

DỰ ÁN

Hệ thống triển khai ứng dụng nội bộ cho doanh nghiệp sản xuất

Tham gia xây dựng quy trình triển khai ứng dụng bằng Jenkins kết hợp Ansible và Docker Swarm. Hệ thống được vận hành trên hạ tầng on-premise, sử dụng Zabbix để giám sát máy chủ và HAProxy để hỗ trợ phân phối truy cập. Công việc tập trung vào duy trì hoạt động ổn định và đơn giản hóa thao tác triển khai định kì.
```

### JD

```
Vị trí: Kỹ sư độ tin cậy trang web của Junior (SRE)
Kinh nghiệm: 1 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: Kubernetes, Docker, Terraform, Ansible, PostgreSQL, MongoDB, AWS, GitLab CI/CD, GitHub Actions
Yêu cầu: At least 1 year of experience in SRE/DevOps roles, preferably with international software projects. Hands-on experience with Docker and Kubernetes. Experience with Terraform, Ansible. Experience with api gateway such as APISIX and Nginx is a strong advantage. Experience with CI/CD tools such as Jenkins, GitLab CI/CD, or GitHub Actions. Familiarity with Grafana for monitor log and log analysis. Basic understanding of networking concepts (TCP/IP, DNS, firewalls, load balancers). Willingness to be on-call during weekends for production issue resolution. Knowledge of AWS architecture and services. Good verbal and written English communication skills.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P14

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Business Analyst với 6,5 năm kinh nghiệm trong lĩnh vực Digital Banking, FinTech và thanh toán điện tử. Tôi có kinh nghiệm phân tích yêu cầu ở phạm vi doanh nghiệp, tái thiết kế quy trình và phối hợp với các bên liên quan cấp quản lý. Định hướng phát triển chuyên sâu về Enterprise Business Analysis, nâng cao hiệu quả quản trị yêu cầu và hỗ trợ phát triển đội ngũ Business Analyst trong các dự án ngân hàng số.

HỌC VẤN

- Thạc sĩ Hệ thống thông tin quản lý – Trường đại học công lập khối kinh tế.
- Cử nhân Công nghệ thông tin.

KỸ NĂNG CHUYÊN MÔN

- Enterprise Requirement Analysis, Stakeholder Management và Business Process Reengineering.
- Phân tích nghiệp vụ Digital Banking và thanh toán điện tử.
- Phân tích yêu cầu tích hợp hệ thống thông qua API.
- SQL với PostgreSQL phục vụ phân tích dữ liệu nghiệp vụ.
- BPMN, UML nâng cao và Camunda Modeler.
- Backlog Prioritization, Jira và Confluence.
- Event Storming, Solution Review và Risk Assessment.
- Power BI phục vụ phân tích và trình bày dữ liệu.
- Agile Scrum, Scrum of Scrums và Mentoring Junior Business Analysts.

KỸ NĂNG MỀM

- Làm việc trực tiếp với các bên liên quan cấp quản lý để thống nhất yêu cầu và ưu tiên nghiệp vụ.
- Điều phối nhóm BA nhỏ, hướng dẫn Junior BA thực hiện phân tích và chuẩn hóa tài liệu.
- Tiếng Anh C1, có khả năng điều phối workshop và viết tài liệu nghiệp vụ chuyên sâu.

KINH NGHIỆM LÀM VIỆC

Senior Business Analyst – Công ty Cổ phần Công nghệ Tài chính Nam Việt
10/2022 – 10/2026 (4 năm)

- Phụ trách Enterprise Requirement Analysis cho các dự án ngân hàng số, làm việc với stakeholder cấp quản lý để xác định phạm vi và thứ tự ưu tiên nghiệp vụ.
- Phân tích các luồng tích hợp hệ thống qua API, thực hiện Solution Review và Risk Assessment nhằm làm rõ tác động của yêu cầu tới các hệ thống liên quan.
- Sử dụng BPMN, UML và Camunda Modeler để mô hình hóa, tái thiết kế quy trình; quản lý backlog và tài liệu trên Jira, Confluence.
- Hướng dẫn Junior BA, điều phối công việc phân tích của nhóm nhỏ và phối hợp trong mô hình Agile Scrum, Scrum of Scrums.

Business Analyst – Công ty TNHH Giải pháp Thanh toán Minh Tâm
04/2020 – 10/2022 (2 năm 6 tháng)

- Phân tích yêu cầu chức năng cho hệ thống thanh toán điện tử, xây dựng mô hình nghiệp vụ để thống nhất cách xử lý với các bên liên quan.
- Sử dụng PostgreSQL và Power BI hỗ trợ phân tích dữ liệu, đồng thời tham gia Event Storming để làm rõ các luồng nghiệp vụ.

DỰ ÁN

Phân tích và tái thiết kế quy trình ngân hàng số

Tham gia phân tích yêu cầu, đánh giá quy trình hiện tại và đề xuất điều chỉnh luồng nghiệp vụ cho các chức năng ngân hàng số. Phối hợp với các bên liên quan trong quá trình ưu tiên backlog, rà soát giải pháp và kiểm soát những thay đổi có ảnh hưởng đến các hệ thống tích hợp.
```

### JD

```
Vị trí: Data & Business Intelligence Leader
Kinh nghiệm: 5 năm
Học vấn: Tốt nghiệp đại học trở lên các ngành: Quản trị kinh doanh, Hệ thống thông tin, CNTT, Phân tích dữ liệu
Kỹ năng chuyên môn: SQL, BigData, DataBricks, Power BI, Python, R
Yêu cầu: Tốt nghiệp đại học trở lên các ngành: Quản trị kinh doanh, Hệ thống thông tin, CNTT, Phân tích dữ liệu... Am hiểu kinh doanh: Hiểu sâu sắc về hoạt động và quy trình kinh doanh, phát triển sản phẩm, có khả năng định hướng thu thập dữ liệu và các sáng kiến BI phù hợp với mục tiêu tổ chức. Kinh nghiệm: Tối thiểu 5 năm kinh nghiệm trong lĩnh vực Business Intelligence, phân tích dữ liệu hoặc các lĩnh vực liên quan, trong đó có ít nhất 2 năm giữ vai trò quản lý. Tư duy phân tích: Sở hữu tư duy phân tích mạnh mẽ, thành thạo các công cụ và kỹ thuật phân tích dữ liệu, mô hình thống kê và trực quan hóa dữ liệu (ví dụ: SQL, BigData, DataBricks, Power BI, Python/R). Khả năng quản lý: Có kinh nghiệm quản lý đội nhóm hiệu quả, kỹ năng giao tiếp và dẫn dắt xuất sắc. Tư duy chiến lược: Có khả năng chuyển 
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P15

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi đã có hơn 1 năm làm việc với PHP và Laravel, chủ yếu phát triển và bảo trì các hệ thống quản trị nội bộ, phần mềm quản lý bán hàng. Công việc thường xuyên là xử lý chức năng CRUD, chỉnh sửa nghiệp vụ và sửa lỗi theo yêu cầu người dùng. Tôi muốn tiếp tục nâng cao khả năng làm Backend bằng Laravel, viết code dễ bảo trì hơn và cải thiện kỹ năng xử lý dữ liệu với MySQL.

HỌC VẤN

Cử nhân Hệ thống thông tin
Đại học tư thục

Có kiến thức nền tảng về hệ thống thông tin, cơ sở dữ liệu và phát triển ứng dụng web.

KỸ NĂNG CHUYÊN MÔN

- Ngôn ngữ: PHP, SQL.
- Framework: Laravel.
- Database: MySQL, Eloquent ORM.
- API: RESTful API.
- Testing: PHPUnit cơ bản, Postman.
- Công cụ: Git, Composer.
- Frontend hỗ trợ: Blade Template, jQuery.
- Hệ điều hành: Linux cơ bản.
- Tiếng Anh: A2, có thể đọc tài liệu kỹ thuật với sự hỗ trợ của công cụ dịch.

KỸ NĂNG MỀM

- Có thể tiếp nhận và xử lý các yêu cầu chỉnh sửa chức năng.
- Phối hợp với đồng nghiệp trong quá trình bảo trì hệ thống.
- Kiên nhẫn kiểm tra lỗi và cập nhật lại code theo phản hồi.
- Chủ động trao đổi khi gặp vấn đề chưa rõ về nghiệp vụ.

KINH NGHIỆM LÀM VIỆC

PHP Laravel Developer
Công ty TNHH Giải pháp Phần mềm An Phát
08/2025 – 09/2026 (14 tháng)

- Phát triển và bảo trì các chức năng CRUD cho hệ thống quản lý bán hàng và phần mềm quản trị nội bộ của doanh nghiệp.
- Sử dụng Laravel, Eloquent ORM và MySQL để truy vấn, thêm, sửa, xóa dữ liệu theo yêu cầu nghiệp vụ.
- Chỉnh sửa các trang quản trị bằng Blade Template và jQuery, cập nhât giao diện khi có thay đổi chức năng.
- Hỗ trợ kiểm tra RESTful API bằng Postman, sửa lỗi phát sinh trong quá trình sử dụng và quản lý mã nguồn bằng Git.

DỰ ÁN

Hệ thống quản lý bán hàng nội bộ

Công nghệ: PHP, Laravel, MySQL, Blade Template, jQuery.

Tham gia bảo trì chức năng quản lý dữ liệu bán hàng và các màn hình quản trị. Chủ yếu xử lý yêu cầu chỉnh sửa, kiểm tra dữ liệu và khắc phục lỗi để các chức năng hoạt động đúng theo nghiệp vụ.

Tôi cũng có tìm hiểu PHPUnit để viết các bài test đơn giản cho một số phần xử lý Backend.
```

### JD

```
Vị trí: Lập Trình Viên PHP Laravel Backend
Kinh nghiệm: 2 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: PHP, Laravel, MySQL, PostgreSQL, MongoDB, HTML, CSS, JavaScript, Git
Yêu cầu: Tối thiểu 2 năm kinh nghiệm làm việc với PHP, đặc biệt là Laravel Framework. Hiểu biết sâu về các kiến trúc RESTful API và cách triển khai chúng. Kinh nghiệm làm việc với hệ quản trị cơ sở dữ liệu (MySQL, PostgreSQL, hoặc MongoDB). Thành thạo HTML, CSS, JavaScript (ưu tiên có kinh nghiệm làm việc với các framework như Vue.js, ReactJS, React Native là điểm cộng). Hiểu biết về các công cụ quản lý mã nguồn như Git. Có khả năng phân tích, xử lý vấn đề và làm việc độc lập hoặc theo nhóm. Kỹ năng giao tiếp tốt, sẵn sàng học hỏi và tiếp thu công nghệ mới.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P16

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có 4 năm kinh nghiệm phát triển phần mềm, trong đó khoảng 1,2 năm làm Java Backend Developer và 2,8 năm phát triển ứng dụng Android native. Quá trình chuyển từ Backend sang Mobile giúp tôi có góc nhìn về cả xử lý dữ liệu phía máy chủ và cách ứng dụng di động tương tác với hệ thống.

Tôi muốn tiếp tục phát triển chuyên môn Android với Kotlin, tập trung vào việc xây dựng các chức năng ổn định, tổ chức mã nguồn rõ ràng và nâng cao chất lượng kiểm thử. Tôi quan tâm đến các sản phẩm trong lĩnh vực thương mại điện tử, vận tải và giao nhận.

HỌC VẤN

Tốt nghiệp Đại học – Ngành Khoa học máy tính
Hệ đào tạo: Chính quy, trường đại học công lập.

KỸ NĂNG CHUYÊN MÔN

- Ngôn ngữ lập trình: Java, Kotlin.
- Android Development: Android SDK, XML Layout, Jetpack Navigation.
- Database: Room Database, MySQL.
- Background Processing: WorkManager.
- Dependency Injection: Hilt.
- Networking: Retrofit.
- Testing: JUnit.
- Backend: Spring Boot cơ bản.
- Công cụ: Gradle, Git, Jira.
- Push Notification: Firebase Cloud Messaging.

KỸ NĂNG MỀM

- Có khả năng tiếp cận công việc từ cả góc độ Backend và Android.
- Đọc hiểu tài liệu kỹ thuật tiếng Anh tốt, giao tiếp kỹ thuật khá.
- Có kinh nghiệm phối hợp công việc phát triển phần mềm thông qua Jira.

KINH NGHIỆM LÀM VIỆC

Android Developer
Công ty Công nghệ Vận tải Nam Việt
12/2023 – 10/2026 (2 năm 10 tháng)

- Phát triển và bảo trì ứng dụng Android phục vụ hoạt động giao nhận, theo dõi trạng thái đơn hàng bằng Kotlin và Android SDK.
- Xây dựng giao diện với XML Layout, sử dụng Jetpack Navigation để tổ chức luồng màn hình và Retrofit để kết nối ứng dụng với dịch vụ Backend.
- Sử dụng Room Database để quản lý dữ liệu cục bộ, WorkManager để thực hiện các tác vụ nền và Firebase Cloud Messaging cho chức năng thông báo.
- Áp dụng Hilt Dependency Injection trong tổ chức mã nguồn, viết kiểm thử với JUnit và quản lý thay đổi bằng Git.

Java Backend Developer
Công ty TNHH Phần mềm Đại Tín
10/2022 – 12/2023 (1 năm 2 tháng)

- Tham gia phát triển các chức năng Backend bằng Java và Spring Boot cho hệ thống phục vụ hoạt động thương mại điện tử.
- Làm việc với MySQL trong quá trình xây dựng và điều chỉnh chức năng xử lý dữ liệu.
- Sử dụng Git để quản lý mã nguồn và Jira để theo dõi công việc phát triển.

DỰ ÁN

Ứng dụng giao nhận và theo dõi đơn hàng

Công nghệ: Kotlin, Android SDK, XML Layout, Retrofit, Room Database, WorkManager, Firebase Cloud Messaging.

Tham gia phát triển các chức năng hiển thị thông tin đơn hàng, theo dõi trạng thái giao nhận và thông báo cập nhật. Tập trung vào phần Android, xử lý luồng dữ liệu và duy trì hoạt động của ứng dụng.
```

### JD

```
Vị trí: Nhà phát triển Android cao cấp (Ứng dụng di động)
Kinh nghiệm: 3 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: Android SDK, Android Studio, Java, Kotlin, MVVM, Clean Architecture, JNI, C/C++
Yêu cầu: Kĩ năng chuyên môn: Nắm vững kiến thức nền tảng về Android (Activity/Fragment Lifecycle, ViewModel, LiveData, Coroutines, Jetpack Components). Có kiến thức và khả năng áp dụng hiệu quả các pattern kiến trúc như MVVM. Hiểu biết cơ bản về Clean Architecture, thể hiện được trong các dự án thực tế. Tư duy tốt modular hóa và tổ chức code rõ ràng, maintainable. Có kiến thức về JNI và có khả năng tích hợp native code (C/C++). Có kinh nghiệm trong việc cải thiện hiệu năng ứng dụng. Có khả năng tạo Custom View. Có kinh nghiệm trong việc tích hợp SDK/dịch vụ bên thứ ba. Kinh nghiệm: Middle- Senior: Tối thiểu 3+ năm kinh nghiệm. Kĩ năng mềm: Khả năng phối hợp tốt với các thành viên khác trong nhóm, hỗ trợ các thành viên Junior/Intern. Có niềm đam mê mãnh liệt và nghiên cứu sâu với công nghệ, các sản 
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P17

### CV

```
MỤC TIÊU NGHỀ NGHIỆP
Tôi có hơn 7 năm phát triển trong lĩnh vực UI/UX, bắt đầu từ thiết kế giao diện và dần đảm nhiệm UX Strategy, nghiên cứu người dùng và tổ chức hệ thống thiết kế cho sản phẩm số. Kinh nghiệm tập trung vào fintech, ngân hàng số, bảo hiểm công nghệ và phần mềm doanh nghiệp. Tôi muốn phát triển luồng sử dụng nhất quán, chú trọng Accessibility Design và mentoring designer.

HỌC VẤN
Cử nhân Thiết kế truyền thông đa phương tiện, tốt nghiệp tại một trường đại học công lập. Đã hoàn thành các khóa đào tạo chuyên sâu về UX Research.

KỸ NĂNG CHUYÊN MÔN
- Figma, Axure RP, UXPin; Advanced Prototyping.
- UX Strategy, User Research, Information Architecture và Accessibility Design.
- Design System Architecture, Design Leadership.
- Google Analytics 4, A/B Testing, Miro.

KỸ NĂNG MỀM
- Design Workshop Facilitation, Stakeholder Communication và trình bày giải pháp thiết kế.
- Mentoring Junior Designers, hỗ trợ nhóm 3–4 designer thống nhất cách làm việc với thư viện component.
- Tiếng Việt bản ngữ; tiếng Anh C1, giao tiếp chuyên môn và trình bày phương án thiết kế.

KINH NGHIỆM LÀM VIỆC

UI Designer – Công ty Giải pháp Số Minh Tâm (08/2019 – 07/2022)
- Thiết kế giao diện cho các ứng dụng phần mềm doanh nghiệp và sản phẩm tài chính số.
- Sắp xếp Information Architecture và dựng prototype để làm rõ màn hình, trạng thái và luồng tương tác.
- Phối hợp hoàn thiện các thành phần giao diện tái sử dụng, giúp duy trì sự nhất quán giữa các màn hình.

Senior UI/UX Designer – Công ty Công nghệ Tài chính Hướng Việt (08/2022 – 09/2026)
- Phụ trách thiết kế luồng giao dịch tài chính, từ User Research đến prototype và phương án tương tác.
- Xây dựng, tổ chức thư viện component theo Design System Architecture, phục vụ việc thiết kế đồng bộ các màn hình.
- Kết hợp Google Analytics 4 và A/B Testing để xem xét hành vi sử dụng, hỗ trợ điều chỉnh thiết kế.
- Hướng dẫn nhóm 3–4 designer, tổ chức workshop và trao đổi giải pháp với các stakeholder liên quan.

DỰ ÁN
Chuẩn hóa trải nghiệm giao dịch ngân hàng số: thiết kế lại cấu trúc thông tin và các bước tương tác, xây dựng prototype trên Figma, Axure RP và UXPin. Phát triển thư viện component chung, chú trọng Accessibility Design.
```

### JD

```
Vị trí: UI/UX Manager
Kinh nghiệm: 5 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: UI/UX Design, Wireframe, Design System
Yêu cầu: Có ít nhất 5 năm kinh nghiệm UIUX Design cho các sản phẩm web/app (Ưu tiên mảng Mobile App). Có ít nhất 2 năm kinh nghiệm ở vị trí tương đương. Về chuyên môn UI: Am hiểu và vận dụng linh hoạt, chuyên sâu về quy tắc thiết kế, Design System, và style thiết kế của nhiều dòng sản phẩm. Về chuyên môn UX: Nắm vững kiến thức về xây dựng Wireframe, trải nghiệm trong app, và userflow cho app. Kiến thức khác: Quy trình phát triển sản phẩm, kiến thức về thị trường và dòng sản phẩm, chỉ số cơ bản về sản phẩm và marketing.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P18

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi học chuyên ngành Lập trình máy tính và đã có 8 tháng thực tập kết hợp làm bán thời gian tại đơn vị thiết kế website. Trong quá trình làm việc, tôi chủ yếu sử dụng PHP, Laravel để phát triển các chức năng quản trị và xử lý dữ liệu. Mục tiêu của tôi là tiếp tục nâng cao khả năng lập trình web, đặc biệt với Laravel và Vue.js 3, để có thể tham gia nhiều hơn vào quá trình xây dựng website cho doanh nghiệp.

HỌC VẤN

Trường Cao đẳng nghề – Ngành Lập trình máy tính
Trình độ: Cao đẳng.

KỸ NĂNG CHUYÊN MÔN

- Backend: PHP, Laravel cơ bản, Laravel Blade.
- Frontend: HTML5, CSS3, JavaScript, Vue.js 3 cơ bản, jQuery.
- Giao diện: Tailwind CSS cơ bản, sử dụng Laravel Blade để xây dựng các trang web.
- Database: MySQL, thao tác dữ liệu và các chức năng CRUD.
- Công cụ: Git, XAMPP, Postman.
- Ngoại ngữ: Tiếng Anh A2, có thể đọc hiểu các tài liệu kỹ thuật đơn giản.

KỸ NĂNG MỀM

- Có khả năng tiếp nhận công việc và phối hợp với các thành viên khác trong quá trình làm website.
- Biết trao đổi khi cần chỉnh sửa giao diện hoặc chức năng theo yêu cầu.
- Có tinh thần học hỏi, rèn luyện thêm qua các công việc thực tế được giao.

KINH NGHIỆM LÀM VIỆC

Công ty TNHH Thiết kế Web An Phúc
Thực tập sinh và nhân viên lập trình Web bán thời gian
02/2026 – 09/2026 (8 tháng)

- Sử dụng PHP và Laravel để phát triển các chức năng quản lý sản phẩm trên trang quản trị website.
- Xây dựng biểu mẫu nhập dữ liệu và thực hiện các chức năng thêm, sửa, xóa, hiển thị thông tin sản phẩm với MySQL.
- Chỉnh sửa giao diện bằng HTML5, CSS3, JavaScript và Laravel Blade theo các yêu cầu trong quá trình làm website.
- Sử dụng XAMPP để chạy website ở môi trường local, Git để quản lý source code và Postman để kiểm tra các chức năng liên quan đến API.

DỰ ÁN

Trang quản trị sản phẩm cho website bán lẻ

Công nghệ: PHP, Laravel, Laravel Blade, MySQL, HTML5, CSS3, JavaScript.

Tham gia lập trình khu vực quản trị sản phẩm, tập trung vào các biểu mẫu và chức năng CRUD. Các phần việc đã làm giúp việc nhập, cập nhật và quản lý thông tin sản phẩm được thực hiện thông qua giao diện quản trị thay vì chỉnh sửa trực tiếp dữ liệu.

Qua dự án này tôi đã có thêm kinh nghiệm thực tế về cách tổ chức code Laravel và xử lý dữ liệu giữa giao diện với database.
```

### JD

```
Vị trí: Lập Trình Viên
Kinh nghiệm: 2 năm
Học vấn: Cao Đẳng trở lên
Kỹ năng chuyên môn: Node.js, Next.js, Typescript, Flutter, C#
Yêu cầu: • Có sản phẩm cá nhân, GitHub/Portfolio rõ ràng.
• Đã từng tham gia dự án thực tế.
• Những bạn có khả năng làm việc độc lập là 1 lợi thế.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P19

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi tốt nghiệp ngành Thiết kế đồ họa và có 6 tháng thực tập thiết kế giao diện tại một công ty EdTech. Tôi mong muốn tiếp tục phát triển trong lĩnh vực UI Design, tập trung vào việc xây dựng giao diện dễ sử dụng, bố cục rõ ràng và phù hợp với nhiều kích thước màn hình. Trong thời gian tới, tôi muốn cải thiện kỹ năng thiết kế trên Figma, cách tổ chức các thành phần giao diện và khả năng tiếp nhận phản hồi để hoàn thiện sản phẩm.

HỌC VẤN

Cử nhân Thiết kế đồ họa – Trường đại học tư thục
Đã tốt nghiệp.

Được đào tạo về các nguyên tắc thiết kế hình ảnh, Typography, Color Theory và cách tổ chức bố cục trực quan.

KỸ NĂNG CHUYÊN MÔN

- Figma: Thiết kế giao diện, sử dụng Auto Layout ở mức cơ bản và xây dựng các màn hình theo yêu cầu.
- UI Design: Áp dụng Visual Hierarchy, Typography và Color Theory trong thiết kế.
- Wireframing: Phác thảo bố cục trước khi triển khai giao diện chi tiết.
- Responsive Layout: Điều chỉnh bố cục phù hợp với kích thước màn hình.
- Prototyping: Tạo prototype cơ bản để thể hiện luồng tương tác.
- FigJam, Google Forms và User Flow đơn giản.
- Adobe Photoshop: Sử dụng ở mức cơ bản.

KỸ NĂNG MỀM

- Giao tiếp nhóm, tiếp nhận và điều chỉnh thiết kế theo phản hồi.
- Có khả năng đọc hiểu tài liệu thiết kế bằng tiếng Anh trình độ B1.
- Sử dụng tiếng Việt thành thạo trong công việc.

KINH NGHIỆM LÀM VIỆC

UI Design Intern – Công ty EdTech Minh Tri
04/2026 – 10/2026 (6 tháng)

- Thiết kế các màn hình giao diện cho ứng dụng học tập theo yêu cầu và hướng dẫn từ designer chính.
- Sử dụng Figma để triển khai bố cục, Typography, màu sắc và các thành phần giao diện.
- Chỉnh sửa thiết kế sau các buổi review nội bộ, tập trung vào tính nhất quán của bố cục và khả năng đọc nội dung.
- Hỗ trợ xây dựng wireframe và prototype cơ bản để trình bày phương án giao diện trước khi hoàn thiện thiết kế.

Qua thời gian thực tập, tôi đã quen hơn với quy trình nhận yêu cầu, thực hiện thiết kế và chỉnh sửa nhiều lần dựa trên góp ý của nhóm.
```

### JD

```
Vị trí: Lập Trình Viên PHP Laravel Backend
Kinh nghiệm: 2 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: PHP, Laravel, MySQL, PostgreSQL, MongoDB, HTML, CSS, JavaScript, Git
Yêu cầu: Tối thiểu 2 năm kinh nghiệm làm việc với PHP, đặc biệt là Laravel Framework. Hiểu biết sâu về các kiến trúc RESTful API và cách triển khai chúng. Kinh nghiệm làm việc với hệ quản trị cơ sở dữ liệu (MySQL, PostgreSQL, hoặc MongoDB). Thành thạo HTML, CSS, JavaScript (ưu tiên có kinh nghiệm làm việc với các framework như Vue.js, ReactJS, React Native là điểm cộng). Hiểu biết về các công cụ quản lý mã nguồn như Git. Có khả năng phân tích, xử lý vấn đề và làm việc độc lập hoặc theo nhóm. Kỹ năng giao tiếp tốt, sẵn sàng học hỏi và tiếp thu công nghệ mới.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P20

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có 6 năm 6 tháng kinh nghiệm phát triển hệ thống dữ liệu doanh nghiệp, chủ yếu trong lĩnh vực ngân hàng, viễn thông và phân tích dữ liệu giao dịch. Chuyên môn tập trung vào kiến trúc Data Lake, xử lý dữ liệu phân tán và xây dựng pipeline batch, streaming. Tôi mong muốn tiếp tục tham gia thiết kế các nền tảng dữ liệu có khả năng mở rộng, đồng thời đóng góp vào việc chuẩn hóa quy trình kỹ thuật và nâng cao chất lượng xử lý dữ liệu.

HỌC VẤN

Đại học – Ngành Kỹ thuật phần mềm
Trường đại học kỹ thuật công lập.

KỸ NĂNG CHUYÊN MÔN

- Ngôn ngữ lập trình: Scala.
- Big Data Processing: Apache Spark, Distributed Data Processing.
- Streaming: Apache Kafka.
- Data Storage: Hadoop HDFS, Apache Hive, Apache Iceberg, S3-compatible Object Storage.
- Data Orchestration: Apache Airflow.
- Data Query: Trino.
- Kiến trúc dữ liệu: Data Lake Architecture.
- Hạ tầng và vận hành: Kubernetes, Linux, Prometheus.
- CI/CD và chất lượng dữ liệu: GitLab CI/CD, Great Expectations.

KỸ NĂNG MỀM

- Dẫn dắt kỹ thuật nhóm nhỏ, phân chia và phối hợp công việc trong quá trình phát triển hệ thống.
- Phân tích vấn đề kỹ thuật, trao đổi phương án thiết kế và xử lý sự cố.
- Tiếng Anh B2, có thể giao tiếp kỹ thuật với đối tác quốc tế.

KINH NGHIỆM LÀM VIỆC

Senior Big Data Engineer – Công ty CP Nền tảng Dữ liệu Thăng Long
04/2023 – 09/2026 (3 năm 6 tháng)

- Chịu trách nhiệm thiết kế pipeline batch và streaming cho hệ thống phân tích dữ liệu giao dịch trong lĩnh vực ngân hàng.
- Xây dựng luồng xử lý bằng Apache Spark, Scala và Apache Kafka, phục vụ khối lượng dữ liệu hàng chục triệu bản ghi mỗi ngày.
- Tham gia thiết kế Data Lake sử dụng Apache Iceberg, kết hợp Trino để hỗ trợ truy vấn và khai thác dữ liệu.
- Dẫn dắt kỹ thuật nhóm nhỏ, phối hợp xây dựng lịch xử lý với Apache Airflow và kiểm tra chất lượng dữ liệu bằng Great Expectations.

Data Engineer – Công ty TNHH Công nghệ Viễn thông Bắc Việt
04/2020 – 03/2023 (3 năm)

- Phát triển pipeline xử lý dữ liệu viễn thông bằng Apache Spark và Scala.
- Làm việc với Hadoop HDFS và Apache Hive để lưu trữ, tổ chức dữ liệu phục vụ phân tích.
- Xây dựng các tác vụ xử lý dữ liệu theo lô, hỗ trợ tổng hợp dữ liệu từ nhiều nguồn trong hệ thống doanh nghiệp.
- Sử dụng Linux và GitLab CI/CD trong quá trình phát triển, cập nhật và triển khai các thành phần xử lý dữ liệu.

DỰ ÁN

Nền tảng phân tích dữ liệu giao dịch quy mô lớn

Tham gia thiết kế kiến trúc Data Lake và hệ thống xử lý dữ liệu phân tán. Sử dụng Apache Kafka, Apache Spark và Apache Airflow để tổ chức các pipeline xử lý batch và streaming. Hệ thống phục vụ phân tích hàng chục triệu bản ghi giao dịch mỗi ngày.
```

### JD

```
Vị trí: Kỹ sư dữ liệu cao cấp
Kinh nghiệm: 4 năm
Học vấn: Đại học hoặc cao hơn liên quan đến 1 trong các ngành kinh tế, tài chính, ngân hàng, hoặc công nghệ thông tin, khoa học máy tính, toán tin ứng dụng
Kỹ năng chuyên môn: Truy vấn, tổ chức, phân tích dữ liệu, Cơ sở dữ liệu quan hệ RDBMS, NoSQL, Thiết kế lập trình cho các hệ thống như hệ thống Data warehouse, Data lake, lakehouse, API, CI/CD, SSIS, Datastage, ODI, Kafka, Spark, Nifi, Airflow, DBT, Databrick, Redshift
Yêu cầu: Đại học hoặc cao hơn liên quan đến 1 trong các ngành kinh tế, tài chính, ngân hàng, hoặc công nghệ thông tin, khoa học máy tính, toán tin ứng dụng. Tối thiểu 4 năm trong lĩnh vực quản lý dữ liệu/báo cáo/phân tích/học máy. Truy vấn, tổ chức, phân tích dữ liệu. Sử dụng các công nghệ cập nhật để xử lý dữ liệu để phát triển và vận hành ngân hàng, tài chính ngân hàng. Triển khai cùng và quản lý đối tác công nghệ thông tin. Cơ sở dữ liệu quan hệ quan hệ RDBMS, NoSQL. Thiết kế lập trình cho các hệ thống như hệ thống Data warehouse, Data lake, lakehouse, API, CI/CD, các dịch vụ xử lý dữ liệu và luồng dữ liệu dạng batch/stream, quản lý luồng vận hành ETL, ELT: SSIS, Datastage, ODI, Kafka, Spark, Nifi, Airflow, DBT, Databrick, Redshift v.v...
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P21

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có 4 năm kinh nghiệm phát triển Backend bằng Go, chủ yếu trong lĩnh vực Fintech, thanh toán điện tử và thương mại điện tử. Công việc tập trung vào xây dựng dịch vụ xử lý giao dịch, tối ưu API và hỗ trợ xử lý sự cố production. Mong muốn tiếp tục phát triển chuyên môn Backend, đặc biệt với Microservices, gRPC và các hệ thống có yêu cầu cao về hiệu năng, độ ổn định.

HỌC VẤN

Kỹ sư Công nghệ thông tin
Trường đại học kỹ thuật công lập

KỸ NĂNG CHUYÊN MÔN

- Ngôn ngữ: Go.
- Backend Framework: Gin Framework.
- Database: PostgreSQL, Redis.
- Kiến trúc và giao tiếp dịch vụ: Microservices, gRPC, Apache Kafka.
- Container: Docker, Kubernetes cơ bản.
- Monitoring: Prometheus, Grafana.
- Công cụ: Git, GitLab CI, Linux, Nginx.
- Testing: Unit Testing.

KỸ NĂNG MỀM

- Tiếng Anh B2, đọc hiểu tài liệu chuyên sâu và trao đổi kỹ thuật tốt.
- Phối hợp với các thành viên trong nhóm để phân tích và xử lý sự cố production.
- Có khả năng tập trung tìm nguyên nhân lỗi và cải thiện chất lượng API.
- Chủ động theo dõi trạng thái dịch vụ trong quá trình vận hành.

KINH NGHIỆM LÀM VIỆC

Backend Developer
Công ty Công nghệ Thanh toán Minh Việt
10/2022 – 10/2026 (4 năm)

- Phát triển Backend bằng Go và Gin Framework cho các dịch vụ thanh toán, xử lý giao dịch và các chức năng liên quan.
- Sử dụng PostgreSQL, Redis và gRPC trong quá trình xây dựng dịch vụ, hỗ trợ truy xuất dữ liệu và giao tiếp giữa các thành phần hệ thống.
- Tham gia phát triển dịch vụ theo kiến trúc Microservices, sử dụng Apache Kafka và Docker trong quá trình triển khai.
- Phối hợp cùng nhóm tối ưu API, theo dõi hoạt động bằng Prometheus, Grafana và xử lý các sự cố phát sinh trên production.

DỰ ÁN

Dịch vụ xử lý giao dịch thanh toán điện tử

Phát triển và bảo trì các thành phần Backend phục vụ luồng giao dịch. Tham gia tối ưu API và hỗ trợ xử lý lỗi trong quá trình vận hành thực tế.

Công nghệ: Go, Gin, PostgreSQL, Redis, gRPC, Apache Kafka, Docker.
```

### JD

```
Vị trí: Nhà phân tích kinh doanh
Kinh nghiệm: 3 năm
Học vấn: Tốt nghiệp đại học trở lên chuyên ngành Công nghệ thông tin, Tài chính hoặc lĩnh vực có liên quan
Kỹ năng chuyên môn: Sử dụng các tool hỗ trợ cho việc xây dựng tài liệu phân tích yêu cầu và prototype, Hiểu về Core Chứng khoán
Yêu cầu: Tốt nghiệp đại học trở lên chuyên ngành Công nghệ thông tin, Tài chính hoặc lĩnh vực có liên quan. Có ít nhất 03 năm kinh nghiệm tham gia các dự án phát triển hệ thống/ quản lý dự án/ phát triển sản phẩm/ xây dựng quy trình tại các Ngân hàng, công ty tài chính, công ty chứng khoán...Có kinh nghiệm về sử dụng các tool hỗ trợ cho việc xây dựng tài liệu phân tích yêu cầu và prototype. Từng làm việc với Core Flex là một lợi thế. Từng làm việc về sản phẩm cấu trúc cho công ty chứng khoán là một lợi thế. Có nền tảng phân tích mô hình tài chính trong nước là 1 lợi thế. Hiểu về Core Chứng khoán. Nắm được các nghiệp vụ chứng khoán. Có kỹ năng phân tích chứng khoán (bao gồm phân tích cơ bản và phân tích kỹ thuật). Có khả năng làm việc nhóm tốt. Trung thực, chủ động trong công việc, có tinh thần trác
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P22

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi tốt nghiệp ngành Thống kê kinh tế và có 8 tháng thực tập phân tích dữ liệu Digital Marketing tại agency quảng cáo. Tôi muốn phát triển chuyên môn về Marketing Analytics, đặc biệt trong việc theo dõi hiệu quả chiến dịch, phân tích marketing funnel và trực quan hóa dữ liệu. Mục tiêu của tôi là nâng cao khả năng sử dụng SQL, BigQuery và Looker Studio để hỗ trợ việc đánh giá hoạt động marketing dựa trên số liệu.

HỌC VẤN

Cử nhân Thống kê kinh tế
Đại học công lập khối kinh tế.

Có nền tảng kiến thức về thống kê, xử lý và phân tích số liệu kinh tế.

KỸ NĂNG CHUYÊN MÔN

- Google Sheets, Microsoft Excel: Tổng hợp và xử lý bảng dữ liệu.
- SQL cơ bản, Google BigQuery cơ bản: Truy vấn dữ liệu phục vụ báo cáo.
- Looker Studio: Xây dựng dashboard trực quan.
- Google Analytics 4: Theo dõi dữ liệu marketing ở mức cơ bản.
- Marketing Funnel Analysis: Phân tích các giai đoạn trong phễu marketing.
- Data Cleaning, Data Visualization.
- Google Tag Manager cơ bản, Python pandas cơ bản.
- Canva; kiến thức lý thuyết về A/B Testing.

KỸ NĂNG MỀM

- Tổng hợp và trình bày thông tin marketing theo yêu cầu báo cáo.
- Phối hợp trong quá trình chuẩn bị dữ liệu đánh giá chiến dịch.
- Tiếng Việt: Bản ngữ.
- Tiếng Anh: B2, đọc hiểu tài liệu và giao tiếp công việc.

KINH NGHIỆM LÀM VIỆC

Marketing Data Analyst Intern
Công ty TNHH Truyền thông BlueWave
02/2026 – 10/2026 (8 tháng)

- Thu thập và tổng hợp dữ liệu từ các nền tảng marketing vào Google Sheets, tạo bảng dữ liệu phục vụ theo dõi chiến dịch.
- Hỗ trợ làm sạch và kiểm tra dữ liệu quảng cáo trước khi lập báo cáo.
- Sử dụng Looker Studio để trực quan hóa số liệu, hỗ trợ nhóm marketing đánh giá hiệu quả chiến dịch.
- Hỗ trợ tổng hợp thông tin theo marketing funnel và chuẩn bị báo cáo định kỳ cho người phụ trách.

DỰ ÁN

Báo cáo hiệu quả chiến dịch Digital Marketing

Tham gia nhóm tổng hợp dữ liệu quảng cáo từ nhiều nền tảng. Sử dụng Google Sheets để xử lý dữ liệu và Looker Studio để thể hiện kết quả. Công việc tập trung vào chuẩn bị dữ liệu, cập nhật báo cáo và hỗ trợ phân tích hiệu quả chiến dịch theo yêu cầu của nhóm.
```

### JD

```
Vị trí: Lập Trình Viên PHP Laravel Backend
Kinh nghiệm: 2 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: PHP, Laravel, MySQL, PostgreSQL, MongoDB, HTML, CSS, JavaScript, Git
Yêu cầu: Tối thiểu 2 năm kinh nghiệm làm việc với PHP, đặc biệt là Laravel Framework. Hiểu biết sâu về các kiến trúc RESTful API và cách triển khai chúng. Kinh nghiệm làm việc với hệ quản trị cơ sở dữ liệu (MySQL, PostgreSQL, hoặc MongoDB). Thành thạo HTML, CSS, JavaScript (ưu tiên có kinh nghiệm làm việc với các framework như Vue.js, ReactJS, React Native là điểm cộng). Hiểu biết về các công cụ quản lý mã nguồn như Git. Có khả năng phân tích, xử lý vấn đề và làm việc độc lập hoặc theo nhóm. Kỹ năng giao tiếp tốt, sẵn sàng học hỏi và tiếp thu công nghệ mới.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P23

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi là Flutter Developer với khoảng 3,3 năm kinh nghiệm phát triển và duy trì ứng dụng di động, chủ yếu trong lĩnh vực quản lý bán hàng và logistics. Trong quá trình làm việc, tôi tập trung vào việc hoàn thiện các chức năng hiện có, bổ sung tính năng theo yêu cầu và xử lý các vấn đề phát sinh trong quá trình vận hành sản phẩm.

Tôi mong muốn tiếp tục phát triển chuyên môn về Flutter, đặc biệt là tổ chức mã nguồn theo Clean Architecture, quản lý trạng thái ứng dụng và nâng cao chất lượng sản phẩm thông qua kiểm thử. Mục tiêu của tôi là tham gia sâu hơn vào quá trình phát triển sản phẩm, đồng thời vận dụng kinh nghiệm bảo trì và mở rộng ứng dụng đã tích lũy.

HỌC VẤN

Tốt nghiệp Đại học – Ngành Công nghệ thông tin
Hệ đào tạo: Chính quy, trường đại học công lập.

KỸ NĂNG CHUYÊN MÔN

- Ngôn ngữ lập trình: Dart.
- Framework: Flutter, phát triển giao diện bằng hệ thống Widget.
- State Management: BLoC.
- Kiến trúc: Clean Architecture ở mức cơ bản.
- Networking và Navigation: Dio, GoRouter.
- Lưu trữ dữ liệu: SQLite, Hive.
- Firebase: Firebase Crashlytics, Firebase Cloud Messaging.
- Tích hợp bản đồ: Google Maps SDK.
- Testing: Flutter Widget Testing, Postman.
- Version Control và CI: Git, GitLab CI cơ bản.

KỸ NĂNG MỀM

- Có kinh nghiệm theo dõi và duy trì một sản phẩm trong thời gian dài, xử lý các yêu cầu thay đổi liên tục.
- Đọc và viết tài liệu kỹ thuật tiếng Anh khá.
- Giao tiếp tiếng Anh trong công việc ở mức trung bình.

KINH NGHIỆM LÀM VIỆC

Flutter Developer
Công ty TNHH Giải pháp Công nghệ Minh Phát
06/2023 – 10/2026 (3 năm 4 tháng)

- Tham gia duy trì và mở rộng ứng dụng Flutter phục vụ quản lý đội ngũ bán hàng, thực hiện các thay đổi về giao diện và luồng thao tác theo nhu cầu vận hành.
- Sử dụng BLoC để quản lý trạng thái, Dio để xử lý giao tiếp dữ liệu và GoRouter để tổ chức luồng chuyển màn hình, giúp các chức năng được triển khai nhất quán với cấu trúc ứng dụng hiện có.
- Làm việc với SQLite, Hive và các dịch vụ Firebase trong quá trình phát triển, hỗ trợ lưu trữ dữ liệu, thông báo và theo dõi lỗi ứng dụng.
- Thực hiện Flutter Widget Testing cho các thành phần giao diện, sử dụng Git để quản lý thay đổi mã nguồn và tham gia các công việc CI cơ bản trên GitLab.

DỰ ÁN

Ứng dụng quản lý đội ngũ bán hàng

Công nghệ: Flutter, Dart, BLoC, Dio, GoRouter, SQLite, Firebase Crashlytics.

Ứng dụng hỗ trợ hoạt động quản lý bán hàng trên thiết bị di động. Công việc của tôi tập trung vào bảo trì chức năng, điều chỉnh giao diện và mở rộng các luồng nghiệp vụ trong quá trình sử dụng thực tế.
```

### JD

```
Vị trí: Android Developer
Kinh nghiệm: 4 năm
Học vấn: Tốt nghiệp Đại học chính quy chuyên ngành CNTT, kinh tế, tài chính ngân hàng
Kỹ năng chuyên môn: Kotlin, Android SDK, Android Studio, Git
Yêu cầu: Tốt nghiệp Đại học chính quy chuyên ngành CNTT, kinh tế, tài chính ngân hàng,... Có từ 4 năm kinh nghiệm phát triển Android bằng Koltin. Hiểu biết vững chắc về sự phát triển toàn diện của thiết bị di động. Cấu trúc dữ liệu và nền tảng thuật toán tốt. Hiểu ít nhất một trong các kiến ​​trúc sau: MVP, MVVM, Clean Architecture. Biết một số mẫu thiết kế (singleton, Factory, kho lưu trữ dữ liệu...). Làm quen với công nghệ mới như Jetpack Compose, Android Material 3, AndroidX, Thành phần kiến ​​trúc Android (LiveData, ViewModel), v.v. Thân thuộc với các ứng dụng di động và phát triển, bao gồm việc sử dụng phần cứng như Accelerometers, Cameras, and Gyroscopes. Thoải mái làm việc như một phần của nhóm đa chức năng và với mã do người khác viết, bao gồm sửa lỗi và tái cấu trúc mã kế thừa. Hiểu biết t
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P24

### CV

```
MỤC TIÊU NGHỀ NGHIỆP
Tôi có 3,5 năm kinh nghiệm làm việc với sản phẩm phần mềm, bắt đầu từ Frontend Development trước khi chuyển sang Product Design. Nền tảng Công nghệ thông tin giúp tôi phối hợp với đội phát triển. Tôi muốn cải thiện trải nghiệm người dùng SaaS và xây dựng Design System nhất quán.

HỌC VẤN
Cử nhân Công nghệ thông tin, tốt nghiệp tại một trường đại học công lập. Tự học thiết kế sản phẩm số.

KỸ NĂNG CHUYÊN MÔN
- Figma, Product Design, Interaction Design và Responsive Design.
- UX Research, User Journey Mapping, Usability Testing và phân tích hành vi người dùng.
- Design System, Interactive Prototyping, Design Handoff; Design Tokens ở mức cơ bản.
- Google Analytics 4, Hotjar, Dovetail; kiến thức HTML/CSS từ giai đoạn làm Frontend.

KỸ NĂNG MỀM
- Trao đổi với đội phát triển bằng bản prototype và tài liệu Design Handoff, giúp thống nhất cách triển khai giao diện.
- Trình bày giải pháp thiết kế bằng tiếng Anh ở mức B2; tiếng Việt là ngôn ngữ bản ngữ.

KINH NGHIỆM LÀM VIỆC

Frontend Developer – Công ty Phần mềm Đường Mây (04/2023 – 03/2024)
- Tham gia xây dựng giao diện phần mềm bằng HTML/CSS theo bản thiết kế được bàn giao.
- Điều chỉnh cách hiển thị giao diện ở các kích thước màn hình khác nhau theo yêu cầu Responsive Design.
- Đối chiếu giao diện triển khai với thiết kế khi phối hợp cùng đội sản phẩm.

Product Designer – Công ty Công nghệ Luồng Việt (04/2024 – 09/2026)
- Thiết kế luồng người dùng cho sản phẩm SaaS phục vụ doanh nghiệp và nghiệp vụ logistics.
- Xây dựng User Journey Mapping và Interactive Prototyping để kiểm tra các bước thao tác trước khi bàn giao.
- Sử dụng Hotjar, Google Analytics 4 và Dovetail hỗ trợ tổng hợp quan sát người dùng và kết quả Usability Testing.
- Duy trì các thành phần trong Design System, bàn giao thiết kế qua Figma để đội phát triển tái sử dụng nhất quán.

DỰ ÁN
Cải thiện luồng thao tác trong phần mềm doanh nghiệp: tham gia UX Research, tạo prototype có tương tác, kiểm tra tính dễ sử dụng và chuẩn hóa thành phần giao diện. Đầu ra gồm prototype và tài liệu bàn giao.
```

### JD

```
Vị trí: Nhân Viên Thiết Kế
Kinh nghiệm: 3 năm
Học vấn: Tốt nghiệp Đại học chuyên ngành Thiết kế đồ họa hoặc các chuyên ngành liên quan
Kỹ năng chuyên môn: Adobe Photoshop, Illustrator, InDesign, CorelDRAW
Yêu cầu: Tốt nghiệp Đại học chuyên ngành Thiết kế đồ họa hoặc các chuyên ngành liên quan. Có ít nhất 3 năm kinh nghiệm làm việc trong lĩnh vực thiết kế đồ họa, đặc biệt là trong ngành hàng tiêu dùng nhanh (FMCG). Có kinh nghiệm thiết kế sản phẩm mỹ phẩm hoặc lĩnh vực làm đẹp là 1 lợi thế. Thành thạo các phần mềm thiết kế đồ họa chuyên nghiệp như Adobe Photoshop, Illustrator, InDesign, CorelDRAW. Nắm vững các nguyên tắc thiết kế đồ họa, bố cục, màu sắc, typography. Có gu thẩm mỹ tốt, khả năng sáng tạo cao, tư duy hình ảnh tốt. Có hiểu biết về các nền tảng mạng xã hội và cách thức hoạt động của chúng. Khả năng làm việc độc lập và làm việc nhóm tốt. Có khả năng quản lý thời gian hiệu quả, đáp ứng tiến độ công việc. Khả năng giao tiếp tốt, trình bày ý tưởng rõ ràng, thuyết phục. Có tinh thần trách nhiệ
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P25

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có 7 năm 6 tháng kinh nghiệm trong lĩnh vực DevOps và Site Reliability Engineering, chủ yếu làm việc với các hệ thống giao dịch và nền tảng dịch vụ trực tuyến có yêu cầu cao về tính sẵn sàng. Tôi định hướng phát triển chuyên sâu về reliability engineering, tự động hóa hạ tầng và quản lý chất lượng vận hành hệ thống. Mong muốn tiếp tục tham gia thiết kế các nền tảng có khả năng mở rộng và xây dựng quy trình ứng phó sự cố hiệu quả.

HỌC VẤN

Tốt nghiệp Đại học chuyên ngành Khoa học máy tính tại một trường đại học kỹ thuật công lập ở Hà Nội.

KỸ NĂNG CHUYÊN MÔN

- Cloud & Container Orchestration: Amazon EKS, Kubernetes.
- Infrastructure as Code: Terraform, Terragrunt.
- GitOps & Configuration: FluxCD, Kustomize.
- Service Mesh: Istio Service Mesh.
- Observability: Prometheus, Grafana Loki, OpenTelemetry.
- Automation & Operating System: Go, Linux.
- AWS Services: AWS Route 53, AWS IAM.
- Reliability Engineering: SLO, Error Budget, Incident Response.

KỸ NĂNG MỀM

- Có kinh nghiệm dẫn dắt nhóm kỹ thuật nhỏ và phân chia công việc cải thiện độ tin cậy hệ thống.
- Khả năng phân tích sự cố, phối hợp xử lý vấn đề trong môi trường vận hành có yêu cầu sẵn sàng cao.
- Chủ động trao đổi và thống nhất phương án kỹ thuật với các thành viên liên quan.
- Tiếng Anh C1, có thể chủ trì họp kỹ thuật và viết tài liệu thiết kế bằng tiếng Anh.

KINH NGHIỆM LÀM VIỆC

Senior Site Reliability Engineer – Công ty Công nghệ Thanh toán Đông Dương
04/2022 – 10/2026 (4 năm 6 tháng)

- Tham gia vận hành hệ thống giao dịch trên Amazon EKS và Kubernetes, tập trung duy trì độ tin cậy và khả năng phục hồi dịch vụ.
- Dẫn dắt nhóm kỹ thuật nhỏ trong việc cải tiến quy trình triển khai tự động bằng Terraform, Terragrunt và FluxCD.
- Thiết lập các chỉ số SLO, theo dõi Error Budget và phối hợp thực hiện Incident Response khi xảy ra sự cố.
- Sử dụng Prometheus, Grafana Loki và OpenTelemetry để tăng khả năng quan sát, hỗ trợ phân tích nguyên nhân sự cố.

DevOps Engineer – Công ty Nền tảng Số Minh Long
04/2019 – 04/2022 (3 năm)

- Triển khai và quản lý các ứng dụng trên Kubernetes, sử dụng Linux làm môi trường vận hành chính.
- Xây dựng cấu hình hạ tầng với Terraform và quản lý cấu hình ứng dụng bằng Kustomize.
- Tham gia cấu hình AWS IAM, AWS Route 53 và sử dụng Go để phát triển các tiện ích phục vụ tự động hóa vận hành.
- Hỗ trợ triển khai Istio Service Mesh nhằm quản lý giao tiếp giữa các dịch vụ trong hệ thống.

DỰ ÁN

Nâng cao độ tin cậy nền tảng giao dịch điện tử

Tham gia cải tiến kiến trúc vận hành cho hệ thống giao dịch có yêu cầu sẵn sàng cao trên Amazon EKS. Áp dụng GitOps với FluxCD, sử dụng Terraform và Terragrunt để quản lý hạ tầng. Đồng thời xây dựng cách theo dõi SLO, Error Budget và quy trình Incident Response để nhóm kỹ thuật có cơ sở đánh giá chất lượng dịch vụ và xử lý sự cố nhất quán hơn.
```

### JD

```
Vị trí: Chuyên gia phân tích/phân tích kinh doanh hệ thống - TA171
Kinh nghiệm: 5 năm
Học vấn: A bachelor's in computer science or related field
Kỹ năng chuyên môn: Core Banking, Card service systems, OLTP software system, microservices architecture, Relational database (MS SQL, MySQL, Postgre, Oracle)
Yêu cầu: Educational Qualifications: A bachelor's in computer science or related field. Relevant Knowledge/ Expertise: Minimum of +5 years hands on experience with at least one of the following Banking system (Core Banking, Card,...). Have experience and expert knowledge in Card service systems or relating. Have strong experience in design solution for Card Products and/or Card services. Have strong experience in solution design for OLTP software system in microservices architecture and/or strong experience in Relational database (MS SQL, MySQL, Postgre, Oracle,..). Understand Banking knowledge (priority for Card businesses). Have experience with ISO messages and International Card Policies (Visa. MasterCard,...). Have experience data flow as well as processes of ATM, CDM, POS,... An understanding 
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P26

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi tốt nghiệp Cao đẳng Công nghệ thông tin, có khoảng 8 tháng kinh nghiệm làm Backend tại startup, gồm 4 tháng thực tập và 4 tháng cộng tác bán thời gian. Tôi đã tham gia xây dựng API cho ứng dụng đặt lịch bằng Node.js và Express.js. Mong muốn tiếp tục làm việc với Backend JavaScript, TypeScript, MongoDB và nâng cao khả năng phát triển API, xử lý nghiệp vụ thực tế.

HỌC VẤN

Cao đẳng Công nghệ thông tin
Trường cao đẳng kỹ thuật

Tập trung học JavaScript, lập trình Backend và làm việc với cơ sở dữ liệu.

KỸ NĂNG CHUYÊN MÔN

- JavaScript, TypeScript cơ bản.
- Node.js, Express.js.
- MongoDB, Mongoose.
- RESTful API, JWT Authentication.
- Git, NPM, Postman.
- Linux cơ bản.
- Tiếng Anh A2-B1, đọc hiểu tài liệu kỹ thuật cơ bản.

KỸ NĂNG MỀM

- Phối hợp với các thành viên trong nhóm khi phát triển API.
- Tiếp nhận yêu cầu và chỉnh sửa chức năng theo phản hồi.
- Có khả năng tự tìm hiểu tài liệu để giải quyết các lỗi thường gặp.
- Làm việc theo phạm vi nhiệm vụ được phân công.

KINH NGHIỆM LÀM VIỆC

Backend Intern
Công ty TNHH Công nghệ Lịch Việt
01/2026 – 04/2026 (4 tháng)

- Tham gia phát triển RESTful API cho ứng dụng đặt lịch trực tuyến sử dụng Node.js và Express.js.
- Hỗ trợ xử lý các thao tác tạo, cập nhật và truy vấn dữ liệu lịch hẹn với MongoDB, Mongoose.
- Sử dụng Postman để kiểm tra API và Git để quản lý mã nguồn trong quá trình thực tập.

Part-time Backend Developer
Công ty TNHH Công nghệ Lịch Việt
05/2026 – 08/2026 (4 tháng)

- Tiếp tục hỗ trợ phát triển và chỉnh sửa API theo yêu cầu của ứng dụng đặt lịch.
- Tham gia xử lý lỗi liên quan đến request, response và dữ liệu trả về từ Backend.
- Phối hợp với nhóm kỹ thuật kiểm tra chức năng trước khi chuyển sang các bước tiếp theo.

DỰ ÁN

Ứng dụng đặt lịch dịch vụ trực tuyến

Công nghệ: Node.js, Express.js, MongoDB, Mongoose, JavaScript.

Tham gia phần Backend của hệ thống, thực hiện các API phục vụ quản lý lịch hẹn và dữ liệu liên quan. Công việc được thực hiện theo phân công của nhóm, có sự hỗ trợ và kiểm tra từ các thành viên có kinh nghiệm.
```

### JD

```
Vị trí: Thực Tập Sinh Lập Trình Web
Kinh nghiệm: Không yêu cầu
Học vấn: Sinh viên năm cuối hoặc mới tốt nghiệp khối ngành CNTT (Kỹ thuật phần mềm/Công nghệ phần mềm)
Kỹ năng chuyên môn: lập trình web, web server, database, html, css, javascript, PHP, Nodejs, Java, Golang, ReactJs, NextJS, Git
Yêu cầu: Yêu cầu ứng viên: Sinh viên năm cuối hoặc mới tốt nghiệp khối ngành CNTT (Kỹ thuật phần mềm/Công nghệ phần mềm). Nắm vững kiến thức cơ bản của lập trình web (web server, database, html, css, javascript ...) và các khái niệm của lập trình hướng đối tượng. Có kinh nghiệm thực tiễn qua các dự án cá nhân hoặc các khóa học lập trình ứng dụng. Đã từng làm việc với PHP, Nodejs, Java, Golang hoặc ReactJs, NextJS là một lợi thế. Hiểu về quá trình thiết kế và chuẩn hóa DB Schema. Có kiến thức về Git. Ưu tiên các bạn có khả năng đọc hiểu, tự học hỏi tốt từ các tài liệu bằng tiếng anh. Năng động, nhiệt tình, ham học hỏi và trách nhiệm trong công việc. Có laptop cá nhân.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P27

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Có khoảng 1,6 năm kinh nghiệm DevOps tại công ty phát triển sản phẩm SaaS. Đã tham gia duy trì GitLab CI/CD pipeline, triển khai dịch vụ bằng Docker và Amazon ECS. Mong muốn tiếp tục phát triển chuyên môn về tự động hóa triển khai, quản lý hạ tầng AWS và tối ưu quy trình vận hành ứng dụng.

HỌC VẤN

Đại học tư thục tại TP. Hồ Chí Minh
Chuyên ngành: Kỹ thuật phần mềm
Trình độ: Đại học

KỸ NĂNG CHUYÊN MÔN

- Hệ thống: Linux Administration.
- CI/CD: GitLab CI/CD, Git.
- Container: Docker, Amazon ECS, AWS ECR.
- Infrastructure: Terraform.
- AWS: IAM, CloudWatch, Application Load Balancer, Secrets Manager.
- Scripting: Python Scripting, Shell Scripting.
- Database: MySQL.
- Ngoại ngữ: Tiếng Anh B2, đọc viết tài liệu kỹ thuật tốt, giao tiếp công việc cơ bản.

KỸ NĂNG MỀM

- Phối hợp với kỹ sư cấp cao trong việc thay đổi hạ tầng.
- Làm việc theo kế hoạch và tài liệu thiết kế có sẵn.
- Chủ động kiểm tra kết quả sau khi triển khai.
- Trao đổi các vấn đề kỹ thuật với thành viên trong nhóm.

KINH NGHIỆM LÀM VIỆC

Công ty TNHH Công nghệ CloudVista
Vị trí: DevOps Engineer
Thời gian: 03/2025 - 10/2026 (1 năm 7 tháng, xấp xỉ 1,6 năm)

- Duy trì GitLab CI/CD pipeline cho các dịch vụ SaaS, hỗ trợ tự động hóa quá trình build và triển khai ứng dụng.
- Đóng gói ứng dụng bằng Docker, quản lý image trên AWS ECR và hỗ trợ triển khai các service lên Amazon ECS.
- Sử dụng Terraform để thực hiện thay đổi tài nguyên AWS theo thiết kế được kỹ sư cấp cao phê duyệt.
- Theo dõi log và thông tin vận hành bằng Amazon CloudWatch, kiểm tra trạng thái dịch vụ sau mỗi lần cập nhật.

DỰ ÁN

Duy trì hạ tầng AWS cho ứng dụng SaaS

- Tham gia vận hành các service container trên Amazon ECS.
- Hỗ trợ cấu hình AWS IAM, Application Load Balancer và quản lý thông tin ứng dụng qua AWS Secrets Manager.
- Sử dụng Python và Shell Scripting để hỗ trợ các thao tác vận hành lặp lại.
- Kết quả: Duy trì quy trình triển khai cho các dịch vụ được phân công, thực hiện các thay đổi hạ tầng theo thiết kế và kiểm tra kết quả sau triển khai.
```

### JD

```
Vị trí: Chuyên Viên Vận Hành Hệ Thống Microsoft Exchange Hybrid
Kinh nghiệm: 2 năm
Học vấn: College degree or bachelor degree in IT
Kỹ năng chuyên môn: Microsoft Exchange, Azure AD, SharePoint, Teams, email protocols, Cloud platforms, Azure, Azure DevOps, Docker, Kubernetes, CI/CD tools, Jenkins, GitLab
Yêu cầu: College degree or bachelor degree in IT. Minimum 2 years of experience operating Microsoft Exchange hybrid or on-premises systems. In-depth knowledge of Microsoft Exchange, Azure AD, SharePoint, Teams, and email protocols. Strong troubleshooting, analytical, and teamwork skills. Nice to have: Experience with Cloud platforms, especially Azure and Azure DevOps. Familiarity with Docker, Kubernetes, and CI/CD tools (Jenkins, GitLab, etc.). Good English communication skills.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P28

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có khoảng 3,2 năm làm frontend, chủ yếu phát triển và duy trì các hệ thống quản lý nội bộ sử dụng Vue 2. Tôi mong muốn tiếp tục làm việc với những sản phẩm có nghiệp vụ rõ ràng, nơi có thể tận dụng kinh nghiệm xử lý dashboard, biểu mẫu và tích hợp dữ liệu từ REST API. Trong thời gian tới, tôi muốn mở rộng phạm vi công việc sang các chức năng mới và từng bước áp dụng Vue 3 vào quá trình phát triển.

HỌC VẤN

Tốt nghiệp đại học ngành Công nghệ phần mềm tại một trường đại học công lập. Kiến thức nền tảng được vận dụng vào công việc phát triển và bảo trì ứng dụng frontend phục vụ doanh nghiệp.

KỸ NĂNG CHUYÊN MÔN

Sử dụng JavaScript ES6+, Vue 2, Vuex và Vue Router để xây dựng các màn hình nghiệp vụ, quản lý trạng thái và điều hướng. Có kinh nghiệm SCSS, Element UI, REST API integration, Webpack và Git. Ngoài ra, tôi sử dụng Axios, Lodash, Postman và Jira trong quá trình làm việc; đã tìm hiểu các chức năng cơ bản của Vue 3.

KỸ NĂNG MỀM

Có thói quen trao đổi yêu cầu của từng biểu mẫu trước khi chỉnh sửa, ghi nhận đầu việc trên Jira và kiểm tra lại giao diện sau khi hoàn thành. Tiếng Anh B1, có thể đọc tài liệu kỹ thuật và trao đổi công việc qua email.

KINH NGHIỆM LÀM VIỆC

Frontend Developer – Công ty TNHH Giải pháp Kho vận An Phát
08/2023 – 10/2026 (3 năm 2 tháng)

- Duy trì các dashboard Vue 2 cho nghiệp vụ logistics và quản lý kho, cập nhật giao diện theo những thay đổi trong quy trình nội bộ.
- Phát triển và chỉnh sửa biểu mẫu quản lý bằng Element UI, SCSS; sử dụng Vuex và Vue Router để giữ dữ liệu và luồng thao tác nhất quán.
- Tích hợp REST API qua Axios, dùng Postman để đối chiếu dữ liệu và xử lý các trường hợp hiển thị chưa đúng trên màn hình.
- Quản lý thay đổi mã nguồn bằng Git, theo dõi yêu cầu và lỗi trên Jira để bàn giao các bản cập nhật.

DỰ ÁN

Hệ thống dashboard và biểu mẫu quản lý kho: Tham gia duy trì các trang theo dõi dữ liệu vận hành và xử lý biểu mẫu nội bộ. Công việc tập trung vào cải tiến khả năng sử dụng và giữ cho các chức năng hiện có hoạt động nhất quán.
```

### JD

```
Vị trí: Mobile Developer (Android Or IOS)
Kinh nghiệm: 4 năm
Học vấn: Bachelor's degree in computer science, Software Engineering, or a related field
Kỹ năng chuyên môn: Kotlin, Swift, RESTful APIs, Git
Yêu cầu: [Required] Education: Bachelor's degree in computer science, Software Engineering, or a related field. Experience: At least 4 years of experience in mobile development. Technical Skills: Strong proficiency in Kotlin (for Android) or Swift (for iOS). Experience with developing and integrating RESTful APIs. Familiarity with mobile UI/UX design principles and best practices. Experience with Git version control. Strong problem-solving skills and ability to work in a fast-paced environment. [Nice to have] Knowledge of MS-SQL/IIS Server. Experience with Firebase Cloud Messaging (FCM) / Apple Push Notification Service (APNS). Familiarity with CI/CD tools (Jenkins) for automated deployment. Experience with Android Management API for enterprise applications. Knowledge of Microsoft 365 Graph API for
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P29

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có khoảng 3,4 năm kinh nghiệm làm Business Analyst trong lĩnh vực InsurTech và bảo hiểm phi nhân thọ, tập trung vào hệ thống quản lý hợp đồng và giải quyết bồi thường. Với nền tảng từng làm Manual QA, tôi chú trọng tính rõ ràng của yêu cầu, quy tắc nghiệp vụ và tiêu chí nghiệm thu. Mong muốn tiếp tục phát triển chuyên môn phân tích nghiệp vụ bảo hiểm, nâng cao chất lượng tài liệu và khả năng phối hợp giữa các bộ phận trong dự án.

HỌC VẤN

Cử nhân Kỹ thuật phần mềm – Trường đại học công lập khối công nghệ.

KỸ NĂNG CHUYÊN MÔN

- Phân tích nghiệp vụ bảo hiểm, đặc biệt là quản lý hợp đồng và xử lý bồi thường.
- Business Process Modeling với Bizagi Modeler, sử dụng BPMN 2.0 để mô hình hóa quy trình.
- Xây dựng tài liệu BRD, FRD, SRS và quản lý Requirement Traceability.
- SQL Server, T-SQL phục vụ truy vấn và đối chiếu dữ liệu nghiệp vụ.
- API Requirement Analysis, Swagger OpenAPI và Postman.
- UAT Planning, Test Case Review và quản lý Change Request.
- PlantUML phục vụ mô tả luồng xử lý hệ thống.

KỸ NĂNG MỀM

- Giao tiếp và phối hợp với Development Team, QA Team trong quá trình làm rõ yêu cầu.
- Trao đổi với các bên nghiệp vụ để thống nhất phạm vi và cách xử lý thay đổi.
- Tiếng Anh B2, có khả năng đọc tài liệu chuyên môn và làm việc với nhóm kỹ thuật quốc tế.

KINH NGHIỆM LÀM VIỆC

Business Analyst – Công ty TNHH Công nghệ Bảo hiểm An Tín
05/2023 – 10/2026 (3 năm 5 tháng)

- Phân tích và làm rõ yêu cầu cho hệ thống quản lý hợp đồng bảo hiểm phi nhân thọ, xây dựng BRD và FRD để Development Team triển khai chức năng.
- Sử dụng Bizagi Modeler và BPMN 2.0 mô hình hóa quy trình tiếp nhận, kiểm tra và xử lý yêu cầu bồi thường, giúp các bên thống nhất luồng nghiệp vụ.
- Phân tích yêu cầu API qua Swagger OpenAPI, sử dụng Postman và T-SQL để kiểm tra dữ liệu, hỗ trợ xác định các trường hợp xử lý chưa nhất quán.
- Lập kế hoạch UAT, review test case cùng QA Team, theo dõi Requirement Traceability và Change Request để bảo đảm yêu cầu được kiểm tra trước nghiệm thu.

DỰ ÁN

Hệ thống quản lý hợp đồng và bồi thường bảo hiểm

Tham gia phân tích quy trình nghiệp vụ từ quản lý thông tin hợp đồng đến xử lý hồ sơ bồi thường. Phụ trách tài liệu yêu cầu, mô hình hóa quy trình và phối hợp kiểm thử nghiệm thu. Kinh nghiệm Manual QA giúp tôi tập trung vào những quy tắc nghiệp vụ dễ gây nhầm lẫn và các tình huống cần xác nhận với người dùng.
```

### JD

```
Vị trí: Chuyên Viên Phân Tích Nghiệp Vụ
Kinh nghiệm: 4 năm
Học vấn: Tốt nghiệp đại học các ngành liên quan đến khoa học máy tính, công nghệ thông tin, kinh tế tài chính hoặc tương đương
Kỹ năng chuyên môn: Kiến thức về công nghệ thông tin, Phát triển phần mềm, UI/UX
Yêu cầu: Tốt nghiệp đại học các ngành liên quan đến khoa học máy tính, công nghệ thông tin, kinh tế tài chính hoặc tương đương. Ưu tiên ứng viên từng tham gia triển khai các hệ thống phần mềm cho Bộ, ngành, UBND, sở ban ngành, hoặc các hệ thống ERP, CRM, quản lý hành chính công. Am hiểu các mô hình phân tích nghiệp vụ, quy trình nghiệp vụ, đặc biệt trong lĩnh vực công/nhà nước là lợi thế. Ưu tiên nắm vững kiến thức về công nghệ thông tin và phát triển phần mềm. Hiểu biết sâu về những quy trình, nghiệp vụ thông dụng liên quan đến kinh tế, tài chính, quản lý doanh nghiệp. Có kiến thức về UI/UX là một lợi thế. Khả năng nắm bắt, học hỏi kỹ thuật mới nhanh. Tư duy logic tốt + khả năng tự học, chủ động, cầu tiến trong công việc. Có khả năng làm việc độc lập, làm việc nhóm, giải quyết vấn đề và chịu được 
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P30

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi là sinh viên mới tốt nghiệp ngành Công nghệ thông tin, có 5 tháng thực tập phát triển ứng dụng web. Trong thời gian thực tập, tôi được tham gia xây dựng giao diện và API cho hệ thống quản lý khóa học. Mong muốn tiếp tục phát triển chuyên môn về React.js, Node.js và Express.js, đồng thời tích lũy kinh nghiệm thực tế trong quá trình phát triển sản phẩm phần mềm.

HỌC VẤN

Đại học công lập – Ngành Công nghệ thông tin
Trình độ: Đại học, đã tốt nghiệp.

KỸ NĂNG CHUYÊN MÔN

- Frontend: JavaScript ES6+, React.js cơ bản, HTML5, CSS3, Bootstrap.
- Backend: Node.js, Express.js, xây dựng RESTful API.
- Database: MongoDB cơ bản, thao tác dữ liệu phục vụ chức năng CRUD.
- Công cụ: Git/GitHub, Postman, Figma cơ bản.
- Ngoại ngữ: Tiếng Anh B1, có khả năng đọc hiểu tài liệu kỹ thuật tương đối tốt.

KỸ NĂNG MỀM

- Có kinh nghiệm phối hợp với các thành viên trong nhóm phát triển phần mềm thông qua công việc thực tập.
- Tiếp nhận yêu cầu và thực hiện các phần việc được giao trong quá trình phát triển ứng dụng.
- Chủ động tìm hiểu tài liệu kỹ thuật khi thực hiện các chức năng mới.

KINH NGHIỆM LÀM VIỆC

Công ty TNHH Phần mềm Minh Phát
Thực tập sinh Web Developer
04/2026 – 08/2026 (5 tháng)

- Tham gia phát triển giao diện hệ thống quản lý khóa học nội bộ bằng React.js, HTML5 và CSS3.
- Sử dụng Node.js và Express.js để xây dựng các RESTful API phục vụ thao tác thêm, xem, sửa và xóa thông tin khóa học.
- Làm việc với MongoDB ở mức cơ bản để lưu trữ và truy xuất dữ liệu cho các chức năng được phân công.
- Sử dụng Postman kiểm tra các API và Git/GitHub để quản lý mã nguồn trong thời gian thực tập.

DỰ ÁN

Hệ thống quản lý khóa học nội bộ

Vai trò: Thực tập sinh phát triển Web
Công nghệ: React.js, Node.js, Express.js, MongoDB, RESTful API.

Tham gia xây dựng giao diện và các chức năng CRUD phục vụ quản lý thông tin khóa học. Phần công việc tập trung vào kết nối giao diện với API và xử lý các thao tác dữ liệu cơ bản. Dự án giúp tôi hiểu rõ hơn cách phối hợp giữa frontend, backend và database trong một ứng dụng web thực tế.
```

### JD

```
Vị trí: Nhân Viên Kinh Doanh Phần Mềm
Kinh nghiệm: Không yêu cầu
Học vấn: Cao Đẳng trở lên
Yêu cầu: Không phù hợp với các bạn thích ổn định, thích làm văn phòng xìu xìu rồi hết tháng nhận lương, không phù hợp với các bạn sợ áp doanh số, sợ áp lực. Chốt sales không phải là mình chốt bán mà là giúp khách hàng tự chốt mua. Có laptop và phương tiện di chuyển cá nhân. Sẵn sàng đi công tác tỉnh thường xuyên (bằng xe khách). Ưu tiên có kinh nghiệm làm việc tại Tech Startup, SaaS, Sales B2B, Sales phần mềm.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P31

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi là Java Backend Engineer với 7,5 năm kinh nghiệm phát triển phần mềm, chủ yếu trong lĩnh vực ngân hàng số, Fintech, thương mại điện tử và phần mềm doanh nghiệp. Trong quá trình làm việc, tôi đã tham gia phát triển các dịch vụ Backend bằng Java, Spring Boot, đồng thời trực tiếp tham gia thiết kế hệ thống theo kiến trúc Microservices.

Bên cạnh công việc lập trình, tôi có kinh nghiệm dẫn dắt nhóm 5 developer, hỗ trợ thành viên về mặt kỹ thuật và phối hợp xử lý các vấn đề hiệu năng, độ ổn định trên môi trường production. Định hướng tiếp theo của tôi là chuyên sâu hơn về System Design, xây dựng hệ thống có khả năng mở rộng tốt và phát triển năng lực Technical Mentoring.

HỌC VẤN

Kỹ sư Khoa học máy tính
Trường đại học kỹ thuật công lập

KỸ NĂNG CHUYÊN MÔN

- Ngôn ngữ và Framework: Java, Spring Boot, Spring Security.
- Database & Caching: PostgreSQL, Redis.
- Kiến trúc hệ thống: Microservices Architecture, System Design.
- Message Streaming: Apache Kafka.
- Container & Cloud: Docker, Kubernetes, AWS.
- CI/CD: Jenkins.
- Monitoring: Prometheus, Grafana.
- Testing: JUnit.
- Team Development: Technical Mentoring.

KỸ NĂNG MỀM

- Tiếng Anh C1, có thể trao đổi chuyên môn và tham gia họp kỹ thuật với khách hàng quốc tế.
- Có kinh nghiệm dẫn dắt nhóm 5 lập trình viên, hỗ trợ giải quyết các vấn đề kỹ thuật.
- Phối hợp cùng nhóm xử lý sự cố và cải thiện độ ổn định của dịch vụ.
- Có khả năng phân tích vấn đề ở góc độ kiến trúc và vận hành.

KINH NGHIỆM LÀM VIỆC

Java Backend Engineer / Technical Lead
Công ty Cổ phần Công nghệ Tài chính Đông Á
04/2019 – 10/2026 (7 năm 6 tháng)

- Phát triển Backend bằng Java và Spring Boot cho các hệ thống ngân hàng số, Fintech và phần mềm doanh nghiệp, tham gia xây dựng các chức năng xử lý nghiệp vụ.
- Thiết kế và phát triển các dịch vụ theo Microservices Architecture, sử dụng PostgreSQL, Redis và Apache Kafka để phục vụ xử lý, trao đổi dữ liệu.
- Tham gia triển khai và theo dõi dịch vụ với Docker, Kubernetes, AWS, Jenkins, Prometheus và Grafana; phối hợp xử lý các vấn đề liên quan đến hiệu năng và độ ổn định production.
- Dẫn dắt nhóm 5 developer, tham gia System Design và Technical Mentoring, hỗ trợ nhóm trong quá trình phát triển và giải quyết vấn đề kỹ thuật.

DỰ ÁN

Nền tảng Backend ngân hàng số và Fintech

Tham gia thiết kế, phát triển và vận hành các dịch vụ Backend theo kiến trúc Microservices. Tập trung vào xử lý nghiệp vụ, tích hợp các thành phần dịch vụ và duy trì hoạt động ổn định trên production.

Công nghệ: Java, Spring Boot, Spring Security, PostgreSQL, Redis, Apache Kafka, Docker, Kubernetes, AWS.
```

### JD

```
Vị trí: Nhà phát triển Salesforce cao cấp
Kinh nghiệm: 4 năm
Học vấn: Cử nhân/kỹ sư chuyên ngành Khoa học máy tính, Công nghệ thông tin hoặc các ngành liên quan
Kỹ năng chuyên môn: Salesforce, Sales Cloud, Service Cloud, Marketing Cloud, Community Cloud, Lightning Platform
Yêu cầu: Cử nhân/kỹ sư chuyên ngành Khoa học máy tính, Công nghệ thông tin hoặc các ngành liên quan. Từ 4 năm kinh nghiệm thiết kế & phát triển các sản phẩm CRM dựa trên nền tảng salesforce (Sales Cloud, Service Cloud, Marketing Cloud, Community Cloud, Lightning Platform,...). Thành thạo tiếng anh giao tiếp. Có các chứng chỉ liên quan tới salesforce là một lợi thế. Có tinh thần trách nhiệm cao, sẵn sàng học hỏi những kiến thức mới. Làm việc nhóm & làm việc độc lập.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P32

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có khoảng 1,6 năm kinh nghiệm làm Data Analysis trong lĩnh vực logistics và giao hàng. Công việc chính của tôi là xử lý dữ liệu vận hành, theo dõi delivery success rate, delivery time và xây dựng các báo cáo hỗ trợ đánh giá hoạt động giao nhận. Tôi muốn tiếp tục phát triển theo hướng Data Analytics, tập trung vào SQL, Python và Exploratory Data Analysis để khai thác dữ liệu hiệu quả hơn, đồng thời cải thiện chất lượng của các báo cáo vận hành.

HỌC VẤN

Cử nhân Công nghệ thông tin – Đại học tư thục.

Có kiến thức nền tảng về lập trình, cơ sở dữ liệu và xử lý thông tin.

KỸ NĂNG CHUYÊN MÔN

- Database: PostgreSQL.
- SQL: Sử dụng CTE, Window Functions để truy vấn, tổng hợp và phân tích dữ liệu.
- Python: pandas, NumPy để xử lý dữ liệu và thực hiện các bước phân tích.
- Data Visualization: Matplotlib, Seaborn, Metabase.
- Exploratory Data Analysis (EDA): Khám phá dữ liệu, tìm kiếm xu hướng và các điểm bất thường.
- Data Quality Validation: Kiểm tra tính hợp lệ và nhất quán của dữ liệu.
- Công cụ khác: Jupyter Notebook, Microsoft Excel, Git.
- REST API cơ bản, Basic Statistical Testing.

KỸ NĂNG MỀM

- Trình bày kết quả phân tích thông qua dashboard và biểu đồ.
- Chủ động xây dựng báo cáo vận hành theo các chỉ số được giao.
- Tiếng Việt: Bản ngữ.
- Tiếng Anh: B1, có khả năng đọc hiểu tài liệu kỹ thuật tốt hơn giao tiếp.

KINH NGHIỆM LÀM VIỆC

Data Analyst
Công ty TNHH Logistics Đông Nam
03/2025 – 10/2026 (1 năm 7 tháng)

- Phân tích dữ liệu giao nhận từ PostgreSQL, xây dựng SQL queries để tổng hợp delivery success rate và delivery time.
- Tự xây dựng báo cáo theo dõi tỷ lệ giao hàng thành công và thời gian giao nhận, cung cấp thông tin cho việc đánh giá hoạt động vận hành.
- Sử dụng Metabase để trình bày các chỉ số dưới dạng dashboard, giúp việc theo dõi dữ liệu thuận tiện hơn.
- Áp dụng Python pandas và NumPy cho một phần công việc Data Cleaning và tổng hợp dữ liệu, thay thế các thao tác xử lý thủ công trước đây.

DỰ ÁN

Delivery Performance Analytics

Thực hiện phân tích dữ liệu hiệu suất giao hàng, tập trung vào hai nhóm chỉ số: delivery success rate và delivery time.

Tôi sử dụng PostgreSQL và SQL để truy vấn dữ liệu, Python pandas để xử lý và Metabase để xây dựng dashboard. Bên cạnh đó, tôi thực hiện EDA bằng Matplotlib, Seaborn nhằm trực quan hóa kết quả phân tích.

Đầu ra là các báo cáo vận hành giúp theo dõi tỷ lệ giao thành công và thời gian giao nhận theo dữ liệu thực tế.
```

### JD

```
Vị trí: Chuyên gia phân tích hoạt động
Kinh nghiệm: 2 năm
Học vấn: Tốt nghiệp Đại học chuyên ngành Phân tích dữ liệu, Hệ thống thông tin, Toán thống kê, Kinh tế, hoặc các ngành liên quan
Kỹ năng chuyên môn: SQL, BigQuery, Metabase, Google Sheets, Python, R
Yêu cầu: Tốt nghiệp Đại học chuyên ngành Phân tích dữ liệu, Hệ thống thông tin, Toán thống kê, Kinh tế, hoặc các ngành liên quan. Tối thiểu 2 năm kinh nghiệm trong phân tích dữ liệu, xây dựng hệ thống báo cáo. Thành thạo SQL và các công cụ phân tích như BigQuery, Metabase, Google Sheets, Python hoặc R là lợi thế. Có kinh nghiệm làm việc với Data Warehouse, Data-mart và luồng ETL. Hiểu biết tốt về thử nghiệm A/B, causal inference, mô hình đánh giá hiệu quả. Có khả năng trình bày, trực quan hóa dữ liệu rõ ràng, dễ hiểu. Kỹ năng quản lý tài liệu, chia sẻ tri thức và truyền đạt quy trình một cách logic, dễ tiếp cận. Có tư duy hệ thống, chú ý chi tiết và tinh thần cải tiến liên tục. Chủ động, có khả năng phối hợp đa phòng ban và quản lý nhiều dự án cùng lúc. Thành thạo tiếng Anh là một lợi thế.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P33

### CV

```
MỤC TIÊU NGHỀ NGHIỆP
Tôi có gần 4 năm kinh nghiệm phân tích dữ liệu trong lĩnh vực Fintech và thanh toán điện tử, phát triển từ Junior Data Analyst lên Middle Data Analyst. Công việc tập trung vào phân tích hành vi giao dịch, xây dựng hệ thống chỉ số khách hàng và chuẩn hóa dữ liệu phục vụ báo cáo. Tôi mong muốn tiếp tục phát triển chuyên môn về Data Modeling, phân tích khách hàng và nâng cao chất lượng dữ liệu để hỗ trợ các quyết định kinh doanh.

HỌC VẤN
Cử nhân Khoa học dữ liệu
Đại học công lập khối kỹ thuật
Được đào tạo về khoa học dữ liệu và các phương pháp phân tích thống kê.

KỸ NĂNG CHUYÊN MÔN
- SQL nâng cao, Snowflake.
- Python pandas, Jupyter Notebook.
- Tableau: Xây dựng dashboard và trực quan hóa dữ liệu.
- dbt, Data Modeling, ETL Data Validation.
- Cohort Analysis, Customer Segmentation.
- Statistical Hypothesis Testing.
- Scikit-learn cơ bản, Excel nâng cao.
- Git, Agile/Scrum.

KỸ NĂNG MỀM
- Stakeholder Communication: Trao đổi yêu cầu và kết quả phân tích với các bên liên quan.
- Phối hợp công việc theo quy trình Agile/Scrum.
- Có khả năng trình bày kết quả phân tích và giải thích các chỉ số dữ liệu.
- Tiếng Anh B2, có thể trao đổi với nhóm kỹ thuật quốc tế.

KINH NGHIỆM LÀM VIỆC
Công ty Công nghệ Thanh toán Ánh Dương
Middle Data Analyst
07/2024 - 10/2026 (2 năm 3 tháng)

- Phụ trách phân tích dữ liệu giao dịch và xây dựng bộ chỉ số khách hàng phục vụ báo cáo hoạt động thanh toán điện tử.
- Sử dụng Snowflake, SQL và Python pandas để xử lý dữ liệu, thực hiện Cohort Analysis và Customer Segmentation.
- Phối hợp với Data Engineer xây dựng Data Modeling bằng dbt, thực hiện ETL Data Validation nhằm đảm bảo tính nhất quán của dữ liệu báo cáo.
- Phát triển dashboard Tableau và thực hiện Statistical Hypothesis Testing để cung cấp thông tin cho các bên liên quan.

Công ty Công nghệ Thanh toán Ánh Dương
Junior Data Analyst
12/2022 - 07/2024 (1 năm 7 tháng)

- Truy vấn và tổng hợp dữ liệu giao dịch bằng SQL để phục vụ báo cáo định kỳ.
- Sử dụng Python pandas và Excel nâng cao để làm sạch, kiểm tra và tổng hợp dữ liệu khách hàng.
- Hỗ trợ phân tích hành vi giao dịch và xây dựng báo cáo trực quan bằng Tableau.

DỰ ÁN
Phân tích hành vi và phân nhóm khách hàng thanh toán điện tử

- Sử dụng Snowflake, SQL và Python pandas để chuẩn bị bộ dữ liệu phân tích.
- Áp dụng Cohort Analysis và Customer Segmentation để nghiên cứu đặc điểm giao dịch của các nhóm khách hàng.
- Xây dựng dashboard Tableau thể hiện các chỉ số khách hàng, hỗ trợ theo dõi hành vi giao dịch theo từng nhóm.
```

### JD

```
Vị trí: Kỹ sư dữ liệu cao cấp
Kinh nghiệm: 4 năm
Học vấn: Đại học hoặc cao hơn liên quan đến 1 trong các ngành kinh tế, tài chính, ngân hàng, hoặc công nghệ thông tin, khoa học máy tính, toán tin ứng dụng
Kỹ năng chuyên môn: Truy vấn, tổ chức, phân tích dữ liệu, Cơ sở dữ liệu quan hệ RDBMS, NoSQL, Thiết kế lập trình cho các hệ thống như hệ thống Data warehouse, Data lake, lakehouse, API, CI/CD, SSIS, Datastage, ODI, Kafka, Spark, Nifi, Airflow, DBT, Databrick, Redshift
Yêu cầu: Đại học hoặc cao hơn liên quan đến 1 trong các ngành kinh tế, tài chính, ngân hàng, hoặc công nghệ thông tin, khoa học máy tính, toán tin ứng dụng. Tối thiểu 4 năm trong lĩnh vực quản lý dữ liệu/báo cáo/phân tích/học máy. Truy vấn, tổ chức, phân tích dữ liệu. Sử dụng các công nghệ cập nhật để xử lý dữ liệu để phát triển và vận hành ngân hàng, tài chính ngân hàng. Triển khai cùng và quản lý đối tác công nghệ thông tin. Cơ sở dữ liệu quan hệ quan hệ RDBMS, NoSQL. Thiết kế lập trình cho các hệ thống như hệ thống Data warehouse, Data lake, lakehouse, API, CI/CD, các dịch vụ xử lý dữ liệu và luồng dữ liệu dạng batch/stream, quản lý luồng vận hành ETL, ELT: SSIS, Datastage, ODI, Kafka, Spark, Nifi, Airflow, DBT, Databrick, Redshift v.v...
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P34

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có 1 năm 7 tháng kinh nghiệm xây dựng và bảo trì các pipeline xử lý dữ liệu theo lịch tại công ty sản phẩm thương mại điện tử. Tôi muốn tiếp tục phát triển chuyên môn Data Engineering, đặc biệt trong thiết kế ETL Pipeline, Batch Data Processing và quản lý dữ liệu phục vụ phân tích kinh doanh. Mục tiêu là nâng cao khả năng vận hành pipeline ổn định và xử lý các luồng dữ liệu có độ phức tạp lớn hơn.

HỌC VẤN

Trình độ: Đại học
Chuyên ngành: Khoa học máy tính
Trường: Đại học tư thục đào tạo Công nghệ thông tin

Được trang bị kiến thức nền tảng về lập trình, cơ sở dữ liệu và xử lý dữ liệu trong hệ thống phần mềm.

KỸ NĂNG CHUYÊN MÔN

- Programming: Python, SQL, Bash Scripting.
- Database: MySQL.
- Data Engineering: ETL Pipeline, Batch Data Processing, Apache Airflow.
- Data Processing: Apache Spark cơ bản.
- Data Storage: MinIO, Parquet.
- Development Tools: Docker, GitLab.
- Monitoring: Grafana cơ bản.
- Integration: REST API.
- Tiếng Anh B2, đọc viết tài liệu kỹ thuật tốt, giao tiếp công việc khá.

KỸ NĂNG MỀM

- Phối hợp với nhóm phát triển sản phẩm trong công việc xử lý dữ liệu.
- Trao đổi các vấn đề kỹ thuật và tiến độ công việc bằng tiếng Anh.
- Theo dõi, xử lý các vấn đề phát sinh trong quá trình bảo trì pipeline.
- Tổng hợp và trình bày kết quả xử lý dữ liệu phục vụ nhu cầu báo cáo.

KINH NGHIỆM LÀM VIỆC

Data Engineer
Công ty Cổ phần Nền tảng Số Nam Việt – TP. Hồ Chí Minh
Thời gian: 1 năm 7 tháng

- Xây dựng và bảo trì các ETL Pipeline bằng Python, SQL và Apache Airflow để xử lý dữ liệu theo lịch.
- Thực hiện Batch Data Processing, chuẩn bị dữ liệu doanh thu và hành vi người dùng phục vụ nhu cầu phân tích của doanh nghiệp.
- Làm việc với MySQL, MinIO và định dạng Parquet trong quá trình lưu trữ, truy xuất và xử lý dữ liệu.
- Theo dõi quá trình thực thi pipeline, kiểm tra kết quả xử lý và khắc phục lỗi phát sinh nhằm duy trì dữ liệu phục vụ báo cáo định kỳ.

DỰ ÁN

ETL Pipeline phục vụ báo cáo doanh thu và phân tích hành vi khách hàng

Tham gia phát triển hệ thống pipeline dữ liệu theo lịch cho sản phẩm thương mại điện tử.

Công nghệ sử dụng: Python, SQL, Apache Airflow, MySQL, MinIO, Parquet.

Công việc bao gồm thu thập, biến đổi và chuẩn bị dữ liệu phục vụ báo cáo doanh thu, đồng thời bảo trì các pipeline hiện có. Kết quả là các luồng xử lý dữ liệu được duy trì để cung cấp dữ liệu định kỳ cho hoạt động phân tích kinh doanh.
```

### JD

```
Vị trí: Lập Trình Viên PHP Laravel Backend
Kinh nghiệm: 2 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: PHP, Laravel, MySQL, PostgreSQL, MongoDB, HTML, CSS, JavaScript, Git
Yêu cầu: Tối thiểu 2 năm kinh nghiệm làm việc với PHP, đặc biệt là Laravel Framework. Hiểu biết sâu về các kiến trúc RESTful API và cách triển khai chúng. Kinh nghiệm làm việc với hệ quản trị cơ sở dữ liệu (MySQL, PostgreSQL, hoặc MongoDB). Thành thạo HTML, CSS, JavaScript (ưu tiên có kinh nghiệm làm việc với các framework như Vue.js, ReactJS, React Native là điểm cộng). Hiểu biết về các công cụ quản lý mã nguồn như Git. Có khả năng phân tích, xử lý vấn đề và làm việc độc lập hoặc theo nhóm. Kỹ năng giao tiếp tốt, sẵn sàng học hỏi và tiếp thu công nghệ mới.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P35

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có hơn 7 năm kinh nghiệm phát triển ứng dụng Android native, tập trung vào các sản phẩm ngân hàng số, fintech và dịch vụ tiêu dùng. Trong quá trình làm việc, tôi phát triển từ lập trình viên triển khai tính năng đến vị trí phụ trách kỹ thuật một nhóm gồm 5 thành viên.

Thế mạnh của tôi là Kotlin, Jetpack Compose, thiết kế kiến trúc Android theo hướng Multi-module và cải thiện chất lượng ứng dụng thông qua kiểm thử, tối ưu quy trình build và theo dõi lỗi. Tôi mong muốn tiếp tục phát triển theo hướng chuyên sâu về kiến trúc Android, đồng thời tham gia định hướng kỹ thuật và hỗ trợ các thành viên trong nhóm.

HỌC VẤN

Tốt nghiệp Đại học – Ngành Kỹ thuật phần mềm
Hệ đào tạo: Chính quy, trường đại học công lập.

KỸ NĂNG CHUYÊN MÔN

- Ngôn ngữ lập trình: Kotlin nâng cao.
- Android Framework: Jetpack Compose, Android Jetpack.
- Architecture: Clean Architecture, Multi-module Architecture.
- Asynchronous Programming: Coroutines, Flow.
- Dependency Injection: Hilt.
- Build System: Gradle Build Optimization.
- Testing: Espresso Testing.
- CI/CD: GitHub Actions.
- Monitoring và Performance: Firebase Crashlytics, Performance Profiling.
- API: RESTful API Design.
- Release: Android App Bundle.
- Engineering Practices: Technical Mentoring, Code Review.

KỸ NĂNG MỀM

- Có kinh nghiệm phụ trách kỹ thuật nhóm 5 lập trình viên.
- Hướng dẫn thành viên trong nhóm thông qua Technical Mentoring và Code Review.
- Giao tiếp công việc bằng tiếng Anh tốt, đọc viết tài liệu kỹ thuật thành thạo.
- Tiếng Nhật trình độ sơ cấp N5.

KINH NGHIỆM LÀM VIỆC

Senior Android Developer / Technical Lead
Công ty Công nghệ Tài chính Hưng Thịnh
08/2022 – 10/2026 (4 năm 2 tháng)

- Phụ trách kỹ thuật nhóm 5 người phát triển ứng dụng Android trong lĩnh vực tài chính, tham gia định hướng triển khai tính năng và review code.
- Tham gia thiết kế Multi-module Architecture kết hợp Clean Architecture, tổ chức các thành phần ứng dụng để hỗ trợ bảo trì và mở rộng chức năng.
- Phát triển các tính năng bằng Kotlin, Jetpack Compose, Coroutines và Flow; sử dụng Hilt để quản lý dependency giữa các thành phần.
- Tham gia cải thiện độ ổn định ứng dụng thông qua Firebase Crashlytics, Performance Profiling, Espresso Testing và tối ưu quá trình build bằng Gradle.

Android Developer
Công ty Giải pháp Di động Thành Công
08/2019 – 08/2022 (3 năm)

- Phát triển và bảo trì các chức năng Android cho ứng dụng dịch vụ tiêu dùng, sử dụng Kotlin và Android Jetpack.
- Tham gia xây dựng các luồng xử lý dữ liệu, kết nối dịch vụ theo thiết kế RESTful API và triển khai các chức năng bất đồng bộ.
- Sử dụng GitHub Actions trong quy trình CI/CD, tham gia kiểm thử bằng Espresso và đóng gói phiên bản Android App Bundle.

DỰ ÁN

Ứng dụng ngân hàng số

Vai trò: Senior Android Developer / Technical Lead.

Công nghệ: Kotlin, Jetpack Compose, Clean Architecture, Multi-module Architecture, Coroutines, Flow, Hilt, Firebase Crashlytics, GitHub Actions.

Tham gia thiết kế cấu trúc module, phát triển tính năng và cải thiện độ ổn định của ứng dụng tài chính. Đồng thời phụ trách Code Review, Technical Mentoring và hỗ trợ nhóm duy trì chất lượng mã nguồn trong quá trình phát triển.
```

### JD

```
Vị trí: Nhà phát triển Android cao cấp (Ứng dụng di động)
Kinh nghiệm: 3 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: Android SDK, Android Studio, Java, Kotlin, MVVM, Clean Architecture, JNI, C/C++
Yêu cầu: Kĩ năng chuyên môn: Nắm vững kiến thức nền tảng về Android (Activity/Fragment Lifecycle, ViewModel, LiveData, Coroutines, Jetpack Components). Có kiến thức và khả năng áp dụng hiệu quả các pattern kiến trúc như MVVM. Hiểu biết cơ bản về Clean Architecture, thể hiện được trong các dự án thực tế. Tư duy tốt modular hóa và tổ chức code rõ ràng, maintainable. Có kiến thức về JNI và có khả năng tích hợp native code (C/C++). Có kinh nghiệm trong việc cải thiện hiệu năng ứng dụng. Có khả năng tạo Custom View. Có kinh nghiệm trong việc tích hợp SDK/dịch vụ bên thứ ba. Kinh nghiệm: Middle- Senior: Tối thiểu 3+ năm kinh nghiệm. Kĩ năng mềm: Khả năng phối hợp tốt với các thành viên khác trong nhóm, hỗ trợ các thành viên Junior/Intern. Có niềm đam mê mãnh liệt và nghiên cứu sâu với công nghệ, các sản 
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P36

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có khoảng 3 năm 8 tháng kinh nghiệm làm việc với dữ liệu, trong đó 1 năm 6 tháng đầu tập trung vào Business Intelligence và 2 năm 2 tháng gần đây chuyển sang Data Engineering. Quá trình làm BI Analyst giúp tôi hiểu khá rõ cách các bộ phận nghiệp vụ sử dụng dữ liệu để theo dõi hoạt động kinh doanh. Sau đó, tôi muốn tham gia sâu hơn vào việc xây dựng hệ thống xử lý dữ liệu, thay vì chỉ làm việc ở lớp báo cáo. Mục tiêu hiện tại của tôi là tiếp tục phát triển chuyên môn về Data Warehouse, ETL Optimization và các dịch vụ dữ liệu trên Azure.

HỌC VẤN

Đại học – Ngành Hệ thống thông tin quản lý
Trường đại học công lập khối kinh tế.

KỸ NĂNG CHUYÊN MÔN

- Cơ sở dữ liệu: SQL Server, T-SQL, Azure SQL Database.
- Xử lý và tích hợp dữ liệu: SSIS, Azure Data Factory, Databricks, PySpark.
- Thiết kế dữ liệu: Data Warehouse, Dimensional Modeling.
- Tối ưu quy trình: ETL Optimization.
- Phân tích và báo cáo: Power BI, DAX.
- Công cụ hỗ trợ: Python, Azure DevOps, Git.

KỸ NĂNG MỀM

- Trao đổi với bộ phận nghiệp vụ để làm rõ nhu cầu sử dụng dữ liệu.
- Phối hợp với thành viên trong nhóm khi phát triển và điều chỉnh pipeline.
- Có thể tham gia họp kỹ thuật và viết tài liệu bằng tiếng Anh ở mức B2.

KINH NGHIỆM LÀM VIỆC

Data Engineer – Công ty TNHH Giải pháp Dữ liệu Đông Việt
08/2024 – 09/2026 (2 năm 2 tháng)

- Tham gia xây dựng Data Warehouse trên Azure phục vụ tổng hợp và phân tích dữ liệu tài chính doanh nghiệp.
- Phát triển pipeline ETL bằng Azure Data Factory, kết hợp Azure SQL Database để lưu trữ dữ liệu sau xử lý.
- Sử dụng Databricks và PySpark trong các công việc biến đổi dữ liệu, chuẩn bị dữ liệu đầu vào cho hệ thống phân tích.
- Rà soát các bước xử lý ETL, điều chỉnh truy vấn và luồng dữ liệu nhằm giảm thao tác xử lý không cần thiết.

BI Analyst – Công ty CP Công nghệ Vận tải Minh Phát
02/2023 – 07/2024 (1 năm 6 tháng)

- Xây dựng báo cáo Power BI theo dõi hoạt động logistics và các chỉ số vận hành.
- Sử dụng T-SQL để truy xuất, tổng hợp dữ liệu từ SQL Server phục vụ báo cáo.
- Thiết kế mô hình dữ liệu theo hướng Dimensional Modeling để hỗ trợ phân tích.
- Phát triển các chỉ số DAX và sử dụng SSIS để chuẩn bị dữ liệu cho báo cáo định kỳ.

DỰ ÁN

Xây dựng Data Warehouse cho dữ liệu tài chính doanh nghiệp

Tham gia thiết kế mô hình dữ liệu, phát triển pipeline ETL trên Azure Data Factory và xử lý dữ liệu bằng Databricks, PySpark. Dữ liệu sau xử lý được tổ chức trên Azure SQL Database nhằm hỗ trợ nhu cầu phân tích và khai thác báo cáo nội bộ.
```

### JD

```
Vị trí: Kỹ Sư Dữ Liệu Cấp Cao
Kinh nghiệm: 4 năm
Học vấn: Tốt nghiệp đại học chuyên ngành Khoa học Máy tính, Kỹ thuật Phần mềm, Hệ thống Thông tin
Kỹ năng chuyên môn: Python, Java, Scala, Go, Javascript, Typescript, R, SQL, GCP, AWS, MongoDB, PostgreSQL, BigQuery, ClickHouse, Redpanda, Kafka, RabbitMQ, Airflow, dbt, Airbyte, Metabase, PowerBI, Looker Studio, GitLab, GitHub, Hadoop, Spark, Databricks, Kubernetes
Yêu cầu: Tốt nghiệp đại học chuyên ngành Khoa học Máy tính, Kỹ thuật Phần mềm hoặc Hệ thống Thông tin. Có chuyên môn về khoa học dữ liệu hoặc bằng cấp cao hơn là một lợi thế lớn. Tối thiểu 4 năm kinh nghiệm trong vai trò kỹ sư dữ liệu, xây dựng nền tảng và pipeline phục vụ phân tích. Thành thạo Python và ít nhất một ngôn ngữ lập trình khác như Java, Scala, Go, Javascript, Typescript, R là một điểm cộng lớn. Thành thạo SQL trên các hệ quản trị cơ sở dữ liệu (DBMS). Có kinh nghiệm với các dịch vụ đám mây như GCP, AWS. Có kinh nghiệm làm việc với nhiều hệ cơ sở dữ liệu OLTP và OLAP như MongoDB, PostgreSQL, BigQuery, ClickHouse,... Có kinh nghiệm với các nền tảng và khái niệm xử lý dữ liệu streaming như Redpanda, Kafka, RabbitMQ, CDC hoặc mã nguồn mở khác. Có kinh nghiệm với các công cụ quản lý pipelin
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P37

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi tốt nghiệp ngành Ứng dụng phần mềm và có kinh nghiệm thực tập Frontend với Vue 3. Mong muốn tiếp tục phát triển kỹ năng xây dựng giao diện web, làm việc với Vue Router, Pinia và các công cụ hỗ trợ phát triển Frontend. Định hướng trở thành lập trình viên có khả năng thực hiện các tính năng giao diện một cách độc lập và đáp ứng yêu cầu thực tế của sản phẩm.

HỌC VẤN

Tốt nghiệp Cao đẳng ngành Ứng dụng phần mềm

Trường cao đẳng kỹ thuật

Có kiến thức về lập trình web, HTML5, CSS3, JavaScript và phát triển ứng dụng giao diện người dùng.

KỸ NĂNG CHUYÊN MÔN

- HTML5, CSS3, JavaScript.
- Vue 3, Vue Router, Pinia cơ bản.
- Tailwind CSS, Figma.
- Axios, Vite, Git.
- Firebase Hosting, Chrome DevTools.

KỸ NĂNG MỀM

- Có khả năng phối hợp trong nhóm phát triển phần mềm.
- Tiếp nhận yêu cầu chỉnh sửa giao diện trong quá trình thực tập.
- Tiếng Anh A2, đọc hiểu tài liệu kỹ thuật đơn giản.

KINH NGHIỆM LÀM VIỆC

Frontend Developer Intern

Công ty Công nghệ An Việt

Thời gian: 0,7 năm

Lĩnh vực: Gia công phần mềm, bán lẻ và dịch vụ đặt lịch

- Tham gia phát triển giao diện quản lý sản phẩm bằng Vue 3, HTML5 và CSS3, hoàn thiện các phần giao diện được phân công.
- Xây dựng giao diện hệ thống đặt lịch dịch vụ, sử dụng Vue Router để tổ chức điều hướng giữa các trang.
- Sử dụng Tailwind CSS để chỉnh sửa bố cục và các thành phần giao diện theo thiết kế Figma.
- Sử dụng Git để quản lý mã nguồn và Chrome DevTools để kiểm tra, xử lý các vấn đề hiển thị.

DỰ ÁN

Hệ thống quản lý sản phẩm và đặt lịch dịch vụ

Công nghệ: Vue 3, JavaScript, Vue Router, Tailwind CSS, Axios, Vite.

Tham gia xây dựng các màn hình quản lý sản phẩm và giao diện đặt lịch trong thời gian thực tập. Công việc chủ yếu là phát triển các phần giao diện theo yêu cầu và chỉnh sửa để đảm bảo hiển thị phù hợp với thiết kế.
```

### JD

```
Vị trí: Thực Tập Sinh Lập Trình Web
Kinh nghiệm: Không yêu cầu
Học vấn: Sinh viên năm cuối hoặc mới tốt nghiệp khối ngành CNTT (Kỹ thuật phần mềm/Công nghệ phần mềm)
Kỹ năng chuyên môn: lập trình web, web server, database, html, css, javascript, PHP, Nodejs, Java, Golang, ReactJs, NextJS, Git
Yêu cầu: Yêu cầu ứng viên: Sinh viên năm cuối hoặc mới tốt nghiệp khối ngành CNTT (Kỹ thuật phần mềm/Công nghệ phần mềm). Nắm vững kiến thức cơ bản của lập trình web (web server, database, html, css, javascript ...) và các khái niệm của lập trình hướng đối tượng. Có kinh nghiệm thực tiễn qua các dự án cá nhân hoặc các khóa học lập trình ứng dụng. Đã từng làm việc với PHP, Nodejs, Java, Golang hoặc ReactJs, NextJS là một lợi thế. Hiểu về quá trình thiết kế và chuẩn hóa DB Schema. Có kiến thức về Git. Ưu tiên các bạn có khả năng đọc hiểu, tự học hỏi tốt từ các tài liệu bằng tiếng anh. Năng động, nhiệt tình, ham học hỏi và trách nhiệm trong công việc. Có laptop cá nhân.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P38

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có khoảng 3,6 năm kinh nghiệm phát triển phần mềm, bắt đầu với Frontend và sau đó chuyển sang phát triển Fullstack. Tôi mong muốn tiếp tục làm việc với TypeScript, Next.js và NestJS, tham gia xây dựng các sản phẩm thương mại điện tử và SaaS có tính ổn định, dễ bảo trì. Mục tiêu của tôi là nâng cao năng lực thiết kế Backend, tối ưu hiệu năng ứng dụng và chủ động đảm nhận các tính năng từ giao diện đến API và cơ sở dữ liệu.

HỌC VẤN

Tốt nghiệp Đại học chuyên ngành Khoa học máy tính tại một trường đại học công lập.

KỸ NĂNG CHUYÊN MÔN

- Ngôn ngữ lập trình: TypeScript.
- Frontend: React.js, Next.js, Tailwind CSS.
- Backend: NestJS, RESTful API, JWT Authentication.
- Database: PostgreSQL, Prisma ORM, Redis.
- DevOps: Docker, GitHub Actions, AWS S3 cơ bản.
- Testing: Jest.

KỸ NĂNG MỀM

- Có khả năng tự triển khai các tính năng Fullstack tương đối độc lập.
- Giao tiếp và phối hợp tốt với các thành viên trong nhóm phát triển.
- Tiếng Anh B2, có thể trao đổi công việc và thảo luận kỹ thuật bằng tiếng Anh.

KINH NGHIỆM LÀM VIỆC

Công ty TNHH Nova Digital
Fullstack Developer | 07/2024 - 10/2026

- Phát triển các tính năng cho sản phẩm thương mại điện tử và SaaS sử dụng Next.js, NestJS và TypeScript.
- Thiết kế RESTful API, xử lý xác thực người dùng bằng JWT Authentication và quản lý dữ liệu với PostgreSQL, Prisma ORM.
- Sử dụng Redis để hỗ trợ xử lý dữ liệu và Docker để đóng gói ứng dụng.
- Tham gia kiểm thử bằng Jest và xây dựng quy trình thực thi tự động với GitHub Actions, hoàn thiện các tính năng từ giao diện đến Backend.

Công ty CP Bright Commerce
Frontend Developer | 03/2023 - 07/2024

- Phát triển giao diện website thương mại điện tử bằng React.js, TypeScript và Tailwind CSS.
- Tích hợp RESTful API để hiển thị dữ liệu sản phẩm và thông tin người dùng.
- Hoàn thiện các màn hình chức năng, phối hợp với nhóm Backend để xử lý vấn đề trong quá trình phát triển.

DỰ ÁN

Hệ thống quản lý bán hàng trực tuyến

Tham gia phát triển các chức năng quản lý dữ liệu và giao diện người dùng trên nền tảng Next.js, NestJS, PostgreSQL. Phụ trách triển khai API, kết nối dữ liệu và hoàn thiện những tính năng được giao.

NGOẠI NGỮ

Tiếng Anh: B2.
```

### JD

```
Vị trí: Nhân Viên IT
Kinh nghiệm: 1 năm
Học vấn: Cao Đẳng trở lên
Kỹ năng chuyên môn: PHP, Laravel, HTML, CSS, Javascript, jQuery, Bootstrap, Angular, VueJS, ReactJS, XML, JSON, API Restful, MySQL, Postgresql, Oracle, Microsoft SQL Server, MongoDB, Github
Yêu cầu: Yêu cầu trên 1 năm kinh nghiệm trở lên ở vị trí tương đương. Thành thạo ngôn ngữ lập trình PHP, có kinh nghiệm sâu một trong các framework như Laravel. Thành thạo HTML/CSS/Javascript/jQuery. Thành thạo ít nhất 1 library/framework để phát triển front-end: Bootstrap, Angular, VueJS, ReactJS,v.v... Thành thạo việc xây dựng và sử dụng web service (XML, JSON). Có kinh nghiệm về API Restful. Có kinh nghiệm sử dụng ít nhất 1 hệ quản trị cơ sở dữ liệu MySQL, Postgresql, Oracle, Microsoft SQL Server, MongoDB. Có kinh nghiệm quản lý dự án, có khả năng làm việc độc lập, làm việc theo đội/nhóm. có khả năng lập kế hoạch trong công việc. Nắm vững các kiến thức về Github. Có kinh nghiệm triển khai phần mềm theo kiến trúc micro-services. Giao tiếp tốt, nhiệt huyết, có trách nhiệm với công việc.
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P39

### CV

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi mong muốn phát triển sự nghiệp trong lĩnh vực Data Engineering, tập trung vào xử lý và quản lý dữ liệu phục vụ hoạt động kinh doanh. Sau 6 tháng thực tập tại doanh nghiệp thương mại điện tử, tôi đã có kinh nghiệm thực tế với SQL, Python và quy trình làm sạch dữ liệu bán hàng. Mục tiêu trước mắt là nâng cao khả năng xây dựng ETL Pipeline và xử lý dữ liệu hiệu quả, từng bước đảm nhận các công việc kỹ thuật có độ phức tạp cao hơn.

HỌC VẤN

Trình độ: Đại học
Chuyên ngành: Hệ thống thông tin
Trường: Đại học công lập chuyên ngành Công nghệ thông tin

Được đào tạo kiến thức nền tảng về hệ thống thông tin, cơ sở dữ liệu và xử lý dữ liệu.

KỸ NĂNG CHUYÊN MÔN

- Ngôn ngữ: Python, SQL.
- Cơ sở dữ liệu: PostgreSQL, viết truy vấn SQL phục vụ khai thác dữ liệu.
- Xử lý dữ liệu: Pandas, Data Cleaning, Data Transformation, ETL cơ bản.
- Phân tích và báo cáo: Excel, Power BI, Metabase.
- Công cụ hỗ trợ: Git, Jupyter Notebook, Linux cơ bản.
- Ngoại ngữ: Tiếng Anh B1, đọc hiểu tài liệu kỹ thuật khá, giao tiếp cơ bản.

KỸ NĂNG MỀM

- Phối hợp với các thành viên trong nhóm để xử lý dữ liệu phục vụ báo cáo.
- Trao đổi yêu cầu liên quan đến dữ liệu và kết quả xử lý trong công việc.
- Chủ động tìm hiểu tài liệu kỹ thuật tiếng Anh khi thực hiện nhiệm vụ.

KINH NGHIỆM LÀM VIỆC

Data Intern
Công ty TNHH Thương mại Điện tử Minh Phát – Hà Nội
Thời gian: 6 tháng

- Sử dụng Python và Pandas để làm sạch dữ liệu bán hàng, xử lý các giá trị thiếu và chuẩn hóa dữ liệu trước khi phân tích.
- Viết truy vấn SQL trên PostgreSQL để truy xuất thông tin đơn hàng, sản phẩm và dữ liệu phục vụ tổng hợp doanh thu.
- Tham gia các bước ETL cơ bản, thực hiện Data Transformation để chuẩn bị dữ liệu cho hoạt động phân tích.
- Hỗ trợ xây dựng báo cáo bằng Excel và Power BI, giúp nhóm kinh doanh theo dõi thông tin bán hàng từ dữ liệu đã được xử lý.

DỰ ÁN

Xử lý dữ liệu và hỗ trợ báo cáo bán hàng

Tham gia chuẩn bị dữ liệu bán hàng tại doanh nghiệp thương mại điện tử. Công việc tập trung vào Data Cleaning, truy vấn SQL và tổng hợp dữ liệu phục vụ báo cáo. Kết quả là các tập dữ liệu được chuẩn hóa để sử dụng trong quá trình phân tích doanh thu.
```

### JD

```
Vị trí: AI Engineer
Kinh nghiệm: Không yêu cầu
Học vấn: Currently pursuing a Bachelor's or Master's degree in Computer Science, AI, or related technical field
Kỹ năng chuyên môn: Python, API integration, REST principles, commercial LLM APIs (OpenAI, Anthropic, etc.), machine learning concepts and algorithms, TensorFlow, PyTorch, scikit-learn
Yêu cầu: Required Qualifications
- Currently pursuing a Bachelor's or Master's degree in Computer Science, AI, or related technical field
- Strong programming skills in Python
- Basic understanding of API integration and REST principles
- Familiarity with commercial LLM APIs (OpenAI, Anthropic, etc.)
- Basic understanding of machine learning concepts and algorithms
- Experience with common ML libraries (e.g., TensorFlow, PyTorch, scikit-learn)
- Solid foundation in mathematics and statistics
- Good problem-solving and analytical skills
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______

---

## P40

### CV

```
MỤC TIÊU NGHỀ NGHIỆP
Tôi có hơn ba năm làm thiết kế đồ họa trong lĩnh vực in ấn và quảng cáo, chủ yếu triển khai ấn phẩm từ định hướng hoặc mẫu thiết kế đã được thống nhất. Tôi thường chỉnh sửa key visual, điều chỉnh kích thước ấn phẩm và chuẩn bị file sản xuất. Tôi muốn tiếp tục phát triển chuyên môn Graphic Design, nhất là với các sản phẩm quảng cáo, FMCG và bao bì, chú trọng chất lượng hình ảnh và file in.

HỌC VẤN
Cử nhân Thiết kế đồ họa, tốt nghiệp tại một trường đại học tư thục.

KỸ NĂNG CHUYÊN MÔN
- Adobe Photoshop, Adobe Illustrator, Adobe InDesign; sử dụng Adobe After Effects ở mức cơ bản.
- Digital Advertising Design, Image Composition, Brand Visual Adaptation.
- Packaging Design, Print Production, Prepress và Photo Retouching.
- Canva, Motion Graphics đơn giản; quản lý và sắp xếp file thiết kế phục vụ bàn giao.

KỸ NĂNG MỀM
- Phối hợp với nhà in trong quá trình chuẩn bị file, trao đổi yêu cầu và kiểm tra sản phẩm đầu ra.
- Quản lý phiên bản file để thuận tiện chỉnh sửa.
- Tiếng Việt bản ngữ; tiếng Anh B1, đọc hiểu tài liệu và trao đổi công việc cơ bản.

KINH NGHIỆM LÀM VIỆC

Nhân viên Thiết kế đồ họa – Công ty In ấn Ánh Sáng (08/2023 – 09/2024)
- Điều chỉnh bố cục, kích thước và thông số của các ấn phẩm theo yêu cầu in thực tế.
- Thực hiện Prepress, kiểm tra file và phối hợp với nhà in để hoàn thiện bản đưa vào sản xuất.
- Chỉnh sửa hình ảnh, xử lý chi tiết trên ấn phẩm, giúp mẫu in bám sát thiết kế đã duyệt.

Graphic Designer – Agency Quảng cáo Góc Nhìn (10/2024 – 09/2026)
- Triển khai các phiên bản Digital Advertising Design từ key visual đã có cho nhiều định dạng hiển thị.
- Sử dụng Photoshop, Illustrator và InDesign để điều chỉnh hình ảnh, chữ và bố cục theo bộ hình ảnh thương hiệu.
- Điều chỉnh thiết kế bao bì và file in, bảo đảm tính nhất quán với mẫu đã duyệt.

DỰ ÁN
Bộ ấn phẩm quảng cáo FMCG: chỉnh sửa key visual, Photo Retouching, thay đổi kích thước và chuẩn bị file sản xuất.
```

### JD

```
Vị trí: 2D Anim / VFX Artist
Kinh nghiệm: 3 năm
Học vấn: Trung học phổ thông (Cấp 3) trở lên
Kỹ năng chuyên môn: Unity, 3D Artist, 2D Animation (traditional & Digital), VFX Software Proficiency (e.g., After Effects, Nuke, Fusion)
Yêu cầu: Có từ 3 năm kinh nghiệm với Unity. Tư duy logic tốt. Tác phong làm việc chuyên nghiệp. Linh hoạt trong quá trình làm việc độc lập vs. làm việc nhóm. Ưu tiên có sản phẩm demo (ghi rõ vai trò trong dự án nếu làm theo team).
```

Điểm của bạn (điền vào blind_v2_labels.csv): ______
