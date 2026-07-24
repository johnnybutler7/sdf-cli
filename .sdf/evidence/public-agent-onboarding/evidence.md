# Evidence

## Intent
Correct stale pre-release onboarding wording by making
`pipx install software-dark-factory` the clear ordinary installation route.
Add an optional agent-assisted route while retaining the documented manual
commands as the canonical, inspectable path, and clarify the reviewable
artefacts produced by the first governed-change walkthrough.

## Review focus
Check that `pipx install software-dark-factory` is the ordinary installation
route; editable installation is clearly contributor-only; and the optional
agent path keeps repository owners responsible for defining and reviewing
`.sdf/verification.yml`. Confirm the copy preserves the portable-baseline,
human-review, approval, and merge boundaries without suggesting that SDF or an
agent acts autonomously.

## Limits
Public documentation only. No CLI or command behaviour, package metadata,
packaged or scaffolded receiver resource, `.sdf` product template, release
artefact, verification configuration, or human review control changed.

## Guidance applied
The governed-change loop required this evidence, configured closeout, and
checked reviewer handoff. Engineering guidance kept the documentation slice
small and reviewable; product guidance kept claims aligned with the released
package and its non-claims; and verification guidance set the configured
closeout boundary. The `readme-agentic-acceptance-boundary` archive provided
bounded precedent for retaining the human-review and non-autonomy language.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "public-agent-onboarding"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/public-agent-onboarding"
  head: "c9549498af40d25ca8a4e0f109b00570c84924a4"
run_context:
  surface: "Codex"
  model: "GPT-5.6 / Terra"
  reasoning: "High"
  speed: "unknown"
started_at: "2026-07-24T16:03:44+00:00"
closed_at: "2026-07-24T16:07:31+00:00"
closeout_status: "passed"
verification:
  total_runs: 7
  failed_runs: 5
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 15.49
    checks:
      - name: "ruff"
        status: "passed"
        duration_seconds: 0.03
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
        duration_seconds: 0.05
      - name: "install-surface-smoke"
        status: "passed"
        duration_seconds: 2.51
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.54
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.30
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 6.81
```
