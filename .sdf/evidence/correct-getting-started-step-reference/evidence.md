# Evidence

## Intent
Correct the released-package installation instructions so their Python
selection cross-reference matches the workflow numbering after the Developer
Preview evaluation-baseline steps were added.

## Review focus
Confirm the installation section now points to step 5, the Python-selection
step, and that the full guide contains no other stale numbered-step references.

## Limits
Documentation and governed evidence only. This does not alter the installation
workflow, CLI behaviour, package release, verification configuration, or PR
status.

## Guidance applied
The governed change loop required evidence and configured closeout. Engineering
guidance kept the correction limited to its user-facing contract. Product
guidance preserved accurate public operational instructions, and verification
guidance retained the configured repository boundary. No prior evidence was
needed for this straightforward documentation correction.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "correct-getting-started-step-reference"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/isolated-sdf-evaluation-baseline"
  head: "2f8563c5855ef5c6ce12c54b0a6c818f3f6d689d"
run_context:
  surface: "unknown"
  model: "unknown"
  reasoning: "unknown"
  speed: "unknown"
started_at: "2026-07-26T08:11:43+00:00"
closed_at: "2026-07-26T08:12:17+00:00"
closeout_status: "passed"
verification:
  total_runs: 1
  failed_runs: 0
  final_pass_followed_earlier_failure: false
  latest_run:
    status: "passed"
    total_duration_seconds: 16.10
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
        duration_seconds: 2.62
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.86
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.49
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 6.76
```
