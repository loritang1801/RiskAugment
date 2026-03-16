"""
Embedding model for converting text to vectors.
Uses BAAI/bge-large-zh-v1.5 for Chinese text embedding.
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple, Union
import math
import random

try:
    import numpy as np
except ImportError:
    np = None

logger = logging.getLogger(__name__)


def resolve_hf_cached_snapshot(model_name: str) -> Optional[Path]:
    """Resolve a Hugging Face cached snapshot directory for a repo id."""
    if not model_name or '/' not in model_name:
        return None

    cache_root = os.getenv('HUGGINGFACE_HUB_CACHE')
    if cache_root:
        hub_root = Path(cache_root)
    else:
        hf_home = os.getenv('HF_HOME')
        hub_root = Path(hf_home) / 'hub' if hf_home else Path.home() / '.cache' / 'huggingface' / 'hub'

    repo_dir = hub_root / f"models--{model_name.replace('/', '--')}"
    if not repo_dir.exists():
        return None

    ref_file = repo_dir / 'refs' / 'main'
    if ref_file.exists():
        snapshot_dir = repo_dir / 'snapshots' / ref_file.read_text(encoding='utf-8').strip()
        if snapshot_dir.exists():
            return snapshot_dir

    snapshots_dir = repo_dir / 'snapshots'
    if not snapshots_dir.exists():
        return None

    candidates = sorted(
        [path for path in snapshots_dir.iterdir() if path.is_dir()],
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )
    return candidates[0] if candidates else None


class EmbeddingModel:
    """Wrapper for embedding model."""
    
    def __init__(self, model_name: str = 'BAAI/bge-large-zh-v1.5', dimension: int = 1024):
        """
        Initialize embedding model.
        
        Args:
            model_name: Name of the embedding model
            dimension: Dimension of the embedding vector
        """
        self.model_name = model_name
        self.dimension = dimension
        self.model = None
        self.model_source = model_name
        self.local_files_only = False
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model."""
        try:
            # Try to import sentence-transformers
            from sentence_transformers import SentenceTransformer

            model_source, local_files_only = self._resolve_model_source()
            self.model_source = model_source
            self.local_files_only = local_files_only
            logger.info(
                "Loading embedding model: requested=%s source=%s local_files_only=%s",
                self.model_name,
                self.model_source,
                self.local_files_only
            )
            self.model = SentenceTransformer(self.model_source, local_files_only=self.local_files_only)
            logger.info(f"Model loaded successfully. Dimension: {self.dimension}")
        except ImportError as e:
            raise RuntimeError("sentence-transformers is not installed") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize embedding model '{self.model_name}' from '{self.model_source}': {e}"
            ) from e

    def _resolve_model_source(self) -> Tuple[str, bool]:
        configured_path = Path(self.model_name).expanduser()
        if configured_path.exists():
            return str(configured_path), True

        cached_snapshot = resolve_hf_cached_snapshot(self.model_name)
        if cached_snapshot is not None:
            return str(cached_snapshot), True

        return self.model_name, False
    
    def embed_text(self, text: str) -> List[float]:
        """
        Convert text to embedding vector.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        if self.model is None:
            raise RuntimeError("Embedding model is not initialized")
        
        try:
            # Encode text to embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # Normalize to unit vector
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error embedding text: {str(e)}")
            raise
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Convert multiple texts to embedding vectors.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if self.model is None:
            raise RuntimeError("Embedding model is not initialized")
        
        try:
            # Encode texts to embeddings
            embeddings = self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
            
            # Normalize to unit vectors
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error embedding texts: {str(e)}")
            raise
    
    def _mock_embedding(self, text: str) -> List[float]:
        """
        Generate mock embedding for testing.
        
        Args:
            text: Input text
            
        Returns:
            Mock embedding vector
        """
        # Use hash of text to generate deterministic mock embedding
        hash_value = hash(text) % (2**32)

        if np is None:
            rng = random.Random(hash_value)
            embedding = [rng.uniform(-1.0, 1.0) for _ in range(self.dimension)]
            norm = math.sqrt(sum(v * v for v in embedding)) or 1.0
            return [v / norm for v in embedding]

        np.random.seed(hash_value)
        embedding = np.random.randn(self.dimension)
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.tolist()
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-1)
        """
        if np is None:
            dot = sum(a * b for a, b in zip(embedding1, embedding2))
            norm1 = math.sqrt(sum(a * a for a in embedding1))
            norm2 = math.sqrt(sum(b * b for b in embedding2))
            denom = norm1 * norm2 or 1.0
            similarity = dot / denom
        else:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        # Ensure value is in [0, 1]
        return float(max(0, min(1, similarity)))
    
    def batch_similarity(self, embeddings1: List[List[float]], embeddings2: List[List[float]]) -> List[List[float]]:
        """
        Calculate cosine similarity between two sets of embeddings.
        
        Args:
            embeddings1: First set of embeddings
            embeddings2: Second set of embeddings
            
        Returns:
            Matrix of similarity scores
        """
        if np is None:
            matrix: List[List[float]] = []
            for emb1 in embeddings1:
                row: List[float] = []
                for emb2 in embeddings2:
                    row.append(self.similarity(emb1, emb2))
                matrix.append(row)
            return matrix

        vecs1 = np.array(embeddings1)
        vecs2 = np.array(embeddings2)
        vecs1 = vecs1 / np.linalg.norm(vecs1, axis=1, keepdims=True)
        vecs2 = vecs2 / np.linalg.norm(vecs2, axis=1, keepdims=True)
        similarities = np.dot(vecs1, vecs2.T)
        return similarities.tolist()


# Global embedding model instance
_embedding_model = None


def get_embedding_model(model_name: str = 'BAAI/bge-large-zh-v1.5', dimension: int = 1024) -> EmbeddingModel:
    """
    Get or create global embedding model instance.
    
    Args:
        model_name: Name of the embedding model
        dimension: Dimension of the embedding vector
        
    Returns:
        EmbeddingModel instance
    """
    global _embedding_model
    
    if _embedding_model is None:
        _embedding_model = EmbeddingModel(model_name, dimension)
    
    return _embedding_model
