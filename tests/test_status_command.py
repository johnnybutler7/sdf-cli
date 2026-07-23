import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from sdf_cli.main import main

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "repos"


class StatusCommandTest(unittest.TestCase):
    def test_minimal_receiver_is_ready(self):
        repo = FIXTURE_ROOT / "minimal-sdf-receiver"
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["status", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn(f"Repository: {repo}", output)
        self.assertIn(f"Resolved repository path: {repo.resolve()}", output)
        self.assertIn(
            "Receiver/operator identity: receiver identity unavailable", output
        )
        self.assertIn("SDF config: present (.sdf/config.yml)", output)
        self.assertIn(
            "SDF agent instructions: present (.sdf/agent-instructions.md)",
            output,
        )
        self.assertNotIn("SDF north star", output)
        self.assertNotIn(".sdf/north-star.md", output)
        self.assertIn(
            "SDF verification config: present (.sdf/verification.yml)",
            output,
        )
        self.assertIn("Root agent bridge: present (AGENTS.md)", output)
        self.assertIn("Overall: ready", output)
        self.assertIn("Evidence:", output)
        self.assertIn(
            "- No governed change evidence has been recorded yet.",
            output,
        )
        self.assertIn(
            "- This means the receiver is ready but no governed change archive "
            "exists for review.",
            output,
        )
        self.assertIn(
            "- Normal next step: make the change, then run "
            f"`sdf close --repo {repo} --change-id <change-id>`.",
            output,
        )
        self.assertIn(
            "- The first close creates evidence and may stop for evidence completion.",
            output,
        )
        self.assertNotIn("sdf start", output)
        self.assertIn("Boundary:", output)
        self.assertIn(
            "- This command reports readiness/status visibility.",
            output,
        )
        self.assertIn("- It does not inspect copied portable file drift.", output)
        self.assertIn(
            "- It does not inspect or repair existing AGENTS.md bridge content.",
            output,
        )
        self.assertIn(
            "sdf init --repo <receiver> --check to inspect canonical",
            output,
        )

    def test_relative_repo_reports_resolved_repository_path(self):
        repo = FIXTURE_ROOT / "minimal-sdf-receiver"
        relative_repo = repo.relative_to(Path.cwd())
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["status", "--repo", str(relative_repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn(f"Repository: {relative_repo}", output)
        self.assertIn(f"Resolved repository path: {repo.resolve()}", output)
        self.assertIn("Overall: ready", output)

    def test_docs_free_receiver_does_not_report_legacy_optional_docs(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            with redirect_stdout(io.StringIO()):
                scaffold_exit_code = main(
                    ["init", "--repo", str(repo)]
                )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                status_exit_code = main(["status", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(scaffold_exit_code, 0)
        self.assertEqual(status_exit_code, 0)
        self.assertIn("Receiver/operator identity: match", output)
        self.assertNotIn("docs/product/north-star.md", output)
        self.assertNotIn("docs/README.md", output)
        self.assertNotIn("docs/AGENTS.md", output)
        self.assertNotIn("optional missing", output)
        self.assertIn("Overall: ready", output)

    def test_ready_receiver_with_evidence_archive_hides_first_change_prompt(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            with redirect_stdout(io.StringIO()):
                scaffold_exit_code = main(
                    ["init", "--repo", str(repo)]
                )
            evidence_archive = repo / ".sdf" / "evidence" / "recorded-change"
            evidence_archive.mkdir(parents=True)
            (evidence_archive / "evidence.md").write_text(
                "# Evidence\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                status_exit_code = main(["status", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(scaffold_exit_code, 0)
        self.assertEqual(status_exit_code, 0)
        self.assertIn("Overall: ready", output)
        self.assertNotIn("No governed change evidence has been recorded yet.", output)
        self.assertNotIn("sdf start", output)

    def test_incomplete_receiver_reports_missing_required_files(self):
        repo = FIXTURE_ROOT / "incomplete-sdf-receiver"
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["status", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("SDF config: present (.sdf/config.yml)", output)
        self.assertIn(
            "SDF agent instructions: missing (.sdf/agent-instructions.md)",
            output,
        )
        self.assertNotIn("SDF north star", output)
        self.assertNotIn(".sdf/north-star.md", output)
        self.assertIn(
            "SDF verification config: missing (.sdf/verification.yml)",
            output,
        )
        self.assertIn("Root agent bridge: present (AGENTS.md)", output)
        self.assertIn("Overall: incomplete", output)
        self.assertIn("Diagnosis:", output)
        self.assertIn(
            "- SDF appears to be installed, but the installation is incomplete "
            "or broken.",
            output,
        )
        self.assertIn("Recovery:", output)
        self.assertIn(
            f"`sdf init --repo {repo}`",
            output,
        )
        self.assertIn(
            f"`sdf init --repo {repo} --check`",
            output,
        )

    def test_uninstalled_receiver_reports_one_install_action(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["status", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("SDF config: missing (.sdf/config.yml)", output)
        self.assertIn(
            "SDF agent instructions: missing (.sdf/agent-instructions.md)",
            output,
        )
        self.assertIn(
            "SDF verification config: missing (.sdf/verification.yml)",
            output,
        )
        self.assertIn("Root agent bridge: missing (AGENTS.md)", output)
        self.assertIn("Overall: uninstalled", output)
        self.assertIn("Diagnosis:", output)
        self.assertIn(
            "- SDF is not installed in this repository.",
            output,
        )
        self.assertIn("Next action:", output)
        self.assertIn(
            f"- To install the starter SDF files, run `sdf init --repo {repo}`.",
            output,
        )
        self.assertNotIn("Recovery:", output)
        self.assertNotIn("sdf status --repo /path/to/receiver", output)
        self.assertNotIn("sdf init --repo", output.split("Next action:", 1)[0])
        self.assertNotIn("--check", output)

    def test_repo_help_names_receiver_and_default(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as raised:
                main(["status", "--help"])

        self.assertEqual(raised.exception.code, 0)
        help_text = " ".join(stdout.getvalue().split())
        self.assertIn("Receiver repository to inspect", help_text)
        self.assertIn(
            "defaults to the current directory when --repo is omitted",
            help_text,
        )
        self.assertIn(
            "--repo /path/to/receiver to inspect a checkout elsewhere",
            help_text,
        )

    def test_invalid_repo_path_exits_with_useful_message(self):
        missing_repo = Path(tempfile.gettempdir()) / "sdf-cli-missing-repo"
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                main(["status", "--repo", str(missing_repo)])

        self.assertEqual(raised.exception.code, 2)
        error = stderr.getvalue()
        self.assertIn(
            "could not inspect receiver repository at supplied --repo path",
            error,
        )
        self.assertIn(str(missing_repo), error)
        self.assertIn(
            "The path does not exist or is not a readable directory.",
            error,
        )
        self.assertIn("Recovery:", error)
        self.assertIn("--repo /path/to/receiver", error)
        self.assertIn("SDF does not create the repository directory", error)
if __name__ == "__main__":
    unittest.main()
