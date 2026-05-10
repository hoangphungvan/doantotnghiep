"""
CJMDataset: Dataset class cho Candidate-Job Matching.

Hỗ trợ hai chế độ:
1. Từ CSV: Đọc danh sách (cv_path, jd_path, label) và xử lý pipeline đầy đủ
2. Từ pre-processed graphs: Load trực tiếp các file .pt đã lưu
"""

import os
import json
from typing import Optional

import torch
import pandas as pd
from torch_geometric.data import Dataset, Data
from tqdm import tqdm

import config
from entity_extractor import extract_entities, read_document
from embedding_generator import EmbeddingGenerator
from graph_builder import build_graph


class CJMDataset(Dataset):
    """
    Dataset cho Candidate-Job Matching bằng GCN.

    Mỗi sample là một đồ thị bipartite 14 nút biểu diễn
    một cặp Candidate-JD.
    """

    def __init__(self, root: str = None, csv_path: str = None,
                 transform=None, pre_transform=None,
                 embedding_generator: Optional[EmbeddingGenerator] = None):
        """
        Args:
            root: Thư mục gốc chứa data (raw/ và processed/)
            csv_path: Đường dẫn tới file CSV (cv_path, jd_path, label)
            embedding_generator: Instance của EmbeddingGenerator (tạo mới nếu None)
        """
        self.csv_path = csv_path
        self._embedding_gen = embedding_generator
        self._data_list = []

        if root is None:
            root = os.path.join(os.path.dirname(__file__), "data")

        super().__init__(root, transform, pre_transform)
        self._load_processed()

    @property
    def embedding_gen(self):
        if self._embedding_gen is None:
            self._embedding_gen = EmbeddingGenerator()
        return self._embedding_gen

    @property
    def raw_file_names(self):
        if self.csv_path and os.path.exists(self.csv_path):
            return [os.path.basename(self.csv_path)]
        return []

    @property
    def processed_file_names(self):
        graph_dir = os.path.join(self.processed_dir, "graphs")
        if os.path.exists(graph_dir):
            return [f for f in os.listdir(graph_dir) if f.endswith('.pt')]
        return []

    @property
    def processed_graph_dir(self):
        path = os.path.join(self.processed_dir, "graphs")
        os.makedirs(path, exist_ok=True)
        return path

    def _load_processed(self):
        """Load tất cả pre-processed graphs."""
        self._data_list = []
        graph_dir = self.processed_graph_dir
        if os.path.exists(graph_dir):
            files = sorted([f for f in os.listdir(graph_dir) if f.endswith('.pt')])
            for f in files:
                data = torch.load(os.path.join(graph_dir, f), weights_only=False)
                self._data_list.append(data)

    def process(self):
        """Xử lý từ CSV: extract -> embed -> build graph -> save."""
        if not self.csv_path or not os.path.exists(self.csv_path):
            return

        df = pd.read_csv(self.csv_path)
        required_cols = {"cv_path", "jd_path", "label"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"CSV phải có các cột: {required_cols}")

        graph_dir = self.processed_graph_dir

        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing pairs"):
            cv_path = row["cv_path"]
            jd_path = row["jd_path"]
            label = float(row["label"])

            try:
                cv_text = read_document(cv_path)
                jd_text = read_document(jd_path)

                cv_entities = extract_entities(cv_text)
                jd_entities = extract_entities(jd_text)

                cv_main, cv_feats = self.embedding_gen.build_node_features(cv_entities)
                jd_main, jd_feats = self.embedding_gen.build_node_features(jd_entities)

                data = build_graph(cv_main, cv_feats, jd_main, jd_feats, label=label)

                data.cv_path = cv_path
                data.jd_path = jd_path
                data.cv_entities = json.dumps(cv_entities, ensure_ascii=False)
                data.jd_entities = json.dumps(jd_entities, ensure_ascii=False)

                save_path = os.path.join(graph_dir, f"graph_{idx:06d}.pt")
                torch.save(data, save_path)

            except Exception as e:
                print(f"[ERROR] Pair {idx} ({cv_path}, {jd_path}): {e}")
                continue

        self._load_processed()

    def len(self):
        return len(self._data_list)

    def get(self, idx):
        return self._data_list[idx]


class CJMInMemoryDataset:
    """
    Phiên bản in-memory đơn giản hơn, không cần file hệ thống.
    Phù hợp cho demo và test nhanh.
    """

    def __init__(self, data_list: list[Data] = None):
        self.data_list = data_list or []

    def add(self, data: Data):
        self.data_list.append(data)

    def __len__(self):
        return len(self.data_list)

    def __getitem__(self, idx):
        return self.data_list[idx]

    def save(self, path: str):
        torch.save(self.data_list, path)

    @classmethod
    def load(cls, path: str):
        data_list = torch.load(path, weights_only=False)
        return cls(data_list)


def create_sample_dataset(num_samples: int = 20,
                          positive_ratio: float = 0.05) -> CJMInMemoryDataset:
    """
    Tạo dataset mẫu với dữ liệu ngẫu nhiên để test pipeline.
    Mô phỏng mất cân bằng lớp: ~5% positive.
    """
    import numpy as np
    np.random.seed(42)

    gen = EmbeddingGenerator()
    feat_dim = gen.embedding_dim * 3
    dataset = CJMInMemoryDataset()

    sample_entities_pool = {
        "soft_skills": [
            ["teamwork", "communication"],
            ["leadership", "problem solving"],
            ["time management", "creativity"],
        ],
        "hard_skills": [
            ["Python", "Machine Learning", "SQL"],
            ["Java", "Spring Boot", "Docker"],
            ["JavaScript", "React", "Node.js"],
        ],
        "education": [["Bachelor"], ["Master"], ["PhD"]],
        "field_of_education": [
            ["Computer Science"],
            ["Business Administration"],
            ["Data Science"],
        ],
        "industry_sector": [
            ["Information Technology"],
            ["Finance"],
            ["Healthcare"],
        ],
        "role": [
            ["Software Engineer"],
            ["Data Analyst"],
            ["Project Manager"],
        ],
    }

    num_positive = max(1, int(num_samples * positive_ratio))
    labels = [1.0] * num_positive + [0.0] * (num_samples - num_positive)
    np.random.shuffle(labels)

    for i, label in enumerate(tqdm(labels, desc="Generating sample data")):
        cv_ents = {
            etype: items[np.random.randint(len(items))]
            for etype, items in sample_entities_pool.items()
        }
        jd_ents = {
            etype: items[np.random.randint(len(items))]
            for etype, items in sample_entities_pool.items()
        }

        cv_main, cv_feats = gen.build_node_features(cv_ents)
        jd_main, jd_feats = gen.build_node_features(jd_ents)

        data = build_graph(cv_main, cv_feats, jd_main, jd_feats, label=label)
        dataset.add(data)

    return dataset


if __name__ == "__main__":
    print("=== Tạo sample dataset ===")
    dataset = create_sample_dataset(num_samples=10)
    print(f"Dataset size: {len(dataset)}")
    print(f"Sample graph: {dataset[0]}")
    print(f"  x shape: {dataset[0].x.shape}")
    print(f"  edge_index shape: {dataset[0].edge_index.shape}")
    print(f"  label: {dataset[0].y}")
