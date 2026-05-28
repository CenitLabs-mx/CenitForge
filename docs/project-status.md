# CenitForge Project Status

CenitForge is currently in **developer preview**.

This document separates current executable capabilities from target-state architecture.

## Status legend

| Status | Meaning |
|---|---|
| Implemented | Code exists and can run today. |
| Seed implementation | Code exists but is not production-hardened. |
| Structural | File/template exists, but behavior is not fully enforced. |
| Planned | Documented target-state; not implemented yet. |

## Current capabilities

| Capability | Status | Location | Notes |
|---|---|---|---|
| Kit validation | Implemented | `scripts/validate-kit.sh`, `scripts/validate_kit.py` | Structural validation only. |
| Project generation | Implemented | `cookiecutter.json`, `templates/` | Generates a project scaffold. |
| Enforcement Verifier | Seed implementation | `templates/{{cookiecutter.project_slug}}/tools/enforcement_verifier.py` | Needs tests and CI wiring. |
| Sanitization Gateway | Seed implementation | `templates/{{cookiecutter.project_slug}}/sanitization/gateway.py` | Regex/classification based; not a complete DLP system. |
| Shadow Safety Contract | Seed implementation | `templates/{{cookiecutter.project_slug}}/tests/shadow/shadow_safety_contract.py` | Useful test harness seed; needs real service adapters. |
| Blast Radius Gate | Seed implementation | `templates/{{cookiecutter.project_slug}}/ci/blast_radius_gate.py` | Needs GitHub Actions integration and fixtures. |
| Semantic Drift Detector | Seed implementation | `templates/{{cookiecutter.project_slug}}/tools/semantic_drift_detector.py` | Optional dependencies; threshold needs calibration. |
| Training docs | Structural | `docs/training/` | Useful onboarding material, not executable control. |
| Production orchestrator | Planned | `orchestrator/` target-state | Not yet implemented as a full Temporal/Airflow workflow. |
| Root package / CLI | Planned | `cenitforge/` target-state | Not yet packaged. |
| Full release CI | Planned | `.github/workflows/` target-state | Current validation is not full production CI. |

## Known gaps

1. Root README previously described generated-template files as if they were root-level files.
2. Quickstart output previously overstated hash verification and production readiness.
3. Tests for sentinel seed implementations are still insufficient.
4. End-to-end demo needs to be made the main proof point.
5. M3 controls need stronger enforcement before any production claim.
6. The generated project may intentionally fail some M3 checks until users configure DB, Vault, sandbox network, and CI.

## Near-term target

The next milestone is `v0.1.0-developer-preview`.

Acceptance criteria:

- `make validate` passes from a clean clone.
- `make smoke` passes from a clean clone.
- `make new-project` generates a project.
- Generated project runs at least one enforcement check.
- Sanitizer blocks or redacts a known unsafe payload.
- Basic unit tests exist for at least three sentinels.
- README and QUICKSTART do not overclaim production readiness.
