# Add your engineering standards to SDF

Installing SDF gives the repository a governed change loop and a trusted
verification boundary. The next step is to connect the repository's own
engineering standards so agents can select and apply the guidance relevant to
each change.

This is how SDF becomes specific to your repository: **repository-owned
standards that SDF routes into the agent's work**. SDF provides the portable
governed loop; your team owns its standards, playbooks, verification, and
evidence.

Standards mapping is a separate governed change. Open its draft pull request
against the repository's current evaluation or integration baseline, using the
established branch and PR workflow. It is not an automatic continuation of an
SDF installation, and it does not require merging anything into `main`.

## Start with the guidance you already have

Before creating new playbooks, inspect the repository for authoritative
guidance that agents can reuse or link to. Useful sources often include:

- `AGENTS.md`, `CLAUDE.md`, and `CONTRIBUTING.md`;
- architecture decision records and engineering handbooks;
- test documentation, CI workflows, and deployment or operational runbooks;
- framework- or language-specific guidance;
- recurring review feedback; and
- stable patterns already present in the codebase.

Prefer linking to or reusing the authoritative source rather than duplicating
it. Create focused new guidance only where an important standard is missing or
too diffuse to apply reliably during a change.

## What playbooks are

Playbooks are focused, repository-owned guidance. They can cover, for example:

- architecture and component boundaries;
- testing expectations;
- framework and language conventions;
- security-sensitive areas;
- maintainability rules;
- domain and product constraints;
- deployment or operational boundaries; and
- review expectations for risky changes.

They are not SDF's universal engineering standards, large process manuals, or
generic best-practice collections. Keep each playbook small enough that an
agent can select and apply it only when it is materially relevant to the work.

## Route your playbooks through SDF

List repository-owned guidance in `.sdf/config.yml`. The `name` gives it a
human-readable identity, `path` points to the repository-owned source, and
`categories` help the agent select relevant guidance. The governed loop should
read the smallest materially relevant set and record in evidence which guidance
shaped the change.

The [SDF CLI configuration](https://github.com/johnnybutler7/sdf-cli/blob/main/.sdf/config.yml)
and its [repository-owned playbooks](https://github.com/johnnybutler7/sdf-cli/tree/main/docs/playbooks)
are working examples. SDF CLI uses its own guidance for engineering discipline,
Python and CLI implementation, product decisions, and verification-specific
work. Adapt the approach to your repository; do not copy these playbooks
wholesale.

```yaml
receiver_playbooks:
  - name: SDF CLI engineering discipline
    path: docs/playbooks/engineering/README.md
    categories:
      - engineering
      - architecture
      - maintainability
      - testing

  - name: SDF CLI Python guidance
    path: docs/playbooks/python/README.md
    categories:
      - implementation
      - python
      - cli
      - filesystem
      - git
      - testing
```

## Begin with a small first slice

Start with the few standards whose absence repeatedly causes poor
implementation decisions, rework, architecture drift, weak testing, difficult
review, or unsafe changes. A useful first structure might be:

```text
docs/playbooks/
  engineering.md
  testing.md
  architecture.md
```

One focused document can also be enough initially:

```text
docs/playbooks/engineering-standards.md
```

Let the playbook set evolve from real governed changes rather than attempting a
large upfront documentation exercise.

## Ask your coding agent to map your standards

> Using this repository's installed SDF Front Door, assess the engineering
> guidance already present in the repository.
>
> Identify the smallest useful set of repository-owned playbooks that would
> help coding agents make better implementation and review decisions. Reuse and
> link existing authoritative documentation where possible rather than
> duplicating it.
>
> Propose:
>
> - which standards should become SDF playbooks;
> - where each playbook should live;
> - the categories that should route relevant work to it;
> - any duplicated, conflicting, or outdated guidance; and
> - the smallest first implementation slice.
>
> Use the SDF CLI repository as a working reference:
>
> - https://github.com/johnnybutler7/sdf-cli/blob/main/.sdf/config.yml
> - https://github.com/johnnybutler7/sdf-cli/tree/main/docs/playbooks
>
> Do not copy its standards wholesale. Adapt the approach to this repository's
> stack, architecture, team practices, and risks.
>
> Treat this as a separate governed change. Use the repository's established
> branch and PR workflow, open a draft pull request against its current
> evaluation or integration baseline, and do not approve or merge it.
