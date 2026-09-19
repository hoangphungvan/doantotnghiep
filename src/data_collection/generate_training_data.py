"""
Script tự động sinh tập hồ sơ CV và tạo các cặp huấn luyện (pairs_it.csv)
dựa trên 20 cụm việc làm CNTT và hướng dẫn Hard/Easy Negative.

Quy trình:
1. Đọc representative_jds.csv và cluster_negative_sampling_guide.json.
2. Sinh ~15-20 hồ sơ CV thực tế ứng với các nhóm chuyên môn CNTT cốt lõi:
   - Backend Java / Spring Boot
   - Frontend React / NextJS
   - DevOps / Cloud AWS
   - QA / Automation Tester
   - Data Analyst / Python / SQL
   - Mobile Developer (Flutter / Swift)
   - Network & Security Engineer
   - Business Analyst (BA)
   - IT Support / Sysadmin
   - UI/UX Designer
   ...
3. Ghép mỗi CV với các JD đại diện theo 4 mức nhãn định lượng:
   - Label 3 (Phù hợp tốt): JD trong cùng cụm (Same Cluster)
   - Label 2 (Phù hợp một phần): JD trong cùng cụm nhưng lệch seniority hoặc thiếu 1 tool
   - Label 1 (Liên quan ngành / Hard Negative): JD từ cụm gần nhất trong không gian embedding
   - Label 0 (Không phù hợp / Easy Negative): JD từ cụm xa nhất
4. Xuất ra:
   - data/raw/cvs/cv_*.txt (các file CV văn bản)
   - data/raw/pairs_it.csv (bảng cặp ghép cv_path, jd_path, label)
"""

import json
import os
import sys
import pandas as pd

# Hỗ trợ chạy trực tiếp từ thư mục gốc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config

