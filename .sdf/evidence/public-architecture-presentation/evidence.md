# Evidence

## Intent
Add a compact public architecture and engineering presentation layer before the
Developer Preview release. `ARCHITECTURE.md` explains the package/receiver
ownership split, governed lifecycle, evidence and verification boundaries,
optional GitHub publication, release pipeline, deliberate trade-offs, and
preview limits; the README now directs technical readers to that overview.

## Review focus
Confirm the documentation remains faithful to the current implementation after
the architectural-sediment cleanup: SDF executes receiver-owned verification,
records evidence without asserting correctness, and preserves human review and
merge control. Check that the two diagrams distinguish ownership, side effects,
and control points; links point to live representative implementation, tests,
evidence, workflow, and finalized PR material; and the README remains concise.

## Limits
This is documentation only. It changes no runtime code, commands, tests,
workflow behaviour, release configuration, package metadata, version identity,
repository settings, or published-release status. It does not claim that
version 0.1.0 is published, that SDF proves correctness, or that publication,
approval, merge, repair, deployment, or external adoption is automatic.

## Guidance applied
The governed change loop shaped the evidence, closeout, and handoff path.
Engineering guidance kept the document scoped to ownership, explicit side
effects, and reviewable boundaries; product guidance kept public claims aligned
with implemented behaviour; verification guidance retained the configured
boundary. The architecture and hiring assessments were used as input but their
prose was not copied. No Python implementation or learning guidance materially
shaped this documentation-only slice.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "public-architecture-presentation"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "codex/public-architecture-presentation"
  head: "9df837c76acec1806d1122915be6557f2771f24d"
run_context:
  surface: "codex_local"
  model: "GPT-5.6 Terra"
  reasoning: "high"
  speed: "standard"
started_at: "2026-07-23T14:35:58+00:00"
closed_at: "2026-07-23T14:37:46+00:00"
closeout_status: "passed"
verification:
  total_runs: 2
  failed_runs: 1
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
    total_duration_seconds: 14.22
    checks:
      - name: "ruff"
        status: "passed"
        duration_seconds: 0.05
      - name: "python-module-size-audit"
        status: "passed"
        duration_seconds: 0.04
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
        duration_seconds: 2.16
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.27
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.04
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 6.42
```
