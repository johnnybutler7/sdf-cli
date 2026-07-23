import unittest
from pathlib import Path


class PostMergePrBodyFinalizerWorkflowTest(unittest.TestCase):
    def test_workflow_uses_the_merged_same_repository_pr_and_merge_sha(self):
        workflow = Path(
            ".github/workflows/post-merge-pr-body-finalizer.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("pull_request:", workflow)
        self.assertIn("merged == true", workflow)
        self.assertIn("head.repo.full_name == github.repository", workflow)
        self.assertIn("pull-requests: write", workflow)
        self.assertIn("merge_commit_sha", workflow)
        self.assertIn("--merge-sha", workflow)
        self.assertNotIn("--base-sha", workflow)
        self.assertNotIn("--durable-sha", workflow)


if __name__ == "__main__":
    unittest.main()
