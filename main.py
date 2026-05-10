"""
Main entry point cho hệ thống Candidate-Job Matching bằng GCN.

Usage:
    python main.py --mode demo        # Chạy demo với dữ liệu mẫu
    python main.py --mode train       # Huấn luyện từ CSV
    python main.py --mode predict     # Dự đoán tương tác
    python main.py --mode extract     # Test trích xuất thực thể
    python main.py --mode pipeline    # Chạy toàn bộ pipeline demo
"""

import argparse
import json
import os
import sys

import torch
import numpy as np

import config


def run_extract_demo():
    """Demo trích xuất thực thể bằng LLM."""
    from entity_extractor import extract_entities

    sample_cv = """
    Nguyễn Văn Minh - Senior Software Engineer
    Email: minh.nguyen@email.com

    HỌC VẤN:
    - Thạc sĩ Khoa học Máy tính, Đại học Bách Khoa Hà Nội (2018-2020)
    - Cử nhân Công nghệ Thông tin, Đại học Bách Khoa Hà Nội (2014-2018)

    KỸ NĂNG CHUYÊN MÔN:
    - Python, Java, Go, SQL, Docker, Kubernetes
    - Machine Learning, Deep Learning, NLP
    - AWS, GCP, CI/CD, Microservices

    KỸ NĂNG MỀM:
    - Lãnh đạo nhóm, quản lý dự án
    - Giao tiếp hiệu quả, thuyết trình
    - Tư duy phản biện, giải quyết vấn đề

    KINH NGHIỆM:
    - Senior ML Engineer tại VNG Corporation (2020-nay)
      Lĩnh vực: Công nghệ thông tin, AI/ML
    - Backend Developer tại FPT Software (2018-2020)
    """

    sample_jd = """
    VỊ TRÍ: Machine Learning Engineer
    CÔNG TY: Công ty Công nghệ ABC

    MÔ TẢ CÔNG VIỆC:
    - Xây dựng và triển khai mô hình ML/DL cho sản phẩm AI
    - Nghiên cứu và áp dụng các kỹ thuật NLP tiên tiến
    - Tối ưu hóa pipeline dữ liệu và model serving

    YÊU CẦU:
    - Tốt nghiệp Đại học trở lên ngành Khoa học Máy tính, Toán học, hoặc liên quan
    - Thành thạo Python, TensorFlow/PyTorch
    - Kinh nghiệm với Docker, Kubernetes, cloud services
    - Kỹ năng làm việc nhóm và giao tiếp tốt

    NGÀNH: Công nghệ thông tin / Trí tuệ nhân tạo
    """

    print("=" * 60)
    print("  DEMO TRÍCH XUẤT THỰC THỂ")
    print("=" * 60)

    print("\n--- Trích xuất từ CV ---")
    cv_entities = extract_entities(sample_cv)
    print(json.dumps(cv_entities, ensure_ascii=False, indent=2))

    print("\n--- Trích xuất từ JD ---")
    jd_entities = extract_entities(sample_jd)
    print(json.dumps(jd_entities, ensure_ascii=False, indent=2))

    return cv_entities, jd_entities


def run_demo():
    """Demo toàn bộ pipeline với dữ liệu mẫu (không cần LLM API)."""
    from dataset import create_sample_dataset
    from train import train

    print("=" * 60)
    print("  DEMO: CANDIDATE-JOB MATCHING GCN")
    print("=" * 60)

    print("\n[1/3] Tạo sample dataset...")
    dataset = create_sample_dataset(num_samples=50, positive_ratio=0.1)
    print(f"  Dataset size: {len(dataset)}")
    print(f"  Sample graph: {dataset[0]}")
    print(f"  Feature dim: {dataset[0].x.shape[1]}")

    labels = [d.y.item() for d in dataset.data_list]
    print(f"  Positive: {sum(l==1 for l in labels)}, Negative: {sum(l==0 for l in labels)}")

    print("\n[2/3] Huấn luyện GCN model...")
    input_dim = dataset[0].x.shape[1]
    model, history = train(
        data_list=dataset.data_list,
        input_dim=input_dim,
        num_epochs=30,
        batch_size=8,
    )

    print("\n[3/3] Thử dự đoán...")
    model.eval()
    with torch.no_grad():
        sample = dataset[0]
        logits = model(sample)
        prob = torch.sigmoid(logits).item()
        print(f"  Sample prediction: score={prob:.4f}, label={'MATCH' if prob >= 0.5 else 'NOT MATCH'}")

    print("\n✓ Demo hoàn tất!")


