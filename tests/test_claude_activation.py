import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sdf_cli.main import main
from sdf_cli.receiver_scaffold_content import starter_content
from sdf_cli.receiver_scaffold_inspection import inspect_receiver_scaffold


class ClaudeActivationTest(unittest.TestCase):
    def test_scaffold_writes_compact_claude_bridge_when_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            with redirect_stdout(io.StringIO()):
                exit_code = main(
                    ["init", "--repo", str(repo)]
                )

            content = (repo / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            "# Claude guidance\n\n"
            "This repository uses SDF guidance for governed AI-assisted delivery.\n\n"
            "Before making changes, read:\n\n"
            "- `.sdf/agent-instructions.md`\n\n"
            "SDF-specific operating guidance lives under `.sdf/`.\n",
            content,
        )

    def test_scaffold_preserves_existing_claude_guidance(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            existing = "receiver-owned Claude guidance\n"
            (repo / "CLAUDE.md").write_text(existing, encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                exit_code = main(
                    ["init", "--repo", str(repo)]
                )

            actual = (repo / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertEqual(existing, actual)

    def test_inspection_reports_existing_claude_file_without_bridge(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "CLAUDE.md").write_text(
                "receiver-owned Claude guidance\n", encoding="utf-8"
            )
            result = inspect_receiver_scaffold(directory)

        self.assertEqual("drifted", self._status_for(result, "CLAUDE.md"))

    def test_inspection_recognizes_existing_claude_activation_bridge(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "CLAUDE.md").write_text(
                starter_content("CLAUDE.md"), encoding="utf-8"
            )
            result = inspect_receiver_scaffold(directory)

        self.assertEqual("matching", self._status_for(result, "CLAUDE.md"))

    def _status_for(self, result: object, path: str) -> str:
        return next(
            inspection.status
            for inspection in result.inspections  # type: ignore[attr-defined]
            if inspection.entry.path == path
        )


if __name__ == "__main__":
    unittest.main()
