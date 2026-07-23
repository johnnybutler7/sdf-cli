import io
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sdf_cli.evidence_archive_check import check_evidence_archive
from sdf_cli.main import main


class EvidenceArchiveScaffoldPrefillTest(unittest.TestCase):
    def test_scaffolded_files_include_known_metadata_from_repo(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            _init_git_repo(repo)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "start",
                        "--repo",
                        str(repo),
                        "--change-id",
                        "prefill-known-fields",
                    ]
                )

            archive = repo / ".sdf" / "evidence" / "prefill-known-fields"
            evidence = (archive / "evidence.md").read_text(encoding="utf-8")

            self.assertEqual(exit_code, 0)
            self.assertIn("change_id: \"prefill-known-fields\"", evidence)
            self.assertIn("repository:", evidence)
            self.assertIn("branch:", evidence)
            self.assertIn("  name: \"main\"", evidence)
            self.assertIn('  path: "."', evidence)
            self.assertNotIn("## Verification", evidence)
            self.assertFalse((archive / "run.md").exists())
            self.assertNotIn(str(repo.resolve()), evidence)

    def test_prefill_does_not_replace_reviewer_judgement_sections(self):
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
                        "judgement-stays-prompted",
                    ]
                )

            archive = repo / ".sdf" / "evidence" / "judgement-stays-prompted"
            evidence = (archive / "evidence.md").read_text(encoding="utf-8")

            self.assertEqual(exit_code, 0)
            self.assertIn("## Intent\n<!-- What changed and why. -->", evidence)
            self.assertIn(
                "## Review focus\n"
                "<!-- What reviewers should check, including meaningful risk. -->",
                evidence,
            )
            self.assertIn(
                "## Limits\n<!-- What this change does not claim or change. -->",
                evidence,
            )
            self.assertIn(
                "## Guidance applied\n"
                "<!-- Guidance that materially shaped this work. -->",
                evidence,
            )
            check = check_evidence_archive(str(repo), "judgement-stays-prompted")
            self.assertFalse(check.passed)
            self.assertEqual(
                [
                    placeholder.section
                    for placeholder in check.files[0].unresolved_placeholders
                ],
                ["## Intent", "## Review focus", "## Limits", "## Guidance applied"],
            )
            self.assertNotIn("TBD", evidence)
            self.assertNotIn("- Command: not run yet.", evidence)


def _init_git_repo(repo: Path) -> None:
    subprocess.run(
        ("git", "init", "-b", "main"),
        cwd=repo,
        check=True,
        capture_output=True,
    )
    (repo / "README.md").write_text("test\n", encoding="utf-8")
    subprocess.run(("git", "add", "README.md"), cwd=repo, check=True)
    subprocess.run(
        (
            "git",
            "-c",
            "user.email=test@example.com",
            "-c",
            "user.name=Test",
            "commit",
            "-m",
            "initial",
        ),
        cwd=repo,
        check=True,
        capture_output=True,
    )


if __name__ == "__main__":
    unittest.main()
