import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tests.open_pr_body_helpers import (
    SHA,
    FakeOpenPrGithub,
    changed_files,
    evidence_bytes,
    observed_pr,
    publication_options,
)

from sdf_cli.open_pr_body_publication import (
    MAX_GITHUB_PR_BODY_CHARACTERS,
    publish_open_pr_body,
)


class OpenPrBodyPublicationTest(unittest.TestCase):
    def test_unchanged_complete_state_updates_only_the_body(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            github = FakeOpenPrGithub(
                evidence=evidence_bytes(root / "source", surface="codex_cloud"),
                changed_files=changed_files(),
            )

            result = publish_open_pr_body(
                publication_options(root / "data"), github=github
            )

        self.assertTrue(result.updated)
        self.assertEqual(result.surface, "codex_cloud")
        self.assertEqual(result.closeout_status, "passed")
        self.assertEqual(len(github.update_calls), 1)
        body = github.update_calls[0][2]
        self.assertIn("# What you are reviewing", body)
        self.assertIn(f"blob/{SHA}/.sdf/evidence/cloud-change/evidence.md", body)
        self.assertIn("recorded passing closeout evidence reused", body)

    def test_claude_cloud_failed_closeout_remains_an_honest_failure(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            github = FakeOpenPrGithub(
                evidence=evidence_bytes(
                    root / "source",
                    surface="claude_cloud",
                    closeout_status="failed",
                ),
                changed_files=changed_files(),
            )

            result = publish_open_pr_body(
                publication_options(root / "data"), github=github
            )

        self.assertTrue(result.updated)
        self.assertEqual(result.surface, "claude_cloud")
        self.assertEqual(result.closeout_status, "failed")
        body = github.update_calls[0][2]
        self.assertIn("recorded failed closeout evidence reused", body)
        self.assertIn("`wheel-packaging-smoke` (failed", body)
        self.assertNotIn("recorded passing closeout evidence reused", body)

    def test_repeated_execution_is_an_exact_body_noop(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = evidence_bytes(root / "source")
            first_github = FakeOpenPrGithub(
                evidence=evidence, changed_files=changed_files()
            )
            first = publish_open_pr_body(
                publication_options(root / "first"), github=first_github
            )
            installed_body = first_github.update_calls[0][2]
            rerun_github = FakeOpenPrGithub(
                evidence=evidence,
                changed_files=changed_files(),
                observations=(observed_pr(body=installed_body),),
            )

            rerun = publish_open_pr_body(
                publication_options(root / "rerun"), github=rerun_github
            )

        self.assertTrue(first.updated)
        self.assertFalse(rerun.updated)
        self.assertIn("already installed", rerun.skip_reason or "")
        self.assertEqual(rerun_github.update_calls, [])

    def test_every_rendered_pr_state_change_is_refused_before_mutation(self):
        later_states = (
            ("body", observed_pr(body="Body changed during publication")),
            (
                "head",
                observed_pr(head_sha="fedcba9876543210fedcba9876543210fedcba98"),
            ),
            ("open state", observed_pr(state="closed")),
            ("draft state", observed_pr(draft=False)),
            ("base", observed_pr(base_ref="release")),
            ("repository", observed_pr(head_repository="fork/sdf-cli")),
        )
        for changed_field, later_state in later_states:
            with (
                self.subTest(changed_field=changed_field),
                TemporaryDirectory() as directory,
            ):
                root = Path(directory)
                github = FakeOpenPrGithub(
                    evidence=evidence_bytes(root / "source"),
                    changed_files=changed_files(),
                    observations=(observed_pr(), later_state),
                )

                result = publish_open_pr_body(
                    publication_options(root / "data"), github=github
                )

                self.assertFalse(result.updated)
                self.assertIn("changed during publication", result.skip_reason or "")
                self.assertEqual(github.update_calls, [])

    def test_non_utf8_evidence_is_a_safe_noop(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            github = FakeOpenPrGithub(
                evidence=b"\xff",
                changed_files=changed_files(),
            )

            result = publish_open_pr_body(
                publication_options(root / "data"), github=github
            )

        self.assertFalse(result.updated)
        self.assertIn("not valid UTF-8", result.skip_reason or "")
        self.assertEqual(github.update_calls, [])

    def test_handoff_over_github_body_limit_is_a_safe_noop(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            github = FakeOpenPrGithub(
                evidence=evidence_bytes(root / "source"),
                changed_files=changed_files(),
            )
            oversized = "x" * (MAX_GITHUB_PR_BODY_CHARACTERS + 1)

            with patch(
                "sdf_cli.open_pr_body_publication.render_pr_body_markdown",
                return_value=oversized,
            ):
                result = publish_open_pr_body(
                    publication_options(root / "data"), github=github
                )

        self.assertFalse(result.updated)
        self.assertIn("exceeds GitHub's body limit", result.skip_reason or "")
        self.assertEqual(github.update_calls, [])


if __name__ == "__main__":
    unittest.main()
