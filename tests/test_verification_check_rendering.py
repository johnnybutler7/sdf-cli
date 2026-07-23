import unittest
from pathlib import Path

from sdf_cli.commands.verification import VerificationResult
from sdf_cli.config.verification import FocusedVerificationSubset, VerificationCommand
from sdf_cli.receiver_scaffold_content import (
    STARTER_VERIFICATION_PLACEHOLDER_COMMAND,
    STARTER_VERIFICATION_PLACEHOLDER_NAME,
)
from sdf_cli.verification_check_rendering import render_verification


class VerificationCheckRenderingTest(unittest.TestCase):
    def test_renders_all_conditional_sections_in_report_order(self):
        result = VerificationResult(
            repo_label="receiver",
            repo_path=Path("receiver"),
            config_present=True,
            commands=(
                VerificationCommand(
                    name=STARTER_VERIFICATION_PLACEHOLDER_NAME,
                    command=STARTER_VERIFICATION_PLACEHOLDER_COMMAND,
                    required=True,
                    track_timing=False,
                ),
            ),
            focused_subsets=(
                FocusedVerificationSubset(
                    "fast", (STARTER_VERIFICATION_PLACEHOLDER_NAME,)
                ),
            ),
            visibility_issues=("focused verification subset fast is incomplete",),
            config_error="verification config must contain version: 1",
        )

        self.assertEqual(
            render_verification(result),
            "\n".join(
                [
                    "SDF verify check",
                    "",
                    "Repository: receiver",
                    "Config: .sdf/verification.yml (present)",
                    "",
                    "Configured commands:",
                    "- configure-receiver-verification",
                    (
                        "  Command: echo 'Configure receiver-owned verification "
                        "commands in .sdf/verification.yml' && exit 1"
                    ),
                    "  Required: yes",
                    "  Track timing: no",
                    "",
                    "Receiver verification placeholder detected:",
                    "- The scaffolded placeholder fails intentionally.",
                    (
                        "- Replace it in .sdf/verification.yml with "
                        "receiver-owned commands."
                    ),
                    "- Then run:",
                    "  sdf verify --repo <receiver>",
                    "",
                    "Config error: verification config must contain version: 1",
                    "",
                    "Focused verification:",
                    "- fast",
                    "  Commands:",
                    "  - configure-receiver-verification",
                    "Focused verification boundary:",
                    "- Focused subsets are read-only visibility here.",
                    "- They are supporting feedback during a slice.",
                    (
                        "- They do not replace `sdf verify --repo .` as the "
                        "full closeout gate."
                    ),
                    "",
                    "Focused verification visibility issues:",
                    "- focused verification subset fast is incomplete",
                    "",
                    "Execution boundary:",
                    (
                        "- `sdf verify` executes the configured commands from the "
                        "selected repository."
                    ),
                    "- Required command failure fails the run.",
                    "- Optional command failure is reported but does not fail the run.",
                    "- This command does not write evidence files.",
                    "- No PR body is updated.",
                    (
                        "- No approve, merge, repair, deploy, or release action is "
                        "performed."
                    ),
                    "",
                    "Overall: incomplete",
                ]
            ),
        )

    def test_renders_missing_config_recovery(self):
        result = VerificationResult(
            repo_label="receiver",
            repo_path=Path("receiver"),
            config_present=False,
            commands=(),
        )

        output = render_verification(result)

        self.assertIn("Configured commands:\n- none discovered", output)
        self.assertIn("Recovery:", output)
        self.assertIn("`sdf init --repo receiver`", output)
        self.assertIn("Overall: incomplete", output)


if __name__ == "__main__":
    unittest.main()
