"""
Micro-Prompt Manager V5
Gestiona el ciclo de vida de micro-prompts: creación, validación,
tracking de blast radius, y generación de context summary.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml


class MaturityLevel(str, Enum):
    M1 = "M1"
    M2 = "M2"
    M3 = "M3"


class RiskClass(str, Enum):
    R0 = "R0"  # docs, estilos
    R1 = "R1"  # feature interna
    R2 = "R2"  # API, datos, auth parcial
    R3 = "R3"  # billing, secrets, PII, prod


class Complexity(str, Enum):
    S = "S"
    M = "M"
    L = "L"


class Priority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


@dataclass
class BlastRadius:
    files_declared: List[str] = field(default_factory=list)
    estimated_lines_changed: int = 0
    max_scope_creep_percent: float = 10.0


@dataclass
class ImpactSurface:
    code: List[str] = field(default_factory=list)
    contracts: List[str] = field(default_factory=list)
    tests: List[str] = field(default_factory=list)
    migrations: List[str] = field(default_factory=list)
    security: bool = False
    billing: bool = False
    tenancy: bool = False


@dataclass
class MicroPromptMetadata:
    id: str
    title: str
    maturity: MaturityLevel
    risk_class: RiskClass
    complexity: Complexity
    priority: Priority
    dependencies: List[str] = field(default_factory=list)
    timeout_minutes: int = 30
    budget_ceiling_usd: float = 2.0
    blast_radius: BlastRadius = field(default_factory=BlastRadius)
    impact_surface: ImpactSurface = field(default_factory=ImpactSurface)
    pr_number: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "draft"  # draft | active | done | cancelled


class MicroPromptManager:
    """
    Gestiona el ciclo de vida de micro-prompts en /docs/micro-prompts/.
    """

    MP_DIR = Path("docs/micro-prompts")
    TEMPLATE_PATH = Path("docs/templates/micro-prompt-template.md")

    RISK_DEFAULTS = {
        RiskClass.R0: {"budget": 0.5, "timeout": 15, "creep": 15.0},
        RiskClass.R1: {"budget": 1.0, "timeout": 20, "creep": 10.0},
        RiskClass.R2: {"budget": 2.0, "timeout": 30, "creep": 10.0},
        RiskClass.R3: {"budget": 5.0, "timeout": 60, "creep": 5.0},
    }

    def __init__(self, repo_root: Path = Path(".")):
        self.repo_root = repo_root
        self.mp_dir = repo_root / self.MP_DIR
        self.mp_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------

    def create(
        self,
        title: str,
        maturity: MaturityLevel,
        risk_class: RiskClass,
        files: List[str],
        estimated_lines: int = 50,
        **kwargs,
    ) -> Path:
        """Crea un nuevo micro-prompt con metadata completa."""
        mp_id = f"MP-{uuid.uuid4().hex[:8].upper()}"

        defaults = self.RISK_DEFAULTS[risk_class]
        metadata = MicroPromptMetadata(
            id=mp_id,
            title=title,
            maturity=maturity,
            risk_class=risk_class,
            complexity=kwargs.get("complexity", Complexity.M),
            priority=kwargs.get("priority", Priority.P2),
            dependencies=kwargs.get("dependencies", []),
            timeout_minutes=kwargs.get("timeout", defaults["timeout"]),
            budget_ceiling_usd=kwargs.get("budget", defaults["budget"]),
            blast_radius=BlastRadius(
                files_declared=files,
                estimated_lines_changed=estimated_lines,
                max_scope_creep_percent=kwargs.get("creep", defaults["creep"]),
            ),
            impact_surface=ImpactSurface(**kwargs.get("impact", {})),
        )

        # Guardar YAML metadata
        yaml_path = self.mp_dir / f"{mp_id}.yaml"
        yaml_path.write_text(yaml.safe_dump(asdict(metadata), sort_keys=False))

        # Generar Markdown usando template
        md_path = self.mp_dir / f"{mp_id}.md"
        md_path.write_text(self._render_markdown(metadata))

        return md_path

    def load(self, mp_id: str) -> MicroPromptMetadata:
        yaml_path = self.mp_dir / f"{mp_id}.yaml"
        if not yaml_path.exists():
            raise FileNotFoundError(f"Micro-prompt {mp_id} no encontrado")
        data = yaml.safe_load(yaml_path.read_text())
        return self._from_dict(data)

    def update_status(self, mp_id: str, status: str) -> None:
        path = self.mp_dir / f"{mp_id}.yaml"
        data = yaml.safe_load(path.read_text())
        data["status"] = status
        path.write_text(yaml.safe_dump(data, sort_keys=False))

    def list_by_status(self, status: str) -> List[MicroPromptMetadata]:
        results = []
        for p in self.mp_dir.glob("*.yaml"):
            data = yaml.safe_load(p.read_text())
            if data.get("status") == status:
                results.append(self._from_dict(data))
        return results

    def validate(self, mp_id: str) -> List[str]:
        """Valida consistencia del micro-prompt."""
        errors = []
        mp = self.load(mp_id)

        # R3 requiere blast radius explícito
        if mp.risk_class == RiskClass.R3 and not mp.blast_radius.files_declared:
            errors.append("R3 requiere blast radius declarado")

        # Impact surface consistency
        if mp.impact_surface.billing and mp.risk_class not in (RiskClass.R2, RiskClass.R3):
            errors.append("Impacto en billing requiere R2 o R3")

        if mp.impact_surface.tenancy and mp.risk_class not in (RiskClass.R2, RiskClass.R3):
            errors.append("Impacto en tenancy requiere R2 o R3")

        # Files exist
        for f in mp.blast_radius.files_declared:
            if not (self.repo_root / f).exists():
                errors.append(f"Archivo declarado no existe: {f}")

        return errors

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------

    def _render_markdown(self, mp: MicroPromptMetadata) -> str:
        return f"""# {mp.title}

