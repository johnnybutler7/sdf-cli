import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sdf_cli.main import main


class EvidenceArchiveScaffoldNextStepsTest(unittest.TestCase):
    def test_timing_only_scaffold_leads_with_close(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            output = run_scaffold(repo, "next-step-slice")

            self.assertIn("created: evidence.md", output)
            self.assertIn("Next:", output)
            self.assertIn(
                f"sdf close --repo {repo} --change-id next-step-slice",
                output,
            )
            self.assertIn(
                f"sdf close --repo {repo} "
                "--change-id next-step-slice --link-mode github "
                "--github-repo owner/name "
                "--github-ref <full-pr-head-sha>",
                output,
            )
            self.assertIn("close the governed change", output)
            self.assertNotIn("sdf closeout", output)
            self.assertIn("local GitHub context cannot be inferred", output)
            self.assertNotIn("run-context write", output)
            self.assertNotIn("finalize-publication", output)
            self.assertNotIn("publication facts", output)
            self.assertIn(
                "--link-mode github --github-repo owner/name "
                "--github-ref <full-pr-head-sha>",
                output,
            )

    def test_scaffold_prints_existing_next_steps_for_present_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            archive = repo / ".sdf" / "evidence" / "present-slice"
            archive.mkdir(parents=True)
            for filename in ("review.md", "verification.md", "run.md"):
                (archive / filename).write_text("existing\n", encoding="utf-8")

            output = run_scaffold(repo, "present-slice")

            self.assertIn("created: evidence.md", output)
            self.assertNotIn("run-context write", output)
            self.assertIn(
                f"sdf close --repo {repo} --change-id present-slice",
                output,
            )
            self.assertIn(
                f"sdf close --repo {repo} "
                "--change-id present-slice --link-mode github "
                "--github-repo owner/name "
                "--github-ref <full-pr-head-sha>",
                output,
            )
            self.assertNotIn("sdf closeout", output)


def run_scaffold(repo: Path, change_id: str) -> str:
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        exit_code = main(
            [
                "start",
                "--repo",
                str(repo),
                "--change-id",
                change_id,
            ]
        )
    if exit_code != 0:
        raise AssertionError(f"Expected scaffold to pass, got {exit_code}")
    return stdout.getvalue()


if __name__ == "__main__":
    unittest.main()
