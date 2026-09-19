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
    from src.extraction.entity_extractor import extract_entities

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
    from src.modeling.dataset import create_sample_dataset
    from src.modeling.train import train

    print("=" * 60)
    print("  DEMO: CANDIDATE-JOB MATCHING GCN")
    print("=" * 60)

    print("\n[1/3] Tạo sample dataset (mỗi CV ghép với nhiều JD, grade 0-3)...")
    dataset = create_sample_dataset(num_queries=10, jds_per_query=5)
    print(f"  Dataset size: {len(dataset)}")
    print(f"  Sample graph: {dataset[0]}")
    print(f"  Feature dim: {dataset[0].x.shape[1]}")

    grades = [d.y.item() for d in dataset.data_list]
    for g in sorted(set(grades)):
        print(f"  {config.GRADE_LABELS[int(g)]} ({int(g)}): {grades.count(g)}")

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
        score = torch.sigmoid(logits).item()
        grade = round(score * config.NUM_GRADES)
        print(f"  Sample prediction: score={score:.4f}, "
              f"grade={grade}/3 ({config.GRADE_LABELS[grade]})")

    print("\n✓ Demo hoàn tất!")


def run_pipeline():
    """
    Chạy toàn bộ pipeline: Extract -> Embed -> Build Graph -> Train.
    Sử dụng LLM API để trích xuất thực thể.
    """
    from src.extraction.entity_extractor import extract_entities
    from src.representation.embedding_generator import EmbeddingGenerator
    from src.representation.graph_builder import build_graph
    from src.modeling.dataset import CJMInMemoryDataset
    from src.modeling.train import train

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
            "label": 3.0,
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
            "label": 2.0,
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
        from src.modeling.model import GCNModel, get_loss_fn
        input_dim = dataset[0].x.shape[1]
        model = GCNModel(input_dim=input_dim)
        model.eval()
        with torch.no_grad():
            for i in range(len(dataset)):
                logits = model(dataset[i])
                score = torch.sigmoid(logits).item()
                grade = round(score * config.NUM_GRADES)
                actual = int(cv_jd_pairs[i]["label"])
                print(f"  Pair {i+1}: score={score:.4f}, grade={grade}/3 "
                      f"(actual={actual}/3 — {config.GRADE_LABELS[actual]})")
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
    from src.modeling.dataset import CJMDataset
    from src.modeling.train import train

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


def run_hybrid_demo():
    """Demo Hybrid Score + Baselines với sample data (không cần API key)."""
    from src.modeling.dataset import create_sample_dataset
    from src.modeling.train import train
    from src.evaluation.hybrid import run_comparison

    print("=" * 60)
    print("  DEMO: HYBRID SCORE (GCN + SBERT) & BASELINES")
    print("=" * 60)

    print("\n[1/3] Tạo sample dataset...")
    dataset = create_sample_dataset(num_queries=10, jds_per_query=5)
    input_dim = dataset[0].x.shape[1]

    print("\n[2/3] Huấn luyện GCN (thành phần graph_score)...")
    model, _ = train(
        data_list=dataset.data_list,
        input_dim=input_dim,
        num_epochs=30,
        batch_size=8,
    )

    print("\n[3/3] Tune α & so sánh các phương pháp...")
    run_comparison(dataset.data_list, model=model, alpha="auto")


def main():
    parser = argparse.ArgumentParser(description="Candidate-Job Matching GCN")
    parser.add_argument(
        "--mode",
        type=str,
        default="demo",
        choices=["demo", "predict", "extract", "pipeline", "prepare", "train", "hybrid"],
        help=(
            "demo     : Test nhanh với data ngẫu nhiên\n"
            "prepare  : Thu thập & chuẩn bị training data (text hoặc file PDF)\n"
            "train    : Huấn luyện model từ data đã chuẩn bị\n"
            "predict  : Dự đoán tương tác\n"
            "extract  : Test trích xuất thực thể LLM\n"
            "pipeline : Full pipeline demo với LLM\n"
            "hybrid   : Hybrid Score + baseline so sánh (NDCG/MRR/Recall)\n"
        ),
    )
    parser.add_argument(
        "--input", type=str, choices=["text", "file"], default="file",
        help="(mode=prepare) Kiểu nhập: text hoặc file",
    )
    parser.add_argument(
        "--csv", type=str, default=None,
        help="(mode=prepare --input file) CSV có sẵn để batch process",
    )
    args = parser.parse_args()

    if args.mode == "demo":
        run_demo()
    elif args.mode == "extract":
        run_extract_demo()
    elif args.mode == "pipeline":
        run_pipeline()
    elif args.mode == "prepare":
        from src.data_collection.prepare_training_data import collect_text_mode, collect_file_mode
        if args.input == "text":
            collect_text_mode()
        else:
            collect_file_mode(csv_path=args.csv)
    elif args.mode == "train":
        # Reset sys.argv để argparse của train.py nhận đúng tham số của nó
        sys.argv = ["train.py"]
        import runpy
        runpy.run_module("src.modeling.train", run_name="__main__")
    elif args.mode == "predict":
        from src.inference.predict import predict_interactive
        predict_interactive()
    elif args.mode == "hybrid":
        run_hybrid_demo()


if __name__ == "__main__":
    main()
