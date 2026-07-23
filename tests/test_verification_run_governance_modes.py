import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sdf_cli.main import main


class VerificationRunGovernanceModesTest(unittest.TestCase):
    def test_inactive_governance_reports_lightweight_installed_state(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_sdf_config(repo, "governance_mode: inactive\n")
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
        self.assertIn("Governance mode:", output)
        self.assertIn(
            "- governance_mode: inactive detected in .sdf/config.yml.",
            output,
        )
        self.assertIn(
            "- SDF Front Door is installed but governed closeout is not "
            "required for this run.",
            output,
        )
        self.assertNotIn("Governed closeout:", output)
        self.assertNotIn("sdf start", output)
        self.assertNotIn("sdf closeout handoff", output)


def write_sdf_config(repo: Path, content: str) -> None:
    config_dir = repo / ".sdf"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "config.yml").write_text(content, encoding="utf-8")


def write_verification_config(repo: Path, content: str) -> None:
    config_dir = repo / ".sdf"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "verification.yml").write_text(content.lstrip(), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
