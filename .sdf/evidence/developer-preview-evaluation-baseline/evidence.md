# Evidence

## Intent
Make the public Developer Preview installation route non-invasive: it now
creates or safely reuses an `sdf-demo` evaluation baseline, installs on a
separate branch, and targets the draft installation PR at that baseline rather
than the receiver's configured default branch.

## Review focus
Check that the copyable prompt has the canonical guide URL and the required
branch relationship; that existing `sdf-demo` branches cannot be overwritten;
and that evaluation, later adoption, cleanup, and the human authority boundary
are unambiguous. Confirm the manual walkthrough retains flexible branch choice.

## Limits
Documentation and governed evidence only. This does not change CLI behaviour,
package version, GitHub defaults, release state, or the manual walkthrough's
disposable example mechanics. It does not create, push, merge, approve, deploy,
release, or delete any receiver-repository branch or pull request.

## Guidance applied
The governed change loop required evidence, configured closeout, and a checked
handoff. Engineering guidance kept the public-documents change focused and
reviewable. Product guidance kept the Developer Preview claims aligned with the
requested human-controlled evaluation boundary. Verification guidance retained
the configured verification boundary. The `portable-baseline-docs` evidence
archive provided bounded precedent for concise public non-claims and evidence.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "developer-preview-evaluation-baseline"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "main"
  head: "3d3f0afbfee90b8d28337b8a7268f4530458bc1a"
run_context:
  surface: "unknown"
  model: "unknown"
  reasoning: "unknown"
  speed: "unknown"
started_at: "2026-07-26T08:05:20+00:00"
closed_at: "2026-07-26T08:07:37+00:00"
closeout_status: "passed"
verification:
  total_runs: 2
  failed_runs: 1
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 15.90
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
        duration_seconds: 2.42
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.76
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.49
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 6.85
```
