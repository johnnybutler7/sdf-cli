import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from sdf_cli.main import main
from sdf_cli.receiver_payload_manifest import RECEIVER_PAYLOAD_MANIFEST
from sdf_cli.receiver_scaffold_content import starter_content


class InitCommandTest(unittest.TestCase):
    def test_top_level_help_exposes_init_without_receiver_navigation(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as raised:
                main(["--help"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn(
            "{init,status,guidance,verify,start,close,publish-open-pr-body,"
            "finalize-merged}",
            stdout.getvalue(),
        )
        self.assertNotIn("{receiver,", stdout.getvalue())

    def test_init_help_exposes_check_without_retired_options(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as raised:
                main(["init", "--help"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("--check", stdout.getvalue())
        self.assertNotIn("--write", stdout.getvalue())
        self.assertNotIn("--inspect", stdout.getvalue())

    def test_default_init_is_short_and_explains_first_use(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["init", "--repo", str(repo)])

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            for entry in RECEIVER_PAYLOAD_MANIFEST:
                self.assertTrue((repo / entry.path).is_file())
            self.assertIn("SDF init", output)
            self.assertLessEqual(len(output.splitlines()), 15)
            self.assertIn("11 created", output)
            self.assertIn(
                "Starter groups: assistant entry files; .sdf guidance, "
                "configuration, and contracts; Git evidence/handoff rules.",
                output,
            )
            self.assertIn("AGENTS.md or CLAUDE.md", output)
            self.assertIn(".sdf guidance", output)
            self.assertIn("SDF never overwrites existing files", output)
            self.assertIn("configure .sdf/verification.yml", output)
            self.assertIn(f"Next action: sdf verify --repo {repo}", output)
            self.assertIn("close-first journey", output)
            self.assertNotIn("SDF init check", output)

    def test_default_init_reports_idempotent_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            with redirect_stdout(io.StringIO()):
                main(["init", "--repo", str(repo)])
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["init", "--repo", str(repo)])

            self.assertEqual(exit_code, 0)
            self.assertIn(
                "0 created, 0 shared rules updated, 11 existing files unchanged",
                stdout.getvalue(),
            )
            self.assertIn("0 missing, 11 matching, 0 drifted", stdout.getvalue())

    def test_default_init_preserves_matching_files_without_rewriting_them(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            matching_path = repo / ".sdf" / "agent-instructions.md"
            matching_path.parent.mkdir(parents=True)
            original = starter_content(".sdf/agent-instructions.md")
            matching_path.write_text(original, encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                exit_code = main(["init", "--repo", str(repo)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(original, matching_path.read_text(encoding="utf-8"))

    def test_clean_receiver_includes_agent_operating_responsibility(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            with redirect_stdout(io.StringIO()):
                exit_code = main(["init", "--repo", str(repo)])

            self.assertEqual(exit_code, 0)
            instructions = (repo / ".sdf" / "agent-instructions.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("## Operating responsibility", instructions)
            self.assertIn("execute the routine SDF loop", instructions)
            self.assertIn("Do not invent repository standards", instructions)

    def test_default_init_reports_and_preserves_drifted_receiver_file(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            drifted_path = repo / ".sdf" / "agent-instructions.md"
            drifted_path.parent.mkdir(parents=True)
            drifted_path.write_text("receiver-owned drift\n", encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["init", "--repo", str(repo)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                "receiver-owned drift\n", drifted_path.read_text(encoding="utf-8")
            )
            output = stdout.getvalue()
            self.assertIn("1 drifted", output)
            self.assertIn("manual review required for 1 entry", output)
            inspection_command = f"sdf init --repo {repo} --check"
            verification_command = f"sdf verify --repo {repo}"
            self.assertIn(inspection_command, output)
            self.assertIn(verification_command, output)
            self.assertLess(
                output.index(inspection_command), output.index(verification_command)
            )
            self.assertNotIn("status: drifted | action: manual-review", output)

    def test_check_is_fully_read_only_and_requires_action_for_missing_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            before = sorted(path.relative_to(repo) for path in repo.rglob("*"))
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["init", "--check", "--repo", str(repo)])

            after = sorted(path.relative_to(repo) for path in repo.rglob("*"))
            self.assertEqual(exit_code, 1)
            self.assertEqual(before, after)
            self.assertIn("SDF init check", stdout.getvalue())
            self.assertIn("- missing:", stdout.getvalue())

    def test_check_requires_acknowledgement_for_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            drifted_path = repo / "AGENTS.md"
            drifted_path.write_text("not a bridge\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                exit_code = main(["init", "--check", "--repo", str(repo)])

            self.assertEqual(exit_code, 1)

    def test_retired_paths_and_options_are_rejected(self):
        for args in (
            ["receiver", "scaffold", "--repo", "."],
            ["init", "--repo", ".", "--write"],
            ["init", "--repo", ".", "--inspect"],
        ):
            with self.subTest(args=args), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    main(args)
            self.assertEqual(raised.exception.code, 2)

    def test_invalid_repo_path_exits_nonzero_with_init_recovery(self):
        missing_repo = Path(tempfile.gettempdir()) / "sdf-cli-missing-init-repo"
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                main(["init", "--repo", str(missing_repo)])

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("repo path is not a readable directory", stderr.getvalue())
        self.assertIn("sdf init", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
