# Evidence

## Intent
Clarify that a disposable clone may be removed through the operating system,
while a linked Git worktree should be removed through normal Git worktree
cleanup so its repository metadata is retained correctly.

## Review focus
Confirm that the cleanup guidance distinguishes disposable clones from linked
worktrees without prescribing destructive Git commands, and that dedicated
branch cleanup remains subject to ordinary Git review.

## Limits
Documentation only. It does not change Git, CLI, or `sdf init` behaviour, add
worktree automation, or alter packaged resources or verification configuration.

## Guidance applied
Applied the governed change loop, SDF CLI engineering discipline, product
maintenance, and verification guidance. The narrow wording change keeps Git
cleanup under explicit human control.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "linked-worktree-cleanup-guidance"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/developer-preview-evaluation-safety"
  head: "9a5e2fb4afc828d2e0a7f5edebd7edd33fe0bcf5"
run_context:
  surface: "codex_desktop"
  model: "GPT-5.6 / Terra"
  reasoning: "high"
  speed: "unknown"
started_at: "2026-07-24T17:25:16+00:00"
closed_at: "2026-07-24T17:25:50+00:00"
closeout_status: "passed"
verification:
  total_runs: 1
  failed_runs: 0
  final_pass_followed_earlier_failure: false
  latest_run:
    status: "passed"
    total_duration_seconds: 16.51
    checks:
      - name: "ruff"
        status: "passed"
        duration_seconds: 0.07
      - name: "python-module-size-audit"
        status: "passed"
        duration_seconds: 0.06
      - name: "documented-sdf-command-consistency"
        status: "passed"
        duration_seconds: 0.08
      - name: "cli-help"
        status: "passed"
        duration_seconds: 0.06
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
        duration_seconds: 2.64
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.91
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.60
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 6.93
```
