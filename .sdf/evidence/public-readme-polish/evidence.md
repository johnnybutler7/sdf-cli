# Evidence

## Intent
Make the public README explain the local, governed SDF loop and its reviewable
outputs within a short first read; add the requested repository homepage and
focused search topics without changing the Developer Preview evaluation model.
Clarify that publication workflows execute trusted default-branch code rather
than untrusted PR-head code, protecting repository credentials.

## Review focus
Confirm the opening claims match the released 0.1.0 package and its local
boundary; the CI badge targets the real `ci.yml` workflow; the `sdf close`
example is captured from the stable executable; and the receiver proof links
the Go installation, subsequent governed change, and committed evidence.
Confirm the publication-workflow explanation accurately states the trusted-code
boundary and does not broaden SDF's authority claims.

## Limits
This changes public documentation and the repository homepage/topics only. It
does not change CLI behaviour, package or release metadata, installed Front
Door contents, verification policy, CI configuration, or approval and merge
authority. It does not establish correctness, security, production readiness,
or remote CI confidence beyond the recorded closeout.

## Guidance applied
The governed change loop required this evidence and configured closeout.
Engineering guidance kept the public polish pass focused; product guidance kept
the local, Developer Preview, and human-authority claims aligned with the
product boundary; and verification guidance retained the configured closeout.
Engineering guidance kept the workflow-security explanation specific to the
trusted default-branch execution boundary.
The `developer-preview-evaluation-baseline` archive was consulted as bounded
precedent for a concise, committed example showing retained failed verification
history before a final pass.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "public-readme-polish"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/public-readme-polish"
  head: "79d0401640cb68d63d7fa20858a490f1c9baab53"
run_context:
  surface: "unknown"
  model: "unknown"
  reasoning: "unknown"
  speed: "unknown"
started_at: "2026-07-26T15:11:06+00:00"
closed_at: "2026-07-26T15:23:00+00:00"
closeout_status: "passed"
verification:
  total_runs: 5
  failed_runs: 1
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 18.31
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
        duration_seconds: 2.75
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 3.16
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.78
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 8.21
```
