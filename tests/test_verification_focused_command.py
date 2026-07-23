import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sdf_cli.main import main


class FocusedVerificationCommandTest(unittest.TestCase):
    def test_verification_boundary_displays_focused_subsets(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: python-unit-tests
    command: PYTHONPATH=src python3 -m unittest discover -s tests
  - name: ruff
    command: python3 -m ruff check src tests
focused:
  - name: python-tests
    commands:
      - python-unit-tests
  - name: static-checks
    commands:
      - ruff
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo), "--check"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Focused verification:", output)
        self.assertIn("- python-tests\n  Commands:\n  - python-unit-tests", output)
        self.assertIn("- static-checks\n  Commands:\n  - ruff", output)
        self.assertIn("Focused verification boundary:", output)
        self.assertIn(
            "- They do not replace `sdf verify --repo .` as the "
            "full closeout gate.",
            output,
        )

    def test_verification_boundary_reports_unknown_focused_command_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: python-unit-tests
    command: PYTHONPATH=src python3 -m unittest discover -s tests
focused:
  - name: static-checks
    commands:
      - ruff
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo), "--check"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Focused verification visibility issues:", output)
        self.assertIn(
            "- focused verification subset static-checks references "
            "unknown command: ruff",
            output,
        )


def write_verification_config(repo: Path, content: str) -> None:
    config_dir = repo / ".sdf"
    config_dir.mkdir()
    (config_dir / "verification.yml").write_text(content.lstrip(), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
