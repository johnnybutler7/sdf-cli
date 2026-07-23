import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from sdf_cli.evidence_archive_scaffold import scaffold_evidence_archive


class EvidenceArchiveScaffoldTimingTest(unittest.TestCase):
    def test_scaffold_does_not_create_local_runtime_state(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            result = scaffold_evidence_archive(
                str(repo),
                "timed-archive",
                slice_timing_clock=lambda: datetime(
                    2026,
                    1,
                    1,
                    9,
                    30,
                    tzinfo=timezone.utc,
                ),
            )
            self.assertEqual(result.exit_code, 0)
            archive = repo / ".sdf" / "evidence" / "timed-archive"
            self.assertTrue(archive.is_dir())
            content = (archive / "evidence.md").read_text(encoding="utf-8")
            self.assertTrue(result.run_context_timing_created)
            self.assertIn(
                'started_at: "2026-01-01T09:30:00+00:00"',
                content,
            )
            self.assertIn("closed_at: null", content)
            self.assertFalse((repo / ".sdf" / "local").exists())

    def test_scaffold_creates_only_archive_files(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            result = scaffold_evidence_archive(str(repo), "archive-only")
            self.assertEqual(result.exit_code, 0)
            self.assertTrue((repo / ".sdf" / "evidence" / "archive-only").is_dir())
            self.assertTrue(
                (repo / ".sdf" / "evidence" / "archive-only" / "evidence.md").is_file()
            )
            self.assertFalse((repo / ".sdf" / "work-items").exists())
            self.assertFalse((repo / ".sdf" / "local").exists())


if __name__ == "__main__":
    unittest.main()
