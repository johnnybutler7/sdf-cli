# Evidence

## Intent
The previous guide mixed uncommitted installation review, a future governed
change, fallback detail, and uncertainty about committing or opening a PR.
Replace `GETTING-STARTED.md` with the deterministic journey: point an agent at
the guide, receive a verified draft installation PR, and stop for human review.
Move the disposable example to `docs/MANUAL-WALKTHROUGH.md` and align the
small public entry-point copy in `README.md`.

## Review focus
Check that the agent authority boundary is unambiguous, installation stops at a
draft PR, and setup is separated from the first governed application change.
Confirm the pinned PyPI instructions and manual walkthrough remain accurate.
PyPI's live package metadata independently confirmed
`software-dark-factory` 0.1.0. No release-source fallback is documented because
PyPI is available and the official v0.1.0 GitHub release has no attached
distribution assets; the guide stops instead of improvising if documented
routes fail.

## Limits
Documentation only. It does not change CLI behaviour, generated Front Door
files, verification semantics, packaging, release state, or human approval,
merge, deployment, and release authority. The manual walkthrough remains an
optional, version-specific example rather than the normal onboarding path.

## Guidance applied
Applied `.sdf/agent-instructions.md`, the governed-change loop, SDF CLI
engineering discipline, and product guidance. The receiver exercise supplied
the ambiguity and final-response requirements. In addition to configured
closeout verification, relative links, documented SDF command consistency, and
GitHub-flavoured Markdown structure were checked directly.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "agent-led-getting-started"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/agent-led-getting-started"
  head: "53079454b1c9b01d20df2d722fe157016de9faac"
run_context:
  surface: "unknown"
  model: "unknown"
  reasoning: "unknown"
  speed: "unknown"
started_at: "2026-07-26T07:13:17+00:00"
closed_at: "2026-07-26T07:17:26+00:00"
closeout_status: "passed"
verification:
  total_runs: 2
  failed_runs: 1
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 16.07
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
        duration_seconds: 2.47
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.72
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.44
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 7.07
```
