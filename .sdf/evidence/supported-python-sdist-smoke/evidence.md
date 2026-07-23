# Evidence

## Intent
Record the first governed change after the clean public import of the canonical
repository. The existing wheel smoke remains intact; this slice adds only the
missing supported-Python source-distribution release boundary.

## Review focus
Confirm the sdist test builds exactly the expected 0.1.0 archive from a clean
export through the PEP 517 configuration, installs that archive into a fresh
environment, and exercises the installed CLI and receiver initialization. Check
that every initialized portable Front Door file is compared with the source
packaged in the sdist, and that CI runs each packaging proof exactly once on
Python 3.11 rather than duplicating either in compatibility jobs.

## Limits
This does not change runtime CLI behaviour, Front Door semantics, identity, or
version; it does not publish an artefact. Passing wheel or sdist packaging
checks proves only the stated installation boundaries, not runtime correctness,
production readiness, approval, deployment, or release publication readiness.

## Guidance applied
Applied the governed-change loop for first canonical evidence and checked
handoff; the engineering and Python CLI packaging/testing guidance for a small,
explicit subprocess and filesystem boundary; and the repository verification
guidance for configured closeout. No prior evidence was consulted because this
is the first canonical archive.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "supported-python-sdist-smoke"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/add-sdist-smoke"
  head: "523da12e9fed43526c436c912e2ffd6996ad3eec"
run_context:
  surface: "codex_local"
  model: "GPT-5.6 Terra"
  reasoning: "medium"
  speed: "standard"
started_at: "2026-07-23T10:38:13+00:00"
closed_at: "2026-07-23T10:39:47+00:00"
closeout_status: "passed"
verification:
  total_runs: 2
  failed_runs: 1
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 15.95
    checks:
      - name: "ruff"
        status: "passed"
        duration_seconds: 0.03
      - name: "python-module-size-audit"
        status: "passed"
        duration_seconds: 0.05
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
        duration_seconds: 2.23
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.39
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.51
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 7.47
```
