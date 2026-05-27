"""
Sanitization Gateway V5
Proxy que intercepta payloads hacia LLMs externos, aplica sanitización
guiada por data-classification.yaml, y genera reporte firmado.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import yaml
from pathlib import Path


class Action(str, Enum):
    ALLOW = "allow"
    REDACT = "redact"
    PSEUDONYMIZE = "pseudonymize"
    SCHEMA_SAFE = "schema_safe"
    BLOCK = "block"


class BlockedPayloadError(Exception):
    """Lanzada cuando un payload contiene campos restricted que no pueden enviarse."""


@dataclass
class DetectionItem:
    type: str           # email, phone, api_key, ssn, restricted_field, etc.
    count: int
    action: Action
    samples: List[str] = field(default_factory=list)  # hasheados, nunca en claro


@dataclass
class SanitizationReport:
    timestamp: str
    payload_original_hash: str
    payload_sanitized_hash: str
    classification_levels_detected: Dict[str, int] = field(default_factory=dict)
    pii_detected: List[DetectionItem] = field(default_factory=list)
    secrets_detected: List[DetectionItem] = field(default_factory=list)
    restricted_fields_detected: List[str] = field(default_factory=list)
    action_taken: str = ""
    llm_destination: str = ""
    tokens_estimated: int = 0
    cost_estimated_usd: float = 0.0
    verdict: str = "ALLOWED"  # ALLOWED | BLOCKED | HUMAN_REVIEW
    signature: str = ""

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["pii_detected"] = [asdict(x) for x in self.pii_detected]
        d["secrets_detected"] = [asdict(x) for x in self.secrets_detected]
        return d


# ------------------------------------------------------------
# PII / Secrets patterns
# ------------------------------------------------------------

PII_PATTERNS = {
    "email":       re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone":       re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}\b"),
    "ssn_us":      re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    "ipv4":        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

SECRET_PATTERNS = {
    "aws_key":      re.compile(r"AKIA[0-9A-Z]{16}"),
    "generic_api":  re.compile(r"\b(?:sk|pk)_(?:live|test)_[A-Za-z0-9]{20,}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}"),
    "jwt":          re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
    "generic_b64":  re.compile(r"(?i)(?:password|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9+/=]{24,}['\"]?"),
}


class SanitizationGateway:
    """
    Gateway stateless que sanitiza payloads usando:
    1. Patrones regex de PII / secrets.
    2. data-classification.yaml para campos restricted.
    """

    def __init__(
        self,
        classification_path: Path = Path("docs/architecture/data-classification.yaml"),
        signing_key: str = "",
    ):
        self.signing_key = signing_key.encode() if signing_key else b""
        self.classification = self._load_classification(classification_path)
        self.pseudonym_cache: Dict[str, str] = {}
        self.pseudonym_counter = 0

    def _load_classification(self, path: Path) -> Dict:
        if path.exists():
            return yaml.safe_load(path.read_text()) or {}
        return {}

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------

    def sanitize(self, payload: str, llm_destination: str = "unknown") -> tuple[str, SanitizationReport]:
        original_hash = self._hash(payload)
        report = SanitizationReport(
            timestamp=datetime.utcnow().isoformat(),
            payload_original_hash=original_hash,
            payload_sanitized_hash="",
            llm_destination=llm_destination,
            tokens_estimated=self._estimate_tokens(payload),
        )

        sanitized = payload

        # 1) Secrets (siempre BLOCK)
        for stype, pattern in SECRET_PATTERNS.items():
            matches = pattern.findall(sanitized)
            if matches:
                report.secrets_detected.append(DetectionItem(
                    type=stype, count=len(matches), action=Action.BLOCK,
                    samples=[self._hash(m)[:12] for m in matches[:3]],
                ))

        # 2) Restricted fields (via classification)
        restricted_found = self._scan_restricted_fields(sanitized, report)

        # 3) PII
        for ptype, pattern in PII_PATTERNS.items():
            matches = pattern.findall(sanitized)
            if matches:
                action = Action.PSEUDONYMIZE if ptype == "email" else Action.REDACT
                report.pii_detected.append(DetectionItem(
                    type=ptype, count=len(matches), action=action,
                ))
                for m in matches:
                    sanitized = sanitized.replace(m, self._apply(m, action, ptype))

        # 4) Veredicto
        if report.secrets_detected or restricted_found:
            report.verdict = "BLOCKED"
            report.action_taken = "Blocked: restricted content detected"
            raise BlockedPayloadError(report.action_taken)
        elif report.pii_detected:
            report.verdict = "ALLOWED"
            report.action_taken = "Sanitized: PII redacted/pseudonymized"
        else:
            report.verdict = "ALLOWED"
            report.action_taken = "No sensitive content detected"

        report.payload_sanitized_hash = self._hash(sanitized)
        report.cost_estimated_usd = report.tokens_estimated * 0.000002  # ejemplo: $2/Mtok
        if self.signing_key:
            report.signature = self._sign(report)

        return sanitized, report

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------

    def _scan_restricted_fields(self, payload: str, report: SanitizationReport) -> bool:
        found = False
        for table, tcfg in self.classification.get("tables", {}).items():
            for fname, fcfg in tcfg.get("fields", {}).items():
                if fcfg.get("level") == "restricted":
                    # Busca referencias al campo por nombre en el payload
                    pattern = re.compile(rf"\b{re.escape(fname)}\b", re.IGNORECASE)
                    if pattern.search(payload):
                        found = True
                        report.restricted_fields_detected.append(f"{table}.{fname}")
        return found

    def _apply(self, value: str, action: Action, ptype: str) -> str:
        if action == Action.REDACT:
            return f"[{ptype.upper()}_REDACTED]"
        if action == Action.PSEUDONYMIZE:
            if value not in self.pseudonym_cache:
                self.pseudonym_counter += 1
                self.pseudonym_cache[value] = f"{ptype}_{self.pseudonym_counter:04d}"
            return self.pseudonym_cache[value]
        return value

    def _hash(self, text: str) -> str:
        return "sha256:" + hashlib.sha256(text.encode()).hexdigest()

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text.split()) * 4 // 3)

    def _sign(self, report: SanitizationReport) -> str:
        import hmac as _hmac
        payload = json.dumps(report.to_dict(), sort_keys=True, default=str)
        return _hmac.new(self.signing_key, payload.encode(), hashlib.sha256).hexdigest()


# ------------------------------------------------------------
# LLM Proxy (FastAPI-ready stub)
# ------------------------------------------------------------

class LLMProxy:
    """
    Wrapper que intercepta llamadas a LLMs externos y pasa el payload
    por el Sanitization Gateway antes de enviarlo.
    """

    def __init__(self, gateway: SanitizationGateway, provider_client):
        self.gateway = gateway
        self.provider = provider_client
        self.reports: List[SanitizationReport] = []

    def call(self, prompt: str, destination: str = "gemini-2.5-pro", **kwargs):
        sanitized, report = self.gateway.sanitize(prompt, llm_destination=destination)
        self.reports.append(report)
        if report.verdict == "BLOCKED":
            raise BlockedPayloadError(report.action_taken)
        return self.provider.generate(sanitized, **kwargs)


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Archivo con payload a sanitizar")
    parser.add_argument("--destination", default="test")
    args = parser.parse_args()

    gw = SanitizationGateway()
    text = Path(args.file).read_text()
    try:
        sanitized, report = gw.sanitize(text, llm_destination=args.destination)
        print(json.dumps(report.to_dict(), indent=2))
    except BlockedPayloadError as exc:
        print(f"❌ BLOCKED: {exc}")
        raise SystemExit(1)
