import tempfile
import unittest
from pathlib import Path

from sdf_cli.config.receiver_playbooks import parse_receiver_playbooks


class ReceiverPlaybooksConfigTest(unittest.TestCase):
    def test_parse_receiver_playbook_declarations(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.yml"
            config_path.write_text(
                "\n".join(
                    [
                        "repo: example",
                        "receiver_playbooks:",
                        "  - name: Python playbook",
                        "    path: docs/playbooks/python/README.md",
                        "    categories:",
                        "      - implementation",
                        "      - python",
                        "  - name: Product north star",
                        "    path: docs/product/north-star.md",
                    ]
                ),
                encoding="utf-8",
            )

            playbooks = parse_receiver_playbooks(config_path)

        self.assertEqual(len(playbooks), 2)
        self.assertEqual(playbooks[0].name, "Python playbook")
        self.assertEqual(playbooks[0].path, "docs/playbooks/python/README.md")
        self.assertEqual(playbooks[0].categories, ("implementation", "python"))
        self.assertEqual(playbooks[1].name, "Product north star")
        self.assertEqual(playbooks[1].categories, ())

    def test_missing_config_returns_no_playbooks(self):
        missing_config = Path(tempfile.gettempdir()) / "missing-sdf-config.yml"

        self.assertEqual(parse_receiver_playbooks(missing_config), ())

    def test_sdf_cli_dogfood_config_declares_category_routers(self):
        config_path = Path(__file__).parents[1] / ".sdf" / "config.yml"

        playbooks = parse_receiver_playbooks(config_path)

        self.assertEqual(
            [(playbook.name, playbook.path) for playbook in playbooks],
            [
                (
                    "SDF CLI engineering discipline",
                    "docs/playbooks/engineering/README.md",
                ),
                (
                    "SDF CLI Python guidance",
                    "docs/playbooks/python/README.md",
                ),
                ("SDF CLI product guidance", "docs/product/README.md"),
                (
                    "SDF CLI verification guidance",
                    "docs/verification/README.md",
                ),
            ],
        )
        self.assertEqual(
            playbooks[2].categories,
            (
                "product",
                "north_star",
                "decision_context",
                "evidence",
                "dogfood",
                "workflow",
                "boundaries",
                "provenance",
            ),
        )

    def test_legacy_leaf_declarations_remain_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.yml"
            config_path.write_text(
                "\n".join(
                    [
                        "receiver_playbooks:",
                        "  - name: Existing leaf guidance",
                        "    path: docs/legacy-playbook.md",
                        "    categories:",
                        "      - implementation",
                    ]
                ),
                encoding="utf-8",
            )

            playbooks = parse_receiver_playbooks(config_path)

        self.assertEqual(len(playbooks), 1)
        self.assertEqual(playbooks[0].path, "docs/legacy-playbook.md")
        self.assertEqual(playbooks[0].categories, ("implementation",))


if __name__ == "__main__":
    unittest.main()
