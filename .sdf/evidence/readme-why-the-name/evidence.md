# Evidence

## Intent
Add a brief README note explaining the origin of the SDF name and linking to the founder memo.

## Review focus
Confirm the note appears immediately before "The governed change loop" and that its wording and destination match the requested copy.

## Limits
Documentation and governed evidence only; no CLI behavior, configuration, release state, or authority boundary changes.

## Guidance applied
The governed change loop required a scoped evidence archive, configured closeout, and checked handoff. Product and verification guidance kept the documentation claim aligned with the implemented governance boundary.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "readme-why-the-name"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/readme-why-the-name"
  head: "036d45a9e574914a2a9ce8861de5f60825b26152"
run_context:
  surface: "codex_desktop"
  model: "gpt-5.6"
  reasoning: "medium"
  speed: "standard"
started_at: "2026-07-27T07:47:09+00:00"
closed_at: "2026-07-27T07:48:23+00:00"
closeout_status: "passed"
verification:
  total_runs: 2
  failed_runs: 1
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 16.18
    checks:
      - name: "ruff"
        status: "passed"
        duration_seconds: 0.05
      - name: "python-module-size-audit"
        status: "passed"
        duration_seconds: 0.06
      - name: "documented-sdf-command-consistency"
        status: "passed"
        duration_seconds: 0.07
      - name: "cli-help"
        status: "passed"
        duration_seconds: 0.05
      - name: "cli-version"
        status: "passed"
        duration_seconds: 0.06
      - name: "status-current-repo"
        status: "passed"
        duration_seconds: 0.06
      - name: "guidance-current-repo"
        status: "passed"
        duration_seconds: 0.07
      - name: "install-surface-smoke"
        status: "passed"
        duration_seconds: 2.52
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 3.00
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.47
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 6.77
```
