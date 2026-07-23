# Evidence

## Intent
Remove verified pre-release architectural sediment identified by an independent
architecture assessment, before public architecture and presentation material is
added. The cleanup deletes five unconsumed modules and two unconsumed wrappers,
renames the live evidence machine-record contract module and its shared
validator, and replaces fixed archive-file accessors with their contract
constants.

## Review focus
Confirm every deletion was revalidated against the current source, tests,
scripts, workflows, resources, packaging inputs, documentation, dynamic-import
surfaces, and golden outputs. Confirm `evidence_contract` is the canonical live
module, its contract-4 compatibility reader remains intact, and contract-5
machine-record rendering remains byte-for-byte stable. Review the narrowed PR
link inference and archive-file interfaces as mechanical removal of ignored
parameters and constant-returning wrappers.

## Limits
Runtime behaviour and public contracts are unchanged: the package version,
distribution/import/executable identities, evidence version and machine-record
schema, parsing and rendering rules, closeout and verification behaviour,
commands and flags, PR-body output, workflows, receiver payload, supported
Python versions, and documentation presentation are unchanged. Historical
contract-4 archives remain readable. Larger post-0.1.0 architecture
consolidation, including package restructuring and documentation additions, is
intentionally deferred.

## Guidance applied
The governed change loop required this archive and the configured closeout
boundary. Engineering and Python CLI guidance kept the cleanup confined to
clear ownership corrections and contract-preserving tests; verification guidance
kept focused feedback separate from the required full closeout. The configured
product playbook path was unavailable in this checkout, so it did not
materially shape the implementation. No material Python learning arose beyond
the existing contract tests: an import-surface assertion and byte-for-byte
machine-record round trip protect the truthful module rename without changing
the record format.
## Machine Record

```yaml
contract: 5
written_by: "software-dark-factory 0.1.0"
change_id: "pre-release-architectural-sediment"
repository:
  name: "sdf-cli"
  path: "."
  github: "johnnybutler7/sdf-cli"
branch:
  name: "remove-pre-release-architectural-sediment"
  head: "cac5416a3ff8e881edbacd0ded6197cf8e54f68c"
run_context:
  surface: "codex_local"
  model: "GPT-5.6 Terra"
  reasoning: "high"
  speed: "standard"
started_at: "2026-07-23T14:11:44+00:00"
closed_at: "2026-07-23T14:16:12+00:00"
closeout_status: "passed"
verification:
  total_runs: 6
  failed_runs: 5
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
        duration_seconds: 2.25
      - name: "wheel-packaging-smoke"
        status: "passed"
        duration_seconds: 2.36
      - name: "source-distribution-packaging-smoke"
        status: "passed"
        duration_seconds: 3.28
      - name: "python-unit-tests"
        status: "passed"
        duration_seconds: 7.72
```
