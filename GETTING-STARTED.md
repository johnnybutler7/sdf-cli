# Getting started with Software Dark Factory

This guide walks through a first evaluation in a small local example. It needs
no external service or GitHub account. The example demonstrates the boundary
that matters: the repository owns the standards and checks; SDF executes that
acceptance boundary and records evidence for human review.

For a first evaluation, use a disposable repository or clone, or a dedicated
evaluation branch—preferably in a separate Git worktree. Begin from a clean Git
state, keep unrelated work out of the evaluation, and do not run it directly
on the repository's default branch. Review all proposed changes, especially
`.sdf/verification.yml`, before deciding whether to commit or push.

You can follow this guide manually, or point your coding agent at it and ask
it to install and configure SDF for your repository. The commands are the same
either way.

## Prerequisites

- Python 3.11 through 3.14.
- `pipx` for the primary installation route, or Python's built-in virtual
  environment support.
- Git, for the example repository and its final local commit.

## Install SDF

Install the published package with:

```shell
pipx install software-dark-factory
```

If you are contributing to SDF itself from a local source checkout, use an
editable installation instead:

```shell
pipx install --editable .
```

The PyPI distribution is **`software-dark-factory`**. Do not infer a PyPI
package name from this repository or the `sdf` executable: `sdf-cli` and `sdf`
are not this project's distribution names.

With a virtual environment, use the intended post-release installation route:

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install software-dark-factory
```

When contributing from a local source checkout, use
`python -m pip install --editable .` instead of the final command.

Confirm the command and the implementation you are running:

```shell
sdf --help
sdf --version
sdf --identity
```

## Create a clean receiver repository

For the simplest route, choose a temporary location, then initialise a Git
repository, enter a dedicated evaluation branch, and install the Front Door:

```shell
mkdir sdf-example
cd sdf-example
git init
git switch -c try/sdf
sdf init
```

Inspect the receiver and the guidance available to it:

```shell
sdf status
sdf guidance
```

`sdf init` may create `.sdf/` (including portable guidance, contracts,
`config.yml`, and starter `verification.yml`) plus root `AGENTS.md` and
`CLAUDE.md` entries. It does not silently replace existing files; when managed
`.gitignore` or `.gitattributes` entries are missing, it may append them. These
are the installed Front Door, not your team's standards. Your repository owns
its configuration, additional playbooks, verification commands, and every
evidence archive.

The starter verification file intentionally fails until you replace it with
checks your repository trusts. For this example, create a tiny test and use
the following `.sdf/verification.yml`:

```yaml
version: 1
commands:
  - name: unit-tests
    command: python3 -m unittest discover -s tests
```

Create `tests/test_greeting.py` with this minimal test:

```python
import unittest


class GreetingTest(unittest.TestCase):
    def test_message(self):
        self.assertEqual("hello", "hello")
```

Now inspect and run the repository-defined boundary:

```shell
sdf verify --check
sdf verify
```

`--check` is read-only. `sdf verify` runs only the commands the receiver has
configured; it does not create evidence, approve a change, or contact GitHub.

At this point, inspect the full diff from `sdf init` and the verification
configuration before continuing. The intended evaluation order is: work in the
isolated branch or worktree, install and initialise SDF, inspect the resulting
diff, adapt and review `.sdf/verification.yml`, then run a small governed
change. Review its evidence and handoff before deciding whether to commit,
push, or open an evaluation pull request.

## Current support boundary

This Developer Preview is tested on Linux and macOS-style POSIX environments;
Windows is not currently tested or claimed. Hosted CI covers Python 3.11–3.14,
plus wheel and source-distribution packaging smokes on Python 3.11.

## Start and close a small governed change

Start an evidence archive before making a small ordinary change:

```shell
sdf start --change-id add-greeting
```

Add your change, such as `greeting.py`, and update the test so it exercises the
new behaviour. Then edit `.sdf/evidence/add-greeting/evidence.md` and fill in
the four human sections:

- Intent
- Review focus
- Limits
- Guidance applied

Close the change:

```shell
sdf close --change-id add-greeting
```

Closeout runs the full repository-defined verification boundary, records the
result in the evidence machine record, and prepares a checked local handoff.
If verification or the four evidence sections are incomplete, correct them and
run the same `sdf close` command again.

After reviewing the work locally, decide whether to keep the evaluation. Only
then commit the change and its evidence:

```shell
git add greeting.py tests/test_greeting.py .sdf
git commit -m "Add greeting example"
sdf close --change-id add-greeting --refresh-handoff
```

The evidence is at `.sdf/evidence/add-greeting/evidence.md`. The refreshed
local handoff is under `.sdf/handoffs/add-greeting/`. Read both before opening
any manually reviewed pull request. SDF does not create, approve, merge, or
deploy that pull request.

After this walkthrough, you should have:

- an installed Front Door and `.sdf` area;
- a repository-owned verification configuration;
- recorded verification history;
- structured evidence; and
- a reviewer handoff for human review.

These records support review; they do not prove correctness or authorise a
merge.

## Remove the example safely

Leave the example directory, confirm that you are in its parent and that the
directory name is exactly `sdf-example`, then remove it using your operating
system's Trash or file manager. Do not run a recursive deletion command until
you have checked the path. A disposable clone or worktree can be removed the
same way after confirming its location; changes on a dedicated branch can be
discarded through your normal Git review and cleanup process. If you created a
virtual environment only for this example, remove that environment separately
after confirming its location.
