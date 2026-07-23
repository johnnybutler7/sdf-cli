import unittest

from sdf_cli.receiver_scaffold_content import starter_content


class ReceiverScaffoldInactiveGuidanceTest(unittest.TestCase):
    def test_packaged_guidance_names_installed_but_inactive_mode(self):
        agent_instructions = starter_content(".sdf/agent-instructions.md")

        self.assertIn("## Activation", agent_instructions)
        self.assertIn("`governance_mode: inactive`", agent_instructions)
        self.assertIn("use the receiver's normal workflow", agent_instructions)
        self.assertIn("operator asks for the loop", agent_instructions)


if __name__ == "__main__":
    unittest.main()
