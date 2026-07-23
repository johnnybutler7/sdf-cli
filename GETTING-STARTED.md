# Getting started with Software Dark Factory

This guide creates a small local example. It needs no external service or
GitHub account. The example demonstrates the boundary that matters: the
repository owns the standards and checks; SDF executes that acceptance boundary
and records evidence for human review.

## Prerequisites

- Python 3.11 through 3.14.
- `pipx` for the primary installation route, or Python's built-in virtual
  environment support.
- Git, for the example repository and its final local commit.

## Install SDF

After the public 0.1.0 release is available on PyPI, install it with:

```shell
pipx install software-dark-factory
```

That package is not published to PyPI yet. From a local source checkout, run:

```shell
pipx install --editable .
```

With a virtual environment, use the intended post-release installation route:

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install software-dark-factory
```

For a local source checkout, use `python -m pip install --editable .` instead
of the final command.

Confirm the command and the implementation you are running:

```shell
sdf --help
sdf --version
sdf --identity
```

## Create a clean receiver repository

Choose a temporary location, then initialise a Git repository and install the
Front Door:

```shell
mkdir sdf-example
cd sdf-example
git init
sdf init
```

Inspect the receiver and the guidance available to it:

```shell
sdf status
sdf guidance
```

`sdf init` creates the portable `.sdf` guidance and contracts, a
`.sdf/config.yml`, and a starter `.sdf/verification.yml`. It may also add an
`AGENTS.md` or `CLAUDE.md` entry point. These are the installed Front Door, not
your team's standards. Your repository owns its configuration, additional
playbooks, verification commands, and every evidence archive.

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

After reviewing the work locally, commit the change and its evidence:

```shell
git add greeting.py tests/test_greeting.py .sdf
git commit -m "Add greeting example"
sdf close --change-id add-greeting --refresh-handoff
```

The evidence is at `.sdf/evidence/add-greeting/evidence.md`. The refreshed
local handoff is under `.sdf/handoffs/add-greeting/`. Read both before opening
any manually reviewed pull request. SDF does not create, approve, merge, or
deploy that pull request.

## Remove the example safely

Leave the example directory, confirm that you are in its parent and that the
directory name is exactly `sdf-example`, then remove it using your operating
system's Trash or file manager. Do not run a recursive deletion command until
you have checked the path. If you created a virtual environment only for this
example, remove that environment separately after confirming its location.
