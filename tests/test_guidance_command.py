import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from sdf_cli.main import main

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "repos"


class GuidanceCommandTest(unittest.TestCase):
    def test_minimal_receiver_guidance_is_ready(self):
        repo = FIXTURE_ROOT / "minimal-sdf-receiver"
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["guidance", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn(f"Repository: {repo}", output)
        self.assertIn(f"Resolved repository path: {repo.resolve()}", output)
        self.assertNotIn("SDF north star", output)
        self.assertNotIn(".sdf/north-star.md", output)
        self.assertIn(
            "SDF agent instructions: present (.sdf/agent-instructions.md)",
            output,
        )
        self.assertNotIn("- .sdf/playbooks/engineering.md", output)
        self.assertNotIn("- .sdf/playbooks/engineering/README.md", output)
        self.assertNotIn(".sdf/playbooks/engineering/", output)
        self.assertIn("- .sdf/playbooks/governed-change-loop.md", output)
        self.assertIn(
            "- Minimal product north star: present "
            "(docs/product/north-star.md) [product, north_star]",
            output,
        )
        self.assertIn(
            "- Minimal Python playbook: present "
            "(docs/playbooks/python/README.md) [implementation, python, cli]",
            output,
        )
        self.assertIn("Boundary:", output)
        self.assertIn(
            "- This command reports available routed guidance.",
            output,
        )
        self.assertIn(
            "- It does not decide which playbooks were applied to a slice.",
            output,
        )
        self.assertIn(
            "- Record slice-local playbook judgement manually in the PR body, "
            "run notes, or configured evidence surface.",
            output,
        )
        self.assertIn("Overall: ready", output)

    def test_current_repo_reports_resolved_repository_path(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["guidance", "--repo", "."])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Repository: .", output)
        self.assertIn(
            f"Resolved repository path: {Path('.').resolve()}",
            output,
        )

    def test_relative_repo_reports_resolved_repository_path(self):
        repo = FIXTURE_ROOT / "minimal-sdf-receiver"
        relative_repo = repo.relative_to(Path.cwd())
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["guidance", "--repo", str(relative_repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn(f"Repository: {relative_repo}", output)
        self.assertIn(f"Resolved repository path: {repo.resolve()}", output)
        self.assertIn("Overall: ready", output)

    def test_missing_configured_receiver_playbook_is_incomplete(self):
        repo = FIXTURE_ROOT / "missing-receiver-playbook"
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["guidance", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn(
            "- Missing Python playbook: missing "
            "(docs/playbooks/python/missing.md) [implementation, python]",
            output,
        )
        self.assertIn("Overall: incomplete", output)

    def test_no_matching_guidance_reports_and_suggests_recovery(self):
        repo = FIXTURE_ROOT / "incomplete-sdf-receiver"
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["guidance", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn(
            "No matching repository guidance was discovered.",
            output,
        )
        self.assertIn(
            "- No portable SDF playbooks or configured receiver playbooks "
            "were found for this repository.",
            output,
        )
        self.assertIn(
            "- Check the receiver's .sdf installation or the --repo path "
            "points at the intended receiver checkout.",
            output,
        )
        self.assertIn("Overall: incomplete", output)

    def test_available_guidance_omits_no_match_message(self):
        repo = FIXTURE_ROOT / "minimal-sdf-receiver"
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["guidance", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertNotIn(
            "No matching repository guidance was discovered.",
            output,
        )

    def test_missing_required_guidance_files_are_incomplete(self):
        repo = FIXTURE_ROOT / "incomplete-sdf-receiver"
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["guidance", "--repo", str(repo)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("SDF config: present (.sdf/config.yml)", output)
        self.assertNotIn("SDF north star", output)
        self.assertNotIn(".sdf/north-star.md", output)
        self.assertIn(
            "SDF agent instructions: missing (.sdf/agent-instructions.md)",
            output,
        )
        self.assertIn("Overall: incomplete", output)

    def test_repo_help_names_receiver_and_default(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as raised:
                main(["guidance", "--help"])

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
        missing_repo = Path(tempfile.gettempdir()) / "sdf-cli-missing-guidance-repo"
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                main(["guidance", "--repo", str(missing_repo)])

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("repo path is not a readable directory", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