CANDIDATE_PROFILES = [
    {
        "cid": 6,
        "name": "Nguyen_Van_Huy",
        "role": "Senior Backend Java Developer",
        "title": "cv_06_backend_java.txt",
        "text": """HỌ VÀ TÊN: Nguyễn Văn Huy - Senior Backend Java Developer
Email: huy.nguyen@email.com | SĐT: 0912345678 | Địa chỉ: Hà Nội
HỌC VẤN:
- Cử nhân Công nghệ Thông tin, Đại học Bách Khoa Hà Nội (2015-2019)
- Chuyên ngành: Khoa học Máy tính, Kỹ thuật phần mềm
KỸ NĂNG CHUYÊN MÔN:
- Ngôn ngữ: Java (Java 8, 11, 17, 21), SQL, JavaScript
- Frameworks: Spring Boot, Spring Cloud, Spring MVC, Hibernate, JPA
- Cơ sở dữ liệu: Oracle, MySQL, PostgreSQL, MongoDB, Redis Cache
- Hệ thống & Kiến trúc: Microservices, RESTful API, Kafka, RabbitMQ, Docker
- Công cụ & Quy trình: Git, Jenkins, CI/CD, Maven, Jira, Agile/Scrum
KỸ NĂNG MỀM:
- Tư duy logic, giải quyết vấn đề phức tạp, kỹ năng làm việc nhóm, quản lý thời gian
KINH NGHIỆM LÀM VIỆC:
- Senior Java Developer tại VNG Corporation (2021 - Nay): Thiết kế kiến trúc Microservices xử lý hàng triệu giao dịch/ngày, tối ưu truy vấn cơ sở dữ liệu Oracle/PostgreSQL.
- Backend Developer tại FPT Software (2019 - 2021): Phát triển REST API bằng Spring Boot, tích hợp message queue Kafka và Redis caching.
""",
    },
    {
        "cid": 8,
        "name": "Tran_Thi_Mai",
        "role": "Frontend Web Developer (ReactJS / NextJS)",
        "title": "cv_08_frontend_react.txt",
        "text": """HỌ VÀ TÊN: Trần Thị Mai - Frontend Web Developer
Email: mai.tran@email.com | SĐT: 0987654321 | Địa chỉ: Hà Nội
HỌC VẤN:
- Cử nhân Công nghệ Thông tin, Đại học Công nghệ - ĐHQGHN (2018-2022)
KỸ NĂNG CHUYÊN MÔN:
- Kỹ thuật Web: HTML5, CSS3, JavaScript (ES6+), TypeScript
- Frameworks/Libraries: ReactJS, NextJS, Redux Toolkit, TailwindCSS, Bootstrap, Material UI
- API & Tools: RESTful API, GraphQL, Webpack, Vite, Git, Postman, Figma to Code
- Testing: Jest, React Testing Library
KỸ NĂNG MỀM:
- Giao tiếp tốt, thẩm mỹ giao diện người dùng cao, tỉ mỉ, làm việc nhóm hiệu quả
KINH NGHIỆM LÀM VIỆC:
- Frontend Developer tại Tiki (2022 - Nay): Xây dựng giao diện thương mại điện tử responsive bằng ReactJS và NextJS, tối ưu hóa Core Web Vitals và SEO.
- Web Developer Intern tại CMC Telecom (2021 - 2022): Lập trình giao diện web bằng HTML, CSS, JavaScript và tích hợp API.
""",
    },
    {
        "cid": 2,
        "name": "Le_Quoc_Bao",
        "role": "DevOps & Cloud Engineer",
        "title": "cv_02_devops_cloud.txt",
        "text": """HỌ VÀ TÊN: Lê Quốc Bảo - DevOps & Cloud Engineer
Email: bao.le@email.com | SĐT: 0934567890 | Địa chỉ: TP. Hồ Chí Minh
HỌC VẤN:
- Kỹ sư Mạng máy tính & Truyền thông dữ liệu, ĐH Bách Khoa TP.HCM (2016-2021)
KỸ NĂNG CHUYÊN MÔN:
- Cloud Providers: AWS (EC2, S3, RDS, EKS, Lambda, CloudWatch), GCP
- Container & Orchestration: Docker, Kubernetes (K8s), Helm
- CI/CD & Automation: Jenkins, GitLab CI, GitHub Actions, Ansible, Terraform
- Giám sát & Logging: Prometheus, Grafana, ELK Stack (Elasticsearch, Logstash, Kibana)
- Scripting: Bash Shell, Python, Linux OS (Ubuntu, CentOS)
KỸ NĂNG MỀM:
- Khả năng xử lý sự cố nhanh, tư duy tự động hóa, làm việc độc lập và phối hợp nhóm tốt
KINH NGHIỆM LÀM VIỆC:
- DevOps Engineer tại Viettel Digital (2021 - Nay): Vận hành cụm Kubernetes production, xây dựng pipeline CI/CD tự động hóa kiểm thử và triển khai microservices lên AWS.
- Cloud Systems Admin tại NashTech (2020 - 2021): Quản trị hạ tầng máy chủ Linux và triển khai Docker container.
""",
    },
    {
        "cid": 10,
        "name": "Pham_Thu_Trang",
        "role": "QA / Software Tester (Manual & Automation)",
        "title": "cv_10_qa_tester.txt",
        "text": """HỌ VÀ TÊN: Phạm Thu Trang - QA / Software Tester
Email: trang.pham@email.com | SĐT: 0978123456 | Địa chỉ: Hà Nội
HỌC VẤN:
- Cử nhân Hệ thống Thông tin, Học viện Công nghệ Bưu chính Viễn thông (2018-2022)
KỸ NĂNG CHUYÊN MÔN:
- Kiểm thử thủ công (Manual Testing): Phân tích yêu cầu, thiết kế Test Case, Test Scenario, Test Plan, Bug Tracking (Jira, Mantis)
- Kiểm thử tự động (Automation Testing): Selenium WebDriver, Postman (API Testing), JMeter (Performance/Load Test), Python/Java cơ bản
- Cơ sở dữ liệu: SQL truy vấn dữ liệu kiểm tra (MySQL, SQL Server)
- Phương pháp: Agile/Scrum, Black-box testing, Regression testing
KỸ NĂNG MỀM:
- Cẩn thận, chi tiết, kỹ năng giao tiếp phản hồi lỗi với lập trình viên, tư duy phản biện
KINH NGHIỆM LÀM VIỆC:
- QA Engineer tại KMS Technology (2022 - Nay): Kiểm thử chức năng và hiệu năng cho hệ thống Fintech, viết kịch bản tự động hóa API bằng Postman và Selenium.
- Tester tại MISA (2021 - 2022): Kiểm thử phần mềm kế toán, tạo báo cáo lỗi và theo dõi tiến độ fix bug trên Jira.
""",
    },
    {
        "cid": 14,
        "name": "Do_Minh_Tuan",
        "role": "Data Analyst / BI Specialist",
        "title": "cv_14_data_analyst.txt",
        "text": """HỌ VÀ TÊN: Đỗ Minh Tuấn - Data Analyst
Email: tuan.do@email.com | SĐT: 0965432109 | Địa chỉ: Hà Nội
HỌC VẤN:
- Cử nhân Toán - Tin ứng dụng, Đại học Khoa học Tự nhiên Hà Nội (2017-2021)
KỸ NĂNG CHUYÊN MÔN:
- Phân tích dữ liệu & BI: SQL nâng cao, Power BI, Tableau, Advanced Excel
- Ngôn ngữ lập trình: Python (Pandas, NumPy, Matplotlib, Seaborn), R
- Xử lý dữ liệu: Data Cleaning, Data Modeling, ETL cơ bản, thống kê mô tả, A/B Testing
KỸ NĂNG MỀM:
- Trình bày trực quan hóa dữ liệu (Storytelling with Data), giao tiếp liên phòng ban, tư duy kinh doanh
KINH NGHIỆM LÀM VIỆC:
- Data Analyst tại Shopee Vietnam (2021 - Nay): Xây dựng dashboard theo dõi KPI vận hành và doanh thu trên Power BI, thực hiện các truy vấn SQL phân tích hành vi người dùng.
- Junior Data Analyst tại MoMo (2020 - 2021): Hỗ trợ xử lý dữ liệu giao dịch và lập báo cáo tài chính định kỳ.
""",
    },
    {
        "cid": 15,
        "name": "Hoang_Duc_Nam",
        "role": "Mobile App Developer (Flutter / Android / iOS)",
        "title": "cv_15_mobile_developer.txt",
        "text": """HỌ VÀ TÊN: Hoàng Đức Nam - Mobile App Developer
Email: nam.hoang@email.com | SĐT: 0945678901 | Địa chỉ: TP. Hồ Chí Minh
HỌC VẤN:
- Kỹ sư Công nghệ Thông tin, Đại học Bách Khoa TP.HCM (2018-2022)
KỸ NĂNG CHUYÊN MÔN:
- Cross-platform: Flutter (Dart), React Native
- Native: Android (Kotlin, Java), iOS cơ bản (Swift)
- Kiến trúc & State Management: BLoC, Provider, MVC, MVVM
- Tích hợp: RESTful API, Firebase (Auth, Firestore, Cloud Messaging), Google Maps SDK, Push Notifications
- Công cụ: Android Studio, Xcode, Git, Postman, CI/CD for Mobile (Fastlane)
KỸ NĂNG MỀM:
- Tinh thần học hỏi cao, chú trọng trải nghiệm người dùng di động (UI/UX), giải quyết vấn đề độc lập
KINH NGHIỆM LÀM VIỆC:
- Flutter Developer tại VNPAY (2022 - Nay): Phát triển các tính năng thanh toán, ví điện tử trên ứng dụng di động đa nền tảng Flutter.
- Android Developer tại Gameloft (2021 - 2022): Tham gia bảo trì và nâng cấp ứng dụng game trên nền tảng Android.
""",
    },
    {
        "cid": 17,
        "name": "Vu_Van_Thang",
        "role": "Network & System Security Engineer",
        "title": "cv_17_network_security.txt",
        "text": """HỌ VÀ TÊN: Vũ Văn Thắng - Network & Security Engineer
Email: thang.vu@email.com | SĐT: 0923456789 | Địa chỉ: Hà Nội
HỌC VẤN:
- Kỹ sư An toàn Thông tin, Học viện An ninh Nhân dân / PTIT (2016-2021)
- Chứng chỉ: CCNA, CCNP Security, CEH (Certified Ethical Hacker)
KỸ NĂNG CHUYÊN MÔN:
- Mạng máy tính: Cisco Router/Switch, LAN, WAN, VPN, BGP, OSPF, VLAN
- Bảo mật hệ thống: Firewall (Fortinet, Palo Alto, Cisco ASA), IDS/IPS, WAF, SIEM, Antivirus Enterprise
- Hệ thống máy chủ: Linux (Ubuntu, RHEL), Windows Server, Active Directory, VMware ESXi
- Đánh giá lỗ hổng: Nessus, Wireshark, Nmap, Pentest cơ bản
KỸ NĂNG MỀM:
- Tinh thần trách nhiệm cao, phản ứng nhanh với sự cố an ninh mạng, làm việc nhóm
KINH NGHIỆM LÀM VIỆC:
- Network Security Specialist tại Ngân hàng Techcombank (2021 - Nay): Vận hành hệ thống tường lửa, giám sát nhật ký an ninh SIEM và triển khai chính sách bảo mật mạng nội bộ.
- Kỹ sư mạng tại FPT Telecom (2019 - 2021): Cấu hình và xử lý sự cố thiết bị mạng doanh nghiệp.
""",
    },
    {
        "cid": 18,
        "name": "Bui_Thi_Yen",
        "role": "Senior Business Analyst (IT BA)",
        "title": "cv_18_business_analyst.txt",
        "text": """HỌ VÀ TÊN: Bùi Thị Yến - Senior Business Analyst (IT BA)
Email: yen.bui@email.com | SĐT: 0918765432 | Địa chỉ: Hà Nội
HỌC VẤN:
- Cử nhân Hệ thống Thông tin Quản lý, Đại học Kinh tế Quốc dân (2016-2020)
- Chứng chỉ: CBAP (Certified Business Analysis Professional), Professional Scrum Master (PSM I)
KỸ NĂNG CHUYÊN MÔN:
- Kỹ năng BA: Khảo sát & thu thập yêu cầu (Elicitation), Phân tích nghiệp vụ, Quản lý phạm vi dự án
- Tài liệu hóa: Viết BRD, SRS, User Stories, Acceptance Criteria, Use Case, Activity Diagram, BPMN 2.0
- Công cụ: Jira, Confluence, Figma, Balsamiq, Draw.io, MS Visio, Trello, SQL cơ bản
- Phương pháp: Agile/Scrum, Waterfall
KỸ NĂNG MỀM:
- Đàm phán và thuyết phục các bên liên quan, kỹ năng thuyết trình, tư duy giải pháp
KINH NGHIỆM LÀM VIỆC:
- Senior IT BA tại One Mount Group (2021 - Nay): Cầu nối giữa bộ phận nghiệp vụ kinh doanh và đội ngũ kỹ thuật phần mềm, làm rõ các tính năng cho ứng dụng VinID.
- Business Analyst tại CMC Global (2020 - 2021): Viết tài liệu đặc tả yêu cầu phần mềm cho dự án khách hàng Nhật Bản.
""",
    },
    {
        "cid": 19,
        "name": "Dinh_Tuan_Anh",
        "role": "IT Project Manager (PM)",
        "title": "cv_19_project_manager.txt",
        "text": """HỌ VÀ TÊN: Đinh Tuấn Anh - IT Project Manager
Email: anh.dinh@email.com | SĐT: 0909876543 | Địa chỉ: Hà Nội
HỌC VẤN:
- Thạc sĩ Quản trị Dự án Công nghệ, Đại học Bách Khoa Hà Nội (2019-2021)
- Cử nhân Công nghệ Thông tin, Đại học Bách Khoa Hà Nội (2014-2018)
- Chứng chỉ: PMP (Project Management Professional), PMI-ACP
KỸ NĂNG CHUYÊN MÔN:
- Quản trị dự án: Lập kế hoạch dự án (Project Planning), Quản lý tiến độ (Scheduling), Quản lý ngân sách & rủi ro
- Phương pháp luận: Agile/Scrum, Kanban, Waterfall, Sprint Planning, Daily Standup, Retrospective
- Công cụ: Jira Software, Confluence, MS Project, ClickUp, Trello
- Kỹ thuật: Hiểu biết sâu về kiến trúc phần mềm, quy trình CI/CD, cơ sở dữ liệu và API
KỸ NĂNG MỀM:
- Lãnh đạo đội ngũ (Team Leadership), giải quyết xung đột, đàm phán với khách hàng, quản lý thời gian
KINH NGHIỆM LÀM VIỆC:
- Project Manager tại Savvycom (2021 - Nay): Quản lý tiến độ và chất lượng cho 3 dự án phát triển phần mềm quy mô 20+ thành viên, đảm bảo giao hàng đúng hạn (On-time Delivery).
- Scrum Master / Technical Lead tại Rikkeisoft (2018 - 2021): Điều phối sprint cho đội ngũ lập trình viên Backend và Frontend.
""",
    },
    {
        "cid": 5,
        "name": "Ngo_Van_Dat",
        "role": "IT Helpdesk & System Support Specialist",
        "title": "cv_05_it_support.txt",
        "text": """HỌ VÀ TÊN: Ngô Văn Đạt - IT Helpdesk & Support
Email: dat.ngo@email.com | SĐT: 0938112233 | Địa chỉ: Hà Nội
HỌC VẤN:
- Cao đẳng Công nghệ Thông tin, Cao đẳng FPT Polytechnic (2019-2022)
KỸ NĂNG CHUYÊN MÔN:
- Hỗ trợ người dùng: Cài đặt và khắc phục sự cố hệ điều hành Windows 10/11, macOS, phần mềm văn phòng MS Office, Google Workspace
- Phần cứng: Lắp ráp, sửa chữa, thay thế linh kiện PC, Laptop, máy in, máy scan, thiết bị chấm công
- Mạng nội bộ: Bấm dây mạng, cấu hình Router Wi-Fi, Switch, kiểm tra thông mạng LAN/WAN cơ bản
- Quản trị tài khoản: Active Directory, cấp quyền truy cập, email doanh nghiệp
KỸ NĂNG MỀM:
- Nhiệt tình, kiên nhẫn, hỗ trợ tận tâm, giao tiếp thân thiện, phản ứng nhanh nhẹn
KINH NGHIỆM LÀM VIỆC:
- Nhân viên IT Support tại Kangaroo Group (2022 - Nay): Hỗ trợ kỹ thuật máy tính cho hơn 300 nhân sự văn phòng, quản lý tài sản thiết bị CNTT.
- Thực tập sinh IT Helpdesk tại Thế Giới Di Động (2021 - 2022): Cài đặt máy và hỗ trợ xử lý sự cố thiết bị tại cửa hàng.
""",
    },
    {
        "cid": 3,
        "name": "Nguyen_Thu_Ha",
        "role": "UI/UX & Graphic Designer",
        "title": "cv_03_ui_ux_designer.txt",
        "text": """HỌ VÀ TÊN: Nguyễn Thu Hà - UI/UX Designer
Email: ha.nguyen@email.com | SĐT: 0915998877 | Địa chỉ: TP. Hồ Chí Minh
HỌC VẤN:
- Cử nhân Thiết kế Đồ họa, Đại học Mỹ thuật Công nghiệp (2017-2021)
KỸ NĂNG CHUYÊN MÔN:
- Thiết kế UI/UX: Figma, Adobe XD, Sketch, Wireframing, Prototyping, Design System, User Journey Map
- Thiết kế Đồ họa: Adobe Photoshop, Adobe Illustrator, After Effects cơ bản
- Kiến thức kỹ thuật: Hiểu biết về HTML/CSS, lưới bố cục (Grid system), responsive design cho Web và Mobile
KỸ NĂNG MỀM:
- Tư duy sáng tạo, thẩm mỹ hiện đại, khả năng nghiên cứu hành vi người dùng, làm việc nhóm ăn ý với Developer
KINH NGHIỆM LÀM VIỆC:
- UI/UX Designer tại Be Group (2021 - Nay): Thiết kế giao diện ứng dụng gọi xe và giao đồ ăn, xây dựng Design System đồng nhất trên iOS và Android.
- Graphic Designer tại VCCorp (2020 - 2021): Thiết kế banner quảng cáo, infographic và ấn phẩm truyền thông số.
""",
    },
    {
        "cid": 0,
        "name": "Tran_Van_Khoa",
        "role": "B2B Software Sales Specialist",
        "title": "cv_00_software_sales.txt",
        "text": """HỌ VÀ TÊN: Trần Văn Khoa - Chuyên viên Kinh doanh Phần mềm B2B
Email: khoa.tran@email.com | SĐT: 0988112233 | Địa chỉ: Hà Nội
HỌC VẤN:
- Cử nhân Quản trị Kinh doanh, Đại học Thương Mại (2018-2022)
KỸ NĂNG CHUYÊN MÔN:
- Bán hàng phần mềm: B2B Sales, Telesales, Demo giải pháp phần mềm SaaS, ERP, CRM
- Đàm phán & Chốt hợp đồng: Kỹ năng thương lượng giá trị hợp đồng, soạn thảo báo giá và hợp đồng kinh tế
- Công cụ: CRM (HubSpot, Salesforce), Tin học văn phòng (Excel, PowerPoint thuyết trình)
KỸ NĂNG MỀM:
- Giao tiếp lưu loát, kỹ năng thuyết phục, chịu được áp lực KPI doanh số, mở rộng mạng lưới quan hệ khách hàng
KINH NGHIỆM LÀM VIỆC:
- Chuyên viên Kinh doanh SaaS tại Base.vn (2022 - Nay): Tiếp cận khách hàng doanh nghiệp, tư vấn giải pháp quản trị doanh nghiệp và hoàn thành 110% KPI doanh số năm.
- Nhân viên tư vấn bán hàng tại KiotViet (2021 - 2022): Tìm kiếm khách hàng mở rộng thị trường phần mềm bán hàng.
""",
    },
]


