import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sdf_cli.receiver_payload_manifest import (
    RECEIVER_PAYLOAD_MANIFEST,
    scaffold_receiver_payload_entries,
)
from sdf_cli.receiver_scaffold_content import (
    GENERATED_STARTER_CONTENT,
    PORTABLE_SOURCE_FILES,
    portable_resource,
    starter_content,
    starter_source_classification,
)

GENERATED_RECEIVER_PLACEHOLDERS = (
    ".sdf/config.yml",
    ".sdf/verification.yml",
    "AGENTS.md",
    "CLAUDE.md",
)

REPO_LOCAL_PORTABLE_RESOURCE_OVERRIDES = (".sdf/agent-instructions.md",)
EXPECTED_STARTER_RECEIVER_FILES = (
    ".sdf/config.yml",
    ".sdf/agent-instructions.md",
    ".sdf/standard-sdf-non-claims.md",
    ".sdf/verification.yml",
    ".sdf/contracts/evidence-archive.md",
    ".sdf/contracts/verification-config.md",
    ".sdf/playbooks/governed-change-loop.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".gitattributes",
    ".gitignore",
)
FORBIDDEN_PORTABLE_LOCAL_TOKENS = (
    "docs/product",
    "docs/playbooks",
    "docs/verification",
    "sdf-cli",
    "Python",
    "Ruby",
    "parity",
    "dogfood",
    "source-repo",
    "git_projects",
)


