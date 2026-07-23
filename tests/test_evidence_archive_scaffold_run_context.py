import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sdf_cli.main import main
from sdf_cli.run_context import load_run_context


class EvidenceArchiveScaffoldRunContextTest(unittest.TestCase):
    def test_scaffold_with_partial_declaration_writes_all_four_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "start",
                        "--repo",
                        str(repo),
                        "--change-id",
                        "declared",
                        "--surface",
                        "codex_local",
                    ]
                )
            context = load_run_context(repo, ".sdf/evidence/declared")

        self.assertEqual(exit_code, 0)
        assert context is not None
        self.assertEqual(
            context.declared,
            {
                "surface": "codex_local",
                "model": "unknown",
                "reasoning": "unknown",
                "speed": "unknown",
            },
        )
        self.assertIn("Declared run context:", stdout.getvalue())
        self.assertNotIn("provider", stdout.getvalue())

    def test_existing_archive_updates_only_supplied_values(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            main(
                [
                    "start",
                    "--repo",
                    str(repo),
                    "--change-id",
                    "update-declared",
                    "--surface",
                    "codex_local",
                    "--model",
                    "gpt-5.5",
                    "--reasoning",
                    "medium",
                    "--speed",
                    "fast",
                ]
            )
            main(
                [
                    "start",
                    "--repo",
                    str(repo),
                    "--change-id",
                    "update-declared",
                    "--model",
                    "gpt-5.6",
                ]
            )
            main(
                [
                    "start",
                    "--repo",
                    str(repo),
                    "--change-id",
                    "update-declared",
                    "--surface",
                    "codex_desktop",
                ]
            )
            context = load_run_context(repo, ".sdf/evidence/update-declared")

        assert context is not None
        self.assertEqual(
            context.declared,
            {
                "surface": "codex_desktop",
                "model": "gpt-5.6",
                "reasoning": "medium",
                "speed": "fast",
            },
        )

    def test_existing_archive_without_values_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            main(
                [
                    "start",
                    "--repo",
                    str(repo),
                    "--change-id",
                    "no-new-declaration",
                    "--surface",
                    "codex_local",
                ]
            )
            evidence = repo / ".sdf/evidence/no-new-declaration/evidence.md"
            before = evidence.read_text(encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "start",
                        "--repo",
                        str(repo),
                        "--change-id",
                        "no-new-declaration",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(before, evidence.read_text(encoding="utf-8"))
            self.assertIn("status: already exists", stdout.getvalue())
            self.assertIn(
                "already exists; no declared run-context values supplied",
                stdout.getvalue(),
            )

    def test_scaffold_without_declaration_keeps_only_timestamps_until_write(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            main(
                [
                    "start",
                    "--repo",
                    str(repo),
                    "--change-id",
                    "timing-only",
                ]
            )
            context = load_run_context(repo, ".sdf/evidence/timing-only")

        assert context is not None
        self.assertEqual(
            context.declared,
            {
                "surface": "unknown",
                "model": "unknown",
                "reasoning": "unknown",
                "speed": "unknown",
            },
        )
        self.assertIsNotNone(context.started_at)
        self.assertIsNone(context.closed_at)


if __name__ == "__main__":
    unittest.main()
