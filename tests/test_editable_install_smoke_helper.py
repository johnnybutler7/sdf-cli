import unittest

from scripts.check_editable_install import _sdf_commands


class EditableInstallSmokeHelperTest(unittest.TestCase):
    def test_default_command_set_includes_full_verification_run(self):
        commands = _sdf_commands(include_full_verification_run=True)

        self.assertEqual(
            commands[-1],
            ("sdf verify", ("verify", "--repo", ".")),
        )

    def test_configured_verification_command_set_skips_recursive_full_run(self):
        commands = _sdf_commands(include_full_verification_run=False)

        self.assertIn(("sdf identity", ("--identity",)), commands)
        self.assertIn(
            ("sdf verify --check", ("verify", "--repo", ".", "--check")),
            commands,
        )
        self.assertNotIn(
            ("sdf verify", ("verify", "--repo", ".")),
            commands,
        )

if __name__ == "__main__":
    unittest.main()
