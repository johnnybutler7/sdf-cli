import tempfile
import unittest
from pathlib import Path

from sdf_cli.receiver_payload_manifest import (
    RECEIVER_PAYLOAD_MANIFEST,
    inspection_receiver_payload_entries,
    scaffold_receiver_payload_entries,
)
from sdf_cli.receiver_scaffold import check_receiver_scaffold, write_receiver_scaffold
from sdf_cli.receiver_scaffold_content import starter_content
from sdf_cli.receiver_scaffold_inspection import inspect_receiver_scaffold


class ReceiverPayloadManifestTest(unittest.TestCase):
    def test_each_entry_declares_the_full_receiver_contract(self):
        paths = [entry.path for entry in RECEIVER_PAYLOAD_MANIFEST]

        self.assertEqual(len(paths), len(set(paths)))
        for entry in RECEIVER_PAYLOAD_MANIFEST:
            with self.subTest(entry.path):
                self.assertIn("receiver-owned", entry.classes)
                self.assertIn(
                    entry.content_kind, {"generated", "portable", "shared"}
                )
                self.assertTrue(entry.write_policy)
                self.assertTrue(entry.comparison_kind)
                self.assertTrue(entry.conflict_handling)
                self.assertIsInstance(entry.scaffold_order, int)
                self.assertIsInstance(entry.inspection_order, int)
                self.assertEqual("missing", entry.fresh_receiver_status)
                self.assertEqual("create", entry.fresh_receiver_action)

    def test_scaffold_and_inspection_use_the_canonical_entry_order(self):
        expected_scaffold_paths = [
            entry.path for entry in scaffold_receiver_payload_entries()
        ]
        expected_inspection_paths = [
            entry.path for entry in inspection_receiver_payload_entries()
        ]

        with tempfile.TemporaryDirectory() as directory:
            scaffold = check_receiver_scaffold(directory)
            inspection = inspect_receiver_scaffold(directory)

        self.assertEqual(
            expected_scaffold_paths, [file.path for file in scaffold.files]
        )
        self.assertEqual(
            expected_inspection_paths,
            [item.entry.path for item in inspection.inspections],
        )

    def test_fresh_receiver_inspection_uses_each_entrys_declared_output(self):
        with tempfile.TemporaryDirectory() as directory:
            result = inspect_receiver_scaffold(str(Path(directory)))

        expected = {
            entry.path: (entry.fresh_receiver_status, entry.fresh_receiver_action)
            for entry in RECEIVER_PAYLOAD_MANIFEST
        }
        observed = {
            item.entry.path: (item.status, item.action) for item in result.inspections
        }
        self.assertEqual(expected, observed)

    def test_playbook_stays_exact_after_known_markdown_formatter_transformation(self):
        playbook_path = ".sdf/playbooks/governed-change-loop.md"
        canonical = starter_content(playbook_path)

        self.assertEqual(canonical, self._component_party_markdown_format(canonical))

        with tempfile.TemporaryDirectory() as directory:
            receiver = Path(directory)
            write_receiver_scaffold(str(receiver))

            clean_result = inspect_receiver_scaffold(str(receiver))
            self.assertTrue(
                all(item.status == "matching" for item in clean_result.inspections)
            )

            installed_playbook = receiver / playbook_path
            formatted = self._component_party_markdown_format(
                installed_playbook.read_text(encoding="utf-8")
            )
            self.assertEqual(canonical, formatted)
            installed_playbook.write_text(formatted, encoding="utf-8")

            formatted_result = inspect_receiver_scaffold(str(receiver))
            self.assertTrue(
                all(item.status == "matching" for item in formatted_result.inspections)
            )

            installed_playbook.write_text(
                formatted.replace("Handoff judgement", "Handoff review"),
                encoding="utf-8",
            )
            drifted_result = inspect_receiver_scaffold(str(receiver))
            statuses = {
                item.entry.path: item.status for item in drifted_result.inspections
            }
            self.assertEqual("drifted", statuses[playbook_path])

    def _component_party_markdown_format(self, content: str) -> str:
        """Model the externally observed formatter rewrite exactly."""
        return content.replace(
            "   ### Handoff judgement\n\n   - ",
            "   ### Handoff judgement\n   - ",
        )


if __name__ == "__main__":
    unittest.main()
