from __future__ import annotations

import unittest
from pathlib import Path

from sdf_cli.verification_results import (
    VerificationCommandResult,
    VerificationRunResult,
)
from sdf_cli.verification_summary import render_verification_summary


class VerificationSummaryTest(unittest.TestCase):
    def test_success_summary_matches_evidence_section_shape(self):
        summary = render_verification_summary(
            verification_result(
                status="passed",
                exit_code=0,
                command_results=(
                    command_result(command="git diff --check", status="passed"),
                    command_result(
                        command="python3 -m unittest discover -s tests",
                        status="passed",
                        duration_seconds=83.41,
                        track_timing=True,
                    ),
                ),
            )
        )

        self.assertIn("SDF verify summary\n", summary)
        self.assertIn("Resolved repository path: /repo\nCommands:\n", summary)
        self.assertIn("- git diff --check: passed", summary)
        self.assertIn(
            "- python3 -m unittest discover -s tests: passed in 1m 23.41s "
            "(tracked timing)",
            summary,
        )
        self.assertIn(
            "Tracked timings:\n"
            "- python3 -m unittest discover -s tests: 1m 23.41s",
            summary,
        )
        self.assertIn("Results:\n- Overall result: passed", summary)
        self.assertIn("- Checks run: 2", summary)
        self.assertIn("- Passed: 2", summary)
        self.assertIn("- Failed: 0", summary)
        self.assertIn("- Total duration: 1m 23.41s", summary)
        self.assertIn("- No files were written.", summary)
        self.assertIn("- No PR body was updated.", summary)
        self.assertIn("- No evidence artifact was generated.", summary)
        self.assertIn("Blockers:\nNone currently.", summary)
        self.assertIn("Transient Notes:\nNone currently.", summary)
        self.assertIn(
            "Boundary:\n"
            "This command does not approve, merge, repair, deploy, or release.",
            summary,
        )

    def test_required_failure_summary_names_blocking_check_and_next_action(self):
        summary = render_verification_summary(
            verification_result(
                status="failed",
                exit_code=1,
                command_results=(
                    command_result(
                        command="git diff --check",
                        status="passed",
                        duration_seconds=0.02,
                    ),
                    command_result(
                        command="python3 -m unittest discover -s tests",
                        status="failed",
                        exit_code=1,
                        duration_seconds=1.24,
                    ),
                ),
            )
        )

        self.assertIn("- git diff --check: passed in 0.02s", summary)
        self.assertIn(
            "- python3 -m unittest discover -s tests: failed in 1.24s",
            summary,
        )
        self.assertIn("- Overall result: failed", summary)
        self.assertIn("- Checks run: 2", summary)
        self.assertIn("- Passed: 1", summary)
        self.assertIn("- Failed: 1", summary)
        self.assertIn("- Total duration: 1.26s", summary)
        self.assertIn(
            "Blockers:\n"
            "- Failed required check: python3 -m unittest discover -s tests\n"
            "  Next: fix the failing check, then rerun "
            "`sdf verify --repo .`.",
            summary,
        )

    def test_invalid_config_summary_reports_no_commands_and_config_blocker(self):
        summary = render_verification_summary(
            verification_result(
                status="config_invalid",
                exit_code=1,
                command_results=(),
                error="verification config is missing",
            )
        )

        self.assertIn("Commands:\n- None run.", summary)
        self.assertIn("- Overall result: failed", summary)
        self.assertIn("- Checks run: 0", summary)
        self.assertNotIn("- Total duration:", summary)
        self.assertIn(
            "Blockers:\n"
            "- Verification was not run: verification config is missing\n"
            "  Next: fix verification configuration, then rerun "
            "`sdf verify --repo .`.",
            summary,
        )

    def test_optional_failure_is_counted_and_reported_as_transient_note(self):
        summary = render_verification_summary(
            verification_result(
                status="passed",
                exit_code=0,
                command_results=(
                    command_result(
                        command="optional smoke",
                        required=False,
                        status="optional_failed",
                        exit_code=1,
                        duration_seconds=0.42,
                    ),
                    command_result(
                        command="required check",
                        status="passed",
                        duration_seconds=0.58,
                    ),
                ),
            )
        )

        self.assertIn("- optional smoke: optional failed in 0.42s", summary)
        self.assertIn("- Overall result: passed", summary)
        self.assertIn("- Failed: 1", summary)
        self.assertIn("- Total duration: 1.00s", summary)
        self.assertIn("Blockers:\nNone currently.", summary)
        self.assertIn(
            "Transient Notes:\n"
            "- Optional check failed but did not block the overall result: "
            "optional smoke",
            summary,
        )

    def test_inactive_governance_mode_reports_no_required_closeout(self):
        summary = render_verification_summary(
            verification_result(
                status="passed",
                exit_code=0,
                command_results=(command_result(command="unit", status="passed"),),
            ),
            governance_mode="inactive",
        )

        self.assertIn("Governance mode:", summary)
        self.assertIn(
            "- governance_mode: inactive detected in .sdf/config.yml.",
            summary,
        )
        self.assertIn(
            "- SDF Front Door is installed but governed closeout is not "
            "required for this run.",
            summary,
        )
        self.assertIn(
            "- Preserve automatic_execution_permitted: false; no evidence "
            "archive or generated PR body is required by this mode.",
            summary,
        )
        self.assertNotIn("Governed closeout:", summary)

    def test_required_governance_mode_reports_closeout(self):
        summary = render_verification_summary(
            verification_result(
                status="passed",
                exit_code=0,
                command_results=(command_result(command="unit", status="passed"),),
            ),
            governance_mode="required",
        )

        self.assertIn("Governed closeout:", summary)
        self.assertIn(
            "- governance_mode: required detected in .sdf/config.yml.",
            summary,
        )


def verification_result(
    *,
    status: str,
    exit_code: int,
    command_results: tuple[VerificationCommandResult, ...],
    repo_label: str | None = ".",
    error: str | None = None,
) -> VerificationRunResult:
    return VerificationRunResult(
        repo_path=Path("/repo"),
        config_path=Path("/repo/.sdf/verification.yml"),
        status=status,
        exit_code=exit_code,
        command_results=command_results,
        repo_label=repo_label,
        error=error,
    )


def command_result(
    *,
    command: str,
    status: str,
    required: bool = True,
    exit_code: int = 0,
    duration_seconds: float | None = None,
    track_timing: bool = False,
) -> VerificationCommandResult:
    return VerificationCommandResult(
        name=command,
        command=command,
        required=required,
        exit_code=exit_code,
        status=status,
        stdout="",
        stderr="",
        duration_seconds=duration_seconds,
        track_timing=track_timing,
    )


if __name__ == "__main__":
    unittest.main()
