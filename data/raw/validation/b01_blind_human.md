# Phiếu chấm mù — đợt thí điểm b01

**Cách chấm (rubric v1.1)** — với mỗi cặp CV–JD, xác định 4 điều rồi tra bảng; chấm độc lập, không trao đổi với người khác:

1. **Vai trò**: *cùng nhóm* (vd Backend với Backend) / *liền kề* (cùng khối nghề: Backend-Frontend-Fullstack-Mobile-QA; DevOps-Sysadmin-IT Support; Data Analyst-Data Engineer; BA-PM; UI/UX-đồ họa) / *khác khối*.
2. **Độ phủ yêu cầu bắt buộc** của JD (bỏ qua ý "ưu tiên/là lợi thế"): *cao* ≥ 70% · *vừa* 40–69% · *thấp* < 40%. Sát ngưỡng thì chọn phía thấp. Chỉ tính kỹ năng CV có bằng chứng.
3. **Lệch cấp độ**: Fresher (<1 năm) · Junior (1–2) · Middle (3–4) · Senior (≥5). Lệch nếu JD cao hơn CV từ 2 cấp, hoặc CV cao hơn JD từ 3 cấp.
4. **Điều kiện cứng** JD ghi bắt buộc mà CV không có (bằng cấp, chứng chỉ, ngoại ngữ, ...), và **công nghệ trong tiêu đề JD** mà CV hoàn toàn không có.

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

Điền điểm vào file `b01_human_labels.csv` (cột `human_grade`). Đừng xem thư mục `data/raw/judgments/` hay file `*_key.csv`.

## CV `SUP_FRE_02`

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi học ngành Kỹ thuật máy tính, đã có 8 tháng thực tập và làm kỹ thuật viên bán thời gian tại trung tâm đào tạo. Công việc chủ yếu là cài đặt hệ điều hành, kiểm tra phần cứng và bảo trì máy tính trong phòng học. Tôi muốn tiếp tục làm Desktop Support Technician, nâng cao kỹ năng xử lý sự cố thiết bị và hỗ trợ người dùng tốt hơn trong môi trường làm việc thực tế.

HỌC VẤN

Trường đại học tư thục
Ngành: Kỹ thuật máy tính
Trình độ: Đại học

KỸ NĂNG CHUYÊN MÔN

- Cài đặt Windows và Ubuntu Desktop cho máy tính cá nhân, máy tính phòng học.
- Sử dụng Clonezilla để triển khai hệ điều hành trên thiết bị đầu cuối.
- Kiểm tra các lỗi phần cứng liên quan đến RAM, SSD và nguồn máy tính.
- Cấu hình BIOS/UEFI, thay đổi thứ tự khởi động khi cài đặt hệ điều hành.
- Sử dụng Hiren's BootCD PE và tạo USB cài đặt hệ điều hành.
- Hỗ trợ người dùng từ xa qua TeamViewer.
- Cấu hình chia sẻ tệp cơ bản trên NAS Synology.
- Kiểm tra Wi-Fi, thiết bị mạng văn phòng và xử lý lỗi trình duyệt, ứng dụng văn phòng.
- Quản lý danh sách thiết bị bằng Google Sheets.
- Tiếng Anh: Đọc hiểu khá, giao tiếp cơ bản.

KỸ NĂNG MỀM

- Trao đổi với người dùng để xác định tình trạng lỗi.
- Viết hướng dẫn xử lý sự cố đơn giản, dễ làm theo.
- Sắp xếp công việc cài đặt và bảo trì thiết bị theo yêu cầu.

KINH NGHIỆM LÀM VIỆC

Trung tâm Đào tạo Kỹ thuật An Bình
Vị trí: IT Technician Intern / Part-time
Thời gian: 02/2026 - 09/2026 (8 tháng)

- Cài đặt Windows, Ubuntu Desktop và phần mềm văn phòng cho máy tính phòng học, đảm bảo thiết bị sẵn sàng cho các buổi đào tạo.
- Dùng Clonezilla để triển khai hệ điều hành, kiểm tra BIOS/UEFI khi máy gặp lỗi khởi động.
- Kiểm tra RAM, SSD, nguồn máy tính và hổ trợ xử lý các sự cố phần cứng thông thường.
- Bảo trì máy tính phòng học, kiểm tra kết nối Wi-Fi và cập nhật danh sách thiết bị trên Google Sheets.

DỰ ÁN

Cài đặt và bảo trì phòng máy đào tạo

Tham gia chuẩn bị máy tính cho phòng học, tạo USB cài đặt hệ điều hành và sử dụng Clonezilla trong quá trình thiết lập thiết bị. Viết hướng dẫn xử lý một số lỗi thông thường để thuận tiện cho việc sử dụng và bảo trì.
```

### `SUP_FRE_02` ↔ `jd_1626`

```
Vị trí: Nhà phân tích kinh doanh sản phẩm
Kinh nghiệm: 2 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: Figma, Miro, Balsamiq
Yêu cầu: Tối thiểu 2-3 năm kinh nghiệm làm BA, ưu tiên trong các dự án liên quan đến e-commerce. Có kinh nghiệm thực tế về UX/UI, đã từng thiết kế flow, wireframe, mockup, prototype (ưu tiên có sản phẩm thực tế đã triển khai). Thành thạo các công cụ hỗ trợ: Figma, Miro, Balsamiq, hoặc tương đương. Kỹ năng giao tiếp, phân tích và trình bày tốt. Hiểu biết về quy trình phát triển phần mềm (Agile/Scrum). Có khả năng làm việc độc lập và phối hợp nhóm tốt.
```

Điểm của bạn: ___

### `SUP_FRE_02` ↔ `jd_0112`

```
Vị trí: Chuyên Viên Kỹ Thuật Vận Hành VoIP
Kinh nghiệm: Không yêu cầu
Học vấn: Cao đẳng/Đại học chuyên ngành CNTT, Viễn thông, Điện tử hoặc các lĩnh vực liên quan
Kỹ năng chuyên môn: Triển khai và vận hành hệ thống VOIP (Asterisk, FreePbx, FreeSWITCH, Kamailio, OpenSIPS, 3CX), Giao thức SIP, RTP, WebRTC, STUN/TURN/ICE, NAT Traversal, Hệ thống tổng đài IP PBX, SIP Trunking, DID, Call Routing, IVR, Linux (Ubuntu, CentOS) và networking (firewall, NAT, VPN, VLAN), Lập trình/scripting bằng Bash, Python, hoặc Lua
Yêu cầu: Tốt nghiệp Cao đẳng/Đại học chuyên ngành CNTT, Viễn thông, Điện tử hoặc các lĩnh vực liên quan. Có kinh nghiệm triển khai và vận hành hệ thống VOIP (Asterisk, FreePbx, FreeSWITCH, Kamailio, OpenSIPS, 3CX). Am hiểu giao thức SIP, RTP, WebRTC, STUN/TURN/ICE, NAT Traversal. Hiểu về hệ thống tổng đài IP PBX, SIP Trunking, DID, Call Routing, IVR. Kinh nghiệm làm việc với Linux (Ubuntu, CentOS) và networking (firewall, NAT, VPN, VLAN). Có khả năng lập trình/scripting bằng Bash, Python, hoặc Lua để tự động hóa các tác vụ VOIP là lợi thế. Kinh nghiệm làm việc với các giải pháp cloud-based VOIP như Twilio, Plivo, Amazon, Connect là một điểm cộng.
```

Điểm của bạn: ___

### `SUP_FRE_02` ↔ `jd_0066`

```
Vị trí: Nhân Viên Kỹ Thuật Máy Tính
Kinh nghiệm: Không yêu cầu
Học vấn: Tốt nghiệp trung cấp trở lên
Kỹ năng chuyên môn: Khắc phục sự cố phần cứng, Khắc phục sự cố phần mềm, Kiến thức về mạng máy tính, Cài đặt hệ điều hành, Cài đặt và cấu hình phần mềm
Yêu cầu: Tuổi từ 25t. Tốt nghiệp trung cấp trở lên. Có thể di chuyển nhiều địa điểm. Trung thực, nhiệt tình, có trách nhiệm, chịu được áp lực trong công việc.
```

Điểm của bạn: ___

### `SUP_FRE_02` ↔ `jd_0084`

```
Vị trí: Nhân Viên Kỹ Thuật Máy Tính
Kinh nghiệm: Không yêu cầu
Học vấn: Tốt nghiệp trung cấp trở lên
Kỹ năng chuyên môn: Khắc Phục Sự Cố Phần Cứng, Phần Mềm, Kiến Thức Về Mạng Máy Tính, Cài Đặt Hệ Điều Hành, Cài Đặt Và Cấu Hình Phần Mềm
Yêu cầu: Tuổi từ 25t. Tốt nghiệp trung cấp trở lên. Có thể di chuyển nhiều địa điểm. Trung thực, nhiệt tình, có trách nhiệm, chịu được áp lực trong công việc.
```

Điểm của bạn: ___

## CV `BA_FRE_01`

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi vừa tốt nghiệp ngành Hệ thống thông tin quản lý và có khoảng 5 tháng thực tập trong lĩnh vực Business Analyst. Tôi mong muốn tiếp tục phát triển kỹ năng phân tích nghiệp vụ, thu thập yêu cầu và xây dựng tài liệu cho các hệ thống phần mềm. Mục tiêu trước mắt là tích lũy kinh nghiệm thực tế và hiểu rõ hơn quy trình phát triển sản phẩm, đặc biệt trong lĩnh vực EdTech.

HỌC VẤN

Cử nhân Hệ thống thông tin quản lý
Đại học công lập khối kinh tế

Trong quá trình học, tôi được tiếp cận kiến thức về hệ thống thông tin và phân tích quy trình nghiệp vụ.

KỸ NĂNG CHUYÊN MÔN

- Requirement Gathering: Ghi nhận và tổng hợp yêu cầu nghiệp vụ cơ bản.
- Viết User Story theo mẫu và xây dựng Acceptance Criteria cho các chức năng đơn giản.
- Sử dụng Draw.io để vẽ Use Case Diagram.
- Phân tích quy trình nghiệp vụ và mô hình hóa bằng BPMN cơ bản.
- Microsoft Excel, Word, PowerPoint để xử lý thông tin và soạn tài liệu.
- Trello để theo dõi các đầu việc.
- SQL SELECT cơ bản để truy vấn thông tin.

KỸ NĂNG MỀM

- Có khả năng ghi chép, tổng hợp và trình bày thông tin theo cấu trúc.
- Phối hợp với BA chính trong quá trình phân tích và làm rõ yêu cầu.
- Tiếp nhận hướng dẫn và điều chỉnh tài liệu theo phản hồi.
- Tiếng Anh B1, đọc hiểu tài liệu kỹ thuật cơ bản.

KINH NGHIỆM LÀM VIỆC

Thực tập sinh Business Analyst
Công ty TNHH Phần mềm Giáo dục Minh Việt
Thời gian: 0,4 năm (khoảng 5 tháng)

- Hỗ trợ BA chính ghi nhận yêu cầu đối với các chức năng của phần mềm quản lý đào tạo.
- Phân tích các quy trình nghiệp vụ đơn giản và thể hiện lại bằng Use Case Diagram, BPMN.
- Viết User Story và Acceptance Criteria theo mẫu, tạo tài liệu đầu vào cho nhóm phát triển.
- Tổng hợp thông tin bằng Excel, Word và cập nhật tiến độ công việc trên Trello.

DỰ ÁN

Hệ thống quản lý đào tạo

Tham gia với vai trò thực tập sinh BA, hỗ trợ mô tả các luồng nghiệp vụ trong phần mềm quản lý đào tạo. Công việc tập trung vào ghi nhận yêu cầu, mô hình hóa quy trình và hoàn thiện tài liệu dưới sự hướng dẫn của BA chính. Kết quả là các nội dung nghiệp vụ được hệ thống hóa thành sơ đồ và tài liệu để nhóm phát triển tham khảo.
```

