import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sdf_cli.main import main
from sdf_cli.receiver_scaffold_content import (
    STARTER_VERIFICATION_PLACEHOLDER_COMMAND,
    STARTER_VERIFICATION_PLACEHOLDER_NAME,
)


class VerificationPlaceholderCommandTest(unittest.TestCase):
    def test_verification_boundary_explains_starter_placeholder(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            self._write_config(
                repo,
                f"""
version: 1
commands:
  - name: {STARTER_VERIFICATION_PLACEHOLDER_NAME}
    command: "{STARTER_VERIFICATION_PLACEHOLDER_COMMAND}"
    required: true
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo), "--check"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn(f"- {STARTER_VERIFICATION_PLACEHOLDER_NAME}", output)
        self.assertIn("Receiver verification placeholder detected:", output)
        self.assertIn(
            "- The scaffolded placeholder fails intentionally.",
            output,
        )
        self.assertIn(
            "- Replace it in .sdf/verification.yml with receiver-owned commands.",
            output,
        )
        self.assertIn("- Then run:\n  sdf verify --repo <receiver>", output)
        self.assertIn("Overall: ready", output)

    def test_verification_boundary_does_not_flag_receiver_owned_command_name(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            self._write_config(
                repo,
                f"""
version: 1
commands:
  - name: {STARTER_VERIFICATION_PLACEHOLDER_NAME}
    command: python3 -m unittest
    required: true
""",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["verify", "--repo", str(repo), "--check"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn(f"- {STARTER_VERIFICATION_PLACEHOLDER_NAME}", output)
        self.assertNotIn("Receiver verification placeholder detected:", output)

    def _write_config(self, repo: Path, content: str) -> None:
        config_dir = repo / ".sdf"
        config_dir.mkdir()
        (config_dir / "verification.yml").write_text(
            content.lstrip(),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
