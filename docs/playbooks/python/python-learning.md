# Python Learning

## Purpose

Capture a concise, reusable Python or Python-CLI lesson only when a change
reveals something that will improve future work in this repository.

## When A Lesson Is Material

A useful lesson may concern:

- a Python language behaviour that affected correctness;
- a standard-library, packaging, or resource boundary;
- subprocess, filesystem, or Git interaction;
- test isolation, typing, dataclass, command-line parsing, or exit semantics;
- an architectural pattern that proved useful in this CLI;
- a recurring implementation trap; or
- a product-specific way this CLI uses Python effectively.

Do not invent a lesson for every change. “No material Python learning” is a
valid conclusion.

## Record It Briefly

When a lesson is material, add one short paragraph or up to three bullets to
the evidence `Guidance applied` section. Tie it to the actual change, explain
why it matters in `sdf-cli`, and note a relevant trade-off when one exists.

Example: **Python learning:** A command accepts a narrow runner callable so a
test can return a controlled subprocess result without invoking a shell. This
makes the execution boundary visible and keeps command tests deterministic.

Avoid generic tutorials, ungrounded claims, and pattern labels that do not help
the next maintainer. The learning note should be reusable, not a changelog.
