# Engineering Discipline Playbook

## Purpose

Use this stack-neutral guidance when a change needs an engineering judgement
beyond language syntax: ownership, boundaries, side effects, tests, or future
maintainability. It applies to this CLI's Python code, documentation, scripts,
and generated artifacts. The governed change loop remains the source for the
delivery and closeout sequence.

## Shape A Reviewable Change

- Keep one primary outcome and avoid unrelated cleanup.
- Give modules, functions, commands, adapters, and renderers clear ownership.
  Split a unit when parsing, policy, rendering, persistence, and external
  operations would change for different reasons.
- Name behaviour and state plainly. Prefer direct control flow to clever or
  indirect routing that hides the decision.
- Keep dependency direction clear: product policy should depend on a small
  local contract, while filesystem, Git, subprocess, and other provider detail
  sit at the edge.
- Separate policy (what this CLI permits or decides) from mechanism (how a
  file is written or command is run). Do not let a persistence update silently
  cause an external action.
- Add an abstraction only when it names a stable concern, protects a boundary,
  or makes variation easier to test. Similar code is not automatically a
  reason for an interface or hierarchy.

## Use SOLID As A Review Lens

Use these principles to find unclear responsibility or coupling, not to create
ceremonial classes.

- **Single responsibility:** separate concerns with distinct reasons to
  change, such as a command workflow and its Markdown renderer.
- **Open/closed:** introduce a small dispatch or strategy only when supported
  variation is real and callers should remain stable.
- **Substitution:** fakes and alternate collaborators must honour the result
  contract exercised by normal paths.
- **Interface segregation:** pass the smallest collaborator a unit needs.
- **Dependency inversion:** construct provider detail at the edge and depend on
  a narrow local protocol, callable, or value where that improves testing and
  review.

The simplest design with explicit responsibilities is preferred.

## Boundaries And Tests

Treat filesystem writes, Git calls, subprocesses, environment access, generated
evidence, approvals, and other externally visible operations as review points.
Make the operation, input, result, and failure handling visible. Preserve
human-controlled approval and merge boundaries; automation must not imply it
can make that decision.

Tests should protect behaviour and explicit contracts, not incidental internal
shape. Use focused unit tests for isolated logic; use command, artifact, or
integration tests when wiring, user-facing output, generated Markdown, or side
effects are in scope. Keep fixtures small and intentional.

For a critical boundary, identify the policy, provider operation, persisted
state, side effect, and evidence needed to review it. Cover a meaningful
non-happy path where risk warrants it.

## Review And Verification

Review the change introduced by the slice. Record a limit or uncertainty
honestly when resolving it would require wider work. Choose verification in
proportion to the risk and contract affected; passing checks support review but
do not replace reviewer understanding.

Ask: can the next maintainer see who owns this decision, where a side effect
happens, what contract the test protects, and what remains uncertain?