**ID:** {mp.id}
**Maturity:** {mp.maturity.value}
**Risk class:** {mp.risk_class.value}
**Complexity:** {mp.complexity.value}
**Priority:** {mp.priority.value}
**Budget ceiling:** ${mp.budget_ceiling_usd}
**Timeout:** {mp.timeout_minutes} min
**Created:** {mp.created_at}

## Blast Radius Declaration
- **Archivos declarados:**
{chr(10).join(f'  - `{f}`' for f in mp.blast_radius.files_declared)}
- **Líneas estimadas:** {mp.blast_radius.estimated_lines_changed}
- **Scope creep máximo:** {mp.blast_radius.max_scope_creep_percent}%

## Impact Surface
- **Code:** {', '.join(mp.impact_surface.code) or 'N/A'}
- **Contracts:** {', '.join(mp.impact_surface.contracts) or 'N/A'}
- **Tests:** {', '.join(mp.impact_surface.tests) or 'N/A'}
- **Migrations:** {', '.join(mp.impact_surface.migrations) or 'N/A'}
- **Security:** {'✅' if mp.impact_surface.security else '❌'}
- **Billing:** {'✅' if mp.impact_surface.billing else '❌'}
- **Tenancy:** {'✅' if mp.impact_surface.tenancy else '❌'}

## Dependencias
{chr(10).join(f'- {d}' for d in mp.dependencies) or 'Ninguna'}

## Objetivo
[Describir exactamente qué debe implementarse]

## Archivos permitidos
{chr(10).join(f'- `{f}`' for f in mp.blast_radius.files_declared)}

## Archivos prohibidos
- secrets
- prod config
- contratos no relacionados
- billing/auth/tenancy fuera de scope

## Contexto obligatorio
- PRD: [ref]
- ADR: [ref]
- API contract: [ref]
- Data model: [ref]
- Test plan: [ref]
- Data classification: `/docs/architecture/data-classification.yaml`

