# Core local install manifest

This document records the file contract used by `sdf init` and
`sdf init --check`. Existing receiver-owned files are inspected rather than
silently replaced.

## Core Manifest

| Path | Class | Content source | Install behavior | Purpose |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | templated, inspected, receiver-owned | SDF Front Door bridge | Write only when absent; otherwise report bridge status. | Routes agents to `.sdf/agent-instructions.md`. |
| `CLAUDE.md` | templated, inspected, receiver-owned | SDF activation bridge | Write only when absent; otherwise report bridge status. | Routes assistant guidance to `.sdf/`. |
| `.gitattributes` | inspected, receiver-owned, shared | SDF evidence attribute | Create or append the exact rule. | Marks generated evidence. |
| `.gitignore` | inspected, receiver-owned, shared | SDF handoff ignore rule | Create or append the exact rule. | Keeps local handoffs untracked. |
| `.sdf/agent-instructions.md` | copied, receiver-owned | Packaged portable resource | Write only when absent; report drift. | Portable operating entry point. |
| `.sdf/config.yml` | generated, receiver-owned | SDF CLI | Write only when absent; report configuration gaps. | Declares governance and local paths. |
| `.sdf/standard-sdf-non-claims.md` | copied, receiver-owned | Packaged portable resource | Write only when absent; report drift. | Records standard delivery limits. |
| `.sdf/verification.yml` | generated, receiver-owned | SDF CLI | Write only when absent; preserve receiver commands. | Defines trusted verification. |
| `.sdf/contracts/evidence-archive.md` | copied, receiver-owned | Packaged portable resource | Write only when absent; report drift. | Defines evidence archive shape. |
| `.sdf/contracts/verification-config.md` | copied, receiver-owned | Packaged portable resource | Write only when absent; report drift. | Defines verification configuration. |
| `.sdf/playbooks/governed-change-loop.md` | copied, receiver-owned | Packaged portable resource | Write only when absent; report drift. | Defines the governed change loop. |

## Optional Receiver Docs/Workflow Pack

Receiver-specific documentation and workflow files remain receiver-owned and
are outside this core install manifest.
