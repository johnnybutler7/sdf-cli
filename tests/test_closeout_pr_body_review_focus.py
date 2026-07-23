import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import write_archive, write_verification_config
from tests.pr_body_command_helpers import run_pr_body_write


class CloseoutPrBodyReviewFocusTest(unittest.TestCase):
    def test_review_focus_drops_boundary_boilerplate(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(
                repo,
                "focused-review",
                focus_lines=[
                    "- Review the PR-body Review focus section.",
                    "- Confirm acceptance bullets remain slice-specific.",
                ],
                boundary_lines=[
                    "- Scope: rendering-only change.",
                    "- No automatic approval, merge, repair, deploy, or release.",
                    "- No local GitHub mutation or hosted behavior.",
                    (
                        "- Slice-specific non-claims: evidence.md evidence "
                        "content stays intact."
                    ),
                ],
            )
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
            )

            result = run_pr_body_write(repo, "focused-review")
            artifact = repo / ".sdf" / "handoffs" / "focused-review" / "pr-body.md"
            content = artifact.read_text(encoding="utf-8")
            review_focus = markdown_section(content, "## Review focus")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("- Review the PR-body Review focus section.", review_focus)
        self.assertIn(
            "- Confirm acceptance bullets remain slice-specific.",
            review_focus,
        )
        self.assertIn(
            "- Slice-specific non-claims: evidence.md evidence content stays intact.",
            review_focus,
        )
        self.assertNotIn("Standard SDF non-claims apply", review_focus)
        self.assertNotIn("- Scope: rendering-only change.", review_focus)
        self.assertNotIn("No automatic approval", review_focus)
        self.assertNotIn("No local GitHub mutation", review_focus)
        self.assertEqual(
            content.count(
                "[Evidence notes](.sdf/evidence/focused-review/"
                "evidence.md#acceptance--review-focus)"
            ),
            1,
        )


def markdown_section(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    section_lines: list[str] = []
    in_section = False
    for line in lines:
        if line == heading:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            section_lines.append(line)
    return "\n".join(section_lines).strip()


if __name__ == "__main__":
    unittest.main()
