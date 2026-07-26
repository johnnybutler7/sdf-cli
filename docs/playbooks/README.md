# Repository Playbooks

These are `sdf-cli`'s repository-owned standards that SDF routes into the
agent's work. They complement the portable governed change loop under `.sdf/`;
they do not replace it or grant approval to merge.

The public `sdf-cli` playbooks are working examples of repository-owned
guidance used by this project itself. They are reference material, not universal
standards or a set every receiver should copy wholesale; receiver repositories
should create or adapt the smallest relevant playbook set for their own context.

## Select Guidance By Work Type

- Read [Engineering Discipline](engineering/README.md) for a change that needs
  a decision about responsibility, boundaries, tests, maintainability, or
  critical side effects.
- Start at the [Python CLI router](python/README.md) for Python implementation,
  CLI, filesystem, Git, subprocess, tests, packaging, resources, or quality
  tooling work.
- Use [Product guidance](../product/README.md) for command-surface or product
  decisions, and [Verification guidance](../verification/README.md) for the
  configured checks and verification-specific fixtures or golden outputs.

Read the smallest set that materially applies. Record the guidance that shaped
the slice in its evidence or handoff; a concise "none material" judgement is
valid when appropriate.

## How This Fits SDF

`.sdf/config.yml` declares these routers. `.sdf/agent-instructions.md` routes
governed work through the portable loop, which selects the relevant repository
guidance and runs the trusted verification boundary. Evidence records the
applied judgement. A human reviewer retains approval and merge control.
