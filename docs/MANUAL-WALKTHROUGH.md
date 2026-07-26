# Manual SDF walkthrough

This optional walkthrough demonstrates SDF mechanics in a disposable local
repository. Use it if you prefer manual installation, maintain SDF, are
troubleshooting, or do not have a repository-capable coding agent.

For the normal agent-led installation journey in an established repository,
use [Getting started](../GETTING-STARTED.md).

The example demonstrates the core boundary: the repository owns its standards
and checks; SDF executes that acceptance boundary and records evidence for
human review. It needs no external service or GitHub account.

## Prerequisites

- Python 3.11 through 3.14.
- `pipx` for the primary installation route, or Python's built-in virtual
  environment support.
- Git.

## Install SDF

Install the pinned published package with:

```shell
pipx install software-dark-factory==0.1.0
```

If you are contributing to SDF itself from a local source checkout, use:

```shell
pipx install --editable .
```

The PyPI distribution is **`software-dark-factory`**. `sdf-cli` and `sdf` are
not this project's distribution names.

With a virtual environment, use:

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install software-dark-factory==0.1.0
```

For local source development, replace the final command with
`python -m pip install --editable .`.

Confirm the implementation:

```shell
sdf --help
sdf --version
sdf --identity
```

## Create the disposable repository

Choose a temporary location, then run:

```shell
mkdir sdf-example
cd sdf-example
git init
git switch -c try/sdf
sdf init
```

Inspect the generated Front Door and guidance:

```shell
sdf status
sdf guidance
```

`sdf init` may create `.sdf/`, root `AGENTS.md` and `CLAUDE.md` entries, and
managed `.gitignore` or `.gitattributes` entries. Review the full diff. These
portable files are a base; the repository owns its configuration, additional
playbooks, verification commands, and evidence.

## Configure a trusted check

The starter verification file intentionally fails until the receiver defines
checks it trusts. For this disposable example, create
`tests/test_greeting.py`:

```python
import unittest


class GreetingTest(unittest.TestCase):
    def test_message(self):
        self.assertEqual("hello", "hello")
```

Replace `.sdf/verification.yml` with:

```yaml
version: 1
commands:
  - name: unit-tests
    command: python3 -m unittest discover -s tests
```

Inspect and run the boundary:

```shell
sdf verify --check
sdf verify
```

`--check` is read-only. `sdf verify` runs the configured checks; it does not
create evidence, approve a change, or contact GitHub.

## Run a small governed change

Start an evidence archive:

```shell
sdf start --change-id add-greeting
```

Add `greeting.py`, then update the test to exercise the new behaviour. Complete
the four human sections in
`.sdf/evidence/add-greeting/evidence.md`:

- Intent
- Review focus
- Limits
- Guidance applied

Close the change:

```shell
sdf close --change-id add-greeting
```

Closeout runs the repository-defined verification boundary, records the
result, and prepares a checked local handoff. If verification or the evidence
sections are incomplete, correct them and run the same command again.

After reviewing the work, commit only the example and its evidence:

```shell
git add greeting.py tests/test_greeting.py .sdf
git commit -m "Add greeting example"
sdf close --change-id add-greeting --refresh-handoff
```

Review `.sdf/evidence/add-greeting/evidence.md` and the refreshed local handoff
under `.sdf/handoffs/add-greeting/`. These records support human review; they
do not prove correctness or authorise approval, merge, deployment, or release.

## Remove the example safely

Leave the example directory and confirm that its full path and directory name
are exactly what you expect. Move it to your operating system's Trash or use
your file manager. Do not run a recursive deletion command against an
unchecked path.

If you used a disposable clone, dedicated worktree, branch, or virtual
environment instead, remove it through the corresponding Git, file-manager,
or environment cleanup workflow after confirming its exact location.