### `BA_FRE_01` ↔ `jd_0037`

```
Vị trí: Lập Trình Viên PHP Laravel Backend
Kinh nghiệm: 2 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: PHP, Laravel, MySQL, PostgreSQL, MongoDB, HTML, CSS, JavaScript, Git
Yêu cầu: Tối thiểu 2 năm kinh nghiệm làm việc với PHP, đặc biệt là Laravel Framework. Hiểu biết sâu về các kiến trúc RESTful API và cách triển khai chúng. Kinh nghiệm làm việc với hệ quản trị cơ sở dữ liệu (MySQL, PostgreSQL, hoặc MongoDB). Thành thạo HTML, CSS, JavaScript (ưu tiên có kinh nghiệm làm việc với các framework như Vue.js, ReactJS, React Native là điểm cộng). Hiểu biết về các công cụ quản lý mã nguồn như Git. Có khả năng phân tích, xử lý vấn đề và làm việc độc lập hoặc theo nhóm. Kỹ năng giao tiếp tốt, sẵn sàng học hỏi và tiếp thu công nghệ mới.
```

Điểm của bạn: ___

### `BA_FRE_01` ↔ `jd_1309`

```
Vị trí: Quản lý dự án/Scrum Master (tên miền Fintech)
Kinh nghiệm: 2 năm
Học vấn: Tốt nghiệp Đại học loại Khá trở lên, ưu tiên chuyên ngành CNTT, Kỹ thuật phần mềm, An toàn thông tin và ngành có liên quan
Kỹ năng chuyên môn: Quản trị dự án, Agile, Scrum, Công cụ quản trị dự án
Yêu cầu: Tốt nghiệp Đại học loại Khá trở lên, ưu tiên chuyên ngành CNTT, Kỹ thuật phần mềm, An toàn thông tin và ngành có liên quan. Tiếng Anh tương đương 550+ TOEIC. Có kinh nghiệm ít nhất 02 năm ở vị trí quản lý dự án công nghệ thông tin hoặc các dự án tương tự (PM). Ưu tiên các ứng viên có chứng chỉ PMP hoặc Scrum Master. Có kinh nghiệm quản trị các dự án theo nhiều mô hình khác nhau như Agile, Waterfall. Có kinh nghiệm Scrum Master tốt, định hướng tìm hiểu sâu về Scrum. Thành thạo các công cụ quản trị dự án và kiểm soát rủi ro. Có trách nhiệm cao và thái độ tốt trong công việc. Có khả năng làm việc độc lập hoặc làm việc theo nhóm tốt. Kỹ năng giao tiếp và trình bày tốt. Làm việc dưới áp lực cao, nhạy bén và tiếp thu nhanh. Ưu tiên ứng viên có thể đi làm ngay hoặc có thể xem xét nhận việc sau tế
```

Điểm của bạn: ___

### `BA_FRE_01` ↔ `jd_0595`

```
Vị trí: Project Manager
Kinh nghiệm: 3 năm
Học vấn: Tốt nghiệp Đại học, Cao đẳng chuyên ngành Công nghệ thông tin hoặc các chuyên ngành có liên quan.
Kỹ năng chuyên môn: PHP, Java, Kotlin, Swift
Yêu cầu: Kinh nghiệm: Từ 3 năm kinh nghiệm quản lý dự án, có khả năng quản lý team 5-10 người. Năng lực chuyên môn, chứng chỉ: Tốt nghiệp Đại học, Cao đẳng chuyên ngành Công nghệ thông tin hoặc các chuyên ngành có liên quan. Có kinh nghiệm lập trình ít nhất một trong các ngôn ngữ: PHP (ưu tiên), Java, Kotlin, Swift. Nắm vững quy trình phát triển sản phẩm phần mềm. Có kinh nghiệm thiết kế hệ thống phần mềm. Có khả năng giao tiếp/ kinh nghiệm làm việc và đề xuất giải pháp cho khách hàng. Ưu tiên ứng viên sở hữu các chứng chỉ quản lý dự án như: PMP, PMI-ACP, PSM... Có hiểu biết và kinh nghiệm thực tế trong việc quản lý dự án theo phương pháp Agile/Scrum. Có khả năng phân tích và đánh giá rủi ro trong dự án. Yêu cầu khác: Có kỹ năng lãnh đạo và giải quyết vấn đề. Có tư duy phát triển, tư duy sản phẩm. 
```

Điểm của bạn: ___

## CV `Backend_MID_01`

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có 3,5 năm kinh nghiệm chuyên trách phát triển Backend với C# và ASP.NET Core, tập trung xây dựng RESTful API, tích hợp hệ thống và xử lý nghiệp vụ doanh nghiệp. Trước đây tôi bắt đầu từ Frontend Developer rồi chuyển hướng sang Backend. Tôi muốn tiếp tục phát triển chuyên môn về thiết kế API, tối ưu xử lý dữ liệu và xây dựng các dịch vụ Backend ổn định, dễ bảo trì cho doanh nghiệp.

HỌC VẤN

Cử nhân Kỹ thuật phần mềm
Trường đại học công lập

KỸ NĂNG CHUYÊN MÔN

- Ngôn ngữ lập trình: C#, LINQ.
- Backend: ASP.NET Core, Entity Framework Core, RESTful API.
- Cơ sở dữ liệu: SQL Server.
- Tích hợp hệ thống: RabbitMQ, OAuth 2.0.
- Công cụ phát triển: Git, Docker, Azure DevOps.
- API Documentation: Swagger/OpenAPI.
- Testing: xUnit.
- CI/CD: Có kinh nghiệm sử dụng trong quy trình phát triển.
- Frontend: React ở mức cơ bản.

KỸ NĂNG MỀM

- Tiếng Anh B2, đọc tài liệu kỹ thuật và trao đổi chuyên môn tốt.
- Có khả năng tiếp cận vấn đề từ góc nhìn Frontend và Backend nhờ kinh nghiệm chuyển đổi vai trò.
- Chủ động tìm hiểu các yêu cầu nghiệp vụ để xây dựng chức năng phù hợp.
- Có kinh nghiệm phối hợp trong các công việc tích hợp hệ thống.

KINH NGHIỆM LÀM VIỆC

.NET Backend Developer
Công ty TNHH Giải pháp Phần mềm An Phát
04/2023 – 10/2026 (3 năm 6 tháng)

- Phát triển và bảo trì RESTful API bằng ASP.NET Core cho các hệ thống quản trị doanh nghiệp và bảo hiểm, đáp ứng các yêu cầu xử lý nghiệp vụ.
- Sử dụng Entity Framework Core, LINQ và SQL Server để xây dựng chức năng truy xuất, cập nhật và quản lý dữ liệu.
- Tham gia tích hợp các thành phần hệ thống sử dụng RabbitMQ và OAuth 2.0, phục vụ trao đổi thông tin và xác thực.
- Sử dụng Swagger/OpenAPI để mô tả API, xUnit để kiểm thử và Git, Docker, Azure DevOps trong quá trình phát triển, bàn giao phần mềm.

DỰ ÁN

Hệ thống quản lý nghiệp vụ bảo hiểm và doanh nghiệp

