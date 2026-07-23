import io
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess

from sdf_cli.verification_runner import run_verification


class VerificationRunnerFactsTest(unittest.TestCase):
    def test_runner_preserves_executor_supplied_structured_facts(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            config = repo / ".sdf"
            config.mkdir()
            (config / "verification.yml").write_text(
                "version: 1\ncommands:\n  - name: unit-tests\n    command: ignored\n",
                encoding="utf-8",
            )
            completed = CompletedProcess("ignored", 0, "", "")
            completed.verification_facts = (("test_count", 3),)

            result = run_verification(
                repo,
                executor=lambda _command, _repo: completed,
                stdout=io.StringIO(),
            )

        self.assertEqual(result.command_results[0].facts, (("test_count", 3),))


if __name__ == "__main__":
    unittest.main()
