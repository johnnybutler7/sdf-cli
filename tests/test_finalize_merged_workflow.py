import unittest

from tests.pr_body_finalize_helpers import (
    GITHUB_REPO,
    OTHER_SHA,
    FakeGithubPrBoundary,
    body_with_branch_links,
    options,
)

from sdf_cli.pr_body_finalize_merged import finalize_merged_pr_body


class FinalizeMergedWorkflowTest(unittest.TestCase):
    def test_rewrites_eligible_live_evidence_links_to_merge_sha(self):
        github = FakeGithubPrBoundary(body_with_branch_links())

        result = finalize_merged_pr_body(options(), github=github)

        self.assertTrue(result.updated)
        self.assertEqual(github.read_calls, [("197", GITHUB_REPO)])
        self.assertEqual(github.update_calls, [("197", GITHUB_REPO)])
        self.assertIsNotNone(github.updated_body)
        assert github.updated_body is not None
        self.assertIn(
            f"blob/{OTHER_SHA}/.sdf/evidence/finalise-links/evidence.md",
            github.updated_body,
        )
        self.assertIn(
            ".sdf/evidence/historical-links/review.md#review-focus",
            github.updated_body,
        )

    def test_preserves_other_live_pr_body_content(self):
        github = FakeGithubPrBoundary(body_with_branch_links("Reviewer-added note."))

        finalize_merged_pr_body(options(), github=github)

        self.assertIsNotNone(github.updated_body)
        assert github.updated_body is not None
        self.assertIn("Reviewer-added note.", github.updated_body)

    def test_no_eligible_links_is_an_honest_no_op(self):
        github = FakeGithubPrBoundary(
            "# What you are reviewing\n\nNo evidence links.\n"
        )

        result = finalize_merged_pr_body(options(), github=github)

        self.assertFalse(result.updated)
        self.assertIn("no eligible", result.skip_reason or "")
        self.assertEqual(github.read_calls, [("197", GITHUB_REPO)])
        self.assertEqual(github.update_calls, [])

    def test_existing_merge_sha_links_are_a_no_op(self):
        github = FakeGithubPrBoundary(
            "[Evidence notes](https://github.com/example/sdf-cli/blob/"
            f"{OTHER_SHA}/.sdf/evidence/finalise-links/evidence.md)"
        )

        result = finalize_merged_pr_body(options(), github=github)

        self.assertFalse(result.updated)
        self.assertEqual(github.update_calls, [])

    def test_other_repositories_evidence_links_are_not_eligible(self):
        github = FakeGithubPrBoundary(
            "[Evidence notes](https://github.com/other/repo/blob/feature/"
            ".sdf/evidence/finalise-links/evidence.md)"
        )

        result = finalize_merged_pr_body(options(), github=github)

        self.assertFalse(result.updated)
        self.assertEqual(github.update_calls, [])


if __name__ == "__main__":
    unittest.main()
