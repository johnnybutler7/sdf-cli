import unittest

from sdf_cli.evidence_archive_placeholders import unresolved_scaffold_placeholders
from sdf_cli.evidence_archive_templates import (
    EvidenceArchiveTemplateContext,
    template_for,
)


class EvidenceArchiveTemplateContextTest(unittest.TestCase):
    def test_scaffold_context_does_not_prefill_human_judgement_fields(self):
        context = EvidenceArchiveTemplateContext(
            change_id="prefill-evidence-scaffold-fields",
            repository="sdf-cli (/work/sdf-cli)",
            branch="codex/prefill-evidence-scaffold-fields",
            head_ref="abc123",
        )

        evidence = template_for("evidence.md", context)

        self.assertIn("## Intent", evidence)
        self.assertIn("## Review focus", evidence)
        self.assertIn("## Limits", evidence)
        self.assertIn("## Guidance applied", evidence)
        self.assertNotIn("prefill-evidence-scaffold-fields", evidence)
        self.assertNotIn("/work/sdf-cli", evidence)
        self.assertNotIn("abc123", evidence)

    def test_scaffold_context_keeps_judgement_fields_empty(self):
        context = EvidenceArchiveTemplateContext(
            change_id="prefill-evidence-scaffold-fields",
            repository="sdf-cli (/work/sdf-cli)",
            branch="codex/prefill-evidence-scaffold-fields",
            head_ref="abc123",
        )

        evidence = template_for("evidence.md", context)

        self.assertNotIn("TBD", evidence)
        self.assertNotIn("- Command: not run yet.", evidence)
        self.assertEqual(evidence.count("## "), 4)

    def test_scaffold_prompts_explain_each_judgement_without_resolving_it(self):
        evidence = template_for("evidence.md")

        self.assertIn("<!-- What changed and why. -->", evidence)
        self.assertIn(
            "<!-- What reviewers should check, including meaningful risk. -->",
            evidence,
        )
        self.assertIn("<!-- What this change does not claim or change. -->", evidence)
        self.assertIn("<!-- Guidance that materially shaped this work. -->", evidence)
        self.assertEqual(
            [placeholder.section for placeholder in unresolved_scaffold_placeholders(
                "evidence.md", evidence
            )],
            ["## Intent", "## Review focus", "## Limits", "## Guidance applied"],
        )


if __name__ == "__main__":
    unittest.main()
