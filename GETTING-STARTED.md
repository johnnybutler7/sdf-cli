# Get SDF installed by your coding agent

Software Dark Factory (SDF) is intended to be installed and configured by a
repository-capable coding agent. Point the agent already working in your
repository at this guide and receive a verified, reviewable SDF installation
pull request against an isolated evaluation baseline.

The journey is:

> Point your agent at this guide → receive a verified, reviewable SDF
> installation PR against an isolated evaluation baseline.

## Give this prompt to your coding agent

Copy and send this prompt from the repository where you want SDF installed:

> Install Software Dark Factory in the repository currently open in your
> workspace by following:
>
> `https://github.com/johnnybutler7/sdf-cli/blob/main/GETTING-STARTED.md`
>
> Set up a non-invasive Developer Preview evaluation. Create an `sdf-demo`
> baseline branch from the repository's current default branch, push it without
> making it the repository's default branch, then create a separate dedicated
> installation branch from `sdf-demo`. Install and configure SDF on the
> installation branch and open the draft installation pull request against
> `sdf-demo`, not the repository's default branch.
>
> Do not change the repository's configured default branch. Configure
> verification from checks the repository already trusts, verify the
> installation, commit only installation-related changes, and stop after
> opening the draft pull request.

The rest of this guide is for the coding agent. The current repository is the
installation target. Do not create a separate `sdf-example` repository.

## Outcome

The default Developer Preview mode is evaluation through an isolated
`sdf-demo` baseline. Install SDF's Front Door on a separate installation branch
from that baseline, adapt it to the repository's existing standards, run the
configured verification, and hand the human a draft installation PR targeting
`sdf-demo`. Stop after opening the draft PR. If GitHub access is unavailable,
stop after preparing the verified local installation branch and report the
publication blocker.

This guide installs SDF only. It does not implement the repository's first
governed application change.

## Authority boundary

You may:

- inspect the repository and its Git state;
- create and push an `sdf-demo` evaluation baseline without changing the
  repository's configured default branch;
- create a separate dedicated installation branch or isolated worktree from
  `sdf-demo`;
- inspect existing languages, package tooling, tests, CI, playbooks, and
  engineering guidance;
- install the released SDF CLI;
- run `sdf init`;
- adapt `.sdf/verification.yml` to checks the repository already trusts;
- run verification;
- commit only SDF installation and configuration changes; and
- push the installation branch and open a draft pull request against
  `sdf-demo` when GitHub access is available.

You must not:

- work directly on the default branch;
- change the repository's configured default branch;
- target the installation PR at `main`, `master`, or another default branch
  during this Developer Preview evaluation;
- change unrelated application behaviour;
- repair unrelated pre-existing failures unless the human explicitly asks;
- weaken trusted required checks merely to obtain a passing result;
- approve or merge a pull request;
- mark a draft pull request ready for review;
- deploy or release anything; or
- delete branches as part of installation; or
- claim that SDF proves correctness.

Creating and pushing `sdf-demo` does not adopt SDF into the repository's
production baseline. Pull-request review, approval, merge, and release
authority remain with humans. The agent must not merge the installation PR or
merge `sdf-demo` into the default branch.

## Installation workflow

Follow these steps in order.

1. Confirm the target and Git state.

   Treat the repository currently open in your workspace as the installation
   target. Confirm its root, current branch, default branch, remotes, and
   working-tree status. Preserve unrelated changes and stop for human direction
   if they prevent a clean installation-only commit.

2. Create or safely reuse the evaluation baseline.

   Create `sdf-demo` at the current default-branch commit and push it when
   GitHub access is available. Do not change the repository's configured
   default branch. Do not make installation changes on `sdf-demo`; it remains
   the clean comparison point.

   If a local or remote `sdf-demo` already exists, do not force-push, reset,
   overwrite, or silently repurpose it. Inspect whether it is clearly an
   existing SDF evaluation baseline and aligned with the intended base commit.
   Reuse it only when it is suitable; otherwise stop and ask the human to
   choose another evaluation branch name.

3. Create the installation branch.

   Create a separate dedicated installation branch or isolated worktree from
   `sdf-demo`, for example `codex/install-software-dark-factory` or
   `try/install-sdf`. Perform all installation changes only there.

4. Inspect repository-owned standards.

   Identify the repository's languages, supported runtimes, package tooling,
   test commands, formatting and static-analysis checks, CI workflows, agent
   instructions, and engineering playbooks. Prefer commands already used by
   maintainers or required by CI.

5. Select Python.

   SDF 0.1.0 supports Python 3.11 through 3.14. Choose a supported interpreter
   that is already available and compatible with the repository's tooling.
   Record the exact Python version used.

6. Install the released package.

   PyPI was independently verified as publishing
   `software-dark-factory` 0.1.0. Prefer an isolated `pipx` installation:

   ```shell
   pipx install --python python3.11 software-dark-factory==0.1.0
   ```

   Replace `python3.11` with the supported interpreter selected in step 4.
   If `pipx` is unavailable but PyPI is reachable, use an isolated virtual
   environment and install the same pinned distribution:

   ```shell
   python3.11 -m venv .venv-sdf
   .venv-sdf/bin/python -m pip install --upgrade pip
   .venv-sdf/bin/python -m pip install software-dark-factory==0.1.0
   ```

   Use the environment's `sdf` executable for the remaining steps and do not
   commit the environment. If the documented PyPI routes fail, stop and report
   the failure. Do not improvise an installation from an arbitrary branch,
   unpinned `main`, or another undocumented source.

