# Evidence

## Intent
Update the public README's opening and problem statement so they explain why
SDF exists: faster, more varied AI-assisted changes need a repository-defined,
executable acceptance boundary and an evidence-backed human reviewer handoff.

## Review focus
Check that the README presents the requested causal chain accurately, retains
the executable-verification-loop definition, and clearly preserves human
acceptance decisions without becoming a founder story or duplicating the
long-form Why SDF material.

## Limits
Documentation only. It does not change CLI behaviour, the repository's
verification boundary, SDF's non-claims, or the separate long-form website
content.

## Guidance applied
The governed-change loop required this archive and configured closeout. The
engineering playbook kept the change small and reviewable. Product guidance
kept operational and non-claim wording aligned with the implemented CLI, and
the verification guidance set the configured closeout boundary.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "readme-agentic-acceptance-boundary"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "main"
  head: "935cc5a148c838e0a317580b83a074487829760b"
run_context:
  surface: "unknown"
  model: "unknown"
  reasoning: "unknown"
  speed: "unknown"
started_at: "2026-07-24T14:09:47+00:00"
closed_at: "2026-07-24T14:11:12+00:00"
closeout_status: "passed"
verification:
  total_runs: 3
  failed_runs: 2
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 15.01
    checks:
      - name: "ruff"
        status: "passed"
        duration_seconds: 0.37
      - name: "python-module-size-audit"
        status: "passed"
        duration_seconds: 0.06
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
        duration_seconds: 2.17
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.33
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.15
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 6.69
```