class ReceiverScaffoldManifestContractTest(unittest.TestCase):
    def test_starter_receiver_files_match_core_contract(self):
        self.assertEqual(
            EXPECTED_STARTER_RECEIVER_FILES,
            tuple(entry.path for entry in scaffold_receiver_payload_entries()),
        )

    def test_portable_source_files_are_explicit_dogfooded_sources(self):
        source_root = self._source_root()

        self.assertEqual(len(PORTABLE_SOURCE_FILES), len(set(PORTABLE_SOURCE_FILES)))
        for relative_path in PORTABLE_SOURCE_FILES:
            with self.subTest(relative_path=relative_path):
                self.assertIn(
                    relative_path,
                    [entry.path for entry in RECEIVER_PAYLOAD_MANIFEST],
                )
                self.assertTrue((source_root / relative_path).is_file())
                self.assertNotIn(relative_path, GENERATED_STARTER_CONTENT)

    def test_portable_source_files_have_packaged_resource_copies(self):
        source_root = self._source_root()

        for relative_path in PORTABLE_SOURCE_FILES:
            with self.subTest(relative_path=relative_path):
                resource = portable_resource(relative_path)
                source_content = (source_root / relative_path).read_text(
                    encoding="utf-8"
                )
                starter = starter_content(relative_path)

                self.assertTrue(resource.is_file())
                self.assertIn("resources/portable_sdf", str(resource))
                if relative_path in REPO_LOCAL_PORTABLE_RESOURCE_OVERRIDES:
                    self.assertIn("Repo-Local Dogfood Activation", source_content)
                    self.assertNotIn("Repo-Local Dogfood Activation", starter)
                    self.assertIn(starter, source_content)
                else:
                    self.assertEqual(source_content, starter)

    def test_packaged_portable_sources_are_free_of_repo_local_terms(self):
        for relative_path in PORTABLE_SOURCE_FILES:
            content = starter_content(relative_path)
            for forbidden in FORBIDDEN_PORTABLE_LOCAL_TOKENS:
                with self.subTest(relative_path=relative_path, forbidden=forbidden):
                    self.assertNotIn(forbidden, content)

    def test_packaged_activation_matches_generated_starter_config_key(self):
        config_content = GENERATED_STARTER_CONTENT[".sdf/config.yml"]
        match = re.search(r"^governance_mode:\s*(\S+)\s*$", config_content, re.M)
        self.assertIsNotNone(match)

        activation_key = f"governance_mode: {match.group(1)}"
        agent_instructions = starter_content(".sdf/agent-instructions.md")

        self.assertIn("governance_mode", agent_instructions)
        self.assertIn(f"`{activation_key}`", agent_instructions)

    def test_packaged_agent_instructions_route_to_loop_and_contracts(self):
        agent_instructions = starter_content(".sdf/agent-instructions.md")
        links = {
            self._resolve_relative_link(".sdf/agent-instructions.md", target)
            for target in self._markdown_link_targets(agent_instructions)
        }

        self.assertIn(".sdf/playbooks/governed-change-loop.md", links)
        self.assertEqual(
            {
                ".sdf/contracts/evidence-archive.md",
                ".sdf/contracts/verification-config.md",
            },
            {path for path in links if path.startswith(".sdf/contracts/")},
        )

    def test_packaged_agent_instructions_assign_routine_loop_to_coding_agent(self):
        agent_instructions = starter_content(".sdf/agent-instructions.md")

        self.assertIn("## Operating responsibility", agent_instructions)
        self.assertIn("execute the routine SDF loop", agent_instructions)
        self.assertIn(
            "Do not invent repository standards or verification commands",
            agent_instructions,
        )
        self.assertIn(
            "Humans retain standards, review, approval, and merge control",
            agent_instructions,
        )

    def test_playbook_contract_references_are_packaged_contracts(self):
        packaged_contracts = {
            path
            for path in PORTABLE_SOURCE_FILES
            if path.startswith(".sdf/contracts/") and path.endswith(".md")
        }

        for relative_path in PORTABLE_SOURCE_FILES:
            if not relative_path.startswith(".sdf/playbooks/"):
                continue
            for target in self._markdown_link_targets(starter_content(relative_path)):
                resolved = self._resolve_relative_link(relative_path, target)
                if not resolved.startswith(".sdf/contracts/"):
                    continue
                with self.subTest(relative_path=relative_path, target=target):
                    self.assertIn(resolved, packaged_contracts)

    def test_packaged_portable_relative_links_resolve_inside_packaged_set(self):
        packaged_sources = set(PORTABLE_SOURCE_FILES)

        for relative_path in PORTABLE_SOURCE_FILES:
            content = starter_content(relative_path)
            for target in self._markdown_link_targets(content):
                if self._is_external_or_anchor_link(target):
                    continue
                with self.subTest(relative_path=relative_path, target=target):
                    resolved = self._resolve_relative_link(relative_path, target)
                    self.assertIn(resolved, packaged_sources)

    def test_starter_content_reads_portable_assets_from_package_resources(self):
        with tempfile.TemporaryDirectory() as directory:
            package_root = Path(directory)
            resource = (
                package_root
                / "resources"
                / "portable_sdf"
                / "sdf"
                / "agent-instructions.md"
            )
            resource.parent.mkdir(parents=True)
            resource.write_text("packaged portable guidance\n", encoding="utf-8")

            with patch(
                "sdf_cli.receiver_scaffold_content.files",
                return_value=package_root,
            ):
                self.assertEqual(
                    "packaged portable guidance\n",
                    starter_content(".sdf/agent-instructions.md"),
                )

    def test_starter_receiver_file_source_split_is_complete(self):
        portable_sources = set(PORTABLE_SOURCE_FILES)
        generated_sources = set(GENERATED_STARTER_CONTENT)
        starter_files = {entry.path for entry in RECEIVER_PAYLOAD_MANIFEST}
        generated_placeholders = set(GENERATED_RECEIVER_PLACEHOLDERS)

        self.assertEqual(len(RECEIVER_PAYLOAD_MANIFEST), len(starter_files))
        self.assertTrue(generated_placeholders <= generated_sources)
        self.assertFalse(generated_placeholders & portable_sources)
        self.assertEqual(
            starter_files,
            portable_sources | generated_sources | {".gitattributes", ".gitignore"},
        )

    def test_starter_source_classification_matches_source_split(self):
        for relative_path in PORTABLE_SOURCE_FILES:
            with self.subTest(relative_path=relative_path):
                self.assertEqual(
                    "portable",
                    starter_source_classification(relative_path),
                )

        for relative_path in GENERATED_STARTER_CONTENT:
            with self.subTest(relative_path=relative_path):
                self.assertEqual(
                    "generated",
                    starter_source_classification(relative_path),
                )

    def _source_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def _markdown_link_targets(self, text: str) -> list[str]:
        return re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text)

    def _is_external_or_anchor_link(self, target: str) -> bool:
        return (
            target.startswith("#")
            or "://" in target
            or target.startswith("mailto:")
        )

    def _resolve_relative_link(self, source_path: str, target: str) -> str:
        target_without_anchor = target.split("#", maxsplit=1)[0]
        return (
            self._source_root()
            .joinpath(source_path)
            .parent.joinpath(target_without_anchor)
            .resolve()
            .relative_to(self._source_root().resolve())
            .as_posix()
        )
