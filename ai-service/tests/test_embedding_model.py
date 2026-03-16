import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.embedding.embedding_model import resolve_hf_cached_snapshot


class EmbeddingModelPathResolutionTest(unittest.TestCase):
    def test_resolve_hf_cached_snapshot_from_cache(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            hub_root = Path(temp_dir) / "hub"
            repo_dir = hub_root / "models--BAAI--bge-large-zh-v1.5"
            snapshot_dir = repo_dir / "snapshots" / "abc123"
            refs_dir = repo_dir / "refs"
            snapshot_dir.mkdir(parents=True)
            refs_dir.mkdir(parents=True)
            (refs_dir / "main").write_text("abc123", encoding="utf-8")

            with patch.dict(os.environ, {"HF_HOME": temp_dir}, clear=False):
                resolved = resolve_hf_cached_snapshot("BAAI/bge-large-zh-v1.5")

        self.assertEqual(snapshot_dir, resolved)


if __name__ == "__main__":
    unittest.main()
