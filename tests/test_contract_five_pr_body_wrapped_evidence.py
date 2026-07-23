import tempfile
import unittest
from pathlib import Path

from tests.contract_five_pr_body_fixtures import (
    known_context,
    write_contract_five_archive,
    write_passing_verification,
)
from tests.pr_body_command_helpers import run_pr_body_write


class ContractFivePrBodyWrappedEvidenceTest(unittest.TestCase):
    def test_wrapped_paragraph_sections_do_not_publish_sentence_fragments(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_contract_five_archive(
                repo,
                "wrapped-paragraphs",
                review_focus=[
                    "Review focus begins with the complete reviewer judgement",
                    "and ends only after the installed distribution requirement.",
                ],
                guidance=[
                    "Guidance begins with the complete workflow rationale",
                    "and ends only after the single-source principle.",
                ],
                declared=known_context(),
            )
            write_passing_verification(repo)

            result = run_pr_body_write(repo, "wrapped-paragraphs")
            content = (
                repo / ".sdf/handoffs/wrapped-paragraphs/pr-body.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "- Review focus begins with the complete reviewer judgement and ends "
            "only after the installed distribution requirement.",
            content,
        )
        self.assertIn(
            "- Guidance begins with the complete workflow rationale and ends only "
            "after the single-source principle.",
            content,
        )
        self.assertNotIn(
            "- Review focus begins with the complete reviewer judgement\n", content
        )
        self.assertNotIn(
            "- Guidance begins with the complete workflow rationale\n", content
        )

    def test_wrapped_evidence_items_remain_complete_before_section_caps(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_contract_five_archive(
                repo,
                "wrapped-evidence",
                intent=wrapped_paragraph() + wrapped_items("Intent", 4),
                review_focus=wrapped_items("Review focus", 6),
                limits=wrapped_items("Limit", 6),
                guidance=wrapped_items("Guidance", 4),
                declared=known_context(),
            )
            write_passing_verification(repo)

            result = run_pr_body_write(repo, "wrapped-evidence")
            content = (
                repo / ".sdf/handoffs/wrapped-evidence/pr-body.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        for label, visible_count in (
            ("Review focus", 5),
            ("Limit", 5),
            ("Guidance", 3),
        ):
            self.assertIn(complete_item(label, visible_count), content)
            self.assertNotIn(f"{label} {visible_count + 1} is a complete", content)
        self.assertIn(
            "- A paragraph-form intent statement remains whole when naturally "
            "wrapped across source lines.",
            content,
        )
        self.assertIn(complete_item("Intent", 3), content)
        self.assertNotIn("Intent 4 is a complete", content)
        self.assertNotIn("## Machine Record", content)
        self.assertNotIn("## Guidance applied\n\n###", content)


def wrapped_items(label: str, count: int) -> list[str]:
    return [
        line
        for index in range(1, count + 1)
        for line in wrapped_item(label, index)
    ]


def wrapped_paragraph() -> list[str]:
    return [
        "A paragraph-form intent statement remains whole when naturally",
        "wrapped across source lines.",
    ]


def wrapped_item(label: str, index: int) -> list[str]:
    return [
        f"- {label} {index} is a complete reviewer-facing statement",
        "that remains attached after natural wrapping.",
    ]


def complete_item(label: str, index: int) -> str:
    return (
        f"- {label} {index} is a complete reviewer-facing statement "
        "that remains attached after natural wrapping."
    )
