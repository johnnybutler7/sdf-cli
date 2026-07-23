import io
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from sdf_cli.main import main


class VerificationRunCommandTest(unittest.TestCase):
    def test_verification_display_remains_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: visible-only
    command: python3 -c "print('EXECUTED_VISIBLE_ONLY')"
""",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo), "--check"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("- visible-only", output)
        self.assertIn(
            "  Command: python3 -c \"print('EXECUTED_VISIBLE_ONLY')\"",
            output,
        )
        self.assertIn("  Required: yes", output)
        self.assertIn("  Track timing: no", output)
        self.assertNotIn("EXECUTED_VISIBLE_ONLY\n", output)
        self.assertNotIn("PASS visible-only", output)

    def test_verification_display_shows_tracked_timing_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: tracked
    command: python3 -c "print('tracked')"
    track_timing: true
""",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo), "--check"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("- tracked", output)
        self.assertIn("  Track timing: yes", output)

    def test_verification_run_exits_zero_when_commands_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("==> ok: python3 -c \"print('ok')\"", output)
        self.assertIn("ok", output)
        self.assertIn("PASS ok", output)
        self.assertIn("SDF verify summary", output)
        self.assertIn(f"Resolved repository path: {repo.resolve()}", output)
        self.assertRegex(
            output,
            re.escape("- python3 -c \"print('ok')\": passed in ") + r"\d+\.\d{2}s",
        )
        self.assertIn("- Overall result: passed", output)
        self.assertRegex(output, r"- Total duration: \d+\.\d{2}s")
        self.assertIn("- No evidence artifact was generated.", output)

    def test_required_governance_points_to_evidence_and_pr_body_closeout(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_required_sdf_config(repo)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        for expected in (
            "Governed closeout:",
            "- governance_mode: required detected in .sdf/config.yml.",
            "- Normal next step: make the change, then close it with evidence:",
            f"sdf close --repo {repo} --change-id <change-id>",
            "- The first close creates evidence and may stop for evidence "
            "completion; complete it, then close again.",
            "Use the checked generated PR-body handoff as the default PR body",
        ):
            self.assertIn(expected, output)
        self.assertNotIn("sdf start", output)

    def test_verification_run_surfaces_tracked_timing_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: tracked
    command: python3 -c "print('tracked')"
    track_timing: true
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertRegex(
            output,
            re.escape("- python3 -c \"print('tracked')\": passed in ")
            + r"\d+\.\d{2}s \(tracked timing\)",
        )
        self.assertRegex(output, r"Tracked timings:\n- tracked: \d+\.\d{2}s")

    def test_commands_run_from_selected_repo_root(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / "repo-marker.txt").write_text("present", encoding="utf-8")
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: cwd-check
    command: python3 -c "print(open('repo-marker.txt').read())"
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo)])

        self.assertEqual(exit_code, 0)
        self.assertIn("present", stdout.getvalue())

    def test_required_failure_exits_one_and_stops(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: required-fail
    command: python3 -c "import sys; sys.exit(1)"
  - name: skipped
    command: python3 -c "print('skipped')"
""",
            )
            stdout = io.StringIO()
            stderr = io.StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(["verify", "--repo", str(repo)])

        self.assertEqual(exit_code, 1)
        self.assertIn("FAIL required-fail", stdout.getvalue())
        self.assertNotIn("skipped", stdout.getvalue())
        self.assertIn(
            "Required verification command failed; execution stopped: required-fail",
            stderr.getvalue(),
        )

    def test_optional_failure_continues(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: optional-fail
    command: python3 -c "import sys; sys.exit(1)"
    required: false
  - name: later-pass
    command: python3 -c "print('later')"
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("FAIL optional-fail (optional; execution continued)", output)
        self.assertIn("PASS later-pass", output)

    def test_invalid_repo_path_exits_two_through_argparse(self):
        missing_repo = Path(tempfile.gettempdir()) / "sdf-cli-missing-run-repo"
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                main(["verify", "--repo", str(missing_repo)])

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("repo path is not a readable directory", stderr.getvalue())

def write_verification_config(repo: Path, content: str) -> None:
    config_dir = repo / ".sdf"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "verification.yml").write_text(content.lstrip(), encoding="utf-8")


def write_required_sdf_config(repo: Path) -> None:
    config_dir = repo / ".sdf"
    config_dir.mkdir(exist_ok=True)
    config_path = config_dir / "config.yml"
    config_path.write_text("governance_mode: required\n", encoding="utf-8")
