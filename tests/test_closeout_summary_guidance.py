import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import (
    write_archive,
    write_verification_config,
)
from tests.pr_body_command_helpers import run_pr_body_write


class CloseoutSummaryGuidanceTest(unittest.TestCase):
    def test_uses_consulted_playbooks_only_as_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(
                repo,
                "consulted-fallback",
                playbook_applied_lines=[],
                playbook_consulted_lines=[
                    "- `.sdf/playbooks/engineering.md`.",
                    "- `docs/playbooks/python/README.md`.",
                ],
            )
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
            )
            result = run_pr_body_write(repo, "consulted-fallback")
            output = (
                repo / ".sdf" / "handoffs" / "consulted-fallback" / "pr-body.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("## Guidance applied", output)
        self.assertIn("- Consulted: `.sdf/playbooks/engineering.md`.", output)
        self.assertIn("- Consulted: `docs/playbooks/python/README.md`.", output)
        self.assertIn(
            "- [Evidence notes](.sdf/evidence/consulted-fallback/"
            "evidence.md#guidance-applied)",
            output,
        )


if __name__ == "__main__":
    unittest.main()
