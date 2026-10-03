import os
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = LLM_API_KEY
# Alias tương thích ngược nếu còn dùng tên cũ
GEMINI_API_KEY = LLM_API_KEY
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen/qwen3.8-27b")
LLM_RPM_LIMIT = 28  # để chừa margin dưới mức 30 RPM thật
GEMINI_RPM_LIMIT = 28

# Model đa ngôn ngữ (hỗ trợ tiếng Việt tốt hơn all-MiniLM-L6-v2 vốn chủ yếu tiếng Anh).
# paraphrase-multilingual-MiniLM-L12-v2 cùng dim 384 nên không đổi kiến trúc model.
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")

# Thay đổi schema entity phải tạo lại cache, graph và checkpoint để tránh
# trộn artifact của hai phiên bản biểu diễn khác nhau.
ARTIFACT_VERSION = "v4_certification_catalog_expanded"

ENTITY_TYPES = [
    "soft_skills",
    "hard_skills",
    "education",
    "field_of_education",
    "industry_sector",
    "role",
    "certifications",
]
NUM_ENTITY_TYPES = len(ENTITY_TYPES)

# Trọng số cho từng loại entity — ảnh hưởng đến edge weight trong đồ thị.
# Nguyên tắc: loại entity càng quyết định khả năng match → trọng số càng cao.
# role: quan trọng nhất — sai level (fresher vs senior) là lỗi nghiêm trọng.
# hard_skills: kỹ năng chuyên môn — phải khớp mới đủ điều kiện.
# field_of_education: ngành học — quan trọng với vị trí chuyên sâu.
# industry_sector: lĩnh vực ngành — ảnh hưởng đến sự phù hợp văn hóa.
# education: trình độ — quan trọng nhưng có thể linh hoạt hơn.
# soft_skills: ít quyết định nhất — hầu như JD nào cũng yêu cầu tương tự.
ENTITY_WEIGHTS = {
    "role":              3.0,
    "hard_skills":       2.5,
    "field_of_education": 2.0,
    "industry_sector":   1.5,
    "education":         1.5,
    "soft_skills":       1.0,
    # Chỉ các chứng chỉ nằm trong CERTIFICATION_CATALOG mới nhận trọng số này.
    "certifications":    2.0,
}

