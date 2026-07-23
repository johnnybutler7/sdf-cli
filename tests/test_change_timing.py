import io
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tests.closeout_summary_fixtures import replace_section, write_verification_config

from sdf_cli.closeout_handoff import run_closeout_handoff
from sdf_cli.evidence_archive_scaffold import scaffold_evidence_archive
from sdf_cli.run_context import load_run_context
from sdf_cli.run_context_writer import write_run_context_artifact


class ChangeTimingTest(unittest.TestCase):
    def test_scaffold_and_write_preserve_only_started_at(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            started_at = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)
            scaffold_evidence_archive(
                str(repo), "minimal-timing", slice_timing_clock=lambda: started_at
            )
            write_run_context_artifact(
                repo=str(repo), change_id="minimal-timing", surface="codex_local",
                model="gpt-5.5", reasoning="medium", speed="fast",
            )
            context = load_run_context(repo, ".sdf/evidence/minimal-timing")

        assert context is not None
        self.assertEqual(context.started_at, "2026-01-01T09:00:00+00:00")
        self.assertIsNone(context.closed_at)

    def test_successful_handoff_sets_closed_at_without_rendering_timing(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            scaffold_evidence_archive(str(repo), "close-timing")
            evidence = repo / ".sdf/evidence/close-timing/evidence.md"
            content = evidence.read_text(encoding="utf-8")
            for heading, lines in _judgement_sections().items():
                content = replace_section(content, heading, lines)
            evidence.write_text(content, encoding="utf-8")
            write_verification_config(repo, _ok_config())
            write_run_context_artifact(
                repo=str(repo),
                change_id="close-timing",
                surface="codex_local",
                model="gpt-5.5",
                reasoning="medium",
                speed="fast",
            )
            result = run_closeout_handoff(
                repo=str(repo),
                change_id="close-timing",
                stdout=io.StringIO(),
                stderr=io.StringIO(),
                slice_timing_clock=lambda: datetime(
                    2026, 1, 1, 9, 12, 34, tzinfo=timezone.utc
                ),
            )
            context = load_run_context(repo, ".sdf/evidence/close-timing")
            handoff = (repo / ".sdf/handoffs/close-timing/pr-body.md").read_text()

        self.assertEqual(result.exit_code, 0)
        assert context is not None
        self.assertEqual(context.closed_at, "2026-01-01T09:12:34+00:00")
        self.assertNotIn("started_at", handoff)
        self.assertNotIn("closed_at", handoff)


if __name__ == "__main__":
    unittest.main()


def _ok_config() -> str:
    return (
        "version: 1\ncommands:\n  - name: ok\n"
        "    command: python3 -c \"print('ok')\"\n"
    )


def _judgement_sections() -> dict[str, list[str]]:
    return {
        "## Intent": ["- Exercise close timing with contract-5 evidence."],
        "## Review focus": ["- Confirm handoff timing does not leak timestamps."],
        "## Limits": ["- Timing fixture only."],
        "## Guidance applied": ["- None material for this fixture."],
    }
