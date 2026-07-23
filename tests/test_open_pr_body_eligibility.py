import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.open_pr_body_helpers import (
    REPO,
    FakeOpenPrGithub,
    changed_files,
    evidence_bytes,
    observed_pr,
    publication_options,
)

from sdf_cli.open_pr_body_publication import publish_open_pr_body
from sdf_cli.open_pr_publication_readiness import (
    option_error,
    repository_state_ineligibility,
)


class OpenPrBodyEligibilityTest(unittest.TestCase):
    def test_readiness_policy_accepts_complete_trusted_open_draft(self):
        self.assertIsNone(option_error("41", REPO, "main"))
        self.assertIsNone(
            repository_state_ineligibility(
                pr_number="41",
                github_repo=REPO,
                base_branch="main",
                observed=observed_pr(),
            )
        )

    def test_local_surface_preserves_the_existing_pr_body(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            github = FakeOpenPrGithub(
                evidence=evidence_bytes(root / "source", surface="codex_local"),
                changed_files=changed_files(),
            )

            result = publish_open_pr_body(
                publication_options(root / "data"), github=github
            )

        self.assertFalse(result.updated)
        self.assertIn("eligible Cloud surface", result.skip_reason or "")
        self.assertEqual(github.update_calls, [])

    def test_repository_state_refusals_happen_before_evidence_reads(self):
        cases = (
            (observed_pr(state="closed"), "not open"),
            (observed_pr(draft=False), "not an open draft"),
            (observed_pr(head_repository="fork/sdf-cli"), "fork"),
            (observed_pr(base_ref="release"), "trusted base branch"),
            (observed_pr(head_sha="topic-branch"), "head identity"),
            (observed_pr(etag=""), "head identity"),
        )
        for observed, reason in cases:
            with self.subTest(reason=reason), TemporaryDirectory() as directory:
                root = Path(directory)
                github = FakeOpenPrGithub(
                    evidence=b"unused",
                    changed_files=changed_files(),
                    observations=(observed,),
                )

                result = publish_open_pr_body(
                    publication_options(root / "data"), github=github
                )

                self.assertFalse(result.updated)
                self.assertIn(reason, result.skip_reason or "")
                self.assertEqual(github.file_calls, [])
                self.assertEqual(github.update_calls, [])

    def test_missing_ambiguous_and_docs_only_evidence_are_noops(self):
        file_sets = (
            (("src/sdf_cli/example.py",), "missing or ambiguous"),
            (
                (
                    ".sdf/evidence/one/evidence.md",
                    ".sdf/evidence/two/evidence.md",
                    "src/sdf_cli/example.py",
                ),
                "missing or ambiguous",
            ),
            (
                (".sdf/evidence/cloud-change/evidence.md", "docs/README.md"),
                "documentation-only",
            ),
        )
        for files, reason in file_sets:
            with self.subTest(files=files), TemporaryDirectory() as directory:
                root = Path(directory)
                github = FakeOpenPrGithub(evidence=b"unused", changed_files=files)

                result = publish_open_pr_body(
                    publication_options(root / "data"), github=github
                )

                self.assertFalse(result.updated)
                self.assertIn(reason, result.skip_reason or "")
                self.assertEqual(github.update_calls, [])

    def test_mismatched_evidence_repository_identity_is_a_noop(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            github = FakeOpenPrGithub(
                evidence=evidence_bytes(
                    root / "source", repository_name="different-repo"
                ),
                changed_files=changed_files(),
            )

            result = publish_open_pr_body(
                publication_options(root / "data"), github=github
            )

        self.assertFalse(result.updated)
        self.assertIn("repository identity", result.skip_reason or "")
        self.assertEqual(github.update_calls, [])

    def test_eligibility_does_not_depend_on_provider_branch_naming(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            github = FakeOpenPrGithub(
                evidence=evidence_bytes(root / "source", surface="claude_cloud"),
                changed_files=changed_files(),
                observations=(observed_pr(head_repository=REPO),),
            )

            result = publish_open_pr_body(
                publication_options(root / "data"), github=github
            )

        self.assertTrue(result.updated)


if __name__ == "__main__":
    unittest.main()
