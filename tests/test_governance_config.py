import tempfile
import unittest
from pathlib import Path

from sdf_cli.config.governance import (
    governance_inactive,
    governance_mode,
    governance_required,
)


class GovernanceConfigTest(unittest.TestCase):
    def test_required_and_inactive_are_explicit_supported_modes(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            write_sdf_config(repo, "governance_mode: required\n")
            self.assertEqual(governance_mode(repo), "required")
            self.assertTrue(governance_required(repo))
            self.assertFalse(governance_inactive(repo))

            write_sdf_config(repo, "governance_mode: inactive\n")
            self.assertEqual(governance_mode(repo), "inactive")
            self.assertFalse(governance_required(repo))
            self.assertTrue(governance_inactive(repo))

    def test_unknown_mode_does_not_activate_required_or_inactive_helpers(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            write_sdf_config(repo, "governance_mode: optional\n")

            self.assertEqual(governance_mode(repo), "optional")
            self.assertFalse(governance_required(repo))
            self.assertFalse(governance_inactive(repo))


def write_sdf_config(repo: Path, content: str) -> None:
    config_dir = repo / ".sdf"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "config.yml").write_text(content, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
