import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from sdf_cli.main import main

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "repos"


class VerificationCommandTest(unittest.TestCase):
    def test_current_repo_verification_boundary_is_ready(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["verify", "--repo", ".", "--check"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("SDF verify check", output)
        self.assertIn("Repository: .", output)
        self.assertIn("Config: .sdf/verification.yml (present)", output)
        self.assertIn("Configured commands:", output)
        self.assertIn("- python-unit-tests", output)
        self.assertIn(
            "  Command: PYTHONPATH=src:tests python3 -m unittest "
            "$(find tests -maxdepth 1 -name \"test_*.py\" "
            "! -name \"test_wheel_packaging_smoke.py\" "
            "! -name \"test_sdist_packaging_smoke.py\" "
            "-exec basename {} .py \\; | sort)",
            output,
        )
        self.assertIn("  Required: yes", output)
        self.assertIn("- ruff", output)
        self.assertIn("  Command: python3 -m ruff check src tests", output)
        self.assertIn(
            "  Command: python3 scripts/check_python_module_size.py src tests",
            output,
        )
        self.assertIn("- install-surface-smoke", output)
        self.assertIn(
            "  Command: python3 scripts/check_editable_install.py --upgrade-pip "
            "--skip-full-verification-run",
            output,
        )
        self.assertIn("- source-distribution-packaging-smoke", output)
        self.assertIn(
            "  Command: PYTHONPATH=src python3 -m unittest "
            "tests.test_sdist_packaging_smoke",
            output,
        )
        self.assertIn(
            "  Command: PYTHONPATH=src python3 -m sdf_cli.main --help",
            output,
        )
        self.assertIn(
            "  Command: PYTHONPATH=src python3 -m sdf_cli.main --version",
            output,
        )
        self.assertIn(
            "  Command: PYTHONPATH=src python3 -m sdf_cli.main status --repo .",
            output,
        )
        self.assertIn(
            "  Command: PYTHONPATH=src python3 -m sdf_cli.main guidance --repo .",
            output,
        )
        self.assertIn("Focused verification:\n- not configured", output)
        self.assertIn("Focused verification boundary:", output)
        self.assertIn(
            "- Focused subsets are read-only visibility here.",
            output,
        )
        self.assertIn(
            "- They are supporting feedback during a slice.",
            output,
        )
        self.assertIn(
            "- They do not replace `sdf verify --repo .` as the "
            "full closeout gate.",
            output,
        )
        self.assertIn("Execution boundary:", output)
        self.assertIn(
            "- `sdf verify` executes the configured commands "
            "from the selected repository.",
            output,
        )
        self.assertIn("- Required command failure fails the run.", output)
        self.assertIn(
            "- Optional command failure is reported but does not fail the run.",
            output,
        )
        self.assertIn("- This command does not write evidence files.", output)
        self.assertIn("- No PR body is updated.", output)
        self.assertIn(
            "- No approve, merge, repair, deploy, or release action is performed.",
            output,
        )
        self.assertIn("Overall: ready", output)

    def test_minimal_receiver_verification_boundary_is_ready(self):
        repo = FIXTURE_ROOT / "minimal-sdf-receiver"
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["verify", "--repo", str(repo), "--check"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn(f"Repository: {repo}", output)
        self.assertIn("Config: .sdf/verification.yml (present)", output)
        self.assertIn("- fixture verification", output)
        self.assertIn("  Command: python3 -m unittest", output)
        self.assertIn("  Required: yes", output)
        self.assertIn("Execution boundary:", output)
        self.assertIn("Overall: ready", output)

    def test_verification_boundary_shows_optional_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            config_dir = repo / ".sdf"
            config_dir.mkdir()
            (config_dir / "verification.yml").write_text(
                """
version: 1
commands:
  - name: optional-style
    command: python3 -m ruff check src tests
    required: false
""".lstrip(),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo), "--check"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("- optional-style", output)
        self.assertIn("  Command: python3 -m ruff check src tests", output)
        self.assertIn("  Required: no", output)
        self.assertIn("Focused verification:\n- not configured", output)

    def test_missing_verification_config_is_incomplete(self):
        repo = FIXTURE_ROOT / "incomplete-sdf-receiver"
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["verify", "--repo", str(repo), "--check"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("Config: .sdf/verification.yml (missing)", output)
        self.assertIn("Configured commands:\n- none discovered", output)
        self.assertIn("Recovery:", output)
        self.assertIn(f"`sdf status --repo {repo}`", output)
        self.assertIn(f"`sdf init --repo {repo}`", output)
        self.assertIn(f"`sdf init --repo {repo} --check`", output)
        self.assertIn("Execution boundary:", output)
        self.assertIn("Overall: incomplete", output)

    def test_empty_verification_config_is_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            config_dir = repo / ".sdf"
            config_dir.mkdir()
            (config_dir / "verification.yml").write_text(
                "commands:\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo), "--check"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("Config: .sdf/verification.yml (present)", output)
        self.assertIn("Configured commands:\n- none discovered", output)
        self.assertIn("Recovery:", output)
        self.assertIn("Add receiver-owned commands to `.sdf/verification.yml`", output)
        self.assertIn(f"`sdf verify --repo {repo}`", output)
        self.assertIn("Overall: incomplete", output)

    def test_invalid_repo_path_exits_with_useful_message(self):
        missing_repo = Path(tempfile.gettempdir()) / "sdf-cli-missing-verification-repo"
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                main(["verify", "--repo", str(missing_repo), "--check"])

        self.assertEqual(raised.exception.code, 2)
        error = stderr.getvalue()
        self.assertIn("repo path is not a readable directory", error)
        self.assertIn("Recovery:", error)
        self.assertIn("--repo /path/to/receiver", error)

    def test_verification_run_rejects_removed_evidence_file_option(self):
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                main(
                    [
                        "verify",
                        "--repo",
                        ".",
                        "--evidence-file",
                        "evidence.md",
                    ]
                )

        self.assertEqual(raised.exception.code, 2)
        self.assertIn(
            "unrecognized arguments: --evidence-file evidence.md",
            stderr.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
