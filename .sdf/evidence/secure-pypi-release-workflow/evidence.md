# Evidence

## Intent
Add the release-only workflow that builds, independently verifies, and then
publishes the Software Dark Factory wheel and source distribution through PyPI
Trusted Publishing. A published GitHub Release is the deliberate publication
boundary; this pull request does not create a release, tag, PyPI publisher, or
publication.

## Review focus
Confirm the workflow only listens for a published GitHub Release, checks out
that release tag, and rejects every tag that is not exactly the package version
prefixed with `v`. The wheel and sdist must be the only files built, and each
is installed from `dist/` into a separate fresh environment before its version,
identity, help, and clean receiver initialization prove the canonical Front
Door identity. Verify that the uploaded artifact is the same `dist/` directory
the publish job downloads unchanged, and that publishing uses only OIDC
`id-token: write` in the `pypi` environment.

## Limits
This adds release machinery only: it does not publish version 0.1.0, create a
tag or GitHub Release, configure the `pypi` environment, register a PyPI
Trusted Publisher, store a PyPI credential, add TestPyPI, or reserve the
package name. After merge, the repository owner must separately configure the
`pypi` GitHub environment with required manual approval and deployment
restricted to protected `v*` tags where supported, with no stored PyPI
credential. The pending PyPI Trusted Publisher values are project
`software-dark-factory`, GitHub owner `johnnybutler7`, repository `sdf-cli`,
workflow `release.yml`, and environment `pypi`; a pending publisher does not
secure the package name before the first successful publication.

## Guidance applied
Applied the governed-change loop and configured verification boundary for
closeout. Engineering guidance kept the security-sensitive release, artifact,
and publication boundaries explicit and small. Python packaging guidance and
the retained packaging smoke tests shaped the fresh-install verification of
the exact release artifacts. Product guidance preserved the package and Front
Door identity. The `sdf` executable was unavailable on PATH, so the equivalent
source command was used to scaffold and close this repository-local evidence.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "secure-pypi-release-workflow"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/add-pypi-release-workflow"
  head: "100bd05add1db2406d91b0e30702e1c4c5f49d0c"
run_context:
  surface: "codex_local"
  model: "GPT-5.6 Terra"
  reasoning: "high"
  speed: "standard"
started_at: "2026-07-23T10:51:04+00:00"
closed_at: "2026-07-23T10:55:28+00:00"
closeout_status: "passed"
verification:
  total_runs: 3
  failed_runs: 2
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 15.17
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
        duration_seconds: 2.11
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.27
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.16
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 7.28
```
