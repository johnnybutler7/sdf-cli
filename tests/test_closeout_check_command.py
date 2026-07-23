import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tests.evidence_archive_helpers import populated_template_for

from sdf_cli import closeout_check_rendering
from sdf_cli.closeout_check import render_closeout_check_summary, run_closeout_check
from sdf_cli.evidence_archive_contract import CONTRACT_FOUR_ARCHIVE_HEADINGS
from sdf_cli.evidence_front_matter import initialize_evidence_machine_record
from sdf_cli.main import main


class CloseoutCheckCommandTest(unittest.TestCase):
    def test_closeout_navigation_is_retired(self):
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                main(["closeout", "--help"])

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("invalid choice: 'closeout'", stderr.getvalue())

    def test_closeout_check_path_is_retired(self):
        with self.assertRaises(SystemExit) as raised:
            main(["closeout", "check", "--help"])

        self.assertEqual(raised.exception.code, 2)

    def test_success_reports_evidence_verification_and_tracked_timing(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-ran.txt"
            write_archive(repo, "successful-closeout")
            write_verification_config(
                repo,
                f"""
version: 1
commands:
  - name: tracked-ok
    command: touch {marker}
    track_timing: true
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = run_closeout(repo, "successful-closeout")
            verification_ran = marker.exists()

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertTrue(verification_ran)
        self.assertIn("PASS tracked-ok", output)
        self.assertIn("SDF close summary", output)
        self.assertIn(f"- Resolved repository path: {repo.resolve()}", output)
        self.assertIn(
            "- Evidence archive: ready (.sdf/evidence/successful-closeout)",
            output,
        )
        self.assertIn("- Full verification: passed (1 checks run)", output)
        self.assertRegex(output, r"Tracked timings:\n- tracked-ok: \d+\.\d{2}s")
        self.assertIn("- Overall: passed", output)
        self.assertIn(
            "- `sdf close` records the final closeout result in:",
            output,
        )
        self.assertIn(
            "  .sdf/evidence/successful-closeout/evidence.md",
            output,
        )
        self.assertIn(
            "- It also writes and checks the local PR-body artifact.",
            output,
        )

    def test_missing_archive_is_synthesized_before_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-ran.txt"
            write_verification_config(
                repo,
                f"""
version: 1
commands:
  - name: should-not-run
    command: touch {marker}
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = run_closeout(repo, "missing-archive")
            verification_ran = marker.exists()
            evidence = repo / ".sdf" / "evidence" / "missing-archive" / "evidence.md"
            evidence_exists = evidence.exists()

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertTrue(verification_ran)
        self.assertTrue(evidence_exists)
        self.assertIn(
            "- Evidence archive: not ready (contract 5 required) "
            "(.sdf/evidence/missing-archive)",
            output,
        )
        self.assertIn(
            "- Full verification: passed (1 checks run)",
            output,
        )
        self.assertIn("Evidence archive readiness:", output)
        self.assertIn(
            "Evidence archive check: .sdf/evidence/missing-archive",
            output,
        )
        self.assertIn("present: evidence.md", output)
        self.assertIn("unresolved scaffold placeholder", output)
        self.assertIn("- Overall: failed", output)
        self.assertIn("Expected first-close stop:", output)
        self.assertIn(
            "- This is an expected evidence-completion stop, not a "
            "verification failure.",
            output,
        )
        self.assertIn(
            "- Edit `.sdf/evidence/missing-archive/evidence.md` and complete: "
            "Intent, Review focus, Limits, Guidance applied.",
            output,
        )
        self.assertIn("- Then rerun:", output)
        self.assertIn(
            f"  sdf close --repo {repo} --change-id missing-archive",
            output,
        )
        self.assertIn(
            "  .sdf/evidence/missing-archive/evidence.md",
            output,
        )
        self.assertIn(
            "- It also writes and checks the local PR-body artifact.",
            output,
        )

    def test_unready_archive_reports_missing_file_detail_before_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-ran.txt"
            (repo / ".sdf" / "evidence" / "missing-file").mkdir(parents=True)
            (
                repo / ".sdf" / "evidence" / "missing-file" / "verification.md"
            ).write_text("historical\n", encoding="utf-8")
            write_verification_config(
                repo,
                f"""
version: 1
commands:
  - name: should-not-run
    command: touch {marker}
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = run_closeout(repo, "missing-file")
            verification_ran = marker.exists()

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertFalse(verification_ran)
        self.assertIn("Evidence archive readiness:", output)
        self.assertIn("missing file: evidence.md", output)
        self.assertIn(
            "- Full verification: skipped (evidence archive is not recordable; "
            "0 checks run)",
            output,
        )

    def test_summary_rendering_is_re_exported_from_focused_module(self):
        self.assertIs(
            render_closeout_check_summary,
            closeout_check_rendering.render_closeout_check_summary,
        )

    def test_verification_failure_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "verification-fails")
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: required-fail
    command: python3 -c "import sys; sys.exit(1)"
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = run_closeout(repo, "verification-fails")

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("FAIL required-fail", output)
        self.assertIn(
            "- Evidence archive: ready (.sdf/evidence/verification-fails)",
            output,
        )
        self.assertIn("- Full verification: failed (1 checks run)", output)
        self.assertIn("- Overall: failed", output)


def run_closeout(repo: Path, change_id: str) -> int:
    result = run_closeout_check(str(repo), change_id)
    print(render_closeout_check_summary(result))
    return result.exit_code


def write_archive(repo: Path, change_id: str) -> None:
    archive = repo / ".sdf" / "evidence" / change_id
    archive.mkdir(parents=True)
    content = populated_template_for("evidence.md")
    for heading in CONTRACT_FOUR_ARCHIVE_HEADINGS:
        assert heading in content
    evidence = archive / "evidence.md"
    evidence.write_text(content, encoding="utf-8")
    initialize_evidence_machine_record(
        evidence,
        change_id=change_id,
        started_at="2026-01-01T09:00:00+00:00",
        contract_version=4,
    )


def write_verification_config(repo: Path, content: str) -> None:
    config_dir = repo / ".sdf"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "verification.yml").write_text(content.lstrip(), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
