import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from sdf_cli.main import main

ROUTINE_HEADINGS = {
    "evidence.md": [
        "# Evidence",
        "## Intent",
        "## Review focus",
        "## Limits",
        "## Guidance applied",
        "## Machine Record",
    ],
}


class EvidenceArchiveScaffoldCommandTest(unittest.TestCase):
    def test_scaffold_help_includes_archive_loop_examples(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as raised:
                main(["start", "--help"])

        help_text = stdout.getvalue()
        self.assertEqual(raised.exception.code, 0)
        self.assertIn("Examples:", help_text)
        self.assertIn(
            "sdf start --change-id <change-id>",
            help_text,
        )
        self.assertIn(
            "run-context timing in the evidence.md machine record",
            help_text,
        )
        self.assertIn(
            "any supplied declared run-context values.",
            help_text,
        )
        self.assertNotIn(
            "sdf run-context write",
            help_text,
        )
        self.assertNotIn("--include-playbooks", help_text)

    def test_scaffold_creates_routine_archive_files_with_expected_headings(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            result = run_scaffold(repo, "add.cli_evidence-archive")

            archive = repo / ".sdf" / "evidence" / "add.cli_evidence-archive"
            self.assertEqual(result.exit_code, 0)
            self.assertIn(
                "Evidence archive: .sdf/evidence/add.cli_evidence-archive",
                result.stdout,
            )
            self.assertNotIn("slice timing marker:", result.stdout)
            self.assertIn(
                "run-context timing: .sdf/evidence/add.cli_evidence-archive/"
                "evidence.md machine record (created)",
                result.stdout,
            )
            self.assertFalse((repo / ".sdf" / "local").exists())
            for filename, headings in ROUTINE_HEADINGS.items():
                with self.subTest(filename=filename):
                    content = (archive / filename).read_text(encoding="utf-8")
                    self.assertIn(f"created: {filename}", result.stdout)
                    for heading in headings:
                        self.assertIn(heading, content)
                    self.assertNotIn("TBD.", content)
            self.assertFalse((archive / "verification.md").exists())
            evidence = (archive / "evidence.md").read_text(encoding="utf-8")
            self.assertNotIn("## Verification", evidence)
            self.assertNotIn("### Commands", evidence)
            self.assertNotIn("- Command: not run yet.", evidence)
            self.assertNotIn("  - Status: not run yet.", evidence)
            self.assertIn("contract: 5", evidence)
            self.assertIn("repository:", evidence)
            self.assertIn("branch:", evidence)
            self.assertNotIn("  - Timing: not recorded.", evidence)
            self.assertNotIn("  - Tracked timings: not reported.", evidence)

    def test_scaffold_includes_exactly_four_judgement_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            result = run_scaffold(
                repo,
                "add-manual-evidence-archive-scaffold",
            )

            evidence = (
                repo
                / ".sdf"
                / "evidence"
                / "add-manual-evidence-archive-scaffold"
                / "evidence.md"
            )
            content = evidence.read_text(encoding="utf-8")
            self.assertEqual(result.exit_code, 0)
            self.assertNotIn("playbooks.md", result.stdout)
            judgement_headings = [
                line for line in content.splitlines() if line.startswith("## ")
            ]
            self.assertEqual(
                judgement_headings[:-1],
                [
                    "## Intent",
                    "## Review focus",
                    "## Limits",
                    "## Guidance applied",
                ],
            )
            self.assertNotIn("Exact guidance paths consulted", content)
            self.assertNotIn("Playbook/guidance label", content)
            self.assertNotIn("compact PR handoff `## Guidance applied` text", content)
            self.assertNotIn("command evidence from `verification.md`", content)
            self.assertNotIn("playbooks.md", content)

    def test_scaffold_does_not_overwrite_existing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            review = repo / ".sdf" / "evidence" / "existing-slice" / "review.md"
            self._write_file(review, "receiver-owned review\n")

            result = run_scaffold(repo, "existing-slice")

            self.assertEqual(result.exit_code, 0)
            self.assertEqual("receiver-owned review\n", review.read_text("utf-8"))
            self.assertIn("created: evidence.md", result.stdout)
            self.assertNotIn("review.md", result.stdout)
            self.assertNotIn("verification.md", result.stdout)
            self.assertNotIn("run.md", result.stdout)

    def test_historical_sidecars_are_inert_during_scaffold(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            archive = repo / ".sdf" / "evidence" / "partial-slice"
            self._write_file(archive / "review.md", "existing review\n")
            self._write_file(archive / "verification.md", "existing verification\n")

            result = run_scaffold(repo, "partial-slice")

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                "existing review\n",
                (archive / "review.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                "existing verification\n",
                (archive / "verification.md").read_text(encoding="utf-8"),
            )
            self.assertIn("created: evidence.md", result.stdout)
            self.assertNotIn("review.md", result.stdout)
            self.assertNotIn("verification.md", result.stdout)
            self.assertNotIn("run.md", result.stdout)
            self.assertNotIn("playbooks.md", result.stdout)

    def test_invalid_change_ids_fail_clearly_and_create_nothing(self):
        unsafe_change_ids = ["", "../foo", "/tmp/foo", "foo/bar", "foo\\bar"]

        for change_id in unsafe_change_ids:
            with self.subTest(change_id=change_id):
                with tempfile.TemporaryDirectory() as directory:
                    repo = Path(directory)
                    stderr = io.StringIO()

                    with redirect_stderr(stderr):
                        with self.assertRaises(SystemExit) as raised:
                            main(
                                [
                        "start",
                                    "--repo",
                                    str(repo),
                                    "--change-id",
                                    change_id,
                                ]
                            )

                    self.assertEqual(raised.exception.code, 2)
                    self.assertIn("change-id must use only", stderr.getvalue())
                    self.assertFalse((repo / ".sdf").exists())

    def test_output_reports_created_and_present_files(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            self._write_file(
                repo / ".sdf" / "evidence" / "mixed-slice" / "review.md",
                "existing review\n",
            )

            result = run_scaffold(repo, "mixed-slice")

            self.assertEqual(result.exit_code, 0)
            self.assertIn("Evidence archive: .sdf/evidence/mixed-slice", result.stdout)
            self.assertIn("created: evidence.md", result.stdout)
            self.assertNotIn("review.md", result.stdout)
            self.assertNotIn("verification.md", result.stdout)
            self.assertNotIn("run.md", result.stdout)

    def _write_file(self, path: Path, content: str = "placeholder\n") -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


class CommandResult:
    def __init__(self, exit_code: int, stdout: str) -> None:
        self.exit_code = exit_code
        self.stdout = stdout


def run_scaffold(
    repo: Path,
    change_id: str,
) -> CommandResult:
    stdout = io.StringIO()
    argv = [
        "start",
        "--repo",
        str(repo),
        "--change-id",
        change_id,
    ]
    with redirect_stdout(stdout):
        exit_code = main(argv)
    return CommandResult(exit_code=exit_code, stdout=stdout.getvalue())
