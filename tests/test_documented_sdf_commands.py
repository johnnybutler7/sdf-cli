import tempfile
import unittest
from pathlib import Path

from scripts.check_documented_sdf_commands import (
    HISTORICAL_MARKER,
    SourceModuleInvocation,
    UnsupportedCommand,
    ordinary_source_module_invocations,
    render,
    unsupported_commands,
)


class DocumentedSdfCommandsTest(unittest.TestCase):
    def test_reports_file_line_and_unsupported_command(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "docs" / "workflows" / "guide.md"
            self._write(document, "Run `sdf retired-command --repo .`.\n")

            findings = unsupported_commands(root, frozenset({"close", "verify"}))

        self.assertEqual(
            findings,
            (UnsupportedCommand(document, 1, "retired-command"),),
        )
        self.assertIn("guide.md:1: sdf retired-command", render(findings))

    def test_accepts_registered_commands_in_inline_and_fenced_examples(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "docs" / "workflows" / "guide.md"
            self._write(document, "Use `sdf close`.\n```sh\nsdf verify --repo .\n```\n")

            findings = unsupported_commands(root, frozenset({"close", "verify"}))

        self.assertEqual(findings, ())

    def test_skips_clearly_marked_historical_documents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "docs" / "verification" / "record.md"
            self._write(document, f"{HISTORICAL_MARKER}\n`sdf retired-command`\n")

            findings = unsupported_commands(root, frozenset({"close"}))

        self.assertEqual(findings, ())

    def test_reports_ordinary_source_module_invocation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "README.md"
            self._write(document, "```sh\npython3 -m sdf_cli.main verify\n```\n")

            findings = ordinary_source_module_invocations(root)

        self.assertEqual(findings, (SourceModuleInvocation(document, 2),))

    def test_allows_explicitly_labelled_source_module_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "README.md"
            self._write(
                document,
                "## Source-Module Fallback\n\n```sh\n"
                "PYTHONPATH=src python3 -m sdf_cli.main verify\n```\n",
            )

            findings = ordinary_source_module_invocations(root)

        self.assertEqual(findings, ())

    def test_source_only_failure_has_one_final_failed_status(self):
        finding = SourceModuleInvocation(Path("README.md"), 12)

        report = render((), (finding,))

        self.assertIn("Ordinary source-module invocations:", report)
        self.assertIn("README.md:12", report)
        self.assertEqual(report.count("Overall:"), 1)
        self.assertTrue(report.endswith("Overall: failed"))

    def _write(self, path: Path, contents: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
