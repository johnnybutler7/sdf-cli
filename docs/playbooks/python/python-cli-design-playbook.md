# Python CLI Design Playbook

## Purpose

Use this playbook to keep `sdf-cli` commands small, testable, and reviewable.
It applies when changing command behaviour, options, output, exit semantics,
generated artifacts, or a filesystem, Git, subprocess, environment, or clock
boundary.

## Command Shape

- Keep argument parsing thin and at the CLI edge. `main.py` may build parsers,
  map final exit codes, and print final output; it should not accumulate command
  policy, artifact rendering, mutation, and orchestration.
- Delegate a command to a focused workflow when behaviour is larger than its
  parsing glue. Keep validation, policy decisions, execution, and rendering
  distinguishable.
- Separate execution from rendering. Return an immutable or otherwise explicit
  result object when that makes command outcome and failure handling clear;
  render it at the edge rather than printing from deep logic.
- Keep modules focused. Extract a renderer, validator, writer, or adapter when
  it gives a concern one clear reason to change—not merely to add a pattern.

## Make Side Effects Reviewable

Treat filesystem writes, Git commands, subprocess invocation, environment
reads, and time as explicit boundaries. Construct concrete collaborators at the
edge and inject a clock, command runner, path resolver, or environment access
where that makes a workflow deterministic and easier to test. Keep pure or
low-side-effect functions pure where practical.

An adapter can turn a noisy external result into a small local contract. A
builder can clarify generated Markdown with named sections. A dispatch table or
strategy is useful only when supported variation is real. These patterns should
expose a boundary, not add ceremony.

Avoid hidden automation. In particular, generated evidence and Markdown are
public contracts: make their inputs, stable shape, and assertions clear.
Preserve stable command output and exit-code semantics unless the change
explicitly authorizes them. Approval and merge remain human-controlled
boundaries.

## Test The Contract

Prefer focused behavioural tests over tests tied to internal call order or
internal implementation shape. Test a command at its boundary when options,
routing, output, exit codes, generated artifacts, or side effects change.
Test isolated domain logic directly when it has a clear contract. Use small
fixtures and precise artifact assertions for Markdown, YAML, JSON, and text.

Use fakes that honour the same relevant result contract as the real boundary.
Cover failure paths when a boundary can fail in a way users or reviewers need
to understand. Do not replace the repository verification boundary with only
focused tests.

## Design Review Prompts

- Is parsing separate from orchestration and domain behaviour?
- Can a reviewer locate each side effect and see its result or failure path?
- Does a collaborator expose only the capability this workflow needs?
- Is policy separated from provider mechanism?
- Is an abstraction solving a present boundary or merely anticipating one?
- Do tests protect user-visible behaviour and generated contracts?

Use the [Engineering Discipline](../engineering/README.md) playbook for the
stack-neutral responsibility and boundary review lens, and [Python Learning](python-learning.md)
when the slice reveals a reusable Python-specific lesson.
