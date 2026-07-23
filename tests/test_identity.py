import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from sdf_cli.identity import _installation_identity, _render_identity, render_identity


class IdentityTest(unittest.TestCase):
    def test_source_checkout_execution_reports_source_checkout(self):
        with patch("sdf_cli.identity.metadata.distribution") as distribution:
            distribution.side_effect = __import__(
                "importlib.metadata", fromlist=["PackageNotFoundError"]
            ).PackageNotFoundError

            self.assertEqual(
                _installation_identity(), ("source-checkout", "unavailable")
            )

    def test_editable_install_reports_project_location(self):
        distribution = Mock()
        distribution.read_text.return_value = json.dumps(
            {
                "url": "file:///private/tmp/old-sdf-checkout",
                "dir_info": {"editable": True},
            }
        )
        with patch("sdf_cli.identity.metadata.distribution", return_value=distribution):
            self.assertEqual(
                _installation_identity(),
                ("editable", str(Path("/private/tmp/old-sdf-checkout"))),
            )

    def test_non_editable_installed_execution_reports_installed(self):
        distribution = Mock()
        distribution.read_text.return_value = None
        with patch("sdf_cli.identity.metadata.distribution", return_value=distribution):
            self.assertEqual(_installation_identity(), ("installed", "unavailable"))

    def test_source_checkout_wins_when_it_differs_from_installed_distribution(self):
        distribution = Mock()
        distribution.read_text.return_value = None
        distribution.locate_file.return_value = "/site-packages/sdf_cli"
        with patch("sdf_cli.identity.metadata.distribution", return_value=distribution):
            self.assertEqual(
                _installation_identity(Path("/worktree/src/sdf_cli")),
                ("source-checkout", "unavailable"),
            )

    def test_malformed_editable_metadata_is_honest_about_unknown_location(self):
        distribution = Mock()
        distribution.read_text.return_value = json.dumps(
            {"url": "https://example.test/sdf-cli", "dir_info": {"editable": True}}
        )
        with patch("sdf_cli.identity.metadata.distribution", return_value=distribution):
            self.assertEqual(_installation_identity(), ("editable", "unknown"))

    def test_unavailable_git_metadata_is_reported_without_failing(self):
        with patch("sdf_cli.identity._git_output", return_value=None):
            output = render_identity()

        self.assertIn("git_repository_root: unavailable", output)
        self.assertIn("git_commit: unavailable", output)

    def test_identity_exposes_source_and_contract_separately_from_version(self):
        output = render_identity()

        self.assertIn("package_version: 0.1.0", output)
        self.assertIn("executable_location:", output)
        self.assertIn("imported_package_location:", output)
        self.assertIn("evidence_contract_version: 5", output)

    def test_same_package_version_can_be_distinguished_by_source_and_contract(self):
        first = _render_identity(
            (
                ("package_version", "0.1.0"),
                ("imported_package_location", "/private/tmp/old/sdf_cli"),
                ("evidence_contract_version", "4"),
            )
        )
        second = _render_identity(
            (
                ("package_version", "0.1.0"),
                ("imported_package_location", "/worktree/src/sdf_cli"),
                ("evidence_contract_version", "5"),
            )
        )

        self.assertNotEqual(first, second)
        self.assertIn("package_version: 0.1.0", first)
        self.assertIn("package_version: 0.1.0", second)
        self.assertIn("/private/tmp/old/sdf_cli", first)
        self.assertIn("evidence_contract_version: 5", second)


if __name__ == "__main__":
    unittest.main()
