# Python Quality Tooling Playbook

## Purpose

Quality tools support this repository's standards; they do not define quality
on their own. Use this playbook for Ruff, formatting, lint rules, typing,
complexity or module-size checks, suppressions, waivers, and Python development
dependency decisions.

## Decide Deliberately

Before adding a tool, rule, dependency, or check, state the concrete defect
class or review burden it addresses, why existing checks are insufficient, its
local and continuous-verification impact, and how contributors can run it.
Prefer a small, predictable toolset. Deferral is valid when the current
boundary is sufficient.

Keep formatter adoption separate from behavioural changes unless combining
them is necessary and explained. Do not add a formatter simply because Python
projects often have one; adopt it when it removes a real style or review cost.

`sdf-cli` currently uses Ruff for a narrow lint/style baseline. Broaden rules
only in a focused quality slice that explains the new signal and expected
remediation. Treat typing, complexity, and maintainability checks as useful
contract or design signals—not automatic ceremony or proof that code is good.

## Respond To Findings

First consider a simpler design, clearer naming, or a smaller responsibility.
For CLI code, mixed parsing, validation, policy, rendering, and side effects
often indicate a design problem before they indicate a tooling problem.

Use a suppression or waiver only when fixing the warning now is less safe or
less proportionate than accepting it. Keep it narrow and record:

- the rule or check and exact scope;
- why it is accepted now;
- the risk or trade-off; and
- a concrete signal that should reopen the decision.

Do not weaken an existing check, add a broad suppression, or add a dependency
without the same deliberate justification. A waiver must not become permission
for an oversized or mixed-responsibility unit to keep growing.

## Verification

Run relevant fast feedback while working when useful, then use the configured
verification boundary for governed closeout. Keep the actual command and tool
configuration in [verification guidance](../../verification/README.md) and
[`.sdf/verification.yml`](../../../.sdf/verification.yml); do not duplicate a
second quality gate here.

Record a quality-tooling decision, including a justified deferral, in evidence
or the handoff when it materially shaped the slice.
