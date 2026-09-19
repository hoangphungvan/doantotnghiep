"""
Bước 2 & 3: Phân cụm 1.906 JD, chọn tập con đại diện & Tạo ma trận Hard/Easy Negatives.

Tác vụ:
1. Đọc 1.906 embedding vector đặc trưng (role + hard_skills) từ data/cache/jd_embeddings_cache.pt.
2. Áp dụng KMeans (K=20 cụm) để phân chia thị trường việc làm CNTT thành các nhóm chuyên môn chuẩn xác:
   - Backend Java / Spring Boot
   - Frontend React / NextJS / Vue
   - Backend Python / AI / Django
   - Data Engineer / Machine Learning
   - DevOps / Cloud (AWS, Azure, K8s)
   - QA / Software Tester
   - Mobile Developer (iOS, Android, Flutter)
   - Embedded / C/C++ Firmware
   - IT Support / System Admin / Helpdesk
   - UI/UX & Graphic Designer
   - Tech Lead / Solution Architect / PM
   ...
3. Tìm JD gần centroid nhất mỗi cụm -> Ra tập ~20-30 JD đại diện (representative_jds.csv).
4. Tính ma trận khoảng cách Cosine giữa các Centroid để định lượng:
   - Cùng cụm (Cosine = 1.0) -> Positive (Label 3) & Partial Match (Label 2)
   - Cụm gần nhất (Cosine cao) -> Hard Negative (Label 1: Liên quan ngành)
   - Cụm xa nhất (Cosine thấp) -> Easy Negative (Label 0: Không phù hợp)
5. Xuất các file cấu hình và hướng dẫn sinh dữ liệu cho bước tiếp theo.
"""

import collections
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# Hỗ trợ chạy trực tiếp từ thư mục gốc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config


def get_cluster_label(jds_in_cluster: list[dict]) -> str:
    """Tự động phân tích và tạo tên gợi nhớ cho cụm dựa trên top titles và top skills."""
    roles = []
    skills = []
    for item in jds_in_cluster:
        roles.append(item.get("job_title", ""))
        ents = item.get("entities", {})
        skills.extend(ents.get("hard_skills", []))

    # Đếm tần suất
    top_skills = [item[0] for item in collections.Counter(skills).most_common(4) if item[0]]
    # Đếm từ khóa chính trong title
    title_words = []
    for r in roles:
        cleaned = r.replace("-", " ").replace("/", " ").replace("(", " ").replace(")", " ")
        title_words.extend([w.strip() for w in cleaned.split() if len(w.strip()) >= 2])
    
    # Tìm keyword phổ biến nhất
    stop_words = {"nhân", "viên", "lập", "trình", "kỹ", "sư", "chuyên", "viên", "thực", "tập", "sinh", "và", "cho", "tại", "senior", "junior", "middle"}
    filtered_words = [w for w in title_words if w.lower() not in stop_words]
    top_keywords = [item[0] for item in collections.Counter(filtered_words).most_common(3) if item[0]]

    kw_str = " / ".join(top_keywords[:2]) if top_keywords else "IT General"
    skill_str = ", ".join(top_skills[:3]) if top_skills else "General"
    return f"{kw_str} ({skill_str})"


