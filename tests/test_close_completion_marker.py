import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import write_archive, write_verification_config
from tests.pr_body_command_helpers import run_handoff

SUCCESSFUL_CLOSE_COMPLETION_MARKER = (
    "SDF close complete: verification passed, evidence recorded, and local "
    "handoff checked."
)


class CloseCompletionMarkerTest(unittest.TestCase):
    def test_verification_failure_does_not_print_completion_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "verification-failure")
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: required-fail
    command: python3 -c "import sys; sys.exit(1)"
""",
            )

            result = run_handoff(repo, "verification-failure")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("closeout check: failed", result.stdout)
        self.assertIn("pr-body write: skipped", result.stdout)
        self.assertIn("1. required-fail: failed (exit 1)", result.stdout)
        self.assertNotIn(SUCCESSFUL_CLOSE_COMPLETION_MARKER, result.stdout)


if __name__ == "__main__":
    unittest.main()
