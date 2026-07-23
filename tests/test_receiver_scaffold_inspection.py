import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sdf_cli.main import main
from sdf_cli.receiver_payload_manifest import RECEIVER_PAYLOAD_MANIFEST
from sdf_cli.receiver_scaffold_inspection import inspect_receiver_scaffold


class InitCheckTest(unittest.TestCase):
    def test_clean_receiver_check_matches_golden_output(self):
        self._assert_command_matches_golden(
            "receiver-scaffold-inspect-clean-receiver",
            "receiver-scaffold-inspect-clean-receiver.txt",
            expected_exit_code=1,
        )

    def test_existing_core_receiver_check_matches_golden_output(self):
        self._assert_command_matches_golden(
            "receiver-scaffold-inspect-existing-core",
            "receiver-scaffold-inspect-existing-core.txt",
            expected_exit_code=1,
        )

    def test_drifted_copied_playbook_check_matches_golden_output(self):
        self._assert_command_matches_golden(
            "receiver-scaffold-inspect-drifted-playbook",
            "receiver-scaffold-inspect-drifted-playbook.txt",
            expected_exit_code=1,
        )

    def test_check_does_not_write_to_target_repo(self):
        fixture = self._fixture("receiver-scaffold-inspect-clean-receiver")
        before = sorted(
            path.relative_to(fixture).as_posix() for path in fixture.rglob("*")
        )

        with redirect_stdout(io.StringIO()):
            exit_code = main(["init", "--repo", str(fixture), "--check"])

        after = sorted(
            path.relative_to(fixture).as_posix() for path in fixture.rglob("*"))
        self.assertEqual(exit_code, 1)
        self.assertEqual(before, after)

    def test_inspection_reports_bridge_gap_and_conflict(self):
        fixture = self._fixture("receiver-scaffold-inspect-drifted-playbook")
        result = inspect_receiver_scaffold(str(fixture))
        statuses = {
            inspection.entry.path: inspection.status
            for inspection in result.inspections
        }

        self.assertEqual("drifted", statuses["AGENTS.md"])
        self.assertEqual("drifted", statuses[".sdf/playbooks/governed-change-loop.md"])
        self.assertEqual(1, result.exit_code)

    def test_manifest_paths_remain_unchanged(self):
        manifest_text = (
            Path(__file__).resolve().parents[1]
            / "docs/product/boundaries/core-local-install-manifest.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(
            [entry.path for entry in RECEIVER_PAYLOAD_MANIFEST],
            self._core_manifest_paths(manifest_text),
        )

    def _assert_command_matches_golden(
        self,
        fixture_name: str,
        golden_name: str,
        *,
        expected_exit_code: int,
    ) -> None:
        repo = f"tests/fixtures/repos/{fixture_name}"
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["init", "--repo", repo, "--check"])

        golden = (self._golden_dir() / golden_name).read_text(encoding="utf-8")
        self.assertEqual(expected_exit_code, exit_code)
        self.assertEqual(golden, stdout.getvalue())

    def _fixture(self, name: str) -> Path:
        return Path(__file__).resolve().parent / "fixtures" / "repos" / name

    def _golden_dir(self) -> Path:
        return Path(__file__).resolve().parent / "golden"

    def _core_manifest_paths(self, text: str) -> list[str]:
        start = text.index("## Core Manifest")
        end = text.index("## Optional Receiver Docs/Workflow Pack", start)
        section = text[start:end]
        return [
            line.split("|", maxsplit=2)[1].strip().strip("`")
            for line in section.splitlines()
            if line.startswith("| `")
        ]


if __name__ == "__main__":
    unittest.main()
