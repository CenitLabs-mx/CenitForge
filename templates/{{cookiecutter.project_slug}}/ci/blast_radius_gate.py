"""
Blast Radius Gate V5
Compara los archivos declarados en el micro-prompt con los archivos
realmente modificados en el PR. Bloquea si hay scope creep > umbral.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml


@dataclass
class BlastRadiusReport:
    pr_number: int
    micro_prompt_id: str
    declared_files: List[str] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    undeclared_files: List[str] = field(default_factory=list)
    scope_creep_count: int = 0
    scope_creep_percent: float = 0.0
    verdict: str = "PASS"  # PASS | FAIL
    max_allowed_percent: float = 10.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


def extract_pr_number_from_env() -> int:
    # GitHub Actions
    ref = os.environ.get("GITHUB_REF", "")
    m = re.search(r"refs/pull/(\d+)/", ref)
    if m:
        return int(m.group(1))
    # Fallback: argumento
    if len(sys.argv) > 1:
        return int(sys.argv[1])
    raise SystemExit("No se pudo determinar PR number")


def get_modified_files_in_pr(base_ref: str = "origin/main") -> Set[str]:
    """Obtiene archivos modificados vs rama base usando git diff."""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
            text=True,
        )
        return {line.strip() for line in out.splitlines() if line.strip()}
    except subprocess.CalledProcessError:
        # Fallback: diff contra HEAD~1
        out = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"], text=True,
        )
        return {line.strip() for line in out.splitlines() if line.strip()}


def find_micro_prompt_for_pr(pr_number: int, repo_root: Path) -> Optional[Dict]:
    """
    Busca el micro-prompt asociado al PR.
    Estrategia: parsear body del PR o buscar en docs/micro-prompts/ el más reciente.
    """
    mp_dir = repo_root / "docs" / "micro-prompts"
    if not mp_dir.exists():
        return None
    # Buscar por PR number en metadata
    for f in mp_dir.glob("*.yaml"):
        try:
            data = yaml.safe_load(f.read_text()) or {}
        except Exception:
            continue
        if data.get("pr_number") == pr_number:
            return data
    # Fallback: último modificado
    candidates = sorted(mp_dir.glob("*.yaml"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        return yaml.safe_load(candidates[0].read_text())
    return None


def evaluate_blast_radius(
    pr_number: int,
    declared: List[str],
    modified: Set[str],
    max_percent: float = 10.0,
) -> BlastRadiusReport:
    declared_set = set(declared)
    undeclared = sorted(modified - declared_set)

    total = len(modified) if modified else 1
    creep_percent = (len(undeclared) / total) * 100

    verdict = "PASS" if creep_percent <= max_percent else "FAIL"

    return BlastRadiusReport(
        pr_number=pr_number,
        micro_prompt_id="MP-unknown",
        declared_files=sorted(declared_set),
        modified_files=sorted(modified),
        undeclared_files=undeclared,
        scope_creep_count=len(undeclared),
        scope_creep_percent=round(creep_percent, 2),
        verdict=verdict,
        max_allowed_percent=max_percent,
    )


def format_pr_comment(report: BlastRadiusReport) -> str:
    if report.verdict == "PASS":
        return f"""## ✅ Blast Radius Gate PASS

- **Archivos declarados:** {len(report.declared_files)}
- **Archivos modificados:** {len(report.modified_files)}
- **Scope creep:** {report.scope_creep_percent}% (≤ {report.max_allowed_percent}%)
"""
    return f"""## ❌ Blast Radius Gate FAILED

**Scope Creep:** {report.scope_creep_count} archivos no declarados ({report.scope_creep_percent:.1f}%)

### Archivos no declarados:
{chr(10).join(f"- `{f}`" for f in report.undeclared_files)}

### Acción requerida:
1. Si los archivos eran necesarios, genera un **Architecture Change Request (ACR)**.
2. Si fue error, revierte los cambios no declarados.
3. Actualiza el micro-prompt con el nuevo blast radius.
4. Solicita re-review.
"""


def main() -> int:
    repo_root = Path.cwd()
    pr_number = extract_pr_number_from_env()
    modified = get_modified_files_in_pr()

    mp = find_micro_prompt_for_pr(pr_number, repo_root)
    if not mp:
        print("⚠️  No se encontró micro-prompt para este PR. Asumiendo todos los archivos como declarados.")
        declared = list(modified)
    else:
        declared = mp.get("blast_radius", {}).get("files_declared", [])

    max_percent = (mp or {}).get("blast_radius", {}).get("max_scope_creep_percent", 10.0)

    report = evaluate_blast_radius(pr_number, declared, modified, max_percent)

    # Guardar reporte
    out_path = Path("/tmp/blast_radius_report.json")
    out_path.write_text(json.dumps(asdict(report), indent=2))
    print(f"Reporte guardado en: {out_path}")

    # Imprimir comentario
    print(format_pr_comment(report))

    return 0 if report.verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
