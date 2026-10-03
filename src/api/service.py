"""Application service that connects FastAPI to the existing ML pipeline."""

from __future__ import annotations

import os
import tempfile
import threading
from pathlib import Path
from typing import Any, Optional

import config
from src.extraction.entity_extractor import (
    extract_entities,
    extract_from_file,
    normalize_entities,
)
from src.inference.predict import CJMPredictor
from src.evaluation.scoring import combine_hybrid_score


class ModelUnavailableError(RuntimeError):
    """Raised when matching is requested before a trained checkpoint exists."""


class AIService:
    """Thread-safe facade for extraction, matching and ranking operations."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or config.MODEL_FILE
        self.default_alpha = float(os.getenv("HYBRID_ALPHA", "0.2"))
        self.max_upload_bytes = int(os.getenv("AI_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
        self._predictor: Optional[CJMPredictor] = None
        self._lock = threading.RLock()

    @property
    def predictor(self) -> CJMPredictor:
        """Load the model and Sentence-BERT once, on the first match request."""
        with self._lock:
            if self._predictor is not None:
                return self._predictor
            if not Path(self.model_path).exists():
                raise ModelUnavailableError(
                    f"Chưa có model checkpoint: {self.model_path}. "
                    "Hãy huấn luyện model trước khi gọi matching/ranking."
                )
            try:
                self._predictor = CJMPredictor(model_path=self.model_path)
            except Exception as exc:
                raise ModelUnavailableError(f"Không thể khởi tạo AI model: {exc}") from exc
            return self._predictor

    def is_ready(self) -> bool:
        """Readiness does not force-load a large model into memory."""
        return Path(self.model_path).exists()

    def metadata(self) -> dict[str, Any]:
        return {
            "artifact_version": config.ARTIFACT_VERSION,
            "embedding_model": config.EMBEDDING_MODEL_NAME,
            "embedding_dimension": 384,
            "node_feature_dimension": 1152,
            "graph_nodes": config.NUM_NODES,
            "entity_types": list(config.ENTITY_TYPES),
            "ranking_k": list(config.RANKING_KS),
            "default_hybrid_alpha": self.default_alpha,
            "model_path": self.model_path,
            "model_available": Path(self.model_path).exists(),
        }

    @staticmethod
    def _count_entities(entities: dict[str, list[str]]) -> int:
        return sum(len(items) for items in entities.values())

    @staticmethod
    def _normalize(entity_payload: Optional[dict[str, list[str]]]) -> dict[str, list[str]]:
        return normalize_entities(entity_payload or {})

    def extract(self, text: str, document_type: str = "document") -> dict[str, Any]:
        entities = extract_entities(text)
        return {
            "document_type": document_type,
            "entities": entities,
            "entity_count": self._count_entities(entities),
        }

    def _entities_for_text(
        self,
        text: Optional[str],
        entities: Optional[dict[str, list[str]]],
    ) -> dict[str, list[str]]:
        if entities is not None:
            return self._normalize(entities)
        if text is None or not text.strip():
            raise ValueError("Cần cung cấp text hoặc entities cho cả CV và JD.")
        return extract_entities(text)

    @staticmethod
    def _explanation(cv_entities: dict, jd_entities: dict) -> dict[str, Any]:
        matched: dict[str, list[str]] = {}
        missing: dict[str, list[str]] = {}
        for entity_type in config.ENTITY_TYPES:
            cv_items = {str(item).strip().casefold(): str(item).strip()
                        for item in cv_entities.get(entity_type, []) if str(item).strip()}
            jd_items = {str(item).strip().casefold(): str(item).strip()
                        for item in jd_entities.get(entity_type, []) if str(item).strip()}
            overlap = sorted(cv_items[key] for key in cv_items.keys() & jd_items.keys())
            absent = sorted(jd_items[key] for key in jd_items.keys() - cv_items.keys())
            if overlap:
                matched[entity_type] = overlap
            if absent:
                missing[entity_type] = absent

        cert_overlap = matched.get("certifications", [])
        return {
            "matched_entities": matched,
            "missing_jd_entities": missing,
            "certification_match": bool(cert_overlap),
            "summary": (
                "Có chứng chỉ phù hợp với yêu cầu JD."
                if cert_overlap
                else "Không có chứng chỉ phù hợp hoặc JD không yêu cầu chứng chỉ."
            ),
        }

    def match_entities(
        self,
        cv_entities: dict[str, list[str]],
        jd_entities: dict[str, list[str]],
        alpha: Optional[float] = None,
        include_entities: bool = True,
    ) -> dict[str, Any]:
        cv_entities = self._normalize(cv_entities)
        jd_entities = self._normalize(jd_entities)
        used_alpha = self.default_alpha if alpha is None else float(alpha)
        result = self.predictor.predict_from_entities(
            cv_entities,
            jd_entities,
            alpha=used_alpha,
        )

        graph_score = float(result.get("graph_score", result["score"]))
        semantic_score = float(result.get("semantic_score", 0.0))
        hybrid_score = float(
            result.get(
                "hybrid_score",
                combine_hybrid_score(graph_score, semantic_score, used_alpha),
            )
        )

        response = {
            "score": round(hybrid_score, 4),
            "hybrid_score": round(hybrid_score, 4),
            "graph_score": round(graph_score, 4),
            "base_score": result.get("base_score"),
            "semantic_score": round(semantic_score, 4),
            "hybrid_alpha": used_alpha,
            "certification_match_ratio": result.get("certification_match_ratio", 0.0),
            "grade": result["grade"],
            "grade_label": result["grade_label"],
            "label": result["label"],
            "graph_grade": result.get("graph_grade"),
            "graph_grade_label": result.get("graph_grade_label"),
            "graph_label": result.get("graph_label"),
            "explanation": self._explanation(cv_entities, jd_entities),
            "graph": {
                "nodes": result.get("graph_nodes", config.NUM_NODES),
                "edges": result.get("graph_edges", 0),
                "node_feature_dimension": 1152,
            },
        }
        if include_entities:
            response["cv_entities"] = cv_entities
            response["jd_entities"] = jd_entities
        return response

    def match_text(
        self,
        cv_text: Optional[str],
        jd_text: Optional[str],
        cv_entities: Optional[dict[str, list[str]]] = None,
        jd_entities: Optional[dict[str, list[str]]] = None,
        alpha: Optional[float] = None,
        include_entities: bool = True,
    ) -> dict[str, Any]:
        cv = self._entities_for_text(cv_text, cv_entities)
        jd = self._entities_for_text(jd_text, jd_entities)
        return self.match_entities(cv, jd, alpha=alpha, include_entities=include_entities)

    def match_uploaded_files(
        self,
        cv_name: str,
        cv_content: bytes,
        jd_name: str,
        jd_content: bytes,
        alpha: Optional[float] = None,
        include_entities: bool = True,
    ) -> dict[str, Any]:
        if len(cv_content) > self.max_upload_bytes or len(jd_content) > self.max_upload_bytes:
            raise ValueError(f"Mỗi file không được vượt quá {self.max_upload_bytes} bytes.")

        cv_entities = self._extract_uploaded_file(cv_name, cv_content)
        jd_entities = self._extract_uploaded_file(jd_name, jd_content)
        return self.match_entities(cv_entities, jd_entities, alpha, include_entities)

    @staticmethod
    def _extract_uploaded_file(filename: str, content: bytes) -> dict[str, list[str]]:
        suffix = Path(filename or "document.txt").suffix or ".txt"
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                temp.write(content)
                temp_path = temp.name
            return extract_from_file(temp_path)
        finally:
            if temp_path:
                try:
                    Path(temp_path).unlink(missing_ok=True)
                except OSError:
                    pass

    def rank(
        self,
        cv_text: Optional[str],
        cv_entities: Optional[dict[str, list[str]]],
        jobs: list[dict[str, Any]],
        alpha: Optional[float] = None,
        include_entities: bool = False,
    ) -> dict[str, Any]:
        candidate_entities = self._entities_for_text(cv_text, cv_entities)
        ranked = []
        for job in jobs:
            job_entities = self._entities_for_text(job.get("jd_text"), job.get("jd_entities"))
            result = self.match_entities(
                candidate_entities,
                job_entities,
                alpha=alpha,
                include_entities=include_entities,
            )
            result["job_id"] = job["job_id"]
            result["metadata"] = job.get("metadata", {})
            ranked.append(result)

        ranked.sort(key=lambda item: item["score"], reverse=True)
        for position, item in enumerate(ranked, start=1):
            item["rank"] = position
        return {
            "count": len(ranked),
            "ranking": ranked,
            "query": {"entity_count": self._count_entities(candidate_entities)},
        }
