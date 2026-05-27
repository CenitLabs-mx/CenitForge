"""
Knowledge Quarantine Enforcer V5
Controla qué artifacts del Learning Loop pueden alimentar cada feed,
aplicando reglas de procedencia y decay function.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class KnowledgeArtifact:
    id: str
    source_type: str        # production_incident | user_feedback | market_research | security_incident
    title: str
    content: str
    created_at: datetime
    tags: List[str]
    path: str
    current_weight: float = 1.0


class KnowledgeQuarantineEnforcer:
    """
    Aplica cuarentena sobre artifacts antes de inyectarlos en un feed.
    """

    VALID_FEEDS = {
        "market_scoring", "opportunity_scorecard", "prd_generation",
        "threat_model", "test_plan", "runbooks", "critic_memory",
    }

    def __init__(self, config_path: Path = Path("docs/learning/knowledge-quarantine.yaml")):
        self.config = self._load_config(config_path)
        self.rules: List[Dict] = self.config.get("quarantine_rules", [])

    @staticmethod
    def _load_config(path: Path) -> Dict:
        if not path.exists():
            raise FileNotFoundError(f"Quarantine config missing: {path}")
        return yaml.safe_load(path.read_text()) or {}

    def can_use_artifact(self, artifact: KnowledgeArtifact, target_feed: str) -> bool:
        if target_feed not in self.VALID_FEEDS:
            raise ValueError(f"Feed desconocido: {target_feed}")

        rule = self._find_rule(artifact.source_type)
        if not rule:
            # Sin regla → permitir con decay genérico
            return self._check_decay(artifact, {"half_life_days": 180, "min_weight": 0.1})

        forbidden = rule.get("forbidden_feeds", [])
        if target_feed in forbidden:
            return False

        allowed = rule.get("allowed_feeds")
        if allowed and target_feed not in allowed:
            return False

        decay_cfg = rule.get("decay_function", {"half_life_days": 180, "min_weight": 0.1})
        return self._check_decay(artifact, decay_cfg)

    def _find_rule(self, source_type: str) -> Optional[Dict]:
        for r in self.rules:
            if r.get("source_type") == source_type:
                return r
        return None

    @staticmethod
    def _check_decay(artifact: KnowledgeArtifact, decay_cfg: Dict) -> bool:
        age_days = (datetime.utcnow() - artifact.created_at).days
        half_life = decay_cfg.get("half_life_days", 180)
        weight = 0.5 ** (age_days / half_life)
        artifact.current_weight = weight
        return weight >= decay_cfg.get("min_weight", 0.1)

    def get_artifacts_for_feed(
        self, feed: str, artifacts: List[KnowledgeArtifact]
    ) -> List[KnowledgeArtifact]:
        valid = [a for a in artifacts if self.can_use_artifact(a, feed)]
        return sorted(valid, key=lambda a: a.current_weight, reverse=True)

    def audit_report(self, artifacts: List[KnowledgeArtifact]) -> Dict:
        """Genera reporte de cuántos artifacts son válidos por feed."""
        report: Dict[str, Dict] = {}
        for feed in self.VALID_FEEDS:
            valid = self.get_artifacts_for_feed(feed, artifacts)
            report[feed] = {
                "total_artifacts": len(artifacts),
                "valid_artifacts": len(valid),
                "quarantined": len(artifacts) - len(valid),
            }
        return report


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--feed", required=True)
    parser.add_argument("--artifacts-dir", default="docs/learning/raw")
    args = parser.parse_args()

    enforcer = KnowledgeQuarantineEnforcer()
    artifacts_dir = Path(args.artifacts_dir)
    artifacts = []
    for f in artifacts_dir.glob("*.yaml"):
        data = yaml.safe_load(f.read_text()) or {}
        artifacts.append(KnowledgeArtifact(
            id=data.get("id", f.stem),
            source_type=data.get("source_type", "unknown"),
            title=data.get("title", ""),
            content=data.get("content", ""),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
            tags=data.get("tags", []),
            path=str(f),
        ))

    valid = enforcer.get_artifacts_for_feed(args.feed, artifacts)
    print(f"✅ {len(valid)}/{len(artifacts)} artifacts válidos para feed '{args.feed}'")
    for a in valid[:10]:
        print(f"  - {a.id} (weight={a.current_weight:.2f})")
