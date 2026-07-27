# Software Dark Factory

[![PyPI version](https://img.shields.io/pypi/v/software-dark-factory.svg)](https://pypi.org/project/software-dark-factory/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/software-dark-factory.svg)](https://pypi.org/project/software-dark-factory/)
[![CI](https://github.com/johnnybutler7/sdf-cli/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/johnnybutler7/sdf-cli/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

Software Dark Factory (SDF) is the executable verification loop for governed
AI-assisted software delivery: it makes a repository's standards, checks, and
review evidence executable before human review.

> **Developer Preview / Alpha.** SDF 0.1.0 is for evaluation and local
> repository workflows. It is not production-ready.

SDF runs locally in your repository. It requires no hosted SDF account or API
key, sends no code, prompts, or evidence to an SDF service, and includes no
telemetry. Repository-configured verification commands remain under the
repository's control and may have their own network behaviour.

Your team defines what acceptable delivery means. SDF makes those standards,
checks, and evidence executable before human review.

SDF exists to help teams benefit from agentic speed without lowering the
engineering bar or taking approval and merge authority away from people.

**Why the name?** SDF began with a lights-off ambition. Building towards it showed that greater autonomy first requires repository-owned standards, executable verification, retained evidence and clear human authority boundaries. [Read the origin and direction](https://www.softwaredarkfactory.com/founder-memo#why-the-name).

## The governed change loop

- `sdf init` installs the repository Front Door.
- `sdf start --change-id <id>` optionally scaffolds evidence when early
  declaration is useful; it is not required for every change.
- `sdf close --change-id <id>` runs the repository's full configured
  verification boundary and prepares the reviewer handoff. Focused checks can
  support the work, but are not closeout.
- `sdf status` optionally checks the installed Front Door and release identity.

Approval and merge remain outside SDF.

## What SDF produces

For each governed change, SDF retains structured evidence—including verification
history—and a consistent handoff for the human reviewer.

<details>
<summary>Example <code>sdf close</code> output from the stable 0.1.0 CLI</summary>

```text
SDF close
Resolved repository path: .
closeout check: passed
closeout result record: written (.sdf/evidence/public-readme-polish/evidence.md machine record)
pr-body write: written (.sdf/handoffs/public-readme-polish/pr-body.md)
pr-body check: ready
github: not mutated
…
SDF close complete: verification passed, evidence recorded, and local handoff checked.
```

</details>

<details>
<summary>Example evidence record: a final pass retains the earlier failure</summary>

The full committed [evidence record](https://github.com/johnnybutler7/sdf-cli/blob/2f8563c5855ef5c6ce12c54b0a6c818f3f6d689d/.sdf/evidence/developer-preview-evaluation-baseline/evidence.md)
shows the reviewer judgement and complete machine record. This trimmed section
shows that the final pass does not erase the previous failed run.

````markdown
## Intent
Make the public Developer Preview installation route non-invasive: it now
creates or safely reuses an `sdf-demo` evaluation baseline and targets the
draft installation PR at that baseline.

## Review focus
Check the canonical guide URL, the required branch relationship, protection for
an existing `sdf-demo` branch, and the human authority boundary.

## Limits
Documentation and governed evidence only. This does not change CLI behaviour,
package version, GitHub defaults, or release state.

## Guidance applied
The governed change loop required evidence, configured closeout, and a checked
handoff. Engineering, product, and verification guidance kept the documented
evaluation boundary accurate and reviewable.

## Machine Record

```yaml
closeout_status: "passed"
verification:
  total_runs: 2
  failed_runs: 1
  final_pass_followed_earlier_failure: true
  latest_run:
    status: "passed"
```
````

</details>

## Install SDF safely

> **Developer Preview:** The agent-led journey creates an isolated `sdf-demo`
> baseline from the receiver's default branch, then prepares the installation
> on a separate branch. It leaves the configured default branch unchanged.

Point your coding agent at the [Getting Started guide](GETTING-STARTED.md) and
ask it to install and configure Software Dark Factory in the repository
currently open in its workspace. The intended journey is:

> Point your agent at the guide → receive a verified, reviewable SDF
> installation PR against an isolated evaluation baseline.

The guide provides one copyable prompt and a bounded agent workflow that stops
after opening a draft installation PR against `sdf-demo`. For manual
installation, mechanics inspection, troubleshooting, or environments without a
coding agent, use the [manual walkthrough](docs/MANUAL-WALKTHROUGH.md).

`software-dark-factory` version 0.1.0 is published on PyPI. The agent-led
[Getting Started guide](GETTING-STARTED.md) covers installation,
repository-owned configuration, verification, and the draft PR handoff.

The published package can be installed with:

```shell
pipx install software-dark-factory==0.1.0
```

| Surface | Name |
| --- | --- |
| GitHub repository | `sdf-cli` |
| PyPI package | `software-dark-factory` |
| CLI command | `sdf` |

The repository, Python distribution, and executable intentionally use different
names.

If you prefer a virtual environment, install the published distribution with:

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install software-dark-factory==0.1.0
```

Editable installation is for contributors or local source development. Use
`pipx install --editable .` or replace the final virtual-environment command
with `python -m pip install --editable .`.

## Public receiver proof

The public [ecommerce-microservices-example](https://github.com/johnnybutler7/ecommerce-microservices-example)
is a real Go receiver, not an SDF tutorial fixture:

1. [PR #21 installed SDF 0.1.0](https://github.com/johnnybutler7/ecommerce-microservices-example/pull/21)
   into an isolated `sdf-demo` evaluation baseline, with its
   [installation evidence](https://github.com/johnnybutler7/ecommerce-microservices-example/blob/f0e739a23752577053d47200a0c2f242f0422880/.sdf/evidence/install-software-dark-factory/evidence.md).
2. [PR #22 then took an ordinary catalog-validation change](https://github.com/johnnybutler7/ecommerce-microservices-example/pull/22)
   through the installed Front Door, with its
   [governed evidence](https://github.com/johnnybutler7/ecommerce-microservices-example/blob/83498a2b5a00978e4dc89096b8308047dbf15813/.sdf/evidence/catalog-product-validation/evidence.md).

The second change did not need to restate SDF instructions: the installed
repository guidance supplied the workflow.

## Continue at your pace

[Install SDF safely](GETTING-STARTED.md)
→ [Review the first governed change](https://github.com/johnnybutler7/ecommerce-microservices-example/pull/22)
→ [Add your repository's standards](docs/ADD-YOUR-STANDARDS.md)
→ Continue with repository-specific guidance and verification.

Adding playbooks is a separate, useful next step—not a prerequisite for a safe
evaluation. See the stable [v0.1.0 release notes](https://github.com/johnnybutler7/sdf-cli/releases/tag/v0.1.0)
for the released Developer Preview.

## The problem

AI lets more people and coding agents produce more software changes, faster.
As the volume and variation of changes increase, pull requests can arrive with
uneven scope, engineering standards, verification, evidence, and review
context. Reviewers are then left to reconstruct what was requested, which
repository expectations applied, what checks actually ran, and what risks or
limits remain.

A useful change still needs to meet the repository's own acceptance boundary:
its guidance, playbooks, tests, risks, and review expectations. SDF makes that
boundary more executable and carries the resulting context, verification
history, and evidence into a consistent human reviewer handoff.

SDF supports the acceptance decision. It does not approve, merge, deploy, or
prove that the change is correct.

## What SDF does

- Installs a portable repository Front Door and a local `.sdf` operating area.
- Reads repository-owned guidance, playbooks, and configured verification checks.
- Runs and records the repository-defined verification boundary during closeout.
- Preserves passed, failed, and blocked verification history.
- Produces structured, per-change evidence and a consistent handoff for human PR review.

## What SDF does not do

SDF is not an autonomous software factory, an AI coding agent, a code-review
bot, or a hosted scanning platform. It does not prove correctness, approve or
merge changes, repair code, deploy software, or supply universal engineering
standards. The repository and its reviewers remain responsible for those
decisions.

## Initialisation commands

The coding agent normally performs and verifies these commands through the
[Getting Started guide](GETTING-STARTED.md). For manual evaluation, see the
[manual walkthrough](docs/MANUAL-WALKTHROUGH.md).

```shell
sdf init
sdf status
sdf guidance
```

`sdf init` may create `.sdf/` (including its guidance, contracts,
`config.yml`, and starter `verification.yml`) plus root `AGENTS.md` and
`CLAUDE.md` entries. It does not silently replace existing files; when managed
`.gitignore` or `.gitattributes` entries are missing, it may append them. The
starter `.sdf/verification.yml` is an intentional placeholder: define the
checks your repository trusts before running `sdf verify`.

Installation should be reviewed and merged before beginning a separate
governed application change. The [manual walkthrough](docs/MANUAL-WALKTHROUGH.md)
demonstrates that later workflow in a disposable example.

## The governed workflow

1. The repository declares its guidance, playbooks, risks, and verification
   boundary.
2. A change records its intent, review focus, limits, and applicable guidance.
3. SDF executes the configured checks at closeout and records the result.
4. A human reviewer uses that evidence and the code to make the review,
   approval, and merge decisions.

## The repository Front Door

The packaged canonical Front Door is the portable baseline distributed with
SDF. `sdf init` copies the required portable guidance into a receiver
repository's `.sdf` directory and adds a root entry point where needed. Inside
that repository, the configuration, playbooks, checks, and evidence are
repository-owned. The SDF CLI executes that local loop; it does not silently
overwrite repository customisation during a later package upgrade.

## Portable baseline, repository-owned extensions

SDF 0.1.0 is the portable baseline for the governed-change loop. This base
Developer Preview supplies the common governed-change contract and executable
loop for repository guidance, configured verification, retained evidence, and
human reviewer handoff.

It is intentionally generic enough for different technology stacks, monoliths
and microservices, repository sizes, product shapes, delivery processes, levels
of AI adoption, and team experience or confidence with coding agents. The
portable baseline does not attempt to supply every repository's engineering
standards. Each receiver repository owns its `.sdf` configuration, verification
boundary, repository-owned playbooks, and evidence expectations, extending the
baseline with the checks, risks, and guidance appropriate to its stack,
architecture, product, team, and delivery workflow. This team-specific
adaptation is expected product behaviour, not a workaround or a gap.

Receiver-specific implementations may also extend the baseline with, for
example, model, token, and cost accounting; retained evidence used as working
memory for future changes; recurring analysis of evidence to identify repeated
friction or engineering hotspots; human-reviewed learning and improvement
loops; or team- and application-specific evidence fields and policies. These
are examples of receiver-specific adaptation, not capabilities automatically
enabled or guaranteed by the base distribution in SDF 0.1.0. SDF does not
autonomously rewrite its own standards or approve changes.

## Reviewer evidence

Each governed change has `.sdf/evidence/<change-id>/evidence.md`. It gives a
reviewer the change intent and acceptance context, review focus including
meaningful risk, limits, and guidance applied. Its machine record captures the
verification history and results, branch and change context, and recorded run
context such as AI usage when available. Repositories may also retain related
work-item evidence or confidence judgements when their own workflow calls for
them; SDF does not invent those claims.

## Current support boundary

- Developer Preview / Alpha for local repository workflows.
- Python 3.11 through 3.14.
- Hosted CI covers compatibility checks on Python 3.11–3.14 plus wheel and
  source-distribution packaging smokes on Python 3.11.
- Supported and tested on Linux and macOS-style POSIX environments. Windows is
  not currently tested or claimed.
- No correctness, approval, merge, repair, deployment, or production-readiness
  claim.

## Engineering overview

SDF keeps repository policy with the repository and makes the execution,
evidence, and review boundaries inspectable. See [ARCHITECTURE.md](ARCHITECTURE.md)
for the system model, lifecycle, trust boundaries, and Developer Preview limits.

- A zero-runtime-dependency Python CLI, tested on Python 3.11–3.14.
- Non-destructive, manifest-driven [receiver installation](src/sdf_cli/receiver_payload_manifest.py).
- A canonical [evidence record](src/sdf_cli/evidence_contract.py) with atomic
  updates and human-narrative preservation.
- [GitHub publication workflows](.github/workflows/publish-open-pr-body.yml)
  execute only trusted default-branch code, never PR-head code, so an untrusted
  pull request cannot run arbitrary code with repository credentials. They also
  guard PR-body mutation; see the
  [hostile-input regression test](tests/test_publish_open_pr_body_workflow.py).
- A [release pipeline](.github/workflows/release.yml) that functionally verifies
  the exact wheel and source distribution before Trusted Publishing.

Representative implementation: [verification command execution](src/sdf_cli/verification_command_execution.py),
[a finalized evidence handoff](https://github.com/johnnybutler7/sdf-cli/pull/4).

## Learn more

- [Getting started](GETTING-STARTED.md)
- [Manual walkthrough](docs/MANUAL-WALKTHROUGH.md)
- [Governed change playbook](.sdf/playbooks/governed-change-loop.md)
- [Repository-owned playbook examples](docs/playbooks/README.md)
- [Apache-2.0 licence](LICENSE)
- [Software Dark Factory website](https://www.softwaredarkfactory.com/)
- [Repository](https://github.com/johnnybutler7/sdf-cli)

## Contributing

SDF is in Developer Preview. Issue reports and evaluation feedback are welcome.