7. Confirm the running implementation.

   Run:

   ```shell
   sdf --help
   sdf --version
   sdf --identity
   ```

   Confirm that the identity and version match the intended released
   installation. If using the virtual-environment route, invoke
   `.venv-sdf/bin/sdf` instead.

8. Install the Front Door.

   From the target repository root, run:

   ```shell
   sdf init
   ```

9. Review every generated or modified file.

   Inspect the complete diff. `sdf init` may create `.sdf/`, add root
   `AGENTS.md` and `CLAUDE.md` entries, and append managed `.gitignore` or
   `.gitattributes` entries. It does not make those files correct for this
   repository without review.

10. Replace the starter verification command.

   The generated `.sdf/verification.yml` intentionally contains a failing
   placeholder. Replace it with exact checks the repository already trusts.
   Do not invent new acceptance standards as part of installation.

11. Classify verification honestly.

    Required checks are blocking and default to `required: true`. Use
    `required: false` only for useful reviewer-visible feedback that the
    repository genuinely treats as non-blocking. Do not downgrade a trusted
    required check to make the installation pass.

12. Preserve pre-existing failures.

    Run or inspect the selected checks closely enough to distinguish
    installation regressions from pre-existing failures. Do not silently hide,
    repair, or relabel unrelated failures. Record them as limitations and ask
    the human for direction if a required failure blocks closeout.

13. Inspect and verify the installation.

    Run:

    ```shell
    sdf status
    sdf guidance
    sdf verify --check
    sdf verify
    ```

    `sdf verify --check` is read-only. `sdf verify` runs only the
    repository-configured commands. Passing verification supports review; it
    does not prove correctness.

14. Record governed setup evidence when appropriate.

    If the installed Front Door declares governance required for committed or
    pull-request work, follow its governed-change loop and record this
    installation as a setup change. Keep installation evidence separate from
    any future application change.

15. Commit only the installation.

    Review the final diff and stage only the SDF Front Door, repository-owned
    verification configuration, installation evidence, and directly related
    documentation or ignore entries. Do not include unrelated work.

16. Open a draft installation pull request.

    Push the installation branch and open a draft PR when GitHub access is
    available. Its head is the installation branch and its base is `sdf-demo`;
    never target `main`, `master`, or another default branch for this normal
    Developer Preview evaluation. The PR must explain the installed Front Door,
    repository-owned checks, verification results, limitations, and points for
    human review. Do not approve it, merge it, or mark it ready for review.

17. Stop and return control to the human.

    Do not begin an application change, deployment, release, or any follow-up
    mutation.

## Final response

Report:

- receiver default branch detected;
- evaluation baseline branch created or reused;
- installation branch used;
- draft PR base and head branches;
- confirmation that the repository's configured default branch was not
  changed;
- SDF version;
- installation source;
- Python version used;
- generated or modified files;
- configured blocking verification checks;
- optional or non-blocking checks;
- verification results;
- pre-existing failures or other limitations;
- draft PR link, if created; and
- items requiring human review.

Do not tell the human to begin the first governed application change
immediately, suggest approval or merge, or claim that SDF is fully adopted
before review. If an installation fallback was used, add a clearly labelled
**Installation note** and describe it neutrally.

The branch relationship must be unmistakable, for example:

```text
Default branch: main — unchanged
Evaluation baseline: sdf-demo
Installation branch: codex/install-software-dark-factory
Draft PR: codex/install-software-dark-factory → sdf-demo
```

## Evaluation, adoption, and cleanup

### Developer Preview evaluation — default

`sdf-demo` is a clean baseline created from the repository's default branch.
The installation PR targets `sdf-demo`, so the team can inspect, test, merge,
retain, or later remove the evaluation without touching the default branch.

### Deliberate adoption — later, explicit

Evaluation is not production adoption. After evaluation, a human may
deliberately choose to install or promote SDF into the repository's normal
baseline through a separately authorised and reviewed PR against the default
branch. Do not instruct the installation agent to merge `sdf-demo` into `main`
or another default branch, and do not imply that merging the evaluation PR into
`sdf-demo` completes adoption.

### Cleanup if the team does not continue

The human may close the draft installation PR and remove the installation
branch through normal Git or GitHub controls. Delete `sdf-demo` only after
confirming no wanted work depends on it. Do not use force-pushes or broad
recursive deletion commands. The agent does not perform this cleanup, and the
repository's default branch remains unchanged.

## After the installation PR

This guide installs SDF's Front Door for evaluation. A first governed
application change is a separate follow-up task. After a human has deliberately
adopted SDF into the repository's normal baseline, they may ask:

> Using this repository's installed SDF Front Door, implement `<specific
> change>` as a governed change and open a draft pull request for review.

For manual installation, mechanics inspection, troubleshooting, or an
environment without a coding agent, use the optional
[manual walkthrough](docs/MANUAL-WALKTHROUGH.md).

## Current support boundary

SDF 0.1.0 is a Developer Preview tested on Python 3.11 through 3.14 in Linux
and macOS-style POSIX environments. Windows is not currently tested or
claimed. SDF supplies a portable base; each receiver repository owns and
adapts its standards, verification boundary, playbooks, and evidence.