# Catalog chứng chỉ được phép tham gia matching. Tên trong entity luôn được
# chuẩn hóa về đúng một giá trị trong catalog này.
CERTIFICATION_CATALOG = (
    # AWS / Cloud
    "AWS Certified Cloud Practitioner",
    "AWS Certified AI Practitioner",
    "AWS Certified Solutions Architect - Associate",
    "AWS Certified Developer - Associate",
    "AWS Certified SysOps Administrator - Associate",
    "AWS Certified Data Engineer - Associate",
    "AWS Certified Machine Learning Engineer - Associate",
    "AWS Certified Solutions Architect - Professional",
    "AWS Certified DevOps Engineer - Professional",
    "AWS Certified Advanced Networking - Specialty",
    "AWS Certified Security - Specialty",
    "AWS Certified Machine Learning - Specialty",
    # Microsoft Azure
    "Azure Fundamentals",
    "Azure AI Fundamentals",
    "Azure Data Fundamentals",
    "Azure Administrator Associate",
    "Azure Developer Associate",
    "Azure Security Engineer Associate",
    "Azure Network Engineer Associate",
    "Azure Solutions Architect Expert",
    "DevOps Engineer Expert",
    "Azure Data Engineer Associate",
    "Azure Enterprise Data Analyst Associate",
    "Azure AI Engineer Associate",
    "Azure Database Administrator Associate",
    # Google Cloud
    "Cloud Digital Leader",
    "Associate Cloud Engineer",
    "Professional Cloud Architect",
    "Professional Cloud Developer",
    "Professional Cloud DevOps Engineer",
    "Professional Cloud Security Engineer",
    "Professional Cloud Network Engineer",
    "Professional Data Engineer",
    "Professional Machine Learning Engineer",
    "Professional Cloud Database Engineer",
    # Kubernetes / Cloud Native
    "Kubernetes and Cloud Native Associate",
    "Kubernetes and Cloud Native Security Associate",
    "Certified Kubernetes Application Developer",
    "Certified Kubernetes Administrator",
    "Certified Kubernetes Security Specialist",
    # HashiCorp / IaC
    "HashiCorp Certified Terraform Associate",
    "HashiCorp Certified Vault Associate",
    "HashiCorp Certified Consul Associate",
    # Red Hat / Linux
    "Red Hat Certified System Administrator",
    "Red Hat Certified Engineer",
    "Red Hat Certified Specialist in Containers",
    "Red Hat Certified Specialist in OpenShift Administration",
    "Red Hat Certified OpenShift Application Developer",
    "Red Hat Certified Architect",
    "Linux Foundation Certified IT Associate",
    "Linux Foundation Certified System Administrator",
    "Linux Foundation Certified Engineer",
    "CompTIA Linux+",
    # Cisco / Networking
    "Cisco Certified Support Technician Networking",
    "CCNA",
    "Cisco DevNet Associate",
    "Cisco CyberOps Associate",
    "CCNP Enterprise",
    "CCNP Security",
    "CCNP Data Center",
    "CCNP Service Provider",
    "CCNP Collaboration",
    "Cisco DevNet Professional",
    "CCIE Enterprise Infrastructure",
    "CCIE Enterprise Wireless",
    "CCIE Security",
    "CCIE Data Center",
    "CCIE Service Provider",
    # CompTIA
    "CompTIA A+",
    "CompTIA Network+",
    "CompTIA Security+",
    "CompTIA Server+",
    "CompTIA Cloud+",
    "CompTIA CySA+",
    "CompTIA PenTest+",
    "CompTIA Data+",
    "CompTIA DataSys+",
    "CompTIA Project+",
    "CompTIA CASP+ SecurityX",
    # Cybersecurity
    "Certified Ethical Hacker",
    "CISSP",
    "SSCP",
    "Certified in Cybersecurity",
    "CCSP",
    "CSSLP",
    "OSCP",
    "OSWA",
    "OSWE",
    "OSEP",
    "OSED",
    "CRTP",
    "GIAC Security Essentials",
    "GIAC Certified Incident Handler",
    "GIAC Certified Intrusion Analyst",
    "GIAC Penetration Tester",
    "GIAC Web Application Penetration Tester",
    "GIAC Certified Forensic Analyst",
    # Java / .NET / Microsoft development
    "Oracle Certified Foundations Associate Java",
    "Oracle Certified Professional Java SE 8 Programmer",
    "Oracle Certified Professional Java SE 11 Developer",
    "Oracle Certified Professional Java SE 17 Developer",
    "Oracle Certified Professional Java SE 21 Developer",
    "VMware Spring Certified Professional",
    "Power Platform Fundamentals",
    "Power Platform Developer Associate",
    "Power Platform Functional Consultant Associate",
    "GitHub Foundations",
    "GitHub Actions",
    "GitHub Advanced Security",
    "GitHub Administration",
    # Database / Data Engineering / AI
    "Oracle Database SQL Certified Associate",
    "Oracle Database Administration I",
    "Oracle Database Administration II",
    "Oracle Database Administration Professional",
    "Oracle Autonomous Database Cloud Professional",
    "MongoDB Associate Developer",
    "MongoDB Associate Database Administrator",
    "MongoDB Associate Data Modeler",
    "EDB PostgreSQL Associate",
    "EDB PostgreSQL Professional",
    "Redis Certified Developer",
    "Neo4j Certified Professional",
    "Databricks Certified Data Engineer Associate",
    "Databricks Certified Data Engineer Professional",
    "Databricks Certified Associate Developer for Apache Spark",
    "Databricks Certified Data Analyst Associate",
    "SnowPro Core",
    "SnowPro Advanced Data Engineer",
    "SnowPro Advanced Architect",
    "SnowPro Advanced Administrator",
    "dbt Analytics Engineering Certification",
    "Databricks Certified Machine Learning Associate",
    "Databricks Certified Machine Learning Professional",
    "NVIDIA Certified Associate Generative AI LLMs",
    "NVIDIA Certified Professional Generative AI LLMs",
    # Enterprise platforms
    "Salesforce Certified Administrator",
    "Salesforce Platform App Builder",
    "Salesforce Platform Developer I",
    "Salesforce Platform Developer II",
    "Salesforce JavaScript Developer I",
    "Salesforce Data Architect",
    "Salesforce Sharing and Visibility Architect",
    "Salesforce Application Architect",
    "Salesforce System Architect",
    "Salesforce Technical Architect",
    "SAP Certified Associate S/4HANA",
    "SAP Certified Associate ABAP Cloud",
    "SAP Certified Associate SAP HANA",
    "SAP Certified Associate SAP Fiori Application Developer",
    "SAP Certified Associate SAP Integration Developer",
    # Testing / Agile / Management / Architecture
    "ISTQB Certified Tester Foundation Level",
    "ISTQB Agile Tester",
    "ISTQB Advanced Level Test Analyst",
    "ISTQB Advanced Level Technical Test Analyst",
    "ISTQB Advanced Level Test Management",
    "ISTQB Test Automation Engineer",
    "ISTQB Performance Testing",
    "ISTQB Security Tester",
    "ISTQB AI Testing",
    "Professional Scrum Master I",
    "Professional Scrum Master II",
    "Professional Scrum Master III",
    "Professional Scrum Product Owner I",
    "Professional Scrum Product Owner II",
    "Certified ScrumMaster",
    "Certified Scrum Product Owner",
    "SAFe Agilist",
    "PMP",
    "CAPM",
    "PMI-ACP",
    "PMI-PBA",
    "PRINCE2 Foundation",
    "PRINCE2 Practitioner",
    "ITIL 4 Foundation",
    "ITIL 4 Managing Professional",
    "TOGAF Enterprise Architecture Foundation",
    "TOGAF Enterprise Architecture Practitioner",
    # Virtualization / other networking / governance / FinOps
    "VMware Certified Technical Associate",
    "VMware Certified Professional Data Center Virtualization",
    "VMware Certified Professional Network Virtualization",
    "VMware Certified Advanced Professional",
    "Juniper Networks Certified Associate Junos",
    "JNCIS-ENT",
    "JNCIP-ENT",
    "JNCIE-ENT",
    "Huawei Certified ICT Associate",
    "HCIP",
    "HCIE",
    "CISA",
    "CISM",
    "CRISC",
    "CGEIT",
    "ISO IEC 27001 Lead Implementer",
    "ISO IEC 27001 Lead Auditor",
    "FinOps Certified Practitioner",
    "FinOps Certified Professional",
    "FinOps Certified Engineer",
)

