# CenitForge MVP Roadmap

The priority is to move from an excellent blueprint to a small, repeatable, executable proof.

## Milestone 0: Documentation truth alignment

Status: immediate.

Goals:

- README reflects developer-preview scope.
- Quickstart commands match actual behavior.
- Project status page separates implemented, seed, and planned work.
- Claims like production-ready, zero drift, and absolute safety are removed or qualified.

## Milestone 1: Smoke demo

Goal: one command proves the seed guardrails exist and run.

Command:

```bash
make smoke
```

Acceptance criteria:

- sentinel seed files exist;
- Python syntax checks pass;
- sanitizer smoke input is processed;
- output is deterministic enough for CI;
- failures are explicit.

## Milestone 2: Sentinel unit tests

Goal: make quality visible.

Minimum tests:

```text
tests/test_sanitization_gateway.py
  - redacts email
  - blocks API key

tests/test_enforcement_verifier.py
  - signs report
  - blocks missing required control in strict mode

tests/test_blast_radius_gate.py
  - passes declared files
  - fails undeclared files

tests/test_shadow_safety_contract.py
  - intercepts simulated outbound call
```

## Milestone 3: Generated project E2E

Goal: prove the generated project can run its own minimal checks.

Acceptance criteria:

```bash
make new-project
cd ../generated_project
make setup
make validate
```

The validation can fail missing production controls in M3, but M1 should have a clean path with seed controls.

## Milestone 4: Signed report artifact

Goal: produce a tangible artifact.

Output:

```text
reports/enforcement_report.json
```

It must include:

- phase;
- maturity;
- invariant results;
- verdict;
- HMAC signature;
- timestamp.

## Milestone 5: CI integration

Goal: GitHub Actions runs validation and smoke checks on every PR.

Acceptance criteria:

- `make validate` in CI;
- `make smoke` in CI;
- artifact upload for smoke report;
- failing sentinel check blocks PR.

## Milestone 6: v0.1.0-developer-preview release

Release scope:

- clear README;
- working quickstart;
- smoke demo;
- first sentinel tests;
- generated project template;
- status and roadmap docs;
- no production-readiness claims.
