# Evidence

## Intent
Clarify the governed-change lifecycle in `ARCHITECTURE.md`. The previous
diagram correctly showed the main path but omitted the explicit verification
retry loop; this documentation-only change makes that delivery feedback loop
visible without adding a capability or changing product/runtime behaviour.

## Review focus
Confirm the Mermaid diagram shows required verification flowing through a
pass/fail decision, with failures returning to a human or coding agent before
verification runs again. Confirm the adjacent prose preserves human ownership:
SDF records evidence and failed-run history but does not repair changes, CI is
the final enforcement boundary, and humans make merge decisions.

## Limits
No runtime code, tests, workflows, package metadata, version identity, README
content, or product behaviour changed. Failed-run history was already
implemented and recorded; this change improves presentation accuracy rather
than introducing automated repair, automatic retries, or a new capability.

## Guidance applied
The governed change loop shaped evidence and full closeout. Engineering guidance
kept the diagram and prose scoped to explicit ownership and human-controlled
boundaries; verification guidance retained the receiver-owned configured
boundary. No implementation-specific guidance materially shaped this
documentation-only correction.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "architecture-verification-feedback-loop"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/verification-feedback-loop"
  head: "2b5834594cb0822736212cb6de540b791ba9c157"
run_context:
  surface: "codex_local"
  model: "GPT-5.6 Terra"
  reasoning: "medium"
  speed: "standard"
started_at: "2026-07-23T14:55:37+00:00"
closed_at: "2026-07-23T14:59:09+00:00"
closeout_status: "passed"
verification:
  total_runs: 7
  failed_runs: 6
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 14.53
    checks:
      - name: "ruff"
        status: "passed"
        duration_seconds: 0.04
      - name: "python-module-size-audit"
        status: "passed"
        duration_seconds: 0.05
      - name: "documented-sdf-command-consistency"
        status: "passed"
        duration_seconds: 0.05
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
        duration_seconds: 2.11
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.29
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.03
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 6.76
```
