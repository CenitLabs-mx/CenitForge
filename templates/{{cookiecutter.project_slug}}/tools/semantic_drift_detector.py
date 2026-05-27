"""
Semantic Drift Detector V5
Compara embeddings del PRD con embeddings del código/tests producidos
para detectar desviación semántica. Umbral por defecto: 0.85.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _HAS_DEPS = True
except ImportError:
    _HAS_DEPS = False


@dataclass
class DriftReport:
    prd_code_similarity: float
    prd_tests_similarity: float
    overall_similarity: float
    threshold: float
    has_drift: bool
    severity: str  # none | low | medium | high | critical
    prd_reference_hash: str = ""
    code_files_analyzed: List[str] = field(default_factory=list)
    test_files_analyzed: List[str] = field(default_factory=list)


class SemanticDriftDetector:
    """
    Detector de drift semántico basado en embeddings.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        threshold: float = 0.85,
    ):
        if not _HAS_DEPS:
            raise ImportError("Instalar: pip install sentence-transformers numpy")
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold

    def detect(
        self,
        prd_text: str,
        code_files: List[Path],
        test_files: List[Path],
    ) -> DriftReport:
        code_text = self._concat_files(code_files)
        tests_text = self._concat_files(test_files)

        prd_emb = self.model.encode(prd_text)
        code_emb = self.model.encode(code_text) if code_text.strip() else prd_emb
        tests_emb = self.model.encode(tests_text) if tests_text.strip() else prd_emb

        prd_code_sim = float(self._cosine(prd_emb, code_emb))
        prd_tests_sim = float(self._cosine(prd_emb, tests_emb))

        overall = (prd_code_sim * 0.4) + (prd_tests_sim * 0.6)
        has_drift = overall < self.threshold
        severity = self._severity(overall)

        return DriftReport(
            prd_code_similarity=round(prd_code_sim, 4),
            prd_tests_similarity=round(prd_tests_sim, 4),
            overall_similarity=round(overall, 4),
            threshold=self.threshold,
            has_drift=has_drift,
            severity=severity,
            code_files_analyzed=[str(f) for f in code_files],
            test_files_analyzed=[str(f) for f in test_files],
        )

    @staticmethod
    def _cosine(a, b) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    @staticmethod
    def _severity(sim: float) -> str:
        if sim >= 0.95:
            return "none"
        if sim >= 0.90:
            return "low"
        if sim >= 0.85:
            return "medium"
        if sim >= 0.80:
            return "high"
        return "critical"

    @staticmethod
    def _concat_files(files: List[Path]) -> str:
        parts = []
        for f in files:
            if f.exists():
                try:
                    parts.append(f"# {f}\n{f.read_text(errors='ignore')}\n")
                except Exception:
                    pass
        return "\n".join(parts)


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prd", required=True)
    parser.add_argument("--code", nargs="+", default=[])
    parser.add_argument("--tests", nargs="+", default=[])
    parser.add_argument("--threshold", type=float, default=0.85)
    args = parser.parse_args()

    detector = SemanticDriftDetector(threshold=args.threshold)
    prd = Path(args.prd).read_text()
    code = [Path(p) for p in args.code]
    tests = [Path(p) for p in args.tests]

    report = detector.detect(prd, code, tests)
    print(json.dumps(asdict(report), indent=2))
    sys.exit(1 if report.has_drift else 0)
