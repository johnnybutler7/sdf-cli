# Evidence

## Intent
Add concise Developer Preview guidance that directs first-time evaluators to an
isolated, reviewable Git context and preserves the explicit human decision
before committing, pushing, or opening a pull request.

## Review focus
Check that both onboarding routes present a disposable repository or clone as
the safest evaluation path, prefer a separate worktree for a real repository,
and retain manual use alongside the strengthened coding-agent prompt. Confirm
that the wording keeps `.sdf/verification.yml` and every Git publication step
under repository-owner and human control.

## Limits
Documentation only. It does not change CLI or `sdf init` behaviour, add Git
automation, alter packaged resources or verification configuration, or imply
that SDF is expected to damage repositories.

## Guidance applied
Applied the governed change loop, SDF CLI engineering discipline, product
maintenance, and verification guidance. The change remains a narrow,
reviewable documentation slice; configured closeout verification is the
delivery boundary.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "developer-preview-evaluation-safety"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/developer-preview-evaluation-safety"
  head: "a350649a70478706f1dde26699f686f539620a64"
run_context:
  surface: "codex_desktop"
  model: "GPT-5.6 / Terra"
  reasoning: "high"
  speed: "unknown"
started_at: "2026-07-24T17:19:46+00:00"
closed_at: "2026-07-24T17:21:48+00:00"
closeout_status: "passed"
verification:
  total_runs: 4
  failed_runs: 2
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 15.33
    checks:
      - name: "ruff"
        status: "passed"
        duration_seconds: 0.02
      - name: "python-module-size-audit"
        status: "passed"
        duration_seconds: 0.04
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
        duration_seconds: 0.06
      - name: "install-surface-smoke"
        status: "passed"
        duration_seconds: 2.45
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.54
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.32
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 6.68
```
