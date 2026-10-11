"""
Main entry point cho hệ thống Candidate-Job Matching bằng GCN.

Usage:
    python main.py --mode prepare     # Dựng đồ thị từ nhãn + CV + JD
    python main.py --mode train       # Huấn luyện mô hình cuối
    python main.py --mode predict     # Dự đoán (kèm diễn giải) cho một cặp CV-JD
    python main.py --mode extract     # Test trích xuất thực thể
"""

import argparse
import json
import sys

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


def main():
    parser = argparse.ArgumentParser(description="Candidate-Job Matching GCN")
    parser.add_argument(
        "--mode",
        type=str,
        default="predict",
        choices=["predict", "extract", "prepare", "train"],
        help=(
            "prepare : Dựng đồ thị từ nhãn + CV tổng hợp + JD thật\n"
            "train   : Huấn luyện mô hình cuối (muốn cross-validation: python src/modeling/train.py --cv 5)\n"
            "predict : Dự đoán kèm diễn giải cho một cặp CV-JD\n"
            "extract : Test trích xuất thực thể bằng LLM\n"
        ),
    )
    args = parser.parse_args()

    if args.mode == "extract":
        run_extract_demo()
    elif args.mode == "prepare":
        from src.data_collection.prepare_training_data import build_dataset
        build_dataset()
    elif args.mode == "train":
        # Reset sys.argv để argparse của train.py nhận đúng tham số của nó
        sys.argv = ["train.py"]
        import runpy
        runpy.run_module("src.modeling.train", run_name="__main__")
    elif args.mode == "predict":
        from src.inference.predict import predict_interactive
        predict_interactive()


if __name__ == "__main__":
    main()