# Tên viết tắt/mã thường gặp trong CV và JD được quy về catalog ở trên.
CERTIFICATION_ALIASES = {
    "AWS Certified Solutions Architect - Associate": ("SAA-C03", "AWS Solutions Architect Associate"),
    "AWS Certified Solutions Architect - Professional": ("AWS Solutions Architect Professional",),
    "AWS Certified Developer - Associate": ("DVA-C02", "AWS Developer Associate"),
    "AWS Certified SysOps Administrator - Associate": ("SOA-C02",),
    "Azure Fundamentals": ("AZ-900",),
    "Azure AI Fundamentals": ("AI-900",),
    "Azure Data Fundamentals": ("DP-900",),
    "Azure Administrator Associate": ("AZ-104",),
    "Azure Developer Associate": ("AZ-204",),
    "Azure Security Engineer Associate": ("AZ-500",),
    "Azure Network Engineer Associate": ("AZ-700",),
    "Azure Solutions Architect Expert": ("AZ-305",),
    "DevOps Engineer Expert": ("AZ-400",),
    "Azure Data Engineer Associate": ("DP-203",),
    "Azure Enterprise Data Analyst Associate": ("DP-500",),
    "Azure AI Engineer Associate": ("AI-102",),
    "Azure Database Administrator Associate": ("DP-300",),
    "Power Platform Fundamentals": ("PL-900",),
    "Power Platform Developer Associate": ("PL-400",),
    "Power Platform Functional Consultant Associate": ("PL-200",),
    "Kubernetes and Cloud Native Associate": ("KCNA",),
    "Kubernetes and Cloud Native Security Associate": ("KCSA",),
    "Certified Kubernetes Application Developer": ("CKAD",),
    "Certified Kubernetes Administrator": ("CKA",),
    "Certified Kubernetes Security Specialist": ("CKS",),
    "Cisco Certified Support Technician Networking": ("CCST Networking",),
    "CompTIA A+": ("A+",),
    "CompTIA Network+": ("Network+",),
    "CompTIA Security+": ("Security+",),
    "CompTIA Linux+": ("Linux+",),
    "CompTIA CASP+ SecurityX": ("CASP+", "SecurityX"),
    "Certified Ethical Hacker": ("CEH",),
    "Cisco DevNet Associate": ("DEVASC",),
    "Cisco CyberOps Associate": ("CBROPS",),
    "Certified in Cybersecurity": ("CC Certified in Cybersecurity",),
    "Juniper Networks Certified Associate Junos": ("JNCIA-Junos",),
    "Huawei Certified ICT Associate": ("HCIA",),
    "ISTQB Certified Tester Foundation Level": ("CTFL",),
    "Professional Scrum Master I": ("PSM I", "PSM1"),
    "Professional Scrum Master II": ("PSM II", "PSM2"),
    "Professional Scrum Master III": ("PSM III", "PSM3"),
    "Professional Scrum Product Owner I": ("PSPO I", "PSPO1"),
    "Professional Scrum Product Owner II": ("PSPO II", "PSPO2"),
    "Certified ScrumMaster": ("CSM",),
    "Certified Scrum Product Owner": ("CSPO",),
    "PMP": ("Project Management Professional",),
}

