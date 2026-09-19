"""
Bước 1: JD-Only Pass — Trích xuất thực thể và Cache Embeddings cho toàn bộ JD.

Tác vụ:
1. Đọc toàn bộ 1.906 JD ngành CNTT từ data/raw/VietJobs_cntt.csv.
2. Trích xuất 6 loại thực thể cho mỗi JD (từ các trường cấu trúc sẵn có và nội dung văn bản).
3. Lưu vào Entity Cache (data/cache/entity_cache.json) theo cả:
   - Hash SHA256 của nội dung văn bản JD
   - Đường dẫn file text: data/raw/jds/cntt/jd_xxxx_....txt
   - Đường dẫn tuyệt đối
   -> Giúp bất kỳ lệnh nào sau này gọi extract_entities hoặc extract_from_file đều trúng cache ngay lập tức (0% tốn LLM API call).
4. Sinh DeepSets Embeddings (paraphrase-multilingual-MiniLM-L12-v2) cho toàn bộ 1.906 JD.
5. Tạo vector đặc trưng phân cụm (kết hợp role + hard_skills) và lưu toàn bộ vào data/cache/jd_embeddings_cache.pt.
"""

import ast
import os
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm

# Hỗ trợ chạy trực tiếp từ thư mục gốc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.extraction.entity_extractor import (
    get_cache_key,
    set_cached_entity,
    save_entire_cache,
    normalize_path,
)
from src.representation.embedding_generator import EmbeddingGenerator


def clean_list_str(val) -> list[str]:
    """Parse chuỗi biểu diễn list python sang danh sách các chuỗi sạch."""
    if pd.isna(val) or not str(val).strip() or str(val) == "[]":
        return []
    val_str = str(val).strip()
    try:
        parsed = ast.literal_eval(val_str)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
    except Exception:
        pass
    # Fallback tách bằng dấu phẩy
    return [x.strip() for x in val_str.split(",") if x.strip()]


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", text)[:40]


def extract_jd_entities_from_row(row: pd.Series) -> dict:
    """
    Trích xuất 6 nhóm thực thể chuẩn hóa cho 1 JD từ dòng dữ liệu VietJobs.
    """
    # 1. Role: lấy từ job_title
    role = [str(row.get("job_title", "")).strip()] if pd.notna(row.get("job_title")) else []

    # 2. Hard skills
    hard_skills = clean_list_str(row.get("technical_skills"))

    # 3. Soft skills
    soft_skills = clean_list_str(row.get("soft_skills"))

    # 4. Education
    education = clean_list_str(row.get("qualifications"))
    if not education and pd.notna(row.get("qualifications")):
        education = [str(row.get("qualifications")).strip()]

    # 5. Field of education: suy luận từ qualifications hoặc CNTT
    field_of_edu = ["Công nghệ thông tin", "Khoa học máy tính"]
    for edu in education:
        edu_lower = edu.lower()
        if "toán" in edu_lower:
            field_of_edu.append("Toán tin")
        if "điện tử" in edu_lower or "viễn thông" in edu_lower:
            field_of_edu.append("Điện tử viễn thông")
        if "phần mềm" in edu_lower:
            field_of_edu.append("Kỹ thuật phần mềm")
        if "hệ thống" in edu_lower:
            field_of_edu.append("Hệ thống thông tin")
    field_of_edu = list(dict.fromkeys(field_of_edu))  # remove duplicates

    # 6. Industry sector
    industry_sector = ["Công nghệ thông tin", "Kỹ thuật số"]

    return {
        "soft_skills": soft_skills,
        "hard_skills": hard_skills,
        "education": education,
        "field_of_education": field_of_edu,
        "industry_sector": industry_sector,
        "role": role,
    }


