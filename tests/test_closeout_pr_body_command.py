import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import (
    write_archive,
    write_run_context,
    write_sentinel_verification_config,
    write_verification_config,
)
from tests.pr_body_command_helpers import run_pr_body_check, run_pr_body_write

from sdf_cli.main import main


class CloseoutPrBodyCommandTest(unittest.TestCase):
    def test_pr_body_write_path_is_retired(self):
        with self.assertRaises(SystemExit) as raised:
            main(["closeout", "pr-body", "write", "--help"])

        self.assertEqual(raised.exception.code, 2)

    def test_pr_body_write_creates_durable_artifact_with_archive_file_links(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(
                repo,
                "pr-body-write",
                change_summary_lines=["- Adds a durable PR body artifact."],
                focus_lines=["- Review generated evidence links."],
                run_context_lines=["- Surface: codex_local."],
                verification_lines=["- Result: configured checks passed."],
                command_lines=[
                    "- `ok`",
                    "  - Status: passed.",
                    "  - Timing: tracked by command.",
                    "  - Tracked timings: reported.",
                ],
                playbook_applied_lines=["- Testing playbook shaped checks."],
                playbook_consulted_lines=["- `.sdf/playbooks/engineering.md`."],
            )
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('raw output hidden')"
""",
            )

            result = run_pr_body_write(repo, "pr-body-write")
            artifact = repo / ".sdf/handoffs/pr-body-write/pr-body.md"
            content = artifact.read_text(encoding="utf-8")
            self.assertEqual(result.exit_code, 0)
            self.assertIn("status: written", result.stdout)
            self.assertIn("github: not mutated", result.stdout)
            self.assertNotIn("warning: --github-ref", result.stdout)
            self.assertTrue(content.startswith("# What you are reviewing\n"))
            self.assertNotIn("\nEvidence:\n", content)
            evidence_notes = (
                "[Evidence notes](.sdf/evidence/pr-body-write/"
                "evidence.md#acceptance--review-focus)"
            )
            self.assertIn(f"- {evidence_notes}", content)
            self.assertEqual(content.count(evidence_notes), 1)
            self.assertIn("## Guidance applied", content)
            self.assertIn("- Applied: Testing playbook shaped checks.", content)
            self.assertNotIn(
                "- Consulted: `.sdf/playbooks/engineering.md`.",
                content,
            )
            self.assertIn(
                "- [Evidence notes](.sdf/evidence/pr-body-write/"
                "evidence.md#machine-record)",
                content,
            )
            self.assertIn(
                "- [Evidence notes](.sdf/evidence/pr-body-write/"
                "evidence.md#guidance-applied)",
                content,
            )
            self.assertIn(
                "- [Evidence notes](.sdf/evidence/pr-body-write/"
                "evidence.md#verification)",
                content,
            )
            self.assertNotIn("- Review notes: [Review notes]", content)
            self.assertNotIn("- Run evidence: [Run evidence]", content)
            self.assertNotIn("- Playbook evidence: [Playbook evidence]", content)
            self.assertNotIn("- Verification evidence: [Verification", content)
            self.assertNotIn("raw output hidden", content)
            self.assertNotIn(str(repo), content)
    def test_pr_body_write_ignores_run_context_sidecar_when_present(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "pr-body-run-context")
            write_run_context(repo, "pr-body-run-context")
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
            )

            write_result = run_pr_body_write(repo, "pr-body-run-context")
            check_result = run_pr_body_check(repo, "pr-body-run-context")
            artifact = repo / ".sdf/handoffs/pr-body-run-context/pr-body.md"
            content = artifact.read_text(encoding="utf-8")
        self.assertEqual(write_result.exit_code, 0)
        self.assertEqual(check_result.exit_code, 0)
        self.assertIn(
            "- [Evidence notes](.sdf/evidence/pr-body-run-context/"
            "evidence.md#machine-record)",
            content,
        )
        self.assertNotIn("SDF Front Door", content)
        self.assertNotIn("provider", content)
        self.assertNotIn("- Run-context evidence: [Run-context evidence]", content)
        self.assertNotIn(
            "`.sdf/evidence/pr-body-run-context/run-context.yml`",
            content,
        )
        self.assertNotIn("missing evidence link", check_result.stdout)
    def test_pr_body_write_refuses_existing_artifact_without_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "existing-pr-body")
            artifact = repo / ".sdf" / "handoffs" / "existing-pr-body" / "pr-body.md"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("existing\n", encoding="utf-8")
            sentinel = repo / "verification-ran.txt"
            write_sentinel_verification_config(repo, sentinel)

            result = run_pr_body_write(repo, "existing-pr-body")
            self.assertEqual(result.exit_code, 1)
            self.assertIn("status: not written", result.stdout)
            self.assertIn(
                "already exists; use --overwrite during a new full closeout",
                result.stdout,
            )
            self.assertEqual(artifact.read_text(encoding="utf-8"), "existing\n")
            self.assertFalse(sentinel.exists())

    def test_pr_body_write_overwrites_existing_artifact_with_explicit_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "overwrite-pr-body")
            artifact = repo / ".sdf" / "handoffs" / "overwrite-pr-body" / "pr-body.md"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("existing\n", encoding="utf-8")
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
            )

            result = run_pr_body_write(repo, "overwrite-pr-body", overwrite=True)
            content = artifact.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("status: overwritten", result.stdout)
        self.assertTrue(content.startswith("# What you are reviewing\n"))

    def test_pr_body_check_accepts_generated_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "valid-pr-body")
            write_verification_config(
                repo,
                """
version: 1
commands:
  - name: ok
    command: python3 -c "print('ok')"
""",
            )
            write_result = run_pr_body_write(repo, "valid-pr-body")

            check_result = run_pr_body_check(repo, "valid-pr-body")

        self.assertEqual(write_result.exit_code, 0)
        self.assertEqual(check_result.exit_code, 0)
        self.assertIn("status: ready", check_result.stdout)
        self.assertIn("present: pr-body.md", check_result.stdout)
        self.assertNotIn("missing evidence link", check_result.stdout)
        self.assertNotIn("broken evidence link", check_result.stdout)
        self.assertNotIn(
            "repo-relative evidence link in GitHub mode",
            check_result.stdout,
        )

    def test_pr_body_check_rejects_missing_broken_and_absolute_links(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_archive(repo, "invalid-pr-body")
            artifact = repo / ".sdf" / "handoffs" / "invalid-pr-body" / "pr-body.md"
            artifact.parent.mkdir(parents=True)
            artifact.write_text(
                "\n".join(
                    [
                        "# What you are reviewing",
                        "",
                        "## Review focus",
                        "",
                        "## Run context",
                        "",
                        "## Guidance applied",
                        "",
                        "## Verification",
                        "",
                        "- [Evidence notes](.sdf/evidence/invalid-pr-body/missing.md)",
                        "- [Local verification](/Users/example/repo/.sdf/evidence/"
                        "invalid-pr-body/evidence.md)",
                    ]
                ),
                encoding="utf-8",
            )

            result = run_pr_body_check(repo, "invalid-pr-body")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("status: not ready", result.stdout)
        self.assertIn("missing evidence link: evidence.md", result.stdout)
        self.assertIn(
            "broken evidence link: .sdf/evidence/invalid-pr-body/missing.md",
            result.stdout,
        )
        self.assertIn(
            "absolute evidence link: /Users/example/repo/.sdf/evidence/"
            "invalid-pr-body/evidence.md",
            result.stdout,
        )
