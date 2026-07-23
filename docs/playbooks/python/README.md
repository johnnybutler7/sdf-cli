# Python CLI Playbook Router

Use this router for work on the `sdf-cli` Python package and its supporting
tests, scripts, package metadata, and resources. Read only the deeper
playbooks relevant to the slice; the router does not require every document
below for every change.

## Route By Work Type

| Change | Read |
| --- | --- |
| Python implementation or architecture | [Python CLI Design](python-cli-design-playbook.md) and [Python Learning](python-learning.md) |
| CLI commands, options, output, exit codes, or generated Markdown | [Python CLI Design](python-cli-design-playbook.md) |
| Filesystem, Git, subprocess, environment, or clock boundary | [Python CLI Design](python-cli-design-playbook.md) and [Engineering Discipline](../engineering/README.md) when the boundary is critical |
| Tests, fixtures, or golden-output changes | [Python CLI Design](python-cli-design-playbook.md); also use [verification guidance](../../verification/README.md) for the configured verification boundary |
| Packaging, package resources, or installation surface | [Python CLI Design](python-cli-design-playbook.md) and [verification guidance](../../verification/README.md) when installation or packaging checks apply |
| Ruff, formatting, linting, typing, complexity, module-size checks, suppressions, waivers, or quality tools | [Python Quality Tooling](python-quality-tooling-playbook.md) |
| New or changed Python dependency | [Python Quality Tooling](python-quality-tooling-playbook.md), plus [Python CLI Design](python-cli-design-playbook.md) if it changes an implementation boundary |
| A reusable lesson revealed by the slice | [Python Learning](python-learning.md) |

Read [Engineering Discipline](../engineering/README.md) when the change needs
a stack-neutral decision about responsibility, policy versus mechanism,
side-effect control, testing judgement, or maintainability.

## Record The Relevant Judgement

For governed work, record the playbooks that materially shaped the slice in
evidence or the handoff. Python implementation changes should consider the
learning playbook, but “no material Python learning” is a valid conclusion.
Quality or dependency decisions need the quality playbook even when the result
is to defer a tool or dependency.

This router complements the configured product and verification routers; it
does not restate the governed change loop or authorize behaviour, dependency,
or approval changes.