def run_clustering_pipeline(n_clusters: int = 20, reps_per_cluster: int = 2):
    print("=" * 75)
    print(f"  BƯỚC 2 & 3: PHÂN CỤM JD (K={n_clusters}) & XÂY DỰNG QUAN HỆ HARD/EASY NEGATIVES")
    print("=" * 75)

    cache_file = config.JD_EMBEDDINGS_CACHE_FILE
    if not os.path.exists(cache_file):
        raise FileNotFoundError(
            f"Chưa có file cache embeddings: {cache_file}.\n"
            "Vui lòng chạy trước: python src/data_collection/cache_jd_embeddings.py"
        )

    print(f"\n[1/5] Tải dữ liệu embeddings từ {cache_file}...")
    cached_jds = torch.load(cache_file, weights_only=False)
    total_jds = len(cached_jds)
    print(f"  Số lượng JD: {total_jds:,}")

    # Lấy ma trận vector đặc trưng
    vectors = np.stack([item["cluster_vector"].numpy() for item in cached_jds])
    print(f"  Kích thước ma trận đặc trưng: {vectors.shape}")

    print(f"\n[2/5] Chạy thuật toán KMeans (K={n_clusters})...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_ids = kmeans.fit_predict(vectors)
    centroids = kmeans.cluster_centers_

    # Gán cluster_id vào danh sách JD
    for idx, item in enumerate(cached_jds):
        item["cluster_id"] = int(cluster_ids[idx])
        # Khoảng cách Euclidean tới centroid của cụm mình
        c = centroids[cluster_ids[idx]]
        item["dist_to_centroid"] = float(np.linalg.norm(vectors[idx] - c))

    print("\n[3/5] Phân tích đặc trưng các cụm & Chọn JD đại diện (Representatives)...")
    cluster_groups = collections.defaultdict(list)
    for item in cached_jds:
        cluster_groups[item["cluster_id"]].append(item)

    cluster_info = {}
    representative_jds = []

    for cid in range(n_clusters):
        items = cluster_groups[cid]
        items_sorted = sorted(items, key=lambda x: x["dist_to_centroid"])
        label = get_cluster_label(items)
        cluster_info[cid] = {
            "cluster_id": cid,
            "cluster_name": label,
            "size": len(items),
            "top_representatives": [
                {
                    "jd_id": f"jd_{int(it['jd_id']):04d}" if str(it["jd_id"]).isdigit() else str(it["jd_id"]),
                    "job_title": it["job_title"],
                    "file_path": f"jd_{int(it['jd_id']):04d}" if str(it["jd_id"]).isdigit() else str(it["jd_id"]),
                    "hard_skills": it["entities"].get("hard_skills", [])[:5],
                    "dist_to_centroid": round(it["dist_to_centroid"], 4),
                }
                for it in items_sorted[:reps_per_cluster]
            ],
        }

        # Lưu vào danh sách đại diện
        for rank, rep in enumerate(items_sorted[:reps_per_cluster]):
            jd_id_str = f"jd_{int(rep['jd_id']):04d}" if str(rep["jd_id"]).isdigit() else str(rep["jd_id"])
            representative_jds.append({
                "cluster_id": cid,
                "cluster_name": label,
                "rank_in_cluster": rank + 1,
                "jd_id": jd_id_str,
                "job_title": rep["job_title"],
                "file_path": jd_id_str,
                "distance_to_centroid": round(rep["dist_to_centroid"], 4),
                "hard_skills": ", ".join(rep["entities"].get("hard_skills", [])[:8]),
                "soft_skills": ", ".join(rep["entities"].get("soft_skills", [])[:5]),
            })

    # Lưu representative_jds.csv
    rep_df = pd.DataFrame(representative_jds)
    rep_csv_path = os.path.join(config.DATA_PROCESSED_DIR, "representative_jds.csv")
    rep_df.to_csv(rep_csv_path, index=False, encoding="utf-8-sig")
    print(f"  ✓ Đã lưu danh sách {len(representative_jds)} JD đại diện vào: {rep_csv_path}")

    # Lưu jd_clusters.csv
    all_jds_clusters = [
        {
            "jd_id": it["jd_id"],
            "job_title": it["job_title"],
            "cluster_id": it["cluster_id"],
            "cluster_name": cluster_info[it["cluster_id"]]["cluster_name"],
            "distance_to_centroid": round(it["dist_to_centroid"], 4),
            "file_path": it["file_path"],
        }
        for it in cached_jds
    ]
    pd.DataFrame(all_jds_clusters).to_csv(
        os.path.join(config.DATA_PROCESSED_DIR, "jd_clusters.csv"),
        index=False,
        encoding="utf-8-sig"
    )

    print("\n[4/5] Tính toán ma trận khoảng cách Cosine giữa các Centroid (Negative Sampling)...")
    # Chuẩn hóa centroids để tính Cosine Similarity
    norms = np.linalg.norm(centroids, axis=1, keepdims=True)
    normed_centroids = centroids / np.maximum(norms, 1e-8)
    sim_matrix = cosine_similarity(normed_centroids)

    # Lưu ma trận similarity
    sim_df = pd.DataFrame(
        sim_matrix,
        index=[f"C{i}: {cluster_info[i]['cluster_name']}" for i in range(n_clusters)],
        columns=[f"C{i}" for i in range(n_clusters)]
    )
    sim_csv_path = os.path.join(config.DATA_PROCESSED_DIR, "cluster_similarity_matrix.csv")
    sim_df.to_csv(sim_csv_path, encoding="utf-8-sig")

    print("\n[5/5] Xây dựng hướng dẫn gán nhãn Hard / Easy Negatives cho từng cụm...")
    negative_guide = {}

    for cid in range(n_clusters):
        sims = sim_matrix[cid].copy()
        sims[cid] = -1.0  # Loại bỏ chính nó

        # Hard Negatives: Các cụm có similarity cao nhất với cụm này (cùng lĩnh vực, stack gần)
        # Ví dụ: Backend Java vs Backend NodeJS -> Label 1 (Liên quan ngành)
        hard_neg_cids = np.argsort(sims)[::-1][:3]

        # Easy Negatives: Các cụm có similarity thấp nhất (rất xa, hoàn toàn khác mảng)
        # Ví dụ: Web Frontend vs Embedded C hoặc Tester -> Label 0 (Không phù hợp)
        easy_neg_cids = np.argsort(sims)[:3]

        negative_guide[cid] = {
            "cluster_name": cluster_info[cid]["cluster_name"],
            "same_cluster_for_positive_label_3": {
                "cluster_id": cid,
                "label": 3,
                "desc": "Phù hợp tốt (Ứng viên khớp mạnh vị trí và kỹ năng của cụm này)",
            },
            "hard_negatives_label_1": [
                {
                    "cluster_id": int(h_cid),
                    "cluster_name": cluster_info[h_cid]["cluster_name"],
                    "similarity": round(float(sims[h_cid]), 4),
                    "label": 1,
                    "desc": "Liên quan ngành (Cùng khối ngành CNTT nhưng lệch stack/chuyên môn chính)",
                }
                for h_cid in hard_neg_cids
            ],
            "easy_negatives_label_0": [
                {
                    "cluster_id": int(e_cid),
                    "cluster_name": cluster_info[e_cid]["cluster_name"],
                    "similarity": round(float(sims[e_cid]), 4),
                    "label": 0,
                    "desc": "Không phù hợp (Khác biệt hoàn toàn về vai trò & kỹ năng)",
                }
                for e_cid in easy_neg_cids
            ],
        }

    guide_json_path = os.path.join(config.DATA_PROCESSED_DIR, "cluster_negative_sampling_guide.json")
    with open(guide_json_path, "w", encoding="utf-8") as f:
        json.dump(negative_guide, f, ensure_ascii=False, indent=2)

    print(f"  ✓ Đã lưu hướng dẫn gán nhãn tự động vào: {guide_json_path}")

    # In kết quả trực quan
    print("\n" + "=" * 75)
    print("  TỔNG HỢP 20 CỤM VIỆC LÀM CNTT & CẶP HARD/EASY NEGATIVE ĐIỂN HÌNH")
    print("=" * 75)
    print(f"{'Cụm':<5} | {'Số lượng':<8} | {'Tên cụm chuyên môn':<35} | {'Hard Negative (Label 1)':<20}")
    print("-" * 75)
    for cid in range(n_clusters):
        cname = cluster_info[cid]["cluster_name"][:35]
        size = cluster_info[cid]["size"]
        hard_c = negative_guide[cid]["hard_negatives_label_1"][0]
        hard_str = f"C{hard_c['cluster_id']} (sim={hard_c['similarity']:.2f})"
        print(f"C{cid:<4} | {size:<8} | {cname:<35} | {hard_str:<20}")

    print("\n" + "=" * 75)
    print("HOÀN THÀNH BƯỚC 2 & 3: PHÂN CỤM & XÂY DỰNG BỘ GÁN NHÃN ĐỊNH LƯỢNG!")
    print("=" * 75)


if __name__ == "__main__":
    run_clustering_pipeline()
