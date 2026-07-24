# Software Dark Factory

Software Dark Factory (SDF) is the executable verification loop for governed
AI-assisted software delivery: it makes a repository's standards, checks, and
review evidence executable before human review.

> **Developer Preview / Alpha.** SDF 0.1.0 is for evaluation and local
> repository workflows. It is not production-ready.

Your team defines what acceptable delivery means. SDF makes those standards,
checks, and evidence executable before human review.

SDF exists to help teams benefit from agentic speed without lowering the
engineering bar.

## Engineering overview

SDF keeps repository policy with the repository and makes the execution,
evidence, and review boundaries inspectable. See [ARCHITECTURE.md](ARCHITECTURE.md)
for the system model, lifecycle, trust boundaries, and Developer Preview limits.

- A zero-runtime-dependency Python CLI, tested on Python 3.11–3.14.
- Non-destructive, manifest-driven [receiver installation](src/sdf_cli/receiver_payload_manifest.py).
- A canonical [evidence record](src/sdf_cli/evidence_contract.py) with atomic
  updates and human-narrative preservation.
- [GitHub publication workflows](.github/workflows/publish-open-pr-body.yml)
  that avoid PR-head execution and guard PR-body mutation; see the
  [hostile-input regression test](tests/test_publish_open_pr_body_workflow.py).
- A [release pipeline](.github/workflows/release.yml) that functionally verifies
  the exact wheel and source distribution before Trusted Publishing.

Representative implementation: [verification command execution](src/sdf_cli/verification_command_execution.py),
[a finalized evidence handoff](https://github.com/johnnybutler7/sdf-cli/pull/4).

## The problem

AI lets more people and coding agents produce more software changes, faster.
Those changes may come from experienced engineers, newer engineers, people
outside traditional engineering roles using agents, and different coding tools
or workflows.

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

## Try SDF with a coding agent

Point your coding agent at the [Getting Started guide](GETTING-STARTED.md) and
ask it to install and configure Software Dark Factory for the repository. Ask
it to use the documented commands, build `.sdf/verification.yml` from checks
the repository already trusts, and show the full diff before anything is
committed.

You can follow the same steps manually. In either case, review the installed
Front Door, configuration, and verification boundary before committing them.

## Installation

`software-dark-factory` version 0.1.0 is published on PyPI. The normal
installation route is:

```shell
pipx install software-dark-factory
```

For a complete first installation and local walkthrough, see
[Getting started](GETTING-STARTED.md).

The PyPI distribution is **`software-dark-factory`**. Do not infer a PyPI
package name from this repository or the `sdf` executable: `sdf-cli` and `sdf`
are not this project's distribution names.

If you prefer a virtual environment, install the published distribution with:

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install software-dark-factory
```

Editable installation is for contributors or local source development. Use
`pipx install --editable .` or replace the final virtual-environment command
with `python -m pip install --editable .`.

## First use

From the root of the repository you want to govern:

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

For the smallest governed change, start an archive, make the change, complete
its reviewer judgement, and close it:

```shell
sdf start --change-id add-example
# Make the ordinary repository change and complete the four sections in
# .sdf/evidence/add-example/evidence.md.
sdf close --change-id add-example
```

`sdf close` runs the repository-defined checks and records their result. After
committing the change and evidence, refresh the checked local reviewer handoff:

```shell
sdf close --change-id add-example --refresh-handoff
```

See [GETTING-STARTED.md](GETTING-STARTED.md) for a complete, local example.

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

## Learn more

- [Getting started](GETTING-STARTED.md)
- [Governed change playbook](.sdf/playbooks/governed-change-loop.md)
- [Repository-owned playbook examples](docs/playbooks/README.md)
- [Apache-2.0 licence](LICENSE)
- [Software Dark Factory website](https://www.softwaredarkfactory.com/)
- [Repository](https://github.com/johnnybutler7/sdf-cli)

## Contributing

SDF is in Developer Preview. Issue reports and evaluation feedback are welcome.
