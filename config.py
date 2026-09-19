import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
# LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.1-flash-lite")
GEMINI_RPM_LIMIT = 15  # Free tier: 15 requests/minute cho gemini-2.0-flash

# Model đa ngôn ngữ (hỗ trợ tiếng Việt tốt hơn all-MiniLM-L6-v2 vốn chủ yếu tiếng Anh).
# paraphrase-multilingual-MiniLM-L12-v2 cùng dim 384 nên không đổi kiến trúc model.
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")

ENTITY_TYPES = [
    "soft_skills",
    "hard_skills",
    "education",
    "field_of_education",
    "industry_sector",
    "role",
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
}

NUM_NODES = 2 + NUM_ENTITY_TYPES * 2  # 14 nodes: 2 main + 6 candidate + 6 JD

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
CANDIDATE_ENTITY_START = 2           # nodes 2-7
JD_ENTITY_START = 2 + NUM_ENTITY_TYPES  # nodes 8-13

HIDDEN_DIM = 128
NUM_GCN_LAYERS = 3
DROPOUT = 0.3

KNN_K = 10
SHARPENING_P = 4.0

LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4
POS_WEIGHT = 10.0
NUM_EPOCHS = 100
BATCH_SIZE = 32

DATA_RAW_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
DATA_PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")
GRAPH_DIR = os.path.join(DATA_PROCESSED_DIR, "graphs")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
