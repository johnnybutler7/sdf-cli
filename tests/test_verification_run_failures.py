import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from sdf_cli.main import main


class VerificationRunFailureTest(unittest.TestCase):
    def test_missing_config_exits_one(self):
        with tempfile.TemporaryDirectory() as directory:
            stderr = io.StringIO()

            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                exit_code = main(["verify", "--repo", directory])

        self.assertEqual(exit_code, 1)
        self.assertIn("Verification was not run", stderr.getvalue())
        self.assertIn("verification config is missing", stderr.getvalue())

    def test_invalid_config_exits_one(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_verification_config(repo, "version: 1\ncommands: []\n")
            stderr = io.StringIO()

            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                exit_code = main(["verify", "--repo", str(repo)])

        self.assertEqual(exit_code, 1)
        self.assertIn("Verification was not run", stderr.getvalue())
        self.assertIn(
            "verification config commands must not be empty",
            stderr.getvalue(),
        )

    def test_malformed_config_error_identifies_config_path(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            config_path = repo / ".sdf" / "verification.yml"
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name unit
""",
            )
            stderr = io.StringIO()

            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                exit_code = main(["verify", "--repo", str(repo)])

        self.assertEqual(exit_code, 1)
        self.assertIn(
            f"could not parse {config_path}: invalid command field: name unit",
            stderr.getvalue(),
        )

    def test_runner_does_not_write_evidence_files(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            evidence_dir = repo / ".sdf" / "evidence"
            evidence_dir.mkdir(parents=True)
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
            )

            with redirect_stdout(io.StringIO()):
                exit_code = main(["verify", "--repo", str(repo)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(list(evidence_dir.iterdir()), [])


def write_verification_config(repo: Path, content: str) -> None:
    config_dir = repo / ".sdf"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "verification.yml").write_text(content.lstrip(), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
