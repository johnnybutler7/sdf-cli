import unittest

from sdf_cli.pr_body_recovery import recovery_commands


class PrBodyRecoveryTest(unittest.TestCase):
    def test_invalid_handoff_recovery_overwrites_and_rechecks_with_link_context(self):
        close, rerun = recovery_commands(
            "/repo with spaces",
            "invalid handoff",
            overwrite=True,
            link_mode="github",
            github_repo="acme/sdf-cli",
            github_ref="feature/recovery",
        )

        self.assertEqual(
            close,
            "sdf close --repo '/repo with spaces' "
            "--change-id 'invalid handoff' --overwrite --link-mode github "
            "--github-repo acme/sdf-cli --github-ref feature/recovery",
        )
        self.assertEqual(
            rerun,
            "sdf close --repo '/repo with spaces' "
            "--change-id 'invalid handoff' --overwrite --link-mode github "
            "--github-repo acme/sdf-cli --github-ref feature/recovery",
        )


if __name__ == "__main__":
    unittest.main()
