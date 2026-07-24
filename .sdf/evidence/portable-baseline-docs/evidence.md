# Evidence

## Intent
Clarify the public 0.1.0 documentation: SDF is the portable baseline for a
governed-change loop, while each receiver repository owns the extensions that
make that loop fit its engineering and delivery context. Correct stale
pre-release installation and public-project wording, and label this project's
playbooks as examples rather than universal standards.

## Review focus
Confirm the README distinguishes the base Developer Preview from
receiver-owned extensions without claiming optional capabilities as packaged
0.1.0 behaviour. Check that retained evidence, analysis, and learning examples
are explicitly receiver-specific and human-reviewed where appropriate; that
SDF remains non-autonomous for standards and approval; and that PyPI,
installation, playbook, and contributing wording is current and consistent.

## Limits
Documentation only: no runtime code, package version, release artifact,
verification command, automatic accounting, retrieval, learning, playbook
creation, approval, repair, merge, or external-adoption claim changes. The
optional-extension examples are not automatically enabled or guaranteed by
SDF 0.1.0. Standard non-claims remain in
`.sdf/standard-sdf-non-claims.md`.

## Guidance applied
The governed change loop required evidence, configured closeout, and a checked
reviewer handoff. Engineering guidance kept this a focused, reviewable
documentation slice. Product guidance kept public claims aligned with current
behaviour, and verification guidance retained the configured boundary. The
`public-architecture-presentation` evidence archive provided bounded precedent
for public ownership and non-claim wording. Python implementation and learning
guidance did not materially shape this documentation-only slice.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "portable-baseline-docs"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/portable-baseline-docs"
  head: "6cf42b719dcdbf54389b31816a41df12f2031249"
run_context:
  surface: "unknown"
  model: "unknown"
  reasoning: "unknown"
  speed: "unknown"
started_at: "2026-07-24T13:12:26+00:00"
closed_at: "2026-07-24T13:15:35+00:00"
closeout_status: "passed"
verification:
  total_runs: 4
  failed_runs: 3
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 16.45
    checks:
      - name: "ruff"
        status: "passed"
        duration_seconds: 0.05
      - name: "python-module-size-audit"
        status: "passed"
        duration_seconds: 0.06
      - name: "documented-sdf-command-consistency"
        status: "passed"
        duration_seconds: 0.06
      - name: "cli-help"
        status: "passed"
        duration_seconds: 0.05
      - name: "cli-version"
        status: "passed"
        duration_seconds: 0.05
      - name: "status-current-repo"
        status: "passed"
        duration_seconds: 0.05
      - name: "guidance-current-repo"
        status: "passed"
        duration_seconds: 0.05
      - name: "install-surface-smoke"
        status: "passed"
        duration_seconds: 2.50
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.59
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.28
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 7.70
```
