import json
import tempfile
import unittest
from pathlib import Path

from scripts.sdf_context_budget import (
    BOOTSTRAP,
    CLOSEOUT,
    TASK_ROUTED,
    ContextBudgetError,
    _front_door_parts,
    collect_context_budget,
)

REPOSITORY_ROOT = Path(__file__).parent.parent


class SdfContextBudgetTest(unittest.TestCase):
    def test_manifest_backed_sources_are_included_in_routed_categories(self):
        report = collect_context_budget(REPOSITORY_ROOT).as_dict()

        included = report["included_sources"]
        source_categories = {entry["source"]: entry["category"] for entry in included}

        self.assertEqual(
            BOOTSTRAP,
            source_categories["AGENTS.md::SDF Front Door block"],
        )
        self.assertEqual(
            BOOTSTRAP,
            source_categories[
                "package:sdf_cli/resources/portable_sdf/sdf/agent-instructions.md"
            ],
        )
        self.assertEqual(
            TASK_ROUTED,
            source_categories[
                "package:sdf_cli/resources/portable_sdf/sdf/"
                "playbooks/governed-change-loop.md"
            ],
        )
        self.assertEqual(
            TASK_ROUTED,
            source_categories[
                "package:sdf_cli/resources/portable_sdf/sdf/"
                "contracts/verification-config.md"
            ],
        )
        self.assertEqual(
            CLOSEOUT,
            source_categories[
                "package:sdf_cli/resources/portable_sdf/sdf/"
                "contracts/evidence-archive.md"
            ],
        )
        self.assertEqual(
            CLOSEOUT,
            source_categories[
                "package:sdf_cli/resources/portable_sdf/sdf/"
                "standard-sdf-non-claims.md"
            ],
        )

    def test_category_totals_sum_to_the_maximum_sdf_owned_total(self):
        report = collect_context_budget(REPOSITORY_ROOT).as_dict()
        totals = report["totals"]

        for field in ("bytes", "characters", "words", "estimated_tokens"):
            self.assertEqual(
                totals["maximum_sdf_owned"][field],
                totals["cold_discovery"][field]
                + totals["governed_change_incremental"][field]
                + totals["closeout_incremental"][field],
            )

    def test_receiver_owned_routing_and_local_extension_are_excluded(self):
        report = collect_context_budget(REPOSITORY_ROOT).as_dict()
        included_sources = {entry["source"] for entry in report["included_sources"]}
        excluded_sources = {
            entry["source"] for entry in report["excluded_receiver_owned_sources"]
        }

        self.assertNotIn(
            str(REPOSITORY_ROOT / "docs" / "playbooks" / "python" / "README.md"),
            included_sources,
        )
        self.assertIn(
            str(REPOSITORY_ROOT / "docs" / "playbooks" / "python" / "README.md"),
            excluded_sources,
        )
        self.assertIn(
            ".sdf/agent-instructions.md::receiver-local extension",
            excluded_sources,
        )
        self.assertIn(
            ".sdf/evidence/** generated current and prior evidence archives",
            report["excluded_nonstanding_context"],
        )

    def test_json_output_is_stable_for_the_same_repository(self):
        first = json.dumps(
            collect_context_budget(REPOSITORY_ROOT).as_dict(),
            indent=2,
            sort_keys=True,
        )
        second = json.dumps(
            collect_context_budget(REPOSITORY_ROOT).as_dict(),
            indent=2,
            sort_keys=True,
        )

        self.assertEqual(first, second)
        self.assertIn('"token_estimate_method"', first)

    def test_missing_front_door_markers_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "AGENTS.md"
            path.write_text("receiver text only\n", encoding="utf-8")

            with self.assertRaisesRegex(
                ContextBudgetError, "missing SDF Front Door"
            ):
                _front_door_parts(path)


if __name__ == "__main__":
    unittest.main()
