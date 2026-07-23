"""Markdown templates for evidence archive scaffolding."""

from __future__ import annotations

from dataclasses import dataclass

from sdf_cli.evidence_archive_contract import (
    REQUIRED_ARCHIVE_HEADINGS,
)
from sdf_cli.evidence_archive_verification_template import (
    embedded_verification_template_lines,
)

STANDARD_NON_CLAIMS_REFERENCE = "`.sdf/standard-sdf-non-claims.md`"


@dataclass(frozen=True)
class EvidenceArchiveTemplateContext:
    change_id: str = "TBD"
    repository: str = "TBD"
    branch: str = "TBD"
    head_ref: str = "TBD"
    narrative_filename: str = "evidence.md"

    @property
    def archive_path(self) -> str:
        return f".sdf/evidence/{self.change_id}"

    @property
    def boundary_reference(self) -> str:
        return f"`{self.narrative_filename}` `## Boundaries / Non-Claims`"


def template_for(
    filename: str, context: EvidenceArchiveTemplateContext | None = None
) -> str:
    context = context or EvidenceArchiveTemplateContext()
    templates = {
        "evidence.md": _evidence_template,
    }
    return templates[filename](context)


def _evidence_template(context: EvidenceArchiveTemplateContext) -> str:
    del context
    lines = [REQUIRED_ARCHIVE_HEADINGS["evidence.md"][0], ""]
    for heading, prompt in _CONTRACT_FIVE_JUDGEMENT_PROMPTS.items():
        lines.extend([heading, prompt, ""])
    return "\n".join(lines)


_CONTRACT_FIVE_JUDGEMENT_PROMPTS = {
    "## Intent": "<!-- What changed and why. -->",
    "## Review focus": (
        "<!-- What reviewers should check, including meaningful risk. -->"
    ),
    "## Limits": "<!-- What this change does not claim or change. -->",
    "## Guidance applied": "<!-- Guidance that materially shaped this work. -->",
}


def contract_four_template_for(
    filename: str, context: EvidenceArchiveTemplateContext | None = None
) -> str:
    context = context or EvidenceArchiveTemplateContext()
    templates = {
        "evidence.md": _contract_four_evidence_template,
    }
    return templates[filename](context)


def _contract_four_evidence_template(
    context: EvidenceArchiveTemplateContext,
) -> str:
    return "\n".join(
        [
            "# Evidence",
            "",
            "## Request / Provenance",
            "",
            f"- Change ID: `{context.change_id}`.",
            f"- Evidence archive: `{context.archive_path}`.",
            "- Request: TBD.",
            "- Source/provenance: TBD.",
            "- Reference precedent: none consulted.",
            "",
            "## Change Summary",
            "",
            "- Change summary: TBD.",
            "- Changed surface: TBD.",
            "",
            "## Acceptance / Review Focus",
            "",
            "- Review focus: TBD.",
            "- Acceptance checks: TBD.",
            "- Deferred scope affecting review: TBD.",
            "",
            "## Scope",
            "",
            f"- Evidence path: `{context.archive_path}`.",
            "- In scope: TBD.",
            "- Out of scope: TBD.",
            "",
            "## Boundaries / Non-Claims",
            "",
            "- Standard SDF non-claims: see "
            f"{STANDARD_NON_CLAIMS_REFERENCE}.",
            "- Slice-specific non-claims: TBD.",
            "",
            "## Risk / Confidence / Limits",
            "",
            "- Risk: TBD.",
            "- Confidence: TBD.",
            "- Limits: TBD.",
            "",
            "## Guidance Applied",
            "",
            "### Consulted",
            "",
            "- Guidance consulted: TBD.",
            "",
            "### Applied",
            "",
            "- Applied guidance: none material.",
            "",
            "### Not Applicable",
            "",
            "- Not applicable: none material.",
            "",
            "### Why This Mattered",
            "",
            "- Why this mattered: no material guidance judgement to record.",
            "",
            "### Gaps / Learning",
            "",
            "- Gaps: none recorded.",
            "- Learning: none recorded.",
            "",
            *embedded_verification_template_lines(context),
            "## Run / Handoff Context",
            "",
            "- Repository / branch context: see the versioned YAML machine record.",
            "- Material execution or handoff notes: TBD.",
            "- Unknowns: TBD.",
            "",
            "## Handoff / Reviewer Notes",
            "",
            f"- Archive for reviewer inspection: `{context.archive_path}`.",
            "- Reviewer notes: TBD.",
            "- Handoff links or follow-up: TBD.",
            "",
        ]
    )
