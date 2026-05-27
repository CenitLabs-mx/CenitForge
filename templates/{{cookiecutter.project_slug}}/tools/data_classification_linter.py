"""
Data Classification Linter V5
Valida el schema data-classification.yaml contra reglas declaradas
y verifica consistencia con el modelo de datos real.
"""

from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import yaml


SCHEMA_PATH = Path("docs/architecture/data-classification.yaml")
VALID_LEVELS = {"public", "internal", "confidential", "restricted"}
VALID_LOG_POLICIES = {"allow", "redact", "never"}
VALID_LLM_POLICIES = {"allow_raw", "sanitize", "block"}


@dataclass
class Violation:
    rule_id: str
    severity: str  # block | warn
    message: str
    location: str = ""


class DataClassificationLinter:
    def __init__(self, schema_path: Path = SCHEMA_PATH):
        self.schema_path = schema_path
        self.schema: Dict = {}
        self.violations: List[Violation] = []

    def load(self) -> None:
        if not self.schema_path.exists():
            raise FileNotFoundError(f"No encontrado: {self.schema_path}")
        self.schema = yaml.safe_load(self.schema_path.read_text()) or {}

    def lint(self) -> List[Violation]:
        self.load()
        self._check_schema_hash()
        self._check_level_definitions()
        self._check_table_definitions()
        self._check_rule_checks()
        self._check_pii_sanitizer_coverage()
        self._check_restricted_vault_coverage()
        self._check_log_policy_consistency()
        return self.violations

    # ------------------------------------------------------------
    # Checks
    # ------------------------------------------------------------

    def _check_schema_hash(self) -> None:
        declared = self.schema.get("schema_hash")
        if not declared:
            self.violations.append(Violation("DC-HASH", "block", "schema_hash missing"))
            return
        # Recalcular hash excluyendo el campo schema_hash y last_verified
        copy = {k: v for k, v in self.schema.items() if k not in ("schema_hash", "last_verified")}
        computed = "sha256:" + hashlib.sha256(
            yaml.safe_dump(copy, sort_keys=True).encode()
        ).hexdigest()
        if computed != declared:
            self.violations.append(Violation(
                "DC-HASH", "block",
                f"Hash mismatch. Declarado: {declared} | Computado: {computed}. "
                "¿Se modificó sin ACR?",
            ))

    def _check_level_definitions(self) -> None:
        levels = self.schema.get("levels", {})
        for lvl in VALID_LEVELS:
            if lvl not in levels:
                self.violations.append(Violation(
                    "DC-LEVEL", "block", f"Missing level definition: {lvl}"
                ))

    def _check_table_definitions(self) -> None:
        tables = self.schema.get("tables", {})
        for tname, tcfg in tables.items():
            if not isinstance(tcfg, dict):
                self.violations.append(Violation("DC-TABLE", "block", f"Invalid table cfg: {tname}"))
                continue
            for fname, fcfg in tcfg.get("fields", {}).items():
                loc = f"{tname}.{fname}"
                level = fcfg.get("level")
                if level not in VALID_LEVELS:
                    self.violations.append(Violation(
                        "DC-FIELD-LEVEL", "block", f"Invalid level '{level}'", location=loc,
                    ))
                log_p = fcfg.get("log", fcfg.get("log_policy"))
                if log_p and log_p not in VALID_LOG_POLICIES:
                    self.violations.append(Violation(
                        "DC-LOG-POLICY", "block", f"Invalid log policy '{log_p}'", location=loc,
                    ))

    def _check_rule_checks(self) -> None:
        for rule in self.schema.get("rules", []):
            if not rule.get("id"):
                self.violations.append(Violation("DC-RULE-ID", "block", "Rule without id"))
            if rule.get("severity") not in ("block", "warn"):
                self.violations.append(Violation("DC-RULE-SEV", "block", f"Rule {rule.get('id')}: bad severity"))
            if not rule.get("check"):
                self.violations.append(Violation("DC-RULE-CHECK", "block", f"Rule {rule.get('id')}: missing check"))

    def _check_pii_sanitizer_coverage(self) -> None:
        tables = self.schema.get("tables", {})
        for tname, tcfg in tables.items():
            for fname, fcfg in tcfg.get("fields", {}).items():
                if fcfg.get("pii_type") and not fcfg.get("sanitizer"):
                    self.violations.append(Violation(
                        "DC-PII-SANITIZER", "warn",
                        f"PII field without sanitizer assigned",
                        location=f"{tname}.{fname}",
                    ))

    def _check_restricted_vault_coverage(self) -> None:
        tables = self.schema.get("tables", {})
        for tname, tcfg in tables.items():
            for fname, fcfg in tcfg.get("fields", {}).items():
                if fcfg.get("level") == "restricted" and not fcfg.get("vault"):
                    if not fcfg.get("justification"):
                        self.violations.append(Violation(
                            "DC-RESTRICTED-VAULT", "block",
                            "Restricted field without vault or justification",
                            location=f"{tname}.{fname}",
                        ))

    def _check_log_policy_consistency(self) -> None:
        tables = self.schema.get("tables", {})
        for tname, tcfg in tables.items():
            for fname, fcfg in tcfg.get("fields", {}).items():
                level = fcfg.get("level")
                log = fcfg.get("log", fcfg.get("log_policy", "allow"))
                if level in ("confidential", "restricted") and log == "allow":
                    self.violations.append(Violation(
                        "DC-LOG-LEAK", "block",
                        f"Sensitive field with log=allow risks PII leak",
                        location=f"{tname}.{fname}",
                    ))


def main() -> int:
    linter = DataClassificationLinter()
    violations = linter.lint()

    blocking = [v for v in violations if v.severity == "block"]
    warnings = [v for v in violations if v.severity == "warn"]

    if warnings:
        print(f"⚠️  {len(warnings)} warnings:")
        for v in warnings:
            print(f"  [{v.rule_id}] {v.message} @ {v.location}")

    if blocking:
        print(f"❌ {len(blocking)} blocking violations:")
        for v in blocking:
            print(f"  [{v.rule_id}] {v.message} @ {v.location}")
        return 1

    print(f"✅ Data Classification Linter PASS ({len(warnings)} warnings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
