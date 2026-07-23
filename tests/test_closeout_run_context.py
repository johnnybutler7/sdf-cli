import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import (
    write_run_context,
    write_verification_config,
)
from tests.evidence_archive_helpers import populated_template_for
from tests.pr_body_command_helpers import run_pr_body_write


class CloseoutRunContextTest(unittest.TestCase):
    def test_pr_body_renders_declared_values_without_context_extras(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            archive = repo / ".sdf" / "evidence" / "structured-run-context"
            archive.mkdir(parents=True)
            (archive / "evidence.md").write_text(
                populated_template_for("evidence.md"), encoding="utf-8"
            )
            write_run_context(
                repo,
                "structured-run-context",
                model="unknown",
                reasoning="unknown",
                speed="unknown",
            )
            write_verification_config(repo, _ok_config())
            result = run_pr_body_write(repo, "structured-run-context")
            output = (
                repo
                / ".sdf"
                / "handoffs"
                / "structured-run-context"
                / "pr-body.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "- Declared run context: surface codex_local / model unknown / "
            "reasoning unknown / speed unknown",
            output,
        )
        self.assertNotIn("Run-context notice", output)
        self.assertNotIn("provider", output)


if __name__ == "__main__":
    unittest.main()


def _ok_config() -> str:
    return (
        "version: 1\ncommands:\n  - name: ok\n"
        "    command: python3 -c \"print('ok')\"\n"
    )
