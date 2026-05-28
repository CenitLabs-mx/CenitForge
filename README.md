# CenitForge

> **Developer Preview:** executable seed kit for auditable AI-agent software engineering.

CenitForge is an open-source framework and project template for building AI-assisted software delivery pipelines with explicit guardrails: invariant checks, sanitization, blast-radius control, shadow safety, and audit-ready documentation.

The current repository is **not yet a production platform**. It is a **developer-preview blueprint plus executable template seed**. The strongest value today is that it packages the operating model, documentation structure, and first working guardrail implementations that generated projects can evolve into a full production-grade system.

---

## Current status

| Area | Status | Notes |
|---|---|---|
| Master methodology | Implemented as documentation | See `docs/plan-maestro-v5.md`. |
| Cookiecutter project generator | Implemented | Generates a project from `templates/{{cookiecutter.project_slug}}/`. |
| Enforcement Verifier | Seed implementation | Lives inside the generated-project template. |
| Sanitization Gateway | Seed implementation | Lives inside the generated-project template. |
| Shadow Safety Contract | Seed implementation | Lives inside the generated-project template. |
| Blast Radius Gate | Seed implementation | Lives inside the generated-project template. |
| Semantic Drift Detector | Seed implementation | Lives inside the generated-project template. |
| End-to-end production CI | Not complete | Roadmap item; current CI/validation is structural and smoke-level. |
| Full production orchestrator | Not complete | M1 uses checklist/git workflow; M3 orchestrator is planned. |
| Release packaging | Not complete | First target is `v0.1.0-developer-preview`. |

The project intentionally separates **what is already executable** from **what remains a target-state control**. For the detailed implementation status, see [`docs/project-status.md`](docs/project-status.md).

---

## The problem CenitForge addresses

AI coding agents can implement changes quickly, but speed alone creates risk:

```text
Prompt -> AI agent -> code changes -> possible scope creep, weak tests, secrets, tenant leaks, billing mistakes
```

CenitForge aims to convert that workflow into a more auditable production line:

```text
PRD + contracts -> micro-prompt -> sandboxed execution -> guardrail checks -> signed report -> human/CI gate
```

The goal is not to promise perfect safety. The goal is to **reduce architectural drift and make risky agentic changes observable, testable, and reviewable**.

---

## The five sentinel guardrails

The following components are currently provided as **seed implementations inside the generated project template**, not as root-level installed package modules yet:

| Sentinel | Template path | Current maturity |
|---|---|---|
| Programmatic Invariant Verification | `templates/{{cookiecutter.project_slug}}/tools/enforcement_verifier.py` | Seed implementation |
| Sanitization Gateway | `templates/{{cookiecutter.project_slug}}/sanitization/gateway.py` | Seed implementation |
| Shadow Safety Contract | `templates/{{cookiecutter.project_slug}}/tests/shadow/shadow_safety_contract.py` | Seed implementation |
| Blast Radius Gate | `templates/{{cookiecutter.project_slug}}/ci/blast_radius_gate.py` | Seed implementation |
| Semantic Drift Detector | `templates/{{cookiecutter.project_slug}}/tools/semantic_drift_detector.py` | Seed implementation |

Planned package layout for later releases:

```text
cenitforge/
  enforcement/
  sanitization/
  shadow/
  blast_radius/
  drift/
```

Until that package layout exists, documentation should refer to the template paths above.

---

## What you can do today

You can:

1. Validate the kit structure.
2. Generate a parameterized project template.
3. Inspect and adapt the seed guardrails.
4. Run smoke checks that verify the sentinel seed files exist and compile.
5. Use the methodology and templates to run an M1/M2 implementation cycle.

You should not yet assume:

- turnkey production deployment;
- complete CI/CD enforcement;
- complete security coverage;
- complete Terraform/IaC implementation;
- complete orchestrator integration;
- zero context drift;
- automatic compliance certification.

---

## Quickstart

```bash
git clone https://github.com/CenitLabs-mx/CenitForge.git
cd CenitForge
make install
make validate
make smoke
make new-project
```

`make validate` checks the repository structure and the presence of critical kit files.

`make smoke` verifies that the current developer-preview sentinel seed files are present and syntactically valid. It also runs a minimal sanitization smoke check.

After `make new-project`, the generated project will contain the executable seed guardrails under its own `tools/`, `sanitization/`, `ci/`, and `tests/` folders.

See [`QUICKSTART.md`](QUICKSTART.md) for the step-by-step flow.

---

## Repository structure

```text
.
├── README.md
├── QUICKSTART.md
├── CONTRIBUTING.md
├── Makefile
├── cookiecutter.json
├── docs/
│   ├── plan-maestro-v5.md
│   ├── project-status.md
│   └── mvp-roadmap.md
├── scripts/
│   ├── validate-kit.sh
│   ├── validate_kit.py
│   ├── smoke-demo.sh
│   └── new-project.sh
└── templates/
    └── {{cookiecutter.project_slug}}/
        ├── tools/
        ├── sanitization/
        ├── ci/
        ├── tests/
        └── docs/
```

---

## Roadmap

The immediate priority is not more documentation. The immediate priority is proving the smallest useful loop:

```text
Generate project -> run sentinel smoke checks -> produce signed report -> block one unsafe condition -> document result
```

See [`docs/mvp-roadmap.md`](docs/mvp-roadmap.md).

---

## Contributing

CenitForge is released under the MIT License. Contributions are welcome, especially in these areas:

- unit tests for existing sentinels;
- improved sanitization detection;
- stronger invariant checks;
- CI integration examples;
- sample generated projects;
- documentation that clearly separates current state from target state.

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request.

---

## Positioning statement

CenitForge is currently best described as:

> A developer-preview framework and executable project-template seed for building auditable AI-agent software delivery pipelines.

It is **not yet** a fully packaged production platform. That is the roadmap.
