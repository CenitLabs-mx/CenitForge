# Quickstart - CenitForge Developer Preview

This guide is intentionally conservative. It describes what the repository can do today, not the final production vision.

## Prerequisites

```bash
python3 --version   # 3.11+
git --version       # 2.30+
make --version      # GNU Make
```

Optional for project generation:

```bash
pipx --version      # recommended, not required
```

## Step 1: Clone the kit

```bash
git clone https://github.com/CenitLabs-mx/CenitForge.git
cd CenitForge
```

## Step 2: Install kit dependencies

```bash
make install
```

This creates a local virtual environment and installs the minimal dependencies needed by the kit tooling.

## Step 3: Validate kit structure

```bash
make validate
```

Expected result:

```text
Validation PASSED - Kit structure is complete for developer preview.
```

This command checks file presence only. It does **not** certify production readiness.

## Step 4: Run smoke checks

```bash
make smoke
```

Expected result:

```text
Sentinel seed files present
Python syntax checks passed
Sanitization smoke check passed
```

The smoke check verifies that the seed sentinel implementations inside the generated-project template are present and syntactically valid.

## Step 5: Generate a project

```bash
make new-project
```

Example answers:

```text
project_name [Mi SaaS B2B]: CenitBilling
initial_maturity (M1/M2/M3) [M1]: M1
primary_llm_provider [anthropic]: anthropic
has_billing [yes]: yes
has_multi_tenancy [yes]: yes
```

Then enter the generated project:

```bash
cd ../cenitbilling
make setup
```

## Step 6: Validate the generated project

The generated project contains seed guardrails under:

```text
tools/enforcement_verifier.py
sanitization/gateway.py
ci/blast_radius_gate.py
tools/semantic_drift_detector.py
tests/shadow/shadow_safety_contract.py
```

Run its validation command:

```bash
make validate
```

Depending on maturity level and local environment variables, some checks may fail or skip. That is expected for an early generated project. The purpose is to make missing controls visible, not to hide them.

## What this quickstart proves

It proves:

- the kit can be installed;
- the template structure exists;
- seed sentinel files are present;
- Python seed tools compile;
- basic sanitization behavior works;
- a new project can be generated.

It does **not** yet prove:

- production-grade CI/CD;
- full orchestrator integration;
- complete IaC provisioning;
- complete security coverage;
- compliance certification;
- zero context drift.

## Recommended next step

Open:

```bash
code docs/project-status.md
code docs/mvp-roadmap.md
```

Then implement the first real milestone: a signed enforcement report that intentionally blocks one unsafe condition.