# Mức thưởng tối đa khi CV có ít nhất một chứng chỉ mà JD yêu cầu.
CERTIFICATION_SCORE_BONUS = 0.10

NUM_NODES = 2 + NUM_ENTITY_TYPES * 2  # 16 nodes: 2 main + 7 candidate + 7 JD

# ---------------------------------------------------------------------------
# Thang nhãn mức độ phù hợp (graded relevance) 0..NUM_GRADES
# Dùng cho ranking metrics (NDCG@K, MRR, Recall@K).
# Model output sigmoid score trong [0,1]; target train = grade / NUM_GRADES.
# ---------------------------------------------------------------------------
NUM_GRADES = 3
GRADE_LABELS = {
    0: "Không phù hợp",
    1: "Liên quan ngành",
    2: "Phù hợp một phần",
    3: "Phù hợp tốt",
}
# Ngưỡng grade coi là "relevant" khi tính Recall@K / MRR
RELEVANT_GRADE = 2
# Các giá trị K để báo cáo NDCG@K / Recall@K
RANKING_KS = [1, 3, 5, 10]

NODE_CANDIDATE = 0
NODE_JD = 1
CANDIDATE_ENTITY_START = 2           # nodes 2-8
JD_ENTITY_START = 2 + NUM_ENTITY_TYPES  # nodes 9-15

HIDDEN_DIM = 128
NUM_GCN_LAYERS = 3
DROPOUT = 0.3

KNN_K = 10
SHARPENING_P = 4.0

LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4
# Với soft target ordinal 4 mức (grade / NUM_GRADES in {0, 0.33, 0.67, 1.0}),
# đặt None để không nhân hệ số phạt dương tính lệch, phân bố tự cân bằng qua dữ liệu.
POS_WEIGHT = None
NUM_EPOCHS = 100
BATCH_SIZE = 32

DATA_RAW_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
VIETJOBS_IT_CSV = os.path.join(DATA_RAW_DIR, "VietJobs_cntt.csv")
DATA_PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")
DATA_CACHE_DIR = os.path.join(os.path.dirname(__file__), "data", "cache")
SYNTHETIC_CV_DIR = os.path.join(os.path.dirname(__file__), "data", "generated", "synthetic_cvs")
ENTITY_CACHE_FILE = os.path.join(DATA_CACHE_DIR, f"entity_cache_{ARTIFACT_VERSION}.json")
JD_EMBEDDINGS_CACHE_FILE = os.path.join(DATA_CACHE_DIR, f"jd_embeddings_cache_{ARTIFACT_VERSION}.pt")
GRAPH_DIR = os.path.join(DATA_PROCESSED_DIR, f"graphs_{ARTIFACT_VERSION}")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_FILE = os.path.join(MODEL_DIR, f"best_model_{ARTIFACT_VERSION}.pt")
