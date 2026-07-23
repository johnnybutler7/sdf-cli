import unittest
from unittest.mock import patch

from tests.pr_body_command_helpers import run_command
from tests.pr_body_finalize_helpers import (
    GITHUB_REPO,
    OTHER_SHA,
)

from sdf_cli.pr_body_finalize_merged import FinalizeMergedPrBodyResult


class FinalizeMergedCommandTest(unittest.TestCase):
    def test_help_describes_live_github_mutation_boundary(self):
        result = run_command(["finalize-merged", "--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "sdf finalize-merged --pr-number <number>",
            result.stdout,
        )
        self.assertIn("mutates the live GitHub PR body", result.stdout)
        self.assertIn("workflow/CI", result.stdout)

    def test_command_requires_explicit_arguments(self):
        result = run_command(["finalize-merged"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("the following arguments are required", result.stderr)
        self.assertIn("--pr-number", result.stderr)
        self.assertIn("--github-repo", result.stderr)
        self.assertIn("--merge-sha", result.stderr)

    def test_command_rejects_non_full_merge_sha_before_workflow_runs(self):
        result = run_command(
            [
                "finalize-merged",
                "--pr-number",
                "197",
                "--github-repo",
                GITHUB_REPO,
                "--merge-sha",
                "main",
            ]
        )

        self.assertEqual(result.exit_code, 2)
        self.assertIn(
            "--merge-sha must be a full 40-character commit SHA",
            result.stderr,
        )

    def test_command_rejects_invalid_github_repo_before_workflow_runs(self):
        result = run_command(
            [
                "finalize-merged",
                "--pr-number",
                "197",
                "--github-repo",
                "/tmp/repo",
                "--merge-sha",
                OTHER_SHA,
            ]
        )

        self.assertEqual(result.exit_code, 2)
        self.assertIn("--github-repo must look like owner/name", result.stderr)

    def test_retired_nested_path_is_not_an_alias(self):
        result = run_command(["closeout", "pr-body", "finalize-merged"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("invalid choice: 'closeout'", result.stderr)

    def test_top_level_command_dispatches_unchanged_finalizer(self):
        with patch(
            "sdf_cli.commands.finalize_merged.finalize_merged_pr_body",
            return_value=FinalizeMergedPrBodyResult(
                pr_number="197",
                merge_sha=OTHER_SHA,
                updated=False,
                skip_reason=(
                    "no eligible SDF evidence links required a merge-SHA rewrite"
                ),
            ),
        ) as finalizer:
            result = run_command(
                [
                    "finalize-merged",
                    "--pr-number",
                    "197",
                    "--github-repo",
                    GITHUB_REPO,
                    "--merge-sha",
                    OTHER_SHA,
                ]
            )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("updated: no", result.stdout)
        self.assertIn("github: live PR body mutation boundary", result.stdout)
        self.assertEqual(finalizer.call_args.args[0].pr_number, "197")
        self.assertEqual(finalizer.call_args.args[0].github_repo, GITHUB_REPO)
        self.assertEqual(finalizer.call_args.args[0].merge_sha, OTHER_SHA)


if __name__ == "__main__":
    unittest.main()
