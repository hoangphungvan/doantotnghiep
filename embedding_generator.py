"""
Module tạo embedding cho các thực thể sử dụng sentence-transformers.
Áp dụng DeepSets pooling (Mean, Sum, Max) cho nhóm thực thể.
"""

import torch
import torch.nn as nn
import numpy as np
from sentence_transformers import SentenceTransformer

import config


class EmbeddingGenerator:
    """Tạo sentence embeddings và áp dụng DeepSets pooling."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.EMBEDDING_MODEL_NAME
        self.model = SentenceTransformer(self.model_name)
        self.embedding_dim = self.model.get_embedding_dimension()
        print(f"[EmbeddingGenerator] Model: {self.model_name}, dim={self.embedding_dim}")

    def encode(self, texts: list[str]) -> np.ndarray:
        """Encode danh sách text thành embedding vectors."""
        if not texts:
            return np.zeros((0, self.embedding_dim))
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    def deepsets_pool(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Áp dụng DeepSets pooling: concatenate [Mean, Sum, Max].

        Input shape: (num_items, embedding_dim)
        Output shape: (3 * embedding_dim,)
        """
        if len(embeddings) == 0:
            return np.zeros(3 * self.embedding_dim)

        mean_pool = np.mean(embeddings, axis=0)
        sum_pool = np.sum(embeddings, axis=0)
        max_pool = np.max(embeddings, axis=0)

        return np.concatenate([mean_pool, sum_pool, max_pool])

    def embed_entity_group(self, items: list[str]) -> np.ndarray:
        """
        Embed một nhóm thực thể và áp dụng DeepSets pooling.

        Args:
            items: Danh sách các text items (ví dụ: ["Python", "Java", "SQL"])

        Returns:
            Vector (3 * embedding_dim,) sau DeepSets pooling
        """
        if not items:
            return np.zeros(3 * self.embedding_dim)

        embeddings = self.encode(items)
        return self.deepsets_pool(embeddings)

    def build_node_features(self, entities: dict) -> np.ndarray:
        """
        Xây dựng feature vectors cho tất cả 7 nút (1 main + 6 entity) của một bên.

        Args:
            entities: dict với keys từ config.ENTITY_TYPES

        Returns:
            dict mapping entity_type -> pooled_embedding (3*embedding_dim,)
        """
        features = {}
        all_texts = []
        for etype in config.ENTITY_TYPES:
            items = entities.get(etype, [])
            all_texts.extend(items)

        for etype in config.ENTITY_TYPES:
            items = entities.get(etype, [])
            features[etype] = self.embed_entity_group(items)

        main_text = " ".join(all_texts) if all_texts else "unknown"
        main_embedding = self.encode([main_text])[0]
        main_padded = np.zeros(3 * self.embedding_dim)
        main_padded[:self.embedding_dim] = main_embedding

        return main_padded, features


class DeepSetsProjection(nn.Module):
    """
    Lớp projection cho DeepSets output.
    Chuyển từ 3*embedding_dim -> target_dim.
    """

    def __init__(self, input_dim: int, target_dim: int):
        super().__init__()
        self.projection = nn.Sequential(
            nn.Linear(input_dim, target_dim),
            nn.ReLU(),
            nn.LayerNorm(target_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.projection(x)


if __name__ == "__main__":
    gen = EmbeddingGenerator()
    print(f"Embedding dim: {gen.embedding_dim}")

    sample_entities = {
        "soft_skills": ["teamwork", "communication", "leadership"],
        "hard_skills": ["Python", "Machine Learning", "SQL"],
        "education": ["Bachelor"],
        "field_of_education": ["Computer Science"],
        "industry_sector": ["Information Technology"],
        "role": ["Software Engineer"],
    }

    main_feat, entity_feats = gen.build_node_features(sample_entities)
    print(f"Main node feature shape: {main_feat.shape}")
    for etype, feat in entity_feats.items():
        print(f"  {etype}: {feat.shape}")
