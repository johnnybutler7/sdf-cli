import tempfile
import unittest
from pathlib import Path

from tests.verification_config_helpers import load_config

from sdf_cli.config.verification import load_verification_config


class InvalidVerificationConfigTest(unittest.TestCase):
    def test_missing_config_returns_invalid_missing_result(self):
        with tempfile.TemporaryDirectory() as directory:
            config = load_verification_config(Path(directory) / "missing.yml")

        self.assertFalse(config.present)
        self.assertFalse(config.valid)
        self.assertEqual(config.commands, ())
        self.assertEqual(config.error, "verification config is missing")

    def test_missing_version_is_invalid(self):
        self.assert_invalid(
            """
commands:
  - name: unit
    command: python3 -m unittest
""",
            "verification config must contain version: 1",
        )

    def test_non_1_version_is_invalid(self):
        self.assert_invalid(
            """
version: 2
commands:
  - name: unit
    command: python3 -m unittest
""",
            "verification config version must be 1",
        )

    def test_missing_commands_is_invalid(self):
        self.assert_invalid(
            """
version: 1
checks:
  - name: unit
    command: python3 -m unittest
""",
            "verification config must contain commands",
        )

    def test_empty_commands_lists_are_invalid(self):
        for content in ("version: 1\ncommands:\n", "version: 1\ncommands: []\n"):
            with self.subTest(content=content):
                self.assert_invalid(
                    content,
                    "verification config commands must not be empty",
                )

    def test_blank_name_is_invalid(self):
        self.assert_invalid(
            """
version: 1
commands:
  - name: " "
    command: python3 -m unittest
""",
            "verification command 1 must have a non-blank name",
        )

    def test_blank_command_is_invalid(self):
        self.assert_invalid(
            """
version: 1
commands:
  - name: unit
    command: ""
""",
            "verification command 1 must have a non-blank command",
        )

    def test_invalid_required_value_is_invalid(self):
        self.assert_invalid(
            """
version: 1
commands:
  - name: unit
    command: python3 -m unittest
    required: sometimes
""",
            "verification command unit required must be true or false",
        )

    def test_invalid_track_timing_value_is_invalid(self):
        self.assert_invalid(
            """
version: 1
commands:
  - name: unit
    command: python3 -m unittest
    track_timing: sometimes
""",
            "verification command unit track_timing must be true or false",
        )

    def assert_invalid(self, content: str, error: str):
        config = load_config(content)
        self.assertFalse(config.valid)
        self.assertEqual(config.error, f"could not parse {config.path}: {error}")


if __name__ == "__main__":
    unittest.main()
