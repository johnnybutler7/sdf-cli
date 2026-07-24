# Getting started with Software Dark Factory

Point your coding agent at the SDF README and ask it to install and configure
SDF for the current repository. The agent inspects the repository,
initialises SDF non-destructively, and proposes a verification boundary from
commands the repository already trusts. The repository owner decides genuinely
ambiguous policy or verification questions; humans retain review, approval, and
merge control.

## Prerequisites

- Python 3.11 through 3.14.
- `pipx` for the primary installation route, or Python's built-in virtual
  environment support.
- Git, for the example repository and its final local commit.

## Install and configure SDF with a coding agent

Install the published package with:

```shell
pipx install software-dark-factory
```

The PyPI distribution is **`software-dark-factory`**. Do not infer a PyPI
package name from this repository or the `sdf` executable: `sdf-cli` and `sdf`
are not this project's distribution names.

With a virtual environment:

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install software-dark-factory
```

Editable installation is for contributors or local source development only:
use `pipx install --editable .`, or replace the final virtual-environment
command with `python -m pip install --editable .`.

Ask a coding agent to read the README and initialise SDF non-destructively.
The [installation-agent prompt](README.md#prompt-for-an-installation-agent) in
the README is the recommended copyable request. An agent that reads a
repository entry point such as `AGENTS.md` or `CLAUDE.md` will then be directed
to the installed SDF guidance.

The agent normally runs these inspection commands as part of installation. A
repository owner may also run them to inspect the result:

```shell
sdf --help
sdf --version
sdf --identity
```

## What the repository owner decides

The repository owner decides or approves:

- whether governance is active;
- the trusted verification boundary;
- repository-owned playbooks and standards;
- known exceptions or blockers;
- review, approval, and merge.

SDF does not let an agent determine these policy decisions on the owner's
behalf.

## What the coding agent executes

When its tools and permissions allow, the coding agent performing the change
should read `AGENTS.md`, `CLAUDE.md`, and `.sdf/agent-instructions.md` where
applicable; inspect `.sdf/config.yml` and `.sdf/verification.yml`; and run
`sdf guidance`. It loads only relevant receiver playbooks, makes the smallest
bounded change, uses `sdf start` when useful, records concise evidence, uses
`sdf close` for configured closeout, commits the evidence with the
implementation, and refreshes the final checked handoff.

The agent stops and asks for human input when repository policy, permissions,
or the trusted verification boundary are genuinely ambiguous. It does not
invent repository standards or verification commands.

## Give the first governed change

After configuration, ask for the outcome rather than manually coordinating the
loop:

```text
Implement <describe the change>.

Follow this repository's installed SDF guidance and applicable receiver
playbooks. Keep the change bounded, use the configured verification boundary,
record concise evidence, and prepare the final checked handoff for human review.

Do not invent replacement checks, bypass required failures, approve, or merge
the change.
```

## Inspect the result as a human reviewer

Review the code, evidence, configured verification results, and final handoff.
SDF supports that acceptance decision; it does not approve, merge, deploy, or
prove the change correct.

## Manual command reference and troubleshooting

The following manual sequence is useful for inspecting an installation,
troubleshooting an agent run, learning the CLI, or deliberately operating the
loop by hand. It is not the recommended daily workflow.

### Create a clean receiver repository

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

### Start and close a small governed change

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

### Remove the example safely

Leave the example directory, confirm that you are in its parent and that the
directory name is exactly `sdf-example`, then remove it using your operating
system's Trash or file manager. Do not run a recursive deletion command until
you have checked the path. If you created a virtual environment only for this
example, remove that environment separately after confirming its location.

## Current support boundary

This Developer Preview is tested on Linux and macOS-style POSIX environments;
Windows is not currently tested or claimed. Hosted CI covers Python 3.11–3.14,
plus wheel and source-distribution packaging smokes on Python 3.11.