Tham gia xây dựng các API phục vụ xử lý dữ liệu nghiệp vụ, tích hợp giữa các thành phần ứng dụng và hỗ trợ bảo trì chức năng. Công nghệ sử dụng gồm C#, ASP.NET Core, SQL Server, Entity Framework Core và RabbitMQ.
```

### `Backend_MID_01` ↔ `jd_0032`

```
Vị trí: Chuyên Viên Phân Tích Tài Chính
Kinh nghiệm: 4 năm
Học vấn: Đại học trở lên các chuyên ngành Tài chính, Kế toán và các chuyên ngành liên quan dữ liệu
Kỹ năng chuyên môn: Excel: Thành thạo power query, power pivot, hiểu biết các hàm thông dụng, SQL/Postgresql cấp độ từ Intermediate, Power BI Desktop: Xử thành thạo Power Query, Dax, Visualized, Python, AI: ứng dụng trong quy trình phân tích dữ liệu là lợi thế
Yêu cầu: 1. Tốt nghiệp Đại học trở lên các chuyên ngành Tài chính/ Kế toán và các chuyên ngành liên quan dữ liệu. 2. Có ít nhất 4 năm kinh nghiệm làm Data Analyst các công ty, tập đoàn có kho dữ liệu lớn. (Ưu tiên kinh nghiệm quản lý dữ liệu đa nguồn (dữ liệu sản xuất, kinh doanh, tài chính) 3. Kiến thức tư duy và nền tảng về Tài chính và Kế toán.
```

Điểm của bạn: ___

### `Backend_MID_01` ↔ `jd_0442`

```
Vị trí: Nhà phát triển Sitecore
Kinh nghiệm: 3 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: Sitecore CMS, C#, ASP.NET MVC/Web API, SQL Server, HTML, CSS, JavaScript
Yêu cầu: Từ 3–5 năm kinh nghiệm phát triển .NET, trong đó tối thiểu 2–3 năm làm việc thực tế với Sitecore. Thành thạo: Sitecore CMS: templates, components, layouts, personalization, item architecture. Ngôn ngữ & công nghệ: C#, ASP.NET MVC/Web API, SQL Server, HTML/CSS/JS. Có hiểu biết về: Tích hợp hệ thống: RESTful APIs, JSON/XML. CI/CD pipelines (Git, Azure DevOps, Jenkins). Cơ bản về DevOps / hosting / cloud environments (Azure/AWS là lợi thế).
```

Điểm của bạn: ___

## CV `FS_JUN_01`

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có khoảng 1,4 năm kinh nghiệm phát triển và bảo trì ứng dụng web sử dụng ASP.NET Core Web API và Angular. Công việc trước đây chủ yếu liên quan đến hệ thống quản lý nhân sự, bao gồm chỉnh sửa biểu mẫu, giao diện và các API phục vụ nghiệp vụ nội bộ. Tôi muốn tiếp tục nâng cao khả năng làm việc với C#, Angular và SQL Server, đồng thời tích lũy thêm kinh nghiệm trong quá trình xây dựng và phát triển các chức năng phần mềm hoàn chỉnh.

HỌC VẤN

Đại học tư thục – Ngành Kỹ thuật phần mềm
Trình độ: Đại học.

KỸ NĂNG CHUYÊN MÔN

- Backend: C#, ASP.NET Core Web API, RESTful API.
- Frontend: Angular, TypeScript, HTML5, CSS3, Bootstrap.
- Database: SQL Server, Entity Framework Core, LINQ.
- Công cụ: Git, Swagger/OpenAPI, Postman.
- Ngoại ngữ: Tiếng Anh B1, giao tiếp công việc cơ bản.

KỸ NĂNG MỀM

- Có kinh nghiệm phối hợp với nhóm phát triển trong quá trình bảo trì phần mềm.
- Tiếp nhận và xử lý các yêu cầu chỉnh sửa chức năng theo công việc được phân công.
- Cẩn thận khi làm việc với biểu mẫu và dữ liệu trên hệ thống quản lý nội bộ.

KINH NGHIỆM LÀM VIỆC

Công ty TNHH Giải pháp Phần mềm Đại Việt
Junior Software Developer
05/2025 – 09/2026 (1 năm 5 tháng)

- Tham gia bảo trì hệ thống quản lý nhân sự sử dụng ASP.NET Core Web API, Angular và SQL Server.
- Chỉnh sửa các màn hình nhập liệu, biểu mẫu quản lý thông tin nhân sự bằng Angular, TypeScript và HTML5/CSS3.
- Cập nhật các RESTful API đơn giản bằng C#, sử dụng Entity Framework Core và LINQ để thực hiện thao tác dữ liệu.
- Sử dụng Swagger/OpenAPI và Postman để kiểm tra API sau khi chỉnh sửa, giúp xác nhận các chức năng đáp ứng yêu cầu được giao.

DỰ ÁN

Hệ thống quản lý nhân sự nội bộ

Vai trò: Software Developer
Công nghệ: C#, ASP.NET Core Web API, Angular, TypeScript, SQL Server, Entity Framework Core.

Tham gia duy trì và cập nhật các chức năng của hệ thống quản lý nhân sự. Công việc tập trung vào xử lý biểu mẫu, điều chỉnh giao diện và sửa đổi các API đơn giản nhằm đáp ứng thay đổi trong quá trình sử dụng.

Thông qua dự án, tôi tích lũy kinh nghiệm làm việc với ứng dụng có sẵn, tìm hiểu luồng xử lý giữa frontend và backend, cũng như kiểm tra chức năng sau khi cập nhật mã nguồn.
```

### `FS_JUN_01` ↔ `jd_0331`

```
Vị trí: Nhân Viên Kỹ Thuật Lập Trình CNC
Kinh nghiệm: 1 năm
Học vấn: Trung cấp trở lên các chuyên ngành liên quan: Kĩ nghệ gỗ, Công nghệ chế biến lâm sản, Điều khiển - tự động hóa, Cơ khí chế tạo
Kỹ năng chuyên môn: Alphacam, AutoCAD 2D, AutoCAD 3D, Inventor
Yêu cầu: Ưu tiên có 1–2 năm lập trình CNC trong sản xuất gỗ; Sử dụng thành thạo phần mềm Alphacam; AutoCAD 2D, 3D hoặc Inventor; Am hiểu tốt kĩ thuật vận hành các máy CNC (ưu tiên ngành gỗ); Tốt nghiệp Trung cấp trở lên các chuyên ngành liên quan: Kĩ nghệ gỗ, Công nghệ chế biến lâm sản, Điều khiển - tự động hóa, Cơ khí chế tạo,…
```

Điểm của bạn: ___

### `FS_JUN_01` ↔ `jd_0153`

```
Vị trí: Java Developer (Trên 2 Năm Kinh Nghiệm, Onsite Project)
Kinh nghiệm: 2 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: Java, Spring Boot, Hibernate, RESTful APIs, Microservice, Oracle, MySQL, Git, Agile, Postman
Yêu cầu: Tối thiểu 2 năm kinh nghiệm phát triển ứng dụng Java Spring Boot. Thành thạo lập trình Java, có kinh nghiệm với Spring Boot, Hibernate. Hiểu biết về RESTful APIs và kinh nghiệm phát triển microservice. Hiểu biết về CSDL như Oracle, MySQL... Có kinh nghiệm với hệ thống version control (Git) và quy trình phát triển Agile. Sử dụng thành thạo với ít nhất 1 công cụ test API, vd: Postman.
```

Điểm của bạn: ___

### `FS_JUN_01` ↔ `jd_0562`

```
Vị trí: 3D Artist
Kinh nghiệm: 2 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: 3ds Max, Blender, Keyshot
Yêu cầu: Độ tuổi: sinh năm 1997 – 2002. Tối thiểu 2 năm trong lĩnh vực thiết kế 3D sản phẩm. Ưu tiên đã từng tham gia các dự án làm mockup, prototype sản phẩm thật. Sử dụng thành thạo 3ds Max, Blender, Keyshot và các công cụ hỗ trợ khác. Khả năng mỹ thuật tốt, tính năng động, có tư duy sáng tạo logic, tư duy làm việc độc lập và đội nhóm. Thành thạo tiếng anh (Tối thiểu toiec 550).
```

Điểm của bạn: ___

### `FS_JUN_01` ↔ `jd_0294`

```
Vị trí: Nhân Viên IT
Kinh nghiệm: 1 năm
Học vấn: Cao Đẳng trở lên
Kỹ năng chuyên môn: PHP, Laravel, HTML, CSS, Javascript, jQuery, Bootstrap, Angular, VueJS, ReactJS, XML, JSON, API Restful, MySQL, Postgresql, Oracle, Microsoft SQL Server, MongoDB, Github
Yêu cầu: Yêu cầu trên 1 năm kinh nghiệm trở lên ở vị trí tương đương. Thành thạo ngôn ngữ lập trình PHP, có kinh nghiệm sâu một trong các framework như Laravel. Thành thạo HTML/CSS/Javascript/jQuery. Thành thạo ít nhất 1 library/framework để phát triển front-end: Bootstrap, Angular, VueJS, ReactJS,v.v... Thành thạo việc xây dựng và sử dụng web service (XML, JSON). Có kinh nghiệm về API Restful. Có kinh nghiệm sử dụng ít nhất 1 hệ quản trị cơ sở dữ liệu MySQL, Postgresql, Oracle, Microsoft SQL Server, MongoDB. Có kinh nghiệm quản lý dự án, có khả năng làm việc độc lập, làm việc theo đội/nhóm. có khả năng lập kế hoạch trong công việc. Nắm vững các kiến thức về Github. Có kinh nghiệm triển khai phần mềm theo kiến trúc micro-services. Giao tiếp tốt, nhiệt huyết, có trách nhiệm với công việc.
```

Điểm của bạn: ___

### `FS_JUN_01` ↔ `jd_1163`

```
Vị trí: Fullstack Developer
Kinh nghiệm: 3 năm
Học vấn: Tốt nghiệp đại học trở lên chuyên ngành CNTT hoặc các ngành tương đương, Chứng chỉ về CNTT được cấp bởi các tổ chức uy tín
Kỹ năng chuyên môn: SQL, noSQL, Jira, Git, Java core, SpringBoot, Microservice, CICD, Containerization, Angular JS, React JS
Yêu cầu: Tốt nghiệp đại học trở lên chuyên ngành CNTT hoặc các ngành tương đương. Trường hợp không đáp ứng, yêu cầu cung cấp Chứng chỉ về CNTT được cấp bởi các tổ chức uy tín. Kinh nghiệm làm việc thực tế tại các công ty, dự án về vị trí phát triển phần mềm. Có kiến thức về quy trình phát triển phần mềm. Có kinh nghiệm làm việc về cơ sở dữ liệu: SQL. Có kinh nghiệm làm việc về cơ sở dữ liệu: noSQL. Có hiểu biết cơ bản về việc sử dụng các công cụ quản trị trong phát triển phần mềm: Jira, Git… Có hiểu biết về về Java core và SpringBoot. Có kinh nghiệm triển khai ứng dụng theo dạng Cloud Native: Microservice, CICD, Containerization... Có kinh nghiệm về framework và thư viện: Angula JS,React JS… Ưu tiên nhân sự có kinh nghiệm về các hệ thống Message Queue. Ưu tiên nhân sự có hiểu biết về xử lý cache, j
```

Điểm của bạn: ___

## CV `DA_JUN_02`

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi tốt nghiệp ngành Quản trị kinh doanh và có khoảng 1,9 năm kinh nghiệm trong công việc liên quan đến Sales Operations, tổng hợp số liệu và báo cáo kết quả kinh doanh. Trong quá trình làm việc tại doanh nghiệp phân phối hàng tiêu dùng, tôi dần tập trung nhiều hơn vào việc xử lý dữ liệu doanh số, sử dụng Excel nâng cao và Power BI để hỗ trợ phòng kinh doanh theo dõi kết quả hoạt động.

Tôi mong muốn tiếp tục phát triển chuyên môn phân tích dữ liệu kinh doanh, đặc biệt là Sales Performance Analysis, KPI Tracking và xây dựng báo cáo có tính trực quan. Tôi cũng muốn vận dụng kiến thức quản trị kinh doanh cùng kinh nghiệm làm việc với số liệu thực tế để cung cấp các báo cáo rõ ràng và hữu ích cho bộ phận kinh doanh.

HỌC VẤN

Cử nhân Quản trị kinh doanh
Đại học công lập khối kinh tế.

Có nền tảng kiến thức về hoạt động kinh doanh, quản lý và đánh giá kết quả bán hàng.

KỸ NĂNG CHUYÊN MÔN

- Microsoft Excel nâng cao: Tổng hợp, xử lý và đối chiếu dữ liệu kinh doanh.
- Power BI: Sử dụng và cập nhật dashboard báo cáo doanh số.
- Power Query: Chuyển đổi và làm sạch dữ liệu từ các bảng báo cáo.
- SQL Server cơ bản: Truy vấn dữ liệu phục vụ công việc.
- DAX cơ bản: Tạo các phép tính phục vụ báo cáo Power BI.
- Sales Performance Analysis: Tổng hợp và phân tích kết quả bán hàng.
- KPI Tracking: Theo dõi chỉ số hoạt động kinh doanh.
- Data Reconciliation: Đối chiếu số liệu giữa các nguồn báo cáo.
- CRM Reporting, Google Sheets, Microsoft PowerPoint.
- Data Storytelling cơ bản.

KỸ NĂNG MỀM

- Có kinh nghiệm phối hợp trực tiếp với phòng kinh doanh trong quá trình chuẩn bị báo cáo.
- Trình bày số liệu bằng bảng biểu, dashboard và PowerPoint.
- Tổng hợp thông tin theo yêu cầu của các bộ phận liên quan.
- Tiếng Việt: Bản ngữ.
- Tiếng Anh: A2-B1, giao tiếp công việc đơn giản.

KINH NGHIỆM LÀM VIỆC

Nhân viên Sales Operations / Báo cáo dữ liệu kinh doanh
Công ty TNHH Phân phối Hưng Thịnh
11/2024 – 10/2026 (1 năm 11 tháng)

- Phụ trách tổng hợp báo cáo doanh số từ hoạt động phân phối hàng tiêu dùng và bán hàng B2B, sử dụng Microsoft Excel để chuẩn bị số liệu theo yêu cầu của phòng kinh doanh.
- Cập nhật dữ liệu lên các dashboard Power BI có sẵn, giúp bộ phận kinh doanh theo dõi kết quả bán hàng và các KPI liên quan.
- Thực hiện đối chiếu số liệu giữa bảng tổng hợp và dữ liệu báo cáo, kiểm tra những trường hợp chưa thống nhất trước khi hoàn thiện báo cáo.
- Sử dụng Power Query để xử lý và chuẩn hóa dữ liệu đầu vào, đồng thời chuẩn bị báo cáo doanh số định kỳ bằng Excel và PowerPoint.

DỰ ÁN

Báo cáo theo dõi doanh số và KPI kinh doanh

Trong quá trình làm việc, tôi tham gia duy trì hệ thống báo cáo doanh số phục vụ bộ phận kinh doanh của doanh nghiệp phân phối hàng tiêu dùng.

Công việc bao gồm tổng hợp dữ liệu, kiểm tra tính nhất quán của số liệu, cập nhật dashboard Power BI và trình bày kết quả theo các yêu cầu báo cáo.

Thông qua công việc này, tôi tích lũy kinh nghiệm thực tế về Sales Performance Analysis, Data Reconciliation và cách sử dụng dữ liệu để hỗ trợ theo dõi hoạt động bán hàng B2B.
```

### `DA_JUN_02` ↔ `jd_1514`

```
Vị trí: Thực Tập Sinh AI
Kinh nghiệm: Không yêu cầu
Học vấn: Công nghệ thông tin, Chuyên ngành liên quan
Kỹ năng chuyên môn: Python, Java, C++
Yêu cầu: Học chuyên ngành Công nghệ thông tin hoặc các chuyên ngành liên quan. Sinh viên năm thứ 4 và có thể đi làm fulltime. Yêu thích ngành CNTT và chịu được áp lực trong công việc.
```

Điểm của bạn: ___

### `DA_JUN_02` ↔ `jd_1626`

```
Vị trí: Nhà phân tích kinh doanh sản phẩm
Kinh nghiệm: 2 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: Figma, Miro, Balsamiq
Yêu cầu: Tối thiểu 2-3 năm kinh nghiệm làm BA, ưu tiên trong các dự án liên quan đến e-commerce. Có kinh nghiệm thực tế về UX/UI, đã từng thiết kế flow, wireframe, mockup, prototype (ưu tiên có sản phẩm thực tế đã triển khai). Thành thạo các công cụ hỗ trợ: Figma, Miro, Balsamiq, hoặc tương đương. Kỹ năng giao tiếp, phân tích và trình bày tốt. Hiểu biết về quy trình phát triển phần mềm (Agile/Scrum). Có khả năng làm việc độc lập và phối hợp nhóm tốt.
```

Điểm của bạn: ___

### `DA_JUN_02` ↔ `jd_0274`

```
Vị trí: Chuyên gia phân tích hoạt động
Kinh nghiệm: 2 năm
Học vấn: Tốt nghiệp Đại học chuyên ngành Phân tích dữ liệu, Hệ thống thông tin, Toán thống kê, Kinh tế, hoặc các ngành liên quan
Kỹ năng chuyên môn: SQL, BigQuery, Metabase, Google Sheets, Python, R
Yêu cầu: Tốt nghiệp Đại học chuyên ngành Phân tích dữ liệu, Hệ thống thông tin, Toán thống kê, Kinh tế, hoặc các ngành liên quan. Tối thiểu 2 năm kinh nghiệm trong phân tích dữ liệu, xây dựng hệ thống báo cáo. Thành thạo SQL và các công cụ phân tích như BigQuery, Metabase, Google Sheets, Python hoặc R là lợi thế. Có kinh nghiệm làm việc với Data Warehouse, Data-mart và luồng ETL. Hiểu biết tốt về thử nghiệm A/B, causal inference, mô hình đánh giá hiệu quả. Có khả năng trình bày, trực quan hóa dữ liệu rõ ràng, dễ hiểu. Kỹ năng quản lý tài liệu, chia sẻ tri thức và truyền đạt quy trình một cách logic, dễ tiếp cận. Có tư duy hệ thống, chú ý chi tiết và tinh thần cải tiến liên tục. Chủ động, có khả năng phối hợp đa phòng ban và quản lý nhiều dự án cùng lúc. Thành thạo tiếng Anh là một lợi thế.
```

Điểm của bạn: ___

## CV `QA_MID_01`

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi có 3,6 năm kinh nghiệm trong lĩnh vực kiểm thử phần mềm, bắt đầu từ Manual Testing và chuyển sang Automation Testing. Đã tham gia phát triển, bảo trì bộ kiểm thử giao diện tự động cho sản phẩm SaaS và phần mềm quản lý nhân sự. Mong muốn tiếp tục nâng cao năng lực thiết kế và tối ưu automation framework, đồng thời đóng góp vào việc duy trì chất lượng sản phẩm trong các chu kỳ phát triển.

HỌC VẤN

Tốt nghiệp Đại học, chuyên ngành Kỹ thuật phần mềm tại một trường đại học công lập.

Có nền tảng kiến thức về phát triển phần mềm và kiểm thử ứng dụng.

KỸ NĂNG CHUYÊN MÔN

- Automation Testing với Playwright.
- Ngôn ngữ lập trình TypeScript, JavaScript.
- Xây dựng test script theo Page Object Model.
- End-to-End Testing và Cross-browser Testing.
- Tích hợp kiểm thử tự động với Jenkins CI.
- Sử dụng Git để quản lý mã nguồn.
- PostgreSQL để kiểm tra dữ liệu liên quan đến kịch bản test.
- Allure Report, Test Data Management.
- Docker ở mức cơ bản.

KỸ NĂNG MỀM

- Làm việc theo quy trình Agile/Scrum.
- Phối hợp với các thành viên phát triển sản phẩm khi xử lý test case thất bại.
- Tiếng Anh B2, đọc tài liệu kỹ thuật và trao đổi công việc với nhóm quốc tế.

KINH NGHIỆM LÀM VIỆC

Automation Tester
Công ty TNHH Phần mềm NovaHR
02/2023 – 09/2026

- Bắt đầu với công việc Manual Tester, thực hiện kiểm tra các chức năng phần mềm quản lý nhân sự trước khi chuyển sang phát triển automation test.
- Xây dựng và duy trì các kịch bản End-to-End Testing bằng Playwright và TypeScript cho nhóm chức năng được phân công.
- Áp dụng Page Object Model để tổ chức mã nguồn kiểm thử, giúp việc cập nhật test script thuận tiện hơn khi giao diện sản phẩm thay đổi.
- Tích hợp bộ kiểm thử vào Jenkins CI, sử dụng Allure Report để theo dõi kết quả chạy test và phân tích những trường hợp thất bại.

DỰ ÁN

Automation Testing cho nền tảng quản lý nhân sự SaaS

Tham gia phát triển bộ kiểm thử giao diện tự động cho các chức năng thuộc hệ thống quản lý nhân sự.

Sử dụng Playwright, TypeScript và JavaScript để viết test script, tổ chức các thành phần theo Page Object Model. Thực hiện Cross-browser Testing và quản lý dữ liệu kiểm thử bằng PostgreSQL.

Các bài test được tích hợp vào Jenkins CI để hỗ trợ kiểm tra sau những thay đổi của sản phẩm. Kết quả được tổng hợp qua Allure Report, giúp nhóm dễ dàng xác định những kịch bản cần kiểm tra lại.

Trong quá trình thực hiện, tôi tập trung vào tính ổn định và khả năng bảo trì của các bài kiểm thử thuộc phạm vi mình phụ trách.
```

### `QA_MID_01` ↔ `jd_1711`

```
Vị trí: Tester Intern
Kinh nghiệm: Không yêu cầu
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: Kiểm thử phần mềm, Kỹ thuật kiểm thử hộp đen, Test API cơ bản, Sử dụng Postman, Sử dụng Firebase, Sử dụng Qonversion
Yêu cầu: • Có các kiến thức cơ bản về Kiểm thử phần mềm
• Nắm vững các kĩ thuật kiểm thử hộp đen (Phân tích giá trị biên, phân vùng tương đương, bảng quyết định,...)
• Năng động, cởi mở, có khả năng hòa nhập và gắn kết với đội nhóm
• Có khả năng phân tích tốt về UX Analytics.
• Biết Test API cơ bản ( biết viết TCs API và biết sử dụng cơ bản Postman (collections, environments, methods, request- response) là điểm cộng
• Biết sử dụng các công cụ phân tích user (Firebase, Qonversion) là 1 lợi thế
• Có khả năng làm việc sâu, chi tiết, cẩn thận, tỷ mỉ.
```

Điểm của bạn: ___

### `QA_MID_01` ↔ `jd_1836`

```
Vị trí: QA Tester
Kinh nghiệm: 3 năm
Học vấn: Tốt nghiệp chuyên ngành CNTT hoặc có chứng chỉ tương đương
Kỹ năng chuyên môn: Kiến thức tổng quan về hệ thống CNTT, Dịch vụ CNTT, CSDL – SQL, Automation Test (API, Web, Mobile, Performance, Security)
Yêu cầu: Tốt nghiệp chuyên ngành CNTT hoặc có chứng chỉ tương đương. Có 3 năm kinh nghiệm trong lĩnh vực kiểm thử phần mềm website và mobile app. ĐÃ LÀM trong các dự án liên quan đến tài chính, banking, ví điện tử, cổng thanh toán, … Có kiến thức tổng quan về hệ thống CNTT, dịch vụ CNTT, hiểu biết về CSDL – SQL. Có hiểu biết về các giai đoạn phát triển của sản phẩm. Có khả năng làm việc với cường độ cao, khả năng nghiên cứu tốt, có khả năng làm độc lập và làm việc theo nhóm. Yêu thích công việc, ham học hỏi, có tinh thần trách nhiệm cao, tỉ mỉ, cẩn thận. Ưu tiên ứng viên có kinh nghiệm làm Automation Test (API, Web, Mobile, Performance, Security …). Ưu tiên có kinh nghiệm lập kế hoạch kiểm thử, tổng hợp vấn đề chất lượng dự án và đưa ra đề xuất cải tiến. Có kinh nghiệm với Agile, Scrum là lợi thế.
```

Điểm của bạn: ___

### `QA_MID_01` ↔ `jd_1162`

```
Vị trí: Nhà phát triển Python trở lại
Kinh nghiệm: 3 năm
Học vấn: Bachelor's degree
Kỹ năng chuyên môn: Python, Fast API, SlqAlchemy, JPA, Alembic, Flyway, Kubernetes, Docker, AWS Cognito, AWS S3, AWS SES, AWS Lambda
Yêu cầu: 3+ years of experience in Python development. Bachelor's degree. Proficiency in Python frameworks such as Fast API. Experience in working with ORM such as SlqAlchemy, JPA. Experience working with DB Configuration Management such as Alembic, Flyway. Experience in debugging in Kubernetes, Docker/Container, Cloud (AWS) environment. Experience in AWS Cognito/AWS S3/AWS SES/AWS Lambda. Strong problem-solving and analytical skills. Good communication skills and the ability to work in a team environment.
```

Điểm của bạn: ___

### `QA_MID_01` ↔ `jd_1163`

```
Vị trí: Fullstack Developer
Kinh nghiệm: 3 năm
Học vấn: Tốt nghiệp đại học trở lên chuyên ngành CNTT hoặc các ngành tương đương, Chứng chỉ về CNTT được cấp bởi các tổ chức uy tín
Kỹ năng chuyên môn: SQL, noSQL, Jira, Git, Java core, SpringBoot, Microservice, CICD, Containerization, Angular JS, React JS
Yêu cầu: Tốt nghiệp đại học trở lên chuyên ngành CNTT hoặc các ngành tương đương. Trường hợp không đáp ứng, yêu cầu cung cấp Chứng chỉ về CNTT được cấp bởi các tổ chức uy tín. Kinh nghiệm làm việc thực tế tại các công ty, dự án về vị trí phát triển phần mềm. Có kiến thức về quy trình phát triển phần mềm. Có kinh nghiệm làm việc về cơ sở dữ liệu: SQL. Có kinh nghiệm làm việc về cơ sở dữ liệu: noSQL. Có hiểu biết cơ bản về việc sử dụng các công cụ quản trị trong phát triển phần mềm: Jira, Git… Có hiểu biết về về Java core và SpringBoot. Có kinh nghiệm triển khai ứng dụng theo dạng Cloud Native: Microservice, CICD, Containerization... Có kinh nghiệm về framework và thư viện: Angula JS,React JS… Ưu tiên nhân sự có kinh nghiệm về các hệ thống Message Queue. Ưu tiên nhân sự có hiểu biết về xử lý cache, j
```

Điểm của bạn: ___

### `QA_MID_01` ↔ `jd_0246`

```
Vị trí: Chuyên Viên Kiểm Thử Phần Mềm
Kinh nghiệm: 2 năm
Học vấn: Tốt nghiệp đại học, cao đẳng hoặc tương đương các chuyên ngành Kế toán, Kiểm toán, Kinh tế, Tài chính doanh nghiệp, HTTT, CNTT
Kỹ năng chuyên môn: Viết Testcase, Thực Hiện Test Case, Báo Cáo Lỗi (bug Reporting), phân tích yêu cầu, Kiểm Thử Chức Năng (functional Testing)
Yêu cầu: • Tốt nghiệp đại học, cao đẳng hoặc tương đương các chuyên ngành Kế toán, Kiểm toán, Kinh tế, Tài chính doanh nghiệp, HTTT, CNTT...
• Có ít nhất 2 năm kinh nghiệm test các hệ thống phần mềm Quản lý kho, bán hàng, sản xuất, kế toán hoặc cả hệ thống ERP
• Yêu nghề, cẩn thận, tỉ mỉ, xử lý công việc linh hoạt
• Có thái độ hòa nhã, thân thiện, chân thành.
```

Điểm của bạn: ___

## CV `PM_MID_01`

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi là kỹ sư Công nghệ phần mềm với gần 4 năm kinh nghiệm quản lý và điều phối dự án tại doanh nghiệp outsourcing. Có kinh nghiệm lập kế hoạch triển khai, quản lý phạm vi, tiến độ, nguồn lực và phối hợp nghiệm thu các dự án web quy mô vừa. Mong muốn tiếp tục phát triển chuyên môn quản lý dự án CNTT, nâng cao hiệu quả phối hợp giữa nhóm phát triển và khách hàng, đồng thời đảm bảo sản phẩm được bàn giao theo phạm vi và tiến độ đã thống nhất.

HỌC VẤN

Kỹ sư Công nghệ phần mềm
Trường đại học công lập

KỸ NĂNG CHUYÊN MÔN

- Lập kế hoạch, xây dựng Work Breakdown Structure (WBS) và quản lý tiến độ dự án phần mềm.
- Quản lý phạm vi, nguồn lực, chi phí và yêu cầu thay đổi trong quá trình triển khai.
- Áp dụng Scrum và Kanban phù hợp với đặc thù từng dự án.
- Sử dụng Microsoft Project để lập kế hoạch, phân bổ công việc và theo dõi tiến độ.
- Xây dựng Gantt Chart, quản lý Risk Register và Issue Log.
- Sử dụng GitLab Issues, Microsoft Teams và Power BI cơ bản.
- Phối hợp nghiệm thu, bàn giao sản phẩm và tổng hợp báo cáo dự án.

KỸ NĂNG MỀM

- Điều phối nhóm phát triển từ 8-12 thành viên.
- Đàm phán và trao đổi yêu cầu với khách hàng.
- Giải quyết xung đột và phối hợp giữa các thành viên.
- Quản lý cuộc trao đổi liên quan đến tiến độ và thay đổi phạm vi dự án.

KINH NGHIỆM LÀM VIỆC

Công ty Cổ phần Giải pháp Phần mềm Đại Nam
IT Project Manager | 12/2022 - 09/2026 (3 năm 10 tháng)

- Lập kế hoạch triển khai các dự án web và hệ thống quản trị doanh nghiệp, xây dựng WBS, xác định đầu việc, phân bổ nguồn lực và theo dõi tiến độ bằng Microsoft Project.
- Điều phối nhóm phát triển 8-12 thành viên, kết hợp Scrum và Kanban theo đặc thù dự án nhằm quản lý công việc và xử lý các vấn đề ảnh hưởng đến kế hoạch.
- Theo dõi Risk Register, Issue Log và Change Request; làm việc với khách hàng để thống nhất các yêu cầu điều chỉnh, đồng thời báo cáo những thay đổi có ảnh hưởng đến phạm vi và tiến độ.
- Tổng hợp chi phí và tình trạng dự án để báo cáo cấp quản lý; phối hợp cùng đội phát triển và khách hàng hoàn thành các bước nghiệm thu, bàn giao phần mềm.

DỰ ÁN

Triển khai hệ thống quản trị doanh nghiệp trên nền tảng web

Phụ trách lập kế hoạch và điều phối nhóm phát triển cho dự án quy mô vừa. Quản lý các mốc công việc, theo dõi yêu cầu thay đổi và tổ chức phối hợp giữa nhóm kỹ thuật với khách hàng trong giai đoạn nghiệm thu. Các báo cáo tiến độ và chi phí được tổng hợp để hỗ trợ cấp quản lý theo dõi dự án.

NGOẠI NGỮ

- Tiếng Anh B2: Giao tiếp trong cuộc họp dự án và viết báo cáo.
- Tiếng Nhật N4: Giao tiếp cơ bản.
```

### `PM_MID_01` ↔ `jd_0512`

```
Vị trí: Quản lý dự án & TechLeader
Kinh nghiệm: 1 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: docker, k8s, gitlab cicd, jenkins, argocd, Agile
Yêu cầu: ● Các ứng viên có nền tảng technical tốt muốn đi lên quản lý. ● Có kinh nghiệm trong việc thiết kế kiến trúc hệ thống, mô hình HA, microservice, docker, k8s, gitlab cicd, jenkins, argocd. ● Tiếng anh ở mức khá, có thể đọc hiểu tài liệu. ● Đã làm quen với Agile, chứng chỉ PMP/PSC1 là 1 điểm cộng. ● Có kinh nghiệm sử dụng các tool quản lý dự án: Jira, MS Project, Google Sheet, v.v. ● Nhanh nhẹn, hoạt bát.
```

Điểm của bạn: ___

### `PM_MID_01` ↔ `jd_0490`

```
Vị trí: Nhân Viên Lập Trình CNC
Kinh nghiệm: 3 năm
Học vấn: Cao đẳng/ Đại học chuyên ngành Cơ khí, chế tạo máy hoặc các ngành nghề liên quan
Kỹ năng chuyên môn: Lập trình CNC, Phần mềm CAM (Mastercam), Gia công cơ khí, Đọc hiểu bản vẽ kỹ thuật
Yêu cầu: Tốt nghiệp Cao đẳng/ Đại học chuyên ngành Cơ khí, chế tạo máy hoặc các ngành nghề liên quan. Có từ 3 năm kinh nghiệm lập trình CNC, vận hành máy CNC. Nắm vững các phần mềm CAM (Mastercam) và các kỹ thuật lập trình gia công CNC. Có kiến thức về gia công cơ khí, vật liệu, công nghệ gia công. Nắm vững các quy trình an toàn lao động trong vận hành máy CNC. Có khả năng đọc hiểu bản vẽ kỹ thuật, phân tích yêu cầu kỹ thuật. Có khả năng làm việc độc lập và làm việc nhóm, chịu được áp lực công việc. Có tinh thần trách nhiệm cao, cẩn thận, tỉ mỉ, ham học hỏi.
```

Điểm của bạn: ___

### `PM_MID_01` ↔ `jd_0595`

```
Vị trí: Project Manager
Kinh nghiệm: 3 năm
Học vấn: Tốt nghiệp Đại học, Cao đẳng chuyên ngành Công nghệ thông tin hoặc các chuyên ngành có liên quan.
Kỹ năng chuyên môn: PHP, Java, Kotlin, Swift
Yêu cầu: Kinh nghiệm: Từ 3 năm kinh nghiệm quản lý dự án, có khả năng quản lý team 5-10 người. Năng lực chuyên môn, chứng chỉ: Tốt nghiệp Đại học, Cao đẳng chuyên ngành Công nghệ thông tin hoặc các chuyên ngành có liên quan. Có kinh nghiệm lập trình ít nhất một trong các ngôn ngữ: PHP (ưu tiên), Java, Kotlin, Swift. Nắm vững quy trình phát triển sản phẩm phần mềm. Có kinh nghiệm thiết kế hệ thống phần mềm. Có khả năng giao tiếp/ kinh nghiệm làm việc và đề xuất giải pháp cho khách hàng. Ưu tiên ứng viên sở hữu các chứng chỉ quản lý dự án như: PMP, PMI-ACP, PSM... Có hiểu biết và kinh nghiệm thực tế trong việc quản lý dự án theo phương pháp Agile/Scrum. Có khả năng phân tích và đánh giá rủi ro trong dự án. Yêu cầu khác: Có kỹ năng lãnh đạo và giải quyết vấn đề. Có tư duy phát triển, tư duy sản phẩm. 
```

Điểm của bạn: ___

### `PM_MID_01` ↔ `jd_1309`

```
Vị trí: Quản lý dự án/Scrum Master (tên miền Fintech)
Kinh nghiệm: 2 năm
Học vấn: Tốt nghiệp Đại học loại Khá trở lên, ưu tiên chuyên ngành CNTT, Kỹ thuật phần mềm, An toàn thông tin và ngành có liên quan
Kỹ năng chuyên môn: Quản trị dự án, Agile, Scrum, Công cụ quản trị dự án
Yêu cầu: Tốt nghiệp Đại học loại Khá trở lên, ưu tiên chuyên ngành CNTT, Kỹ thuật phần mềm, An toàn thông tin và ngành có liên quan. Tiếng Anh tương đương 550+ TOEIC. Có kinh nghiệm ít nhất 02 năm ở vị trí quản lý dự án công nghệ thông tin hoặc các dự án tương tự (PM). Ưu tiên các ứng viên có chứng chỉ PMP hoặc Scrum Master. Có kinh nghiệm quản trị các dự án theo nhiều mô hình khác nhau như Agile, Waterfall. Có kinh nghiệm Scrum Master tốt, định hướng tìm hiểu sâu về Scrum. Thành thạo các công cụ quản trị dự án và kiểm soát rủi ro. Có trách nhiệm cao và thái độ tốt trong công việc. Có khả năng làm việc độc lập hoặc làm việc theo nhóm tốt. Kỹ năng giao tiếp và trình bày tốt. Làm việc dưới áp lực cao, nhạy bén và tiếp thu nhanh. Ưu tiên ứng viên có thể đi làm ngay hoặc có thể xem xét nhận việc sau tế
```

Điểm của bạn: ___

### `PM_MID_01` ↔ `jd_0317`

```
Vị trí: Nhân Viên Quản Lý Dự Án
Kinh nghiệm: Không yêu cầu
Học vấn: Cao Đẳng trở lên
Kỹ năng chuyên môn: Quản lý dự án theo phương pháp Agile, Kiến thức cơ bản về lập trình, Phân tích & thiết kế hệ thống, Cấu trúc dữ liệu, Giải thuật, Java, PHP, .NET, Oracle, SQL Server, MySQL, MariaDB
Yêu cầu: Giao tiếp tiếng Anh tốt, tương đương IELTS 6.0 trở lên. Ưu tiên có kinh nghiệm quản lý dự án theo phương pháp Agile hoặc Scrum. Ưu tiên có kiến thức cơ bản về lập trình, phân tích & thiết kế hệ thống, cấu trúc dữ liệu và giải thuật. Ưu tiên có hiểu biết về một trong các ngôn ngữ lập trình phổ biến như Java, PHP, .NET, và các hệ quản trị cơ sở dữ liệu như Oracle, SQL Server, MySQL, MariaDB. Có kỹ năng lập kế hoạch, giải quyết vấn đề và quản lý công việc tốt; linh hoạt xử lý tình huống. Kỹ năng giao tiếp, làm việc nhóm tốt; chịu được áp lực công việc; có tinh thần trách nhiệm cao; chủ động và sáng tạo. Có kinh nghiệm làm việc trong các dự án thương mại điện tử là một lợi thế.
```

Điểm của bạn: ___

## CV `SYS_JUN_01`

```
MỤC TIÊU NGHỀ NGHIỆP

Có 1,5 năm kinh nghiệm vận hành mạng tại nhà cung cấp dịch vụ Internet. Công việc chính là giám sát hệ thống, tiếp nhận cảnh báo và phối hợp xử lý sự cố kết nối theo ca. Mong muốn tiếp tục phát triển trong lĩnh vực Network Operations, tập trung vào khả năng phân tích cảnh báo, theo dõi chất lượng kết nối và cải thiện hiệu quả xử lý sự cố trong hệ thống mạng.

HỌC VẤN

Đại học kỹ thuật
Ngành: Điện tử Viễn thông
Trình độ: Đại học

Có nền tảng kiến thức về mạng viễn thông và hoạt động của thiết bị mạng, được áp dụng trong công việc giám sát hệ thống tại trung tâm NOC.

KỸ NĂNG CHUYÊN MÔN

- Zabbix: Theo dõi trạng thái và cảnh báo của các thiết bị mạng.
- SNMP monitoring: Giám sát các thông số vận hành mạng.
- Network troubleshooting: Kiểm tra trạng thái router, switch và xử lý bước đầu các cảnh báo mất kết nối.
- Log analysis: Đọc và phân tích log thiết bị mạng ở mức cơ bản.
- Network performance: Kiểm tra độ trễ và packet loss.
- Incident Management: Quản lý ticket sự cố theo quy trình NOC và ITIL Incident Management.
- Grafana: Theo dõi thông tin vận hành qua dashboard.
- MikroTik RouterOS: Có kiến thức thao tác cơ bản.
- Excel: Tổng hợp dữ liệu và lập báo cáo vận hành.

KỸ NĂNG MỀM

- Quen làm việc theo ca và phối hợp chuyển tiếp sự cố giữa các ca trực.
- Có khả năng ghi nhận thông tin sự cố rõ ràng trong ticket.
- Tiếng Anh B1, đọc hiểu log và tài liệu thiết bị mạng.
- Biết tổng hợp tình trạng vận hành và báo cáo các vấn đề phát sinh.

KINH NGHIỆM LÀM VIỆC

Công ty Cổ phần Dịch vụ Internet An Việt
Vị trí: Network Operations Engineer – NOC
Thời gian: 04/2025 – 09/2026 (1 năm 6 tháng)

- Giám sát trạng thái hệ thống mạng bằng Zabbix và SNMP, kiểm tra các cảnh báo liên quan đến router, switch và kết nối mạng trong ca trực.
- Tiếp nhận các cảnh báo mất kết nối, kiểm tra độ trễ và packet loss, ghi nhận thông tin để xác định tình trạng sự cố ban đầu.
- Tạo, cập nhật và chuyển tiếp ticket tới bộ phận phụ trách theo quy trình NOC, duy trì thông tin cần thiết để theo dõi tiến độ xử lý.
- Theo dõi Grafana dashboard, kiểm tra log thiết bị khi cần và tổng hợp báo cáo vận hành bằng Excel phục vụ công tác bàn giao ca.

Kinh nghiệm tập trung vào giám sát, phân loại sự cố và phối hợp vận hành hệ thống mạng của nhà cung cấp dịch vụ Internet.
```

### `SYS_JUN_01` ↔ `jd_0331`

```
Vị trí: Nhân Viên Kỹ Thuật Lập Trình CNC
Kinh nghiệm: 1 năm
Học vấn: Trung cấp trở lên các chuyên ngành liên quan: Kĩ nghệ gỗ, Công nghệ chế biến lâm sản, Điều khiển - tự động hóa, Cơ khí chế tạo
Kỹ năng chuyên môn: Alphacam, AutoCAD 2D, AutoCAD 3D, Inventor
Yêu cầu: Ưu tiên có 1–2 năm lập trình CNC trong sản xuất gỗ; Sử dụng thành thạo phần mềm Alphacam; AutoCAD 2D, 3D hoặc Inventor; Am hiểu tốt kĩ thuật vận hành các máy CNC (ưu tiên ngành gỗ); Tốt nghiệp Trung cấp trở lên các chuyên ngành liên quan: Kĩ nghệ gỗ, Công nghệ chế biến lâm sản, Điều khiển - tự động hóa, Cơ khí chế tạo,…
```

Điểm của bạn: ___

### `SYS_JUN_01` ↔ `jd_0612`

```
Vị trí: Nhân Viên Kỹ Thuật Máy Tính
Kinh nghiệm: 2 năm
Học vấn: Trung cấp, Cao đẳng, Đại học chuyên ngành Công nghệ thông tin, Kỹ thuật máy tính
Kỹ năng chuyên môn: Kiến thức cơ bản về phần cứng, Phần mềm, Mạng máy tính, Sử dụng các công cụ điều khiển từ xa, Phần mềm hỗ trợ IT
Yêu cầu: Tốt nghiệp Trung cấp/Cao đẳng/Đại học chuyên ngành Công nghệ thông tin, Kỹ thuật máy tính hoặc liên quan. Có kiến thức cơ bản về phần cứng, phần mềm, mạng máy tính. Biết sử dụng các công cụ điều khiển từ xa và phần mềm hỗ trợ IT. Trung thực, cẩn thận, có tinh thần trách nhiệm. Ưu tiên có kinh nghiệm ở vị trí tương đương.
```

Điểm của bạn: ___

### `SYS_JUN_01` ↔ `jd_1720`

```
Vị trí: Nhân Viên Network Security
Kinh nghiệm: 1 năm
Học vấn: Tốt nghiệp đại học ngành Công nghệ Thông tin, Điện tử Viễn thông, hoặc chuyên ngành khác có liên quan
Kỹ năng chuyên môn: Linux, Windows, Routing, Switching, Network Security
Yêu cầu: Tốt nghiệp đại học ngành Công nghệ Thông tin hoặc Điện tử Viễn thông hoặc chuyên ngành khác có liên quan. Có kiến thức tốt về Linux, Windows, Routing, Switching, và Network Security. Có kinh nghiệm 1-2 năm về thiết kế, triển khai mạng doanh nghiệp, hoặc có kinh nghiệm vận hành hệ thống mạng, hệ thống hạ tầng CNTT. Hiểu biết các giao thức và công cụ để quản lý, giám sát và phân tích mạng. Ưu tiên có các chứng chỉ CCNA, CCNP, CompTIA Security+, CEH, hoặc tương đương. Ưu tiên có kinh nghiệm triển khai các sản phẩm Security: Firewall, WAF, DBFW, PAM, DLP, SIEM. Có khả năng nghiên cứu công nghệ, sản phẩm và giải pháp mới ứng dụng cho công việc. Có kỹ năng giao tiếp, thuyết trình và viết các tài liệu kỹ thuật.
```

Điểm của bạn: ___

## CV `DE_SEN_01`

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

### `DE_SEN_01` ↔ `jd_1637`

```
Vị trí: Chuyên gia phân tích/phân tích kinh doanh hệ thống - TA171
Kinh nghiệm: 5 năm
Học vấn: A bachelor's in computer science or related field
Kỹ năng chuyên môn: Core Banking, Card service systems, OLTP software system, microservices architecture, Relational database (MS SQL, MySQL, Postgre, Oracle)
Yêu cầu: Educational Qualifications: A bachelor's in computer science or related field. Relevant Knowledge/ Expertise: Minimum of +5 years hands on experience with at least one of the following Banking system (Core Banking, Card,...). Have experience and expert knowledge in Card service systems or relating. Have strong experience in design solution for Card Products and/or Card services. Have strong experience in solution design for OLTP software system in microservices architecture and/or strong experience in Relational database (MS SQL, MySQL, Postgre, Oracle,..). Understand Banking knowledge (priority for Card businesses). Have experience with ISO messages and International Card Policies (Visa. MasterCard,...). Have experience data flow as well as processes of ATM, CDM, POS,... An understanding 
```

Điểm của bạn: ___

### `DE_SEN_01` ↔ `jd_0296`

```
Vị trí: Kỹ Sư Dữ Liệu Cấp Cao
Kinh nghiệm: 4 năm
Học vấn: Tốt nghiệp đại học chuyên ngành Khoa học Máy tính, Kỹ thuật Phần mềm, Hệ thống Thông tin
Kỹ năng chuyên môn: Python, Java, Scala, Go, Javascript, Typescript, R, SQL, GCP, AWS, MongoDB, PostgreSQL, BigQuery, ClickHouse, Redpanda, Kafka, RabbitMQ, Airflow, dbt, Airbyte, Metabase, PowerBI, Looker Studio, GitLab, GitHub, Hadoop, Spark, Databricks, Kubernetes
Yêu cầu: Tốt nghiệp đại học chuyên ngành Khoa học Máy tính, Kỹ thuật Phần mềm hoặc Hệ thống Thông tin. Có chuyên môn về khoa học dữ liệu hoặc bằng cấp cao hơn là một lợi thế lớn. Tối thiểu 4 năm kinh nghiệm trong vai trò kỹ sư dữ liệu, xây dựng nền tảng và pipeline phục vụ phân tích. Thành thạo Python và ít nhất một ngôn ngữ lập trình khác như Java, Scala, Go, Javascript, Typescript, R là một điểm cộng lớn. Thành thạo SQL trên các hệ quản trị cơ sở dữ liệu (DBMS). Có kinh nghiệm với các dịch vụ đám mây như GCP, AWS. Có kinh nghiệm làm việc với nhiều hệ cơ sở dữ liệu OLTP và OLAP như MongoDB, PostgreSQL, BigQuery, ClickHouse,... Có kinh nghiệm với các nền tảng và khái niệm xử lý dữ liệu streaming như Redpanda, Kafka, RabbitMQ, CDC hoặc mã nguồn mở khác. Có kinh nghiệm với các công cụ quản lý pipelin
```

Điểm của bạn: ___

### `DE_SEN_01` ↔ `jd_1896`

```
Vị trí: Data Engineer
Kinh nghiệm: 2 năm
Học vấn: Cao Đẳng trở lên
Kỹ năng chuyên môn: Spark, Python, AWS, Databricks, ETL, Big Data
Yêu cầu: Tối thiểu 2 năm kinh nghiệm làm việc ở vị trí Data Engineer mạnh về spark. Có kinh nghiệm với Python (trên 1 năm), viết mã sạch, dễ bảo trì. Tư duy logic tốt, giải quyết vấn đề hiệu quả. Có kinh nghiệm sử dụng Spark để xử lý dữ liệu lớn (trên 1 năm). Am hiểu cấu trúc dữ liệu, thuật toán lập trình. Có kinh nghiệm xây dựng ETL trên nền tảng Cloud. Ưu tiên ứng viên từng làm việc với AWS hoặc Databricks.
```

Điểm của bạn: ___

## CV `FE_FRE_01`

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi là sinh viên năm cuối ngành Công nghệ thông tin, định hướng phát triển trong lĩnh vực Frontend với ReactJS. Đã có thời gian thực tập tại công ty phần mềm, tham gia xây dựng giao diện trang khóa học và chỉnh sửa các React component theo hướng dẫn của mentor. Mong muốn được làm việc trong môi trường chuyên nghiệp để nâng cao khả năng lập trình JavaScript, ReactJS và tích lũy thêm kinh nghiệm phát triển sản phẩm thực tế.

HỌC VẤN

Sinh viên năm cuối ngành Công nghệ thông tin

Trường đại học công lập

Được học và thực hành các kiến thức lập trình web, tập trung tìm hiểu HTML5, CSS3, JavaScript ES6+ và ReactJS.

KỸ NĂNG CHUYÊN MÔN

- Ngôn ngữ và giao diện: HTML5, CSS3, JavaScript ES6+.
- Framework/Library: ReactJS, React Hooks cơ bản, Bootstrap 5.
- Thiết kế giao diện: Responsive Web Design, Figma cơ bản.
- Công cụ phát triển: Git, Vite, npm, Postman.
- API: REST API integration, kết nối dữ liệu từ API vào giao diện React.

KỸ NĂNG MỀM

- Có khả năng tiếp nhận hướng dẫn và phản hồi từ mentor trong quá trình làm việc.
- Phối hợp với các thành viên trong nhóm khi chỉnh sửa giao diện.
- Tiếng Anh B1, có thể đọc tài liệu kỹ thuật và giao tiếp cơ bản.

KINH NGHIỆM LÀM VIỆC

Frontend Developer Intern

Công ty Phần mềm Minh Phát

Thời gian: 0,4 năm

Lĩnh vực: Giáo dục trực tuyến

- Tham gia xây dựng giao diện trang khóa học trực tuyến bằng ReactJS, HTML5 và CSS3.
- Chỉnh sửa các React component theo yêu cầu và hướng dẫn từ mentor, hoàn thiện phần giao diện được giao.
- Sử dụng React Hooks cơ bản để xử lý dữ liệu trong component, kết hợp Responsive Web Design để điều chỉnh hiển thị trên các kích thước màn hình.
- Sử dụng Git để quản lý thay đổi mã nguồn và phối hợp cập nhật giao diện trong quá trình thực tập.

DỰ ÁN

Giao diện nền tảng khóa học trực tuyến

Công nghệ: ReactJS, JavaScript ES6+, HTML5, CSS3, Bootstrap 5.

Tham gia phát triển và điều chỉnh giao diện trang khóa học trong thời gian thực tập. Công việc tập trung vào xây dựng component, chỉnh sửa bố cục và hỗ trợ tích hợp dữ liệu từ REST API vào các phần giao diện được phân công.
```

### `FE_FRE_01` ↔ `jd_1208`

```
Vị trí: Coaching Data Analyst
Kinh nghiệm: Không yêu cầu
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: Python, R, SQL, Excel, Power BI, Tableau, Jupyter Notebook
Yêu cầu: - Ưu tiên cho người có kinh nghiệm giảng dạy, COACHING
- Tiếng Anh Tốt: IELTS từ 6.0 trở lên, TOIEC từ 800. Kỹ năng Speaking tốt để thực hiện công việc đào tạo, giảng dạy môi trường quốc tế.
- Bạn có tư duy phản biện hoặc kỹ năng giải quyết vấn đề để nhận diện và phân tích vấn đề một cách hiệu quả nhất.
- Có kiến thức về toán thống kê, quen thuộc với ngôn ngữ lập trình: Python hoặc R.
- Có kiến thức về Cơ sở dữ liệu và truy vấn SQL.
- Có thể làm việc với các công cụ phân tích và trực quan hóa như: bảng tính Excel, Power BI, Tableau, Jupyter Notebook, v.v (ƯU TIÊN)
- Rèn luyện các kỹ năng mềm: kỹ năng giao tiếp, thuyết trình, làm việc nhóm tốt.
```

Điểm của bạn: ___

## CV `DEVOPS_MID_02`

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

### `DEVOPS_MID_02` ↔ `jd_0248`

```
Vị trí: Nhân Viên IT SUPPORT
Kinh nghiệm: 2 năm
Học vấn: Tốt nghiệp chuyên ngành Công nghệ thông tin, Mạng máy tính, Khoa học máy tính hoặc các ngành có chứng chỉ liên quan
Kỹ năng chuyên môn: Hệ thống mạng (LAN, WAN, VPN), Giao thức mạng (TCP/IP, DNS, DHCP), Quản trị hệ thống và máy chủ (Windows Server, Linux), Hệ thống quản lý IT (Helpdesk, quản lý tài sản), Bảo mật hệ thống (Firewall, Antivirus, IDS/IPS), Microsoft 365
Yêu cầu: Tốt nghiệp chuyên ngành Công nghệ thông tin, Mạng máy tính, Khoa học máy tính hoặc các ngành có chứng chỉ liên quan. Kinh nghiệm làm việc từ 2 năm trong việc helpdesk và quản lý hệ thống mạng. Am hiểu về hệ thống mạng (LAN, WAN, VPN) và các giao thức mạng như TCP/IP, DNS, DHCP. Kỹ năng quản trị hệ thống và máy chủ (Windows Server, Linux). Có hiểu biết và kinh nghiệm triển khai các hệ thống quản lý IT (Helpdesk, quản lý tài sản, theo dõi hệ thống,…). Kiến thức về bảo mật hệ thống (Firewall, Antivirus, IDS/IPS). Thành thạo việc giám sát, bảo trì và tối ưu hiệu suất hệ thống. Có kinh nghiệm về quản lý các dịch vụ của Microsoft 365. Ưu tiên ứng viên có kinh nghiệm xây dựng ứng dụng trong Power Apps của Microsoft. Không ngừng học hỏi, nâng cao kiến thức để có những chiến lược nâng cấp hệ thống 
```

Điểm của bạn: ___

## CV `MOB_SEN_01`

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

### `MOB_SEN_01` ↔ `jd_1562`

```
Vị trí: Fullstack
Kinh nghiệm: 5 năm
Học vấn: Đại Học trở lên
Kỹ năng chuyên môn: ReactJS, NextJS, NodeJS, React Native, Flutter, AWS (EC2, S3, Lambda, RDS, API Gateway)
Yêu cầu: Tối thiểu 5 năm kinh nghiệm phát triển phần mềm, đặc biệt với ReactJS, NextJS, NodeJS. Tối thiểu 5 năm kinh nghiệm phát triển phần mềm, trong đó có kinh nghiệm vững với React Native và/hoặc Flutter. Thành thạo trong việc thiết kế và phát triển ứng dụng di động đa nền tảng (iOS & Android) sử dụng React Native hoặc Flutter. Có kinh nghiệm triển khai và vận hành hệ thống trên AWS (EC2, S3, Lambda, RDS, API Gateway). Có kinh nghiệm triển khai ứng dụng lên App Store và Google Play. Hiểu rõ về kiến trúc ứng dụng di động, quản lý trạng thái, hiệu năng và các nguyên tắc bảo mật trong ứng dụng fintech. Ưu tiên ứng viên có kinh nghiệm tích hợp API tài chính, dữ liệu đầu tư hoặc danh mục người dùng. Hiểu biết về API tài chính/đầu tư và các nguyên tắc bảo mật trong lĩnh vực fintech là một lợi thế.
```

Điểm của bạn: ___

### `MOB_SEN_01` ↔ `jd_1257`

```
Vị trí: Flutter Developer
Kinh nghiệm: 4 năm
Học vấn: A degree in computer science, software engineering, information technology or related fields
Kỹ năng chuyên môn: Dart, Flutter Framework, Git, REST APIs, State Management (provider, Bloc, Riverpod, Etc.)
Yêu cầu: A degree in computer science, software engineering, information technology or related fields. At least 4 years of experience in app development. Having knowledge of Agile and Scrum project management and why it is necessary. Understanding of commonly used design patterns, like MVC, Repository, DI… UX/UI design exposure and experience in making apps work intuitively and with pixel perfect interfaces. Experience in CI/CD frameworks for mobile applications. Familiarity with RESTful APIs to connect applications to back-end services. Knowledge of UI/UX standards, especially Material Design. Be able to write concise, well-documented (or self-documenting) code. You are highly accountable and take ownership. You also have a collaborative attitude. Good at speaking English.
```

Điểm của bạn: ___

### `MOB_SEN_01` ↔ `jd_0282`

```
Vị trí: Nhân Viên Lập Trình Mobile
Kinh nghiệm: 1 năm
Học vấn: Tốt nghiệp đại học chuyên ngành Công nghệ thông tin hoặc các chuyên ngành khác am hiểu lập trình
Kỹ năng chuyên môn: Flutter, React Native
Yêu cầu: Tốt nghiệp đại học chuyên ngành Công nghệ thông tin hoặc các chuyên ngành khác am hiểu lập trình; Có kỹ năng lập trình Mobile bằng Flutter; React Native hoặc tương đương; Có khả năng phân tích, sáng tạo, chịu áp lực công việc, có tinh thần học hỏi, tận tâm trong công việc; Đã có kinh nghiệm chủ trì hoặc tham gia phát triển ứng dụng Mobibe tối thiểu 1 năm; Làm việc ổn định tại Hà Nội.
```

Điểm của bạn: ___

## CV `DES_JUN_01`

```
MỤC TIÊU NGHỀ NGHIỆP

Tôi là UI/UX Designer với khoảng 1,6 năm kinh nghiệm tại công ty phát triển phần mềm. Đã tham gia thiết kế giao diện cho hai sản phẩm thuộc lĩnh vực thương mại điện tử và quản lý bán hàng. Mong muốn tiếp tục phát triển kỹ năng thiết kế trải nghiệm người dùng, cải thiện cách tổ chức thông tin và xây dựng giao diện có tính nhất quán, dễ thao tác. Ưu tiên môi trường làm việc có quy trình review và trao đổi thiết kế rõ ràng.

HỌC VẤN

Cử nhân Công nghệ đa phương tiện – Trường đại học công lập
Đã tốt nghiệp.

KỸ NĂNG CHUYÊN MÔN

- Figma: UI/UX Design, Component Design và Interactive Prototyping.
- User Flow, Wireframing và Information Architecture.
- Responsive Web Design cho giao diện web.
- Usability Testing cơ bản bằng Maze.
- Phân tích phản hồi người dùng để điều chỉnh thiết kế.
- Design Handoff, HTML/CSS cơ bản.
- Sử dụng Notion và có kiến thức Agile/Scrum cơ bản.

KỸ NĂNG MỀM

- Giao tiếp và trao đổi phản hồi thiết kế trong nhóm.
- Tiếp nhận góp ý từ senior để hoàn thiện màn hình.
- Tiếng Anh B1, giao tiếp công việc cơ bản.
- Sử dụng tiếng Việt thành thạo.

KINH NGHIỆM LÀM VIỆC

UI/UX Designer – Công ty Phần mềm Nam Việt
03/2025 – 10/2026 (1 năm 7 tháng, bao gồm giai đoạn thực tập)

- Bắt đầu với công việc thực tập thiết kế giao diện, sau đó tiếp tục đảm nhận các nhiệm vụ UI/UX Designer trong nhóm sản phẩm.
- Thực hiện wireframe, user flow và thiết kế các màn hình trên Figma cho hai sản phẩm phần mềm.
- Xây dựng prototype tương tác để trình bày luồng thao tác và hỗ trợ review giao diện.
- Chỉnh sửa bố cục, thành phần UI và cách tổ chức thông tin theo phản hồi từ senior và người dùng.

DỰ ÁN

Giao diện sản phẩm thương mại điện tử

Tham gia thiết kế các màn hình giao diện và bố cục responsive. Sử dụng Figma để tạo component và prototype, điều chỉnh phương án sau các vòng review.

Phần mềm quản lý bán hàng

Tham gia xây dựng user flow, wireframe và giao diện phục vụ thao tác quản lý. Hỗ trợ chuẩn bị thiết kế cho quá trình Design Handoff.
```

### `DES_JUN_01` ↔ `jd_0590`

```
Vị trí: Chuyên Viên Thiết Kế
Kinh nghiệm: 1 năm
Học vấn: Cao đẳng
Kỹ năng chuyên môn: Thiết kế đồ họa (Photoshop, Illustrator), Quay dựng video (Premiere Pro, After Effects)
Yêu cầu: Tốt nghiệp từ Cao đẳng. Tối thiểu 01 năm kinh nghiệm ở vị trí tương đương. Có trách nhiệm trong công việc. Năng động, nhiệt tình, sáng tạo.
```

Điểm của bạn: ___
