import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
# LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.1-flash-lite")
GEMINI_RPM_LIMIT = 15  # Free tier: 15 requests/minute cho gemini-2.0-flash

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

ENTITY_TYPES = [
    "soft_skills",
    "hard_skills",
    "education",
    "field_of_education",
    "industry_sector",
    "role",
]
NUM_ENTITY_TYPES = len(ENTITY_TYPES)

NUM_NODES = 2 + NUM_ENTITY_TYPES * 2  # 14 nodes: 2 main + 6 candidate + 6 JD

NODE_CANDIDATE = 0
NODE_JD = 1
CANDIDATE_ENTITY_START = 2       # nodes 2-7
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