## Invariantes globales aplicables
- INV-001: Ninguna query sin tenant_id
- INV-008: Ningún secreto en repo/logs
- INV-012: Ningún PII en logs
- INV-016: Sanitization Gateway para LLMs externos
{self._risk_specific_invariants(mp.risk_class)}

## Tareas
1.
2.
3.

## Tests obligatorios
- Unit:
- Integration:
- Contract (si API):
- Tenant isolation (si tenancy):
- Security (si aplica):
- Mutation (si R2/R3):

## Semantic Drift Budget
- Umbral de similitud coseno: 0.85
- PRD reference: [hash]

## Enforcement Verifier Requirements
- Invariantes a verificar PASS al final: [lista]

## Definition of Done
- Tests pasan
- Lint/typecheck pasan
- No scope creep (blast radius gate PASS)
- Semantic drift > 0.85
- Enforcement Verifier PASS
- No secretos/PII
- Context summary generado
- Critic review listo
"""

    @staticmethod
    def _risk_specific_invariants(risk: RiskClass) -> str:
        if risk == RiskClass.R3:
            return (
                "- INV-003: Webhooks verifican firma\n"
                "- INV-004: Idempotencia en eventos\n"
                "- INV-009: Billing tests antes de deploy\n"
                "- INV-020: Shadow testing para billing changes"
            )
        if risk == RiskClass.R2:
            return "- INV-006: AuthZ en endpoints mutantes"
        return ""

    @staticmethod
    def _from_dict(data: Dict) -> MicroPromptMetadata:
        br = data.get("blast_radius", {})
        impact = data.get("impact_surface", {})
        return MicroPromptMetadata(
            id=data["id"],
            title=data["title"],
            maturity=MaturityLevel(data["maturity"]),
            risk_class=RiskClass(data["risk_class"]),
            complexity=Complexity(data["complexity"]),
            priority=Priority(data["priority"]),
            dependencies=data.get("dependencies", []),
            timeout_minutes=data.get("timeout_minutes", 30),
            budget_ceiling_usd=data.get("budget_ceiling_usd", 2.0),
            blast_radius=BlastRadius(
                files_declared=br.get("files_declared", []),
                estimated_lines_changed=br.get("estimated_lines_changed", 0),
                max_scope_creep_percent=br.get("max_scope_creep_percent", 10.0),
            ),
            impact_surface=ImpactSurface(
                code=impact.get("code", []),
                contracts=impact.get("contracts", []),
                tests=impact.get("tests", []),
                migrations=impact.get("migrations", []),
                security=impact.get("security", False),
                billing=impact.get("billing", False),
                tenancy=impact.get("tenancy", False),
            ),
            pr_number=data.get("pr_number"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            status=data.get("status", "draft"),
        )


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--maturity", choices=["M1", "M2", "M3"], default="M1")
    p_create.add_argument("--risk", choices=["R0", "R1", "R2", "R3"], default="R1")
    p_create.add_argument("--files", nargs="+", required=True)
    p_create.add_argument("--lines", type=int, default=50)

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("--id", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("--status", default="draft")

    args = parser.parse_args()
    manager = MicroPromptManager()

    if args.cmd == "create":
        path = manager.create(
            title=args.title,
            maturity=MaturityLevel(args.maturity),
            risk_class=RiskClass(args.risk),
            files=args.files,
            estimated_lines=args.lines,
        )
        print(f"✅ Creado: {path}")
    elif args.cmd == "validate":
        errors = manager.validate(args.id)
        if errors:
            print(f"❌ {len(errors)} errores:")
            for e in errors:
                print(f"  - {e}")
            raise SystemExit(1)
        print("✅ Validación PASS")
    elif args.cmd == "list":
        for mp in manager.list_by_status(args.status):
            print(f"{mp.id} [{mp.risk_class.value}] {mp.title}")
