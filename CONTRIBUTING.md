# Contributing to CenitForge

Thanks for your interest in CenitForge.

CenitForge is currently a **developer-preview framework and executable template seed**. Contributions should help close the gap between the documented target architecture and the executable developer experience.

## Contribution priorities

Highest priority:

1. Tests for existing sentinel seeds.
2. A reliable `make smoke` / demo loop.
3. Clearer docs that distinguish current state from target state.
4. CI examples that run the sentinels.
5. Safer defaults for generated projects.

Lower priority for now:

- new long-form methodology docs;
- new theoretical guardrails without executable checks;
- production claims that are not backed by tests.

## Types of contributions

| Type | Process |
|---|---|
| Bug fix | Pull request with a regression test when possible |
| Documentation correction | Pull request directly |
| New sentinel/tool | Open an issue first |
| New invariant | RFC + executable preventive or detective check |
| Production claim | Must link to test, CI evidence, or runnable demo |

## Local development

```bash
git clone https://github.com/CenitLabs-mx/CenitForge.git
cd CenitForge
make install
make validate
make smoke
```

If you modify template Python files, run:

```bash
python3 -m py_compile templates/{{cookiecutter.project_slug}}/tools/enforcement_verifier.py
python3 -m py_compile templates/{{cookiecutter.project_slug}}/sanitization/gateway.py
python3 -m py_compile templates/{{cookiecutter.project_slug}}/ci/blast_radius_gate.py
python3 -m py_compile templates/{{cookiecutter.project_slug}}/tools/semantic_drift_detector.py
python3 -m py_compile templates/{{cookiecutter.project_slug}}/tests/shadow/shadow_safety_contract.py
```

## Definition of Done for code changes

A change is ready for review only if:

- `make validate` passes;
- `make smoke` passes;
- docs match the real behavior;
- new claims are backed by runnable code or clearly marked as roadmap;
- failures are explicit rather than hidden behind optimistic messages.

## Adding a new invariant

Every new invariant must include:

1. Name and risk mitigated.
2. Maturity level where it applies: M1, M2, or M3.
3. Preventive control, detective control, or both.
4. Test fixture that demonstrates a pass case.
5. Test fixture that demonstrates a fail case.
6. Documentation update.

A written rule without an executable control is not enough for an invariant.

## Documentation rules

Use these words carefully:

- Use **implemented** only when code exists and can be run.
- Use **seed implementation** when code exists but is not production-hardened.
- Use **planned** when the feature is target-state only.
- Avoid claims like `100% secure`, `zero drift`, `immune to regression`, or `production-ready` unless backed by tests and release evidence.

## Code of conduct

Be respectful, technical, and direct. Prefer evidence over hype.
