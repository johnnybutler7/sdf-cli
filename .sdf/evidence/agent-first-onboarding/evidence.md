# Evidence

## Intent
Make SDF's public onboarding explicitly agent-first: the repository owner sets
the local acceptance boundary, the coding agent performs routine governed
closeout, and the human reviewer retains acceptance decisions.

## Review focus
Check that README and Getting Started prompts are copyable and distinguish
installation from ordinary governed work; that manual commands are secondary;
and that packaged receiver guidance—not only this repository's copy—assigns
routine execution to the coding agent without weakening non-destructive init or
human review boundaries.

## Limits
Documentation, portable guidance, and related tests only. It does not change
CLI behaviour, installation ownership, package/version, verification contract,
third-party agent integration, release publication, or approval/merge control.

## Guidance applied
Applied the portable governed-change loop; SDF CLI engineering discipline;
Python CLI design guidance for packaged resources and contract tests; product
maintenance for claims; and verification guidance. No prior evidence was
consulted because historical archives are intentionally absent from this
baseline.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "agent-first-onboarding"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/agent-first-onboarding"
  head: "549abd0ed486928226f840c75df2e113aff45fcf"
run_context:
  surface: "codex_local"
  model: "GPT-5.6-Terra"
  reasoning: "high"
  speed: "standard"
started_at: "2026-07-24T14:42:31+00:00"
closed_at: "2026-07-24T14:47:50+00:00"
closeout_status: "passed"
verification:
  total_runs: 5
  failed_runs: 4
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 17.41
    checks:
      - name: "ruff"
        status: "passed"
        duration_seconds: 0.05
      - name: "python-module-size-audit"
        status: "passed"
        duration_seconds: 0.05
      - name: "documented-sdf-command-consistency"
        status: "passed"
        duration_seconds: 0.06
      - name: "cli-help"
        status: "passed"
        duration_seconds: 0.06
      - name: "cli-version"
        status: "passed"
        duration_seconds: 0.06
      - name: "status-current-repo"
        status: "passed"
        duration_seconds: 0.06
      - name: "guidance-current-repo"
        status: "passed"
        duration_seconds: 0.06
      - name: "install-surface-smoke"
        status: "passed"
        duration_seconds: 2.59
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.81
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.54
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 8.08
```
