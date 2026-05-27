"""
Enforcement Verifier V5
Valida criptográficamente que los controles técnicos de invariantes existen
antes de permitir transiciones de fase en el Orchestrator.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

import yaml
import psycopg2


# ============================================================
# Data classes
# ============================================================

@dataclass
class VerificationResult:
    invariant_id: str
    status: str  # PASS | FAIL | WARN | SKIP
    evidence: Dict = field(default_factory=dict)
    message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class GateReport:
    phase: str
    maturity: str
    timestamp: str
    results: List[VerificationResult]
    verdict: str  # ALLOW | BLOCK
    signature: str
    project_id: str = ""

    def to_dict(self) -> Dict:
        return {
            "phase": self.phase,
            "maturity": self.maturity,
            "timestamp": self.timestamp,
            "project_id": self.project_id,
            "verdict": self.verdict,
            "signature": self.signature,
            "results": [r.to_dict() for r in self.results],
        }


# ============================================================
# Phase-gate matrix
# ============================================================

PHASE_GATE_MATRIX: Dict[str, Dict[str, List[str]]] = {
    "market_scoring":    {"M1": [], "M2": [], "M3": []},
    "knowledge_pack":    {"M1": ["INV-008", "INV-016"], "M2": ["INV-008", "INV-016"], "M3": ["INV-008", "INV-016"]},
    "prd":               {"M1": ["INV-008", "INV-016"], "M2": ["INV-008", "INV-016"], "M3": ["INV-008", "INV-016"]},
    "architecture_lock": {
        "M1": ["INV-001", "INV-002", "INV-008"],
        "M2": ["INV-001", "INV-002", "INV-005", "INV-006", "INV-008", "INV-013"],
        "M3": [f"INV-{i:03d}" for i in range(1, 21)],
    },
    "task_factory":      {"M1": ["INV-019"], "M2": ["INV-018", "INV-019"], "M3": ["INV-018", "INV-019"]},
    "execution":         {"M1": ["INV-018"], "M2": ["INV-018", "INV-019"], "M3": ["INV-018", "INV-019"]},
    "critic_review":     {"M1": [], "M2": [], "M3": []},
    "ci_cd":             {"M1": ["INV-008", "INV-012"], "M2": ["INV-008", "INV-012"], "M3": [f"INV-{i:03d}" for i in (1,2,3,4,5,6,8,9,12,13,16,17)]},
    "production_deploy": {
        "M1": [],  # M1 no va a producción
        "M2": [f"INV-{i:03d}" for i in range(1, 17)],
        "M3": [f"INV-{i:03d}" for i in range(1, 21)],
    },
    "learning_loop":     {"M1": ["INV-016"], "M2": ["INV-016"], "M3": ["INV-016"]},
}


# ============================================================
# Main verifier
# ============================================================

class EnforcementVerifier:
    """
    Verifica invariantes críticas mediante checks deterministas y firma
    reportes con HMAC-SHA256 para prevenir falsificación.
    """

    def __init__(
        self,
        signing_key: Optional[str] = None,
        db_url: Optional[str] = None,
        repo_root: str = ".",
        orchestrator_client: Optional["OrchestratorClient"] = None,
    ):
        self.signing_key = (signing_key or os.environ.get("ENFORCEMENT_SIGNING_KEY") or "").encode()
        if not self.signing_key:
            raise ValueError("ENFORCEMENT_SIGNING_KEY requerido (vault o env seguro)")
        self.db_url = db_url or os.environ.get("DATABASE_URL")
        self.repo_root = Path(repo_root).resolve()
        self.orchestrator = orchestrator_client
        self.checks: Dict[str, Callable[[], VerificationResult]] = self._register_checks()

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def verify_invariant(self, invariant_id: str) -> VerificationResult:
        check_fn = self.checks.get(invariant_id)
        if not check_fn:
            return VerificationResult(
                invariant_id=invariant_id,
                status="SKIP",
                message=f"No check registered for {invariant_id}",
            )
        try:
            return check_fn()
        except Exception as exc:  # noqa: BLE001
            return VerificationResult(
                invariant_id=invariant_id,
                status="FAIL",
                message=f"Check crashed: {exc}",
            )

    def verify_phase_gate(self, phase: str, maturity: str, project_id: str = "") -> GateReport:
        required = PHASE_GATE_MATRIX.get(phase, {}).get(maturity, [])
        results = [self.verify_invariant(inv) for inv in required]
        verdict = "ALLOW" if all(r.status in ("PASS", "SKIP", "WARN") for r in results) else "BLOCK"

        report = GateReport(
            phase=phase,
            maturity=maturity,
            timestamp=datetime.utcnow().isoformat(),
            project_id=project_id,
            results=results,
            verdict=verdict,
            signature=self._sign(results),
        )
        if self.orchestrator:
            self.orchestrator.record_verification(report)
        return report

    # --------------------------------------------------------
    # Check registration
    # --------------------------------------------------------

    def _register_checks(self) -> Dict[str, Callable[[], VerificationResult]]:
        return {
            "INV-001": self._check_inv_001_rls,
            "INV-002": self._check_inv_002_decimal,
            "INV-003": self._check_inv_003_webhook_middleware,
            "INV-004": self._check_inv_004_unique_event,
            "INV-005": self._check_inv_005_rls_isolation,
            "INV-006": self._check_inv_006_auth_middleware,
            "INV-007": self._check_inv_007_migration_rollback,
            "INV-008": self._check_inv_008_no_secrets,
            "INV-009": self._check_inv_009_billing_gate,
            "INV-010": self._check_inv_010_acr_workflow,
            "INV-011": self._check_inv_011_cache_wrapper,
            "INV-012": self._check_inv_012_log_sanitizer,
            "INV-013": self._check_inv_013_versioned_router,
            "INV-014": self._check_inv_014_vault_restricted,
            "INV-015": self._check_inv_015_synthetic_seed,
            "INV-016": self._check_inv_016_sanitizer_gateway,
            "INV-017": self._check_inv_017_expand_contract,
            "INV-018": self._check_inv_018_egress_allowlist,
            "INV-019": self._check_inv_019_budget_ceiling,
            "INV-020": self._check_inv_020_shadow_flag,
        }

    # --------------------------------------------------------
    # Individual checks
    # --------------------------------------------------------

    def _check_inv_001_rls(self) -> VerificationResult:
        """Verifica RLS habilitado en tablas de negocio."""
        business_tables = self._load_business_tables()
        if not self.db_url:
            return VerificationResult("INV-001", "SKIP", message="No DB_URL")

        with psycopg2.connect(self.db_url) as conn, conn.cursor() as cur:
            cur.execute("SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname='public'")
            rows = {r[0]: r[1] for r in cur.fetchall()}

        missing = [t for t in business_tables if not rows.get(t, False)]
        return VerificationResult(
            "INV-001",
            "PASS" if not missing else "FAIL",
            evidence={"business_tables": business_tables, "missing_rls": missing},
            message=f"{len(missing)} tablas sin RLS" if missing else "RLS OK",
        )

    def _check_inv_002_decimal(self) -> VerificationResult:
        """Verifica que no hay FLOAT/DOUBLE en columnas financieras."""
        migrations_dir = self.repo_root / "migrations"
        if not migrations_dir.exists():
            return VerificationResult("INV-002", "SKIP", message="No migrations dir")

        float_pattern = re.compile(r"\b(FLOAT|DOUBLE PRECISION|REAL)\b", re.IGNORECASE)
        financial_keywords = {"amount", "price", "total", "subtotal", "tax", "fee", "balance", "cents"}
        violations: List[str] = []

        for path in migrations_dir.glob("*.sql"):
            text = path.read_text()
            for line in text.splitlines():
                if any(k in line.lower() for k in financial_keywords) and float_pattern.search(line):
                    violations.append(f"{path.name}: {line.strip()}")

        return VerificationResult(
            "INV-002",
            "PASS" if not violations else "FAIL",
            evidence={"violations": violations},
        )

    def _check_inv_003_webhook_middleware(self) -> VerificationResult:
        return self._grep_check(
            "INV-003",
            patterns=[r"verify_webhook_signature", r"WebhookSignatureMiddleware", r"validate_signature"],
            paths=["src/", "app/"],
            description="webhook signature verification",
        )

    def _check_inv_004_unique_event(self) -> VerificationResult:
        if not self.db_url:
            return VerificationResult("INV-004", "SKIP", message="No DB_URL")
        with psycopg2.connect(self.db_url) as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT table_name FROM information_schema.table_constraints
                WHERE constraint_type='UNIQUE' AND table_name='processed_events'
            """)
            exists = cur.fetchone() is not None
        return VerificationResult(
            "INV-004",
            "PASS" if exists else "FAIL",
            message="UNIQUE constraint on processed_events" if exists else "Missing unique constraint",
        )

    def _check_inv_005_rls_isolation(self) -> VerificationResult:
        if not self.db_url:
            return VerificationResult("INV-005", "SKIP", message="No DB_URL")
        with psycopg2.connect(self.db_url) as conn, conn.cursor() as cur:
            cur.execute("SELECT policyname FROM pg_policies WHERE policyname ILIKE '%tenant%'")
            policies = [r[0] for r in cur.fetchall()]
        return VerificationResult(
            "INV-005",
            "PASS" if policies else "FAIL",
            evidence={"tenant_policies": policies},
        )

    def _check_inv_006_auth_middleware(self) -> VerificationResult:
        return self._grep_check(
            "INV-006",
            patterns=[r"@require_auth", r"AuthMiddleware", r"require_permission", r"auth_required"],
            paths=["src/", "app/"],
            description="auth middleware presence",
        )

    def _check_inv_007_migration_rollback(self) -> VerificationResult:
        migrations_dir = self.repo_root / "migrations"
        if not migrations_dir.exists():
            return VerificationResult("INV-007", "SKIP")
        missing_rollback = []
        for p in migrations_dir.glob("*.py"):
            text = p.read_text()
            if "def downgrade" not in text and "def rollback" not in text:
                missing_rollback.append(p.name)
        return VerificationResult(
            "INV-007",
            "PASS" if not missing_rollback else "FAIL",
            evidence={"missing_rollback": missing_rollback},
        )

    def _check_inv_008_no_secrets(self) -> VerificationResult:
        """Ejecuta gitleaks y verifica vault integration."""
        try:
            result = subprocess.run(
                ["gitleaks", "detect", "--source", str(self.repo_root), "--no-git", "-r", "/tmp/gitleaks.json"],
                capture_output=True, text=True, timeout=120,
            )
            clean = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return VerificationResult("INV-008", "FAIL", message=f"gitleaks unavailable: {exc}")

        vault_configured = any(
            (self.repo_root / p).exists()
            for p in ["infrastructure/vault.hcl", "infrastructure/terraform/vault.tf", "config/vault.yaml"]
        )
        status = "PASS" if clean and vault_configured else "FAIL"
        return VerificationResult(
            "INV-008", status,
            evidence={"gitleaks_clean": clean, "vault_configured": vault_configured},
        )

    def _check_inv_009_billing_gate(self) -> VerificationResult:
        ci_files = list((self.repo_root / ".github" / "workflows").glob("*.yml")) if (self.repo_root / ".github" / "workflows").exists() else []
        billing_gate = any("billing" in f.read_text().lower() for f in ci_files)
        return VerificationResult("INV-009", "PASS" if billing_gate else "FAIL")

    def _check_inv_010_acr_workflow(self) -> VerificationResult:
        return self._grep_check(
            "INV-010",
            patterns=[r"Architecture Change Request", r"ACR-", r"acr-workflow"],
            paths=[".github/", "docs/"],
            description="ACR workflow",
        )

    def _check_inv_011_cache_wrapper(self) -> VerificationResult:
        return self._grep_check(
            "INV-011",
            patterns=[r"tenant_prefix", r"TenantCache", r"scoped_cache"],
            paths=["src/", "app/"],
            description="tenant-prefixed cache",
        )

    def _check_inv_012_log_sanitizer(self) -> VerificationResult:
        return self._grep_check(
            "INV-012",
            patterns=[r"LogSanitizer", r"PIIRedactor", r"sanitize_log"],
            paths=["src/", "app/"],
            description="log sanitizer",
        )

    def _check_inv_013_versioned_router(self) -> VerificationResult:
        router_files = list(self.repo_root.rglob("router*.py")) + list(self.repo_root.rglob("routes*.py"))
        unversioned = []
        for f in router_files:
            for line in f.read_text().splitlines():
                if re.search(r"@(app|router)\.(get|post|put|delete|patch)\(['\"]/[^v]", line):
                    unversioned.append(f"{f.name}: {line.strip()}")
        return VerificationResult(
            "INV-013",
            "PASS" if not unversioned else "FAIL",
            evidence={"unversioned_routes": unversioned},
        )

    def _check_inv_014_vault_restricted(self) -> VerificationResult:
        schema = self._load_data_classification()
        if not schema:
            return VerificationResult("INV-014", "SKIP", message="No data-classification.yaml")
        missing_vault = []
        for table, cfg in schema.get("tables", {}).items():
            for fname, fcfg in cfg.get("fields", {}).items():
                if fcfg.get("level") == "restricted" and not fcfg.get("vault"):
                    missing_vault.append(f"{table}.{fname}")
        return VerificationResult(
            "INV-014",
            "PASS" if not missing_vault else "FAIL",
            evidence={"missing_vault": missing_vault},
        )

    def _check_inv_015_synthetic_seed(self) -> VerificationResult:
        has_seed = any((self.repo_root / p).exists() for p in [
            "seed/synthetic.py", "scripts/seed_synthetic.py", "infrastructure/seed.tf",
        ])
        return VerificationResult("INV-015", "PASS" if has_seed else "FAIL")

    def _check_inv_016_sanitizer_gateway(self) -> VerificationResult:
        return self._grep_check(
            "INV-016",
            patterns=[r"SanitizationGateway", r"LLMProxy", r"sanitize_payload"],
            paths=["src/", "sanitization/", "tools/"],
            description="sanitization gateway",
        )

    def _check_inv_017_expand_contract(self) -> VerificationResult:
        if not self.db_url:
            return VerificationResult("INV-017", "SKIP")
        with psycopg2.connect(self.db_url) as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT relname, n_live_tup FROM pg_stat_user_tables
                WHERE n_live_tup > 100000
            """)
            large_tables = {r[0]: r[1] for r in cur.fetchall()}

        adr_dir = self.repo_root / "docs" / "adr"
        covered = set()
        if adr_dir.exists():
            for p in adr_dir.glob("*.md"):
                text = p.read_text().lower()
                for t in large_tables:
                    if t in text and "expand" in text and "contract" in text:
                        covered.add(t)
        missing = set(large_tables) - covered
        return VerificationResult(
            "INV-017",
            "PASS" if not missing else "FAIL",
            evidence={"large_tables": large_tables, "missing_adr": list(missing)},
        )

    def _check_inv_018_egress_allowlist(self) -> VerificationResult:
        sandbox_cfg = self.repo_root / "infrastructure" / "sandbox.network.yaml"
        if not sandbox_cfg.exists():
            return VerificationResult("INV-018", "FAIL", message="No sandbox.network.yaml")
        cfg = yaml.safe_load(sandbox_cfg.read_text()) or {}
        allowlist = cfg.get("egress_allowlist", [])
        deny_private = cfg.get("deny_private_ranges", False)
        status = "PASS" if allowlist and deny_private else "FAIL"
        return VerificationResult("INV-018", status, evidence={"allowlist": allowlist})

    def _check_inv_019_budget_ceiling(self) -> VerificationResult:
        orchestrator_cfg = self.repo_root / "orchestrator" / "gates.yaml"
        if not orchestrator_cfg.exists():
            return VerificationResult("INV-019", "FAIL")
        cfg = yaml.safe_load(orchestrator_cfg.read_text()) or {}
        has_budget = "budget_limits" in cfg or "budget_monitor" in cfg
        return VerificationResult("INV-019", "PASS" if has_budget else "FAIL")

    def _check_inv_020_shadow_flag(self) -> VerificationResult:
        return self._grep_check(
            "INV-020",
            patterns=[r"shadow_billing", r"ShadowSafetyContract", r"shadow_mode"],
            paths=["src/", "tests/", "infrastructure/"],
            description="shadow billing flag",
        )

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    def _grep_check(
        self, inv_id: str, patterns: List[str], paths: List[str], description: str
    ) -> VerificationResult:
        matches: List[str] = []
        compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
        for rel in paths:
            target = self.repo_root / rel
            if not target.exists():
                continue
            for f in target.rglob("*"):
                if f.is_file() and f.suffix in {".py", ".ts", ".js", ".go", ".yaml", ".yml", ".md"}:
                    try:
                        text = f.read_text(errors="ignore")
                    except Exception:
                        continue
                    if any(rx.search(text) for rx in compiled):
                        matches.append(str(f.relative_to(self.repo_root)))
                        if len(matches) >= 10:
                            break
        return VerificationResult(
            inv_id,
            "PASS" if matches else "FAIL",
            evidence={"matches": matches, "description": description},
        )

    def _load_business_tables(self) -> List[str]:
        schema = self._load_data_classification()
        if schema:
            return list(schema.get("tables", {}).keys())
        # Fallback: parse migrations
        tables: List[str] = []
        migrations_dir = self.repo_root / "migrations"
        if migrations_dir.exists():
            for p in migrations_dir.glob("*.sql"):
                for m in re.finditer(r"CREATE TABLE\s+(?:public\.)?(\w+)", p.read_text(), re.I):
                    tables.append(m.group(1))
        return tables

    def _load_data_classification(self) -> Optional[Dict]:
        path = self.repo_root / "docs" / "architecture" / "data-classification.yaml"
        if path.exists():
            return yaml.safe_load(path.read_text())
        return None

    def _sign(self, results: List[VerificationResult]) -> str:
        payload = json.dumps([r.to_dict() for r in results], sort_keys=True, default=str)
        return hmac.new(self.signing_key, payload.encode(), hashlib.sha256).hexdigest()


# ============================================================
# Orchestrator client (stub)
# ============================================================

class OrchestratorClient:
    """Interfaz mínima para persistir reportes en el ledger del orquestador."""

    def __init__(self, endpoint: str, auth_token: str):
        self.endpoint = endpoint
        self.auth_token = auth_token

    def record_verification(self, report: GateReport) -> None:
        # Implementación real: HTTP POST a Temporal/Airflow
        pass


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enforcement Verifier V5")
    parser.add_argument("--phase", required=True)
    parser.add_argument("--maturity", required=True, choices=["M1", "M2", "M3"])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--project-id", default="")
    args = parser.parse_args()

    verifier = EnforcementVerifier(repo_root=args.repo)
    report = verifier.verify_phase_gate(args.phase, args.maturity, args.project_id)
    print(json.dumps(report.to_dict(), indent=2))
    raise SystemExit(0 if report.verdict == "ALLOW" else 1)