def run_pipeline():
    """
    Chạy toàn bộ pipeline: Extract -> Embed -> Build Graph -> Train.
    Sử dụng LLM API để trích xuất thực thể.
    """
    from entity_extractor import extract_entities
    from embedding_generator import EmbeddingGenerator
    from graph_builder import build_graph
    from dataset import CJMInMemoryDataset
    from train import train

    print("=" * 60)
    print("  FULL PIPELINE: CANDIDATE-JOB MATCHING")
    print("=" * 60)

    cv_jd_pairs = [
        {
            "cv": """Senior Python Developer với 5 năm kinh nghiệm.
            Kỹ năng: Python, Django, FastAPI, PostgreSQL, Docker, AWS.
            Học vấn: Cử nhân CNTT, ĐH Bách Khoa.
            Kỹ năng mềm: teamwork, problem solving.""",
            "jd": """Tuyển Python Backend Developer.
            Yêu cầu: Python, Django/FastAPI, SQL, Docker.
            Học vấn: Cử nhân CNTT trở lên.
            Ngành: Công nghệ thông tin.""",
            "label": 1.0,
        },
        {
            "cv": """Kế toán viên với 3 năm kinh nghiệm.
            Kỹ năng: Excel, SAP, kế toán thuế.
            Học vấn: Cử nhân Kế toán, ĐH Kinh tế.
            Kỹ năng mềm: cẩn thận, chi tiết.""",
            "jd": """Tuyển Python Backend Developer.
            Yêu cầu: Python, Django/FastAPI, SQL, Docker.
            Học vấn: Cử nhân CNTT trở lên.
            Ngành: Công nghệ thông tin.""",
            "label": 0.0,
        },
        {
            "cv": """Data Scientist, 4 năm kinh nghiệm.
            Kỹ năng: Python, R, Machine Learning, Deep Learning, SQL, Spark.
            Học vấn: Thạc sĩ Data Science.
            Kỹ năng mềm: phân tích, trình bày.""",
            "jd": """Tuyển ML Engineer.
            Yêu cầu: Python, ML/DL, cloud, Docker.
            Học vấn: Thạc sĩ trở lên ngành CNTT/Toán.
            Ngành: AI/Machine Learning.""",
            "label": 1.0,
        },
    ]

    print("\n[1/4] Trích xuất thực thể bằng LLM...")
    embedding_gen = EmbeddingGenerator()
    dataset = CJMInMemoryDataset()

    for i, pair in enumerate(cv_jd_pairs):
        print(f"\n  Pair {i+1}/{len(cv_jd_pairs)}:")
        cv_entities = extract_entities(pair["cv"])
        jd_entities = extract_entities(pair["jd"])
        print(f"    CV entities: {json.dumps(cv_entities, ensure_ascii=False)[:100]}...")
        print(f"    JD entities: {json.dumps(jd_entities, ensure_ascii=False)[:100]}...")

        print("  [2/4] Tạo embeddings...")
        cv_main, cv_feats = embedding_gen.build_node_features(cv_entities)
        jd_main, jd_feats = embedding_gen.build_node_features(jd_entities)

        print("  [3/4] Xây dựng đồ thị...")
        data = build_graph(cv_main, cv_feats, jd_main, jd_feats, label=pair["label"])
        dataset.add(data)
        print(f"    Graph: {data.num_nodes} nodes, {data.edge_index.shape[1]} edges")

    print(f"\n[4/4] Huấn luyện model với {len(dataset)} samples...")
    if len(dataset) < 3:
        print("  [WARN] Quá ít dữ liệu để train thực tế, chỉ demo forward pass.")
        from model import GCNModel, get_loss_fn
        input_dim = dataset[0].x.shape[1]
        model = GCNModel(input_dim=input_dim)
        model.eval()
        with torch.no_grad():
            for i in range(len(dataset)):
                logits = model(dataset[i])
                prob = torch.sigmoid(logits).item()
                print(f"  Pair {i+1}: score={prob:.4f}, actual={'MATCH' if cv_jd_pairs[i]['label']==1 else 'NOT MATCH'}")
    else:
        input_dim = dataset[0].x.shape[1]
        model, history = train(
            data_list=dataset.data_list,
            input_dim=input_dim,
            num_epochs=50,
            batch_size=2,
        )

    print("\n✓ Pipeline hoàn tất!")


def run_train_from_csv():
    """Huấn luyện từ file CSV."""
    from dataset import CJMDataset
    from train import train

    csv_path = input("Đường dẫn file CSV (cv_path,jd_path,label): ").strip()
    if not os.path.exists(csv_path):
        print(f"[ERROR] File không tồn tại: {csv_path}")
        return

    print(f"\n[1/2] Loading & processing dataset từ {csv_path}...")
    dataset = CJMDataset(csv_path=csv_path)

    if len(dataset) == 0:
        print("[ERROR] Dataset rỗng. Kiểm tra lại CSV và dữ liệu.")
        return

    print(f"\n[2/2] Training model trên {len(dataset)} samples...")
    input_dim = dataset[0].x.shape[1]
    model, history = train(
        data_list=[dataset[i] for i in range(len(dataset))],
        input_dim=input_dim,
    )


def main():
    parser = argparse.ArgumentParser(description="Candidate-Job Matching GCN")
    parser.add_argument(
        "--mode",
        type=str,
        default="demo",
        choices=["demo", "train", "predict", "extract", "pipeline"],
        help="Chế độ chạy: demo, train, predict, extract, pipeline",
    )
    args = parser.parse_args()

    if args.mode == "demo":
        run_demo()
    elif args.mode == "extract":
        run_extract_demo()
    elif args.mode == "pipeline":
        run_pipeline()
    elif args.mode == "train":
        run_train_from_csv()
    elif args.mode == "predict":
        from predict import predict_interactive
        predict_interactive()


if __name__ == "__main__":
    main()
