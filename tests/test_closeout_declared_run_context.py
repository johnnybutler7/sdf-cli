import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import (
    replace_section,
    write_archive,
    write_sentinel_verification_config,
    write_verification_counter,
)
from tests.pr_body_command_helpers import run_command, run_handoff


class CloseoutDeclaredRunContextTest(unittest.TestCase):
    def test_close_help_documents_declared_run_context(self):
        result = run_command(["close", "--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("--surface", result.stdout)
        self.assertIn("--model", result.stdout)
        self.assertIn("--reasoning", result.stdout)
        self.assertIn("--speed", result.stdout)
        self.assertIn("does not infer model identity", result.stdout)

    def test_late_close_with_all_declared_values_records_run_context(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-ran.txt"
            write_sentinel_verification_config(repo, marker)

            run_handoff(
                repo,
                "late-all-context",
                surface="codex_local",
                model="gpt-5.6",
                reasoning="medium",
                speed="fast",
            )
            evidence = _evidence_text(repo, "late-all-context")

        self.assertIn("contract: 5", evidence)
        self.assertIn('  surface: "codex_local"', evidence)
        self.assertIn('  model: "gpt-5.6"', evidence)
        self.assertIn('  reasoning: "medium"', evidence)
        self.assertIn('  speed: "fast"', evidence)

    def test_late_close_with_partial_declared_values_keeps_unknowns(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-ran.txt"
            write_sentinel_verification_config(repo, marker)

            run_handoff(
                repo,
                "late-partial-context",
                surface="codex_local",
                speed="fast",
            )
            evidence = _evidence_text(repo, "late-partial-context")

        self.assertIn('  surface: "codex_local"', evidence)
        self.assertIn('  model: "unknown"', evidence)
        self.assertIn('  reasoning: "unknown"', evidence)
        self.assertIn('  speed: "fast"', evidence)

    def test_late_close_without_declared_values_keeps_unknowns(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-ran.txt"
            write_sentinel_verification_config(repo, marker)

            run_handoff(repo, "late-no-context")
            evidence = _evidence_text(repo, "late-no-context")

        self.assertIn('  surface: "unknown"', evidence)
        self.assertIn('  model: "unknown"', evidence)
        self.assertIn('  reasoning: "unknown"', evidence)
        self.assertIn('  speed: "unknown"', evidence)

    def test_existing_contract_five_unknown_values_are_completed_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-count.txt"
            write_verification_counter(repo, marker)

            first_result = run_handoff(repo, "complete-existing-context")
            evidence_path = _evidence_path(repo, "complete-existing-context")
            evidence_path.write_text(
                _populate_judgement_fields(evidence_path.read_text(encoding="utf-8")),
                encoding="utf-8",
            )

            result = run_handoff(
                repo,
                "complete-existing-context",
                surface="codex_local",
                model="gpt-5.6",
                reasoning="medium",
                speed="fast",
            )
            evidence = evidence_path.read_text(encoding="utf-8")
            artifact = (
                repo / ".sdf" / "handoffs" / "complete-existing-context"
                / "pr-body.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(first_result.exit_code, 1)
        self.assertEqual(result.exit_code, 0)
        self.assertIn('  surface: "codex_local"', evidence)
        self.assertIn('  model: "gpt-5.6"', evidence)
        self.assertIn('  reasoning: "medium"', evidence)
        self.assertIn('  speed: "fast"', evidence)
        self.assertIn(
            "- Run context: surface=codex_local, model=gpt-5.6, "
            "reasoning=medium, speed=fast.",
            artifact,
        )

    def test_existing_declared_values_are_not_overwritten_by_close(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-count.txt"
            write_verification_counter(repo, marker)

            run_handoff(repo, "preserve-existing-context")
            evidence_path = _evidence_path(repo, "preserve-existing-context")
            evidence_path.write_text(
                _populate_judgement_fields(evidence_path.read_text(encoding="utf-8"))
                .replace('  surface: "unknown"', '  surface: "codex_desktop"')
                .replace('  model: "unknown"', '  model: "gpt-5.5"'),
                encoding="utf-8",
            )

            result = run_handoff(
                repo,
                "preserve-existing-context",
                surface="codex_local",
                model="gpt-5.6",
                reasoning="medium",
                speed="fast",
            )
            evidence = evidence_path.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0)
        self.assertIn('  surface: "codex_desktop"', evidence)
        self.assertIn('  model: "gpt-5.5"', evidence)
        self.assertIn('  reasoning: "medium"', evidence)
        self.assertIn('  speed: "fast"', evidence)
        self.assertNotIn('  surface: "codex_local"', evidence)
        self.assertNotIn('  model: "gpt-5.6"', evidence)

    def test_contract_four_unknown_values_are_completed_without_migration(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            marker = repo / "verification-count.txt"
            write_archive(repo, "existing-contract-four-context")
            write_verification_counter(repo, marker)

            result = run_handoff(
                repo,
                "existing-contract-four-context",
                surface="codex_local",
                model="gpt-5.6",
                reasoning="medium",
                speed="fast",
            )
            evidence = _evidence_text(repo, "existing-contract-four-context")

        self.assertEqual(result.exit_code, 0)
        self.assertIn("contract: 4", evidence)
        self.assertNotIn("contract: 5", evidence)
        self.assertIn('  surface: "codex_local"', evidence)
        self.assertIn('  model: "gpt-5.6"', evidence)
        self.assertIn('  reasoning: "medium"', evidence)
        self.assertIn('  speed: "fast"', evidence)


def _evidence_path(repo: Path, change_id: str) -> Path:
    return repo / ".sdf" / "evidence" / change_id / "evidence.md"


def _evidence_text(repo: Path, change_id: str) -> str:
    return _evidence_path(repo, change_id).read_text(encoding="utf-8")


def _populate_judgement_fields(markdown: str) -> str:
    content = markdown
    judgement = {
        "## Intent": ["- Exercise late-created contract-5 closeout."],
        "## Review focus": ["- Review the concise judgement gate and machine record."],
        "## Limits": ["- Fixture only; no external service behaviour is covered."],
        "## Guidance applied": ["- None material for this fixture."],
    }
    for heading, lines in judgement.items():
        content = replace_section(content, heading, lines)
    return content


if __name__ == "__main__":
    unittest.main()