def generate_pairs_and_cvs():
    print("=" * 75)
    print("  SINH TẬP DỮ LIỆU HUẤN LUYỆN (CV + CẶP GHÉP THEO PHÂN CỤM VIETJOBS)")
    print("=" * 75)

    cv_dir = os.path.join(config.DATA_RAW_DIR, "cvs")
    os.makedirs(cv_dir, exist_ok=True)

    rep_csv_path = os.path.join(config.DATA_PROCESSED_DIR, "representative_jds.csv")
    guide_json_path = os.path.join(config.DATA_PROCESSED_DIR, "cluster_negative_sampling_guide.json")

    if not os.path.exists(rep_csv_path) or not os.path.exists(guide_json_path):
        raise FileNotFoundError(
            "Thiếu representative_jds.csv hoặc cluster_negative_sampling_guide.json.\n"
            "Vui lòng chạy trước: python src/data_collection/cluster_jds.py"
        )

    rep_df = pd.read_csv(rep_csv_path)
    with open(guide_json_path, "r", encoding="utf-8") as f:
        guide = json.load(f)

    # 1. Lưu các file text CV
    print(f"\n[1/3] Lưu {len(CANDIDATE_PROFILES)} file CV vào {cv_dir}...")
    cv_file_map = {}
    for prof in CANDIDATE_PROFILES:
        filepath = os.path.join(cv_dir, prof["title"])
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(prof["text"].strip())
        cv_file_map[prof["cid"]] = filepath
        print(f"  ✓ {prof['title']} ({prof['role']})")

    # 2. Xây dựng các cặp (CV, JD, label)
    print("\n[2/3] Ghép cặp theo ma trận tương đồng (Label 3, 2, 1, 0)...")
    pairs = []

    # Gom các JD đại diện theo cluster_id
    reps_by_cluster = {}
    for _, row in rep_df.iterrows():
        cid = int(row["cluster_id"])
        if cid not in reps_by_cluster:
            reps_by_cluster[cid] = []
        reps_by_cluster[cid].append(row["file_path"])

    for prof in CANDIDATE_PROFILES:
        cid = prof["cid"]
        cv_path = cv_file_map[cid]

        # A. Label 3: Phù hợp tốt (JD đại diện top 1 của cùng cụm)
        same_cluster_jds = reps_by_cluster.get(cid, [])
        if same_cluster_jds:
            pairs.append({
                "cv_path": cv_path,
                "jd_path": same_cluster_jds[0],
                "label": 3,
                "note": "Same Cluster (Good Match)",
            })

        # B. Label 2: Phù hợp một phần (JD đại diện thứ 2 của cùng cụm hoặc cụm liền kề)
        if len(same_cluster_jds) > 1:
            pairs.append({
                "cv_path": cv_path,
                "jd_path": same_cluster_jds[1],
                "label": 2,
                "note": "Same Cluster Rank 2 (Partial Match)",
            })

        # C. Label 1: Liên quan ngành / Hard Negative (JD từ cụm gần nhất trong embedding space)
        cluster_guide = guide.get(str(cid), {})
        hard_negs = cluster_guide.get("hard_negatives_label_1", [])
        for h in hard_negs[:2]:
            h_cid = h["cluster_id"]
            h_jds = reps_by_cluster.get(h_cid, [])
            if h_jds:
                pairs.append({
                    "cv_path": cv_path,
                    "jd_path": h_jds[0],
                    "label": 1,
                    "note": f"Hard Negative (Cluster {h_cid}, sim={h['similarity']})",
                })

        # D. Label 0: Không phù hợp / Easy Negative (JD từ cụm xa nhất)
        easy_negs = cluster_guide.get("easy_negatives_label_0", [])
        for e in easy_negs[:2]:
            e_cid = e["cluster_id"]
            if e_cid == cid:
                continue
            e_jds = reps_by_cluster.get(e_cid, [])
            if e_jds:
                pairs.append({
                    "cv_path": cv_path,
                    "jd_path": e_jds[0],
                    "label": 0,
                    "note": f"Easy Negative (Cluster {e_cid}, sim={e['similarity']})",
                })

    # 3. Xuất file pairs_it.csv
    pairs_df = pd.DataFrame(pairs)
    out_csv = os.path.join(config.DATA_RAW_DIR, "pairs_it.csv")
    pairs_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print(f"\n[3/3] Đã tạo thành công {len(pairs_df)} cặp huấn luyện tại: {out_csv}")
    print("\nPhân bố nhãn:")
    for lbl, count in pairs_df["label"].value_counts().sort_index().items():
        print(f"  Nhãn {lbl} ({config.GRADE_LABELS.get(lbl, '')}): {count} cặp")

    print("=" * 75)
    print("HOÀN TẤT SINH DỮ LIỆU HUẤN LUYỆN!")
    print("=" * 75)
    return out_csv


if __name__ == "__main__":
    generate_pairs_and_cvs()
