import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from sdf_cli.main import main


class VerificationFocusedRunCommandTest(unittest.TestCase):
    def test_full_run_behaviour_is_unchanged_without_focused_option(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(repo, full_and_focused_config())
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("PASS full-only", output)
        self.assertIn("PASS focused-ok", output)
        self.assertNotIn("Focused run:", output)

    def test_focused_subset_success_runs_only_referenced_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(repo, full_and_focused_config())
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "verify",
                        "--repo",
                        str(repo),
                        "--focused",
                        "fast-feedback",
                    ]
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertNotIn("PASS full-only", output)
        self.assertIn("PASS focused-ok", output)
        self.assertIn("Focused run: fast-feedback", output)
        self.assertIn("supporting feedback only", output)
        self.assertIn("Full closeout gate: sdf verify --repo PATH", output)

    def test_required_failure_in_focused_subset_fails_run(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: focused-fail
    command: python3 -c "import sys; sys.exit(1)"
focused:
  - name: fast-feedback
    commands:
      - focused-fail
""",
            )
            stdout = io.StringIO()
            stderr = io.StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(
                    [
                        "verify",
                        "--repo",
                        str(repo),
                        "--focused",
                        "fast-feedback",
                    ]
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("FAIL focused-fail", stdout.getvalue())
        self.assertIn("Required verification command failed", stderr.getvalue())

    def test_optional_failure_in_focused_subset_does_not_fail_run(self):
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
focused:
  - name: fast-feedback
    commands:
      - optional-fail
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "verify",
                        "--repo",
                        str(repo),
                        "--focused",
                        "fast-feedback",
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "FAIL optional-fail (optional; execution continued)",
            stdout.getvalue(),
        )

    def test_unknown_focused_subset_fails_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(repo, full_and_focused_config())
            stdout = io.StringIO()
            stderr = io.StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(
                    ["verify", "--repo", str(repo), "--focused", "missing"]
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("unknown focused verification subset: missing", stderr.getvalue())
        self.assertIn("- Verification was not run", stdout.getvalue())

def full_and_focused_config() -> str:
    return """
version: 1
commands:
  - name: full-only
    command: python3 -c "print('full')"
  - name: focused-ok
    command: python3 -c "print('focused')"
focused:
  - name: fast-feedback
    commands:
      - focused-ok
"""


def write_verification_config(repo: Path, content: str) -> None:
    config_dir = repo / ".sdf"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "verification.yml").write_text(content.lstrip(), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
