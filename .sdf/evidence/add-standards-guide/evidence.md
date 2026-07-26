# Evidence

## Intent
Add an optional, agent-led standards-mapping journey after SDF installation so
teams can route their own focused engineering guidance into governed work.

## Review focus
- The guide keeps the portable SDF loop distinct from repository-owned
  standards and does not present SDF CLI's examples as universal guidance.
- Installation still stops after its draft PR; standards mapping is optional,
  separate, and bounded to a draft PR against the current baseline.
- The SDF CLI configuration example and canonical GitHub links are accurate.

## Limits
Documentation and governed evidence only. It does not change CLI behaviour,
generated Front Door files, verification semantics, package or release state,
repository settings, or automatic playbook generation; it does not approve or
merge a pull request.

## Guidance applied
- `.sdf/playbooks/governed-change-loop.md` shaped evidence, closeout, and draft
  PR handoff.
- `docs/playbooks/engineering/README.md` kept the documentation change focused
  and reviewable.
- `docs/product/README.md` kept public claims aligned with the existing CLI
  boundary.
- `docs/verification/README.md` and `.sdf/verification.yml` define the
  configured verification closeout.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "add-standards-guide"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/add-standards-guide"
  head: "7ee477c3a18f62da7e1dc571063717b43727e253"
run_context:
  surface: "codex_local"
  model: "GPT-5.6 Terra"
  reasoning: "High"
  speed: "fast"
started_at: "2026-07-26T13:32:15+00:00"
closed_at: "2026-07-26T13:34:29+00:00"
closeout_status: "passed"
verification:
  total_runs: 2
  failed_runs: 1
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 16.96
    checks:
      - name: "ruff"
        status: "passed"
        duration_seconds: 0.05
      - name: "python-module-size-audit"
        status: "passed"
        duration_seconds: 0.04
      - name: "documented-sdf-command-consistency"
        status: "passed"
        duration_seconds: 0.07
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
        duration_seconds: 2.69
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.91
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.55
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 7.43
```