def run_jd_cache_pipeline():
    print("=" * 70)
    print("  BƯỚC 1: TRÍCH XUẤT THỰC THỂ & CACHE EMBEDDINGS CHO 1.906 JD")
    print("=" * 70)

    csv_path = getattr(config, "VIETJOBS_IT_CSV", os.path.join(config.DATA_RAW_DIR, "VietJobs_cntt.csv"))

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Không tìm thấy file: {csv_path}")

    print(f"\n[1/4] Đọc dữ liệu từ {csv_path}...")
    df = pd.read_csv(csv_path)
    total_jds = len(df)
    print(f"  Tổng số JD: {total_jds:,}")

    # Đảm bảo thư mục cache tồn tại
    os.makedirs(config.DATA_CACHE_DIR, exist_ok=True)

    print("\n[2/4] Trích xuất thực thể & cập nhật Entity Cache...")
    entity_records = []

    for idx, row in tqdm(df.iterrows(), total=total_jds, desc="Trích xuất thực thể"):
        entities = extract_jd_entities_from_row(row)

        jd_id_str = str(row.get("jd_id", f"jd_{idx+1:04d}"))
        formatted_text = str(row.get("formatted_jd_text", ""))
        text_hash = get_cache_key(formatted_text) if formatted_text else None

        # Lưu cache theo text_hash và jd_id
        if text_hash:
            set_cached_entity(text_hash, entities, save=False)
        set_cached_entity(jd_id_str, entities, save=False)
        set_cached_entity(str(idx + 1), entities, save=False)

        entity_records.append({
            "jd_id": jd_id_str,
            "job_title": str(row.get("job_title", "")),
            "file_path": jd_id_str,
            "text_hash": text_hash,
            "entities": entities,
        })

    # Lưu file cache ra đĩa
    save_entire_cache()
    print(f"  ✓ Đã lưu Entity Cache thành công vào: {config.ENTITY_CACHE_FILE}")

    print("\n[3/4] Thu thập tất cả chuỗi văn bản duy nhất để Batch Encode...")
    unique_texts = set()
    for item in entity_records:
        ents = item["entities"]
        all_texts_for_jd = []
        for etype in config.ENTITY_TYPES:
            for txt in ents.get(etype, []):
                if txt.strip():
                    unique_texts.add(txt.strip())
                    all_texts_for_jd.append(txt.strip())
        main_text = " ".join(all_texts_for_jd) if all_texts_for_jd else "unknown"
        unique_texts.add(main_text)

    unique_text_list = list(unique_texts)
    print(f"  Tổng số chuỗi văn bản duy nhất cần encode: {len(unique_text_list):,}")

    print("\n  Khởi tạo EmbeddingGenerator (paraphrase-multilingual-MiniLM-L12-v2)...")
    emb_gen = EmbeddingGenerator()

    print(f"  Đang Batch Encode {len(unique_text_list):,} chuỗi văn bản (batch_size=128)...")
    raw_embeddings = emb_gen.model.encode(
        unique_text_list,
        batch_size=128,
        show_progress_bar=True,
        convert_to_numpy=True,
    )
    text_to_embedding = {txt: raw_embeddings[i] for i, txt in enumerate(unique_text_list)}
    dim = emb_gen.embedding_dim

    print("\n[4/4] Tính DeepSets Embeddings & Vector phân cụm cho toàn bộ 1.906 JD...")
    cached_jds = []

    for item in tqdm(entity_records, desc="Sinh DeepSets features"):
        ents = item["entities"]
        features = {}
        all_texts_for_jd = []

        for etype in config.ENTITY_TYPES:
            items = ents.get(etype, [])
            group_texts = [x.strip() for x in items if x.strip()]
            all_texts_for_jd.extend(group_texts)

            if not group_texts:
                features[etype] = np.zeros(3 * dim)
            else:
                embs = np.stack([text_to_embedding[t] for t in group_texts])
                mean_pool = np.mean(embs, axis=0)
                sum_pool = np.sum(embs, axis=0)
                max_pool = np.max(embs, axis=0)
                features[etype] = np.concatenate([mean_pool, sum_pool, max_pool])

        # Main text embedding
        main_text = " ".join(all_texts_for_jd) if all_texts_for_jd else "unknown"
        main_emb = text_to_embedding.get(main_text, np.zeros(dim))
        main_padded = np.zeros(3 * dim)
        main_padded[:dim] = main_emb

        # Vector đặc trưng phân cụm: kết hợp role (1152-dim) và hard_skills (1152-dim)
        role_vec = features.get("role", np.zeros(3 * dim))
        skills_vec = features.get("hard_skills", np.zeros(3 * dim))
        cluster_vec = np.concatenate([role_vec, skills_vec])

        # Chuẩn hóa L2
        norm = np.linalg.norm(cluster_vec)
        if norm > 1e-8:
            cluster_vec = cluster_vec / norm

        cached_jds.append({
            "jd_id": item["jd_id"],
            "job_title": item["job_title"],
            "file_path": item["file_path"],
            "abs_path": item.get("abs_path", item["file_path"]),
            "text_hash": item["text_hash"],
            "entities": ents,
            "main_padded": torch.from_numpy(main_padded).float(),
            "features": {k: torch.from_numpy(v).float() for k, v in features.items()},
            "cluster_vector": torch.from_numpy(cluster_vec).float(),
        })

    # Lưu toàn bộ embeddings cache
    torch.save(cached_jds, config.JD_EMBEDDINGS_CACHE_FILE)
    print(f"\n✓ Đã lưu Embeddings Cache cho {len(cached_jds):,} JD tại: {config.JD_EMBEDDINGS_CACHE_FILE}")
    print("=" * 70)
    print("HOÀN THÀNH BƯỚC 1: JD-ONLY PASS!")
    print("=" * 70)


if __name__ == "__main__":
    run_jd_cache_pipeline()
