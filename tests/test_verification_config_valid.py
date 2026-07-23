import unittest

from tests.verification_config_helpers import load_config


class ValidVerificationConfigTest(unittest.TestCase):
    def test_valid_config_defaults_required_to_true(self):
        config = load_config(
            """
version: 1
commands:
  - name: python-unit-tests
    command: PYTHONPATH=src python3 -m unittest discover -s tests
"""
        )

        self.assertTrue(config.present)
        self.assertTrue(config.valid)
        self.assertIsNone(config.error)
        self.assertEqual(len(config.commands), 1)
        self.assertEqual(config.commands[0].name, "python-unit-tests")
        self.assertEqual(
            config.commands[0].command,
            "PYTHONPATH=src python3 -m unittest discover -s tests",
        )
        self.assertTrue(config.commands[0].required)
        self.assertFalse(config.commands[0].track_timing)

    def test_valid_config_accepts_required_false(self):
        config = load_config(
            """
version: 1
commands:
  - name: optional-check
    command: python3 -m unittest
    required: false
"""
        )

        self.assertTrue(config.valid)
        self.assertFalse(config.commands[0].required)

    def test_valid_config_accepts_track_timing_true(self):
        config = load_config(
            """
version: 1
commands:
  - name: unit
    command: python3 -m unittest
    track_timing: true
"""
        )

        self.assertTrue(config.valid)
        self.assertTrue(config.commands[0].track_timing)

    def test_scalar_fields_accept_trailing_comments(self):
        config = load_config(
            """
version: 1  # config version
commands:
  - name: optional-check  # readable label
    command: python3 -m unittest
    required: false  # nonblocking feedback
    track_timing: true  # preserve timing context
"""
        )

        self.assertTrue(config.valid)
        self.assertFalse(config.commands[0].required)
        self.assertTrue(config.commands[0].track_timing)

    def test_command_hashes_and_quoted_hashes_are_preserved(self):
        config = load_config(
            """
version: 1
commands:
  - name: "unit # focused"
    command: printf '# keep this hash'
"""
        )

        self.assertTrue(config.valid)
        self.assertEqual(config.commands[0].name, "unit # focused")
        self.assertEqual(config.commands[0].command, "printf '# keep this hash'")

    def test_command_order_is_preserved(self):
        config = load_config(
            """
version: 1
commands:
  - name: first
    command: first command
  - name: second
    command: second command
    required: false
"""
        )

        self.assertEqual(
            tuple(command.name for command in config.commands),
            ("first", "second"),
        )
        self.assertEqual(
            tuple(command.command for command in config.commands),
            ("first command", "second command"),
        )

    def test_quoted_command_values_parse(self):
        config = load_config(
            """
version: 1
commands:
  - name: unit
    command: "PYTHONPATH=src python3 -m unittest discover -s tests"
"""
        )

        self.assertTrue(config.valid)
        self.assertEqual(
            config.commands[0].command,
            "PYTHONPATH=src python3 -m unittest discover -s tests",
        )

    def test_focused_subsets_parse_referenced_command_names(self):
        config = load_config(
            """
version: 1
commands:
  - name: python-unit-tests
    command: PYTHONPATH=src python3 -m unittest discover -s tests
  - name: ruff
    command: python3 -m ruff check src tests
focused:
  - name: python-tests
    commands:
      - python-unit-tests
  - name: static-checks
    commands:
      - ruff
"""
        )

        self.assertTrue(config.valid)
        self.assertEqual(
            tuple(subset.name for subset in config.focused_subsets),
            ("python-tests", "static-checks"),
        )
        self.assertEqual(config.focused_subsets[0].commands, ("python-unit-tests",))
        self.assertEqual(config.focused_subsets[1].commands, ("ruff",))
        self.assertEqual(config.visibility_issues, ())

    def test_focused_subsets_can_be_absent(self):
        config = load_config(
            """
version: 1
commands:
  - name: python-unit-tests
    command: PYTHONPATH=src python3 -m unittest discover -s tests
"""
        )

        self.assertTrue(config.valid)
        self.assertEqual(config.focused_subsets, ())
        self.assertEqual(config.visibility_issues, ())

    def test_unknown_focused_command_reference_is_visibility_issue(self):
        config = load_config(
            """
version: 1
commands:
  - name: python-unit-tests
    command: PYTHONPATH=src python3 -m unittest discover -s tests
focused:
  - name: static-checks
    commands:
      - ruff
"""
        )

        self.assertTrue(config.valid)
        self.assertEqual(
            config.visibility_issues,
            (
                "focused verification subset static-checks references "
                "unknown command: ruff",
            ),
        )


if __name__ == "__main__":
    unittest.main()
