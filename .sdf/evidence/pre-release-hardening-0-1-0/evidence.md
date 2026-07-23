# Evidence

## Intent
Complete the bounded required-before-0.1.0 hardening requested after an
independent adversarial release audit. No release blocker or critical
vulnerability was found; this slice addresses concrete outsider-facing
criticism before the Developer Preview release.

## Review focus
Confirm immutable action pins preserve the release workflow's OIDC publishing
boundary, the PyPI-name warning names only this distribution, and the sdist
contains installable product material rather than repository test
infrastructure. Review the deliberately narrow inline-comment parser,
non-destructive contract-5 machine-record recovery, public security guidance,
metadata, documentation truth, and long-command help separation. Repository
settings were updated outside source: description and six relevant topics were
set; Wiki and Projects were disabled.

## Limits
The version, distribution/import/executable identities, release trigger,
Trusted Publishing values, `pypi` environment, required check names, and
repository-owned verification trust model are unchanged. This does not publish,
tag, release, bump a version, add Windows CI, add Dependabot, or implement the
audit's deferred timeout, streaming, ancestry, migration, or workflow-policy
recommendations.

## Guidance applied
The governed change loop required a new evidence archive and configured
closeout. Engineering and Python CLI guidance kept parsing, recovery, output,
and packaging changes small and contract-tested. Verification guidance retained
the configured local boundary. Product guidance kept support and non-claim
documentation aligned with implemented behavior. The limited parser accepts
ordinary scalar comments without adding a YAML runtime dependency; malformed
tool-owned records are reported and never auto-repaired. Current action SHAs
were resolved from the actions' official release tags before pinning.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "pre-release-hardening-0-1-0"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/pre-release-hardening-0-1-0"
  head: "c2285c035332af12f1f0efb25d3d9f672275de93"
run_context:
  surface: "codex_local"
  model: "GPT-5.6 Terra"
  reasoning: "high"
  speed: "standard"
started_at: "2026-07-23T12:29:14+00:00"
closed_at: "2026-07-23T12:37:58+00:00"
closeout_status: "passed"
verification:
  total_runs: 3
  failed_runs: 2
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 15.46
    checks:
      - name: "ruff"
        status: "passed"
        duration_seconds: 0.03
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
        duration_seconds: 2.23
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.42
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.16
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 7.32
```
