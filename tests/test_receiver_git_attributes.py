import tempfile
import unittest
from pathlib import Path

from sdf_cli.receiver_git_attributes import (
    SDF_EVIDENCE_GENERATED_ATTRIBUTE,
    ensure_sdf_evidence_generated_attribute,
)


class ReceiverGitAttributesTest(unittest.TestCase):
    def test_creates_missing_file_with_evidence_rule(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".gitattributes"

            self.assertEqual("created", ensure_sdf_evidence_generated_attribute(path))
            self.assertEqual(
                SDF_EVIDENCE_GENERATED_ATTRIBUTE + "\n",
                path.read_text(encoding="utf-8"),
            )

    def test_appends_missing_rule_without_reformatting_content(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".gitattributes"
            path.write_text("*.png binary", encoding="utf-8")

            self.assertEqual("updated", ensure_sdf_evidence_generated_attribute(path))
            self.assertEqual(
                "*.png binary\n" + SDF_EVIDENCE_GENERATED_ATTRIBUTE + "\n",
                path.read_text(encoding="utf-8"),
            )

    def test_leaves_existing_exact_rule_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".gitattributes"
            content = SDF_EVIDENCE_GENERATED_ATTRIBUTE + "\n*.md text\n"
            path.write_text(content, encoding="utf-8")

            self.assertEqual("current", ensure_sdf_evidence_generated_attribute(path))
            self.assertEqual(content, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
