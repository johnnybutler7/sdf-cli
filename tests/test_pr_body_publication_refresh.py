from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import (
    write_archive,
    write_verification_config,
    write_verification_counter,
)
from tests.contract_five_pr_body_fixtures import (
    known_context,
    write_contract_five_archive,
)
from tests.pr_body_command_helpers import run_command, run_handoff

from sdf_cli.evidence_archive_check import check_evidence_archive
from sdf_cli.pr_body import render_pr_body_markdown
from sdf_cli.pr_body_refresh import _recorded_closeout_result


class PrBodyPublicationRefreshTest(unittest.TestCase):
    def test_evidence_wording_refresh_reuses_passing_closeout(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = initialized_repo(Path(directory))
            write_contract_five_archive(
                repo,
                "refresh-ready",
                intent=["- Make generated handoff publication deterministic."],
                review_focus=["- Review commit-linked evidence links."],
                declared=known_context(),
            )
            marker = repo / "verification-count.txt"
            write_verification_counter(repo, marker)

            before_commit = run_handoff(repo, "refresh-ready")
            first_body = handoff(repo, "refresh-ready").read_text(encoding="utf-8")
            evidence = repo / ".sdf/evidence/refresh-ready/evidence.md"
            evidence.write_text(
                evidence.read_text(encoding="utf-8").replace(
                    "Make generated handoff publication deterministic.",
                    "Make generated handoff publication stable.",
                ),
                encoding="utf-8",
            )
            commit(repo, "commit implementation and evidence")
            head = git_output(repo, "rev-parse", "HEAD")

            refreshed = run_command(
                [
                    "close",
                    "--repo",
                    str(repo),
                    "--change-id",
                    "refresh-ready",
                    "--refresh-handoff",
                ]
            )
            published_body = handoff(repo, "refresh-ready").read_bytes()
            marker_content = marker.read_text(encoding="utf-8")
            recorded = _recorded_closeout_result(
                repo, "refresh-ready", check_evidence_archive(repo, "refresh-ready")
            )
            self.assertIsNotNone(recorded)
            expected_body = (
                render_pr_body_markdown(
                    recorded,
                    link_mode="github",
                    github_repo="acme/sdf-cli",
                    github_ref=head,
                )
                + "\n"
            ).encode()

        self.assertEqual(before_commit.exit_code, 0)
        self.assertIn("not publication-ready", before_commit.stdout)
        self.assertIn("/blob/", first_body)
        self.assertEqual(refreshed.exit_code, 0)
        self.assertEqual(marker_content, "1")
        self.assertIn("publication-ready", refreshed.stdout)
        self.assertIn("github: not mutated", refreshed.stdout)
        self.assertIn(
            f"/blob/{head}/.sdf/evidence/refresh-ready/evidence.md",
            published_body.decode(),
        )
        self.assertEqual(published_body, expected_body)

    def test_refresh_blocks_github_handoff_when_evidence_changed_after_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = prepared_committed_archive(Path(directory), "uncommitted-evidence")
            evidence = repo / ".sdf/evidence/uncommitted-evidence/evidence.md"
            evidence.write_text(
                evidence.read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )

            result = run_command(
                [
                    "close",
                    "--repo",
                    str(repo),
                    "--change-id",
                    "uncommitted-evidence",
                    "--refresh-handoff",
                ]
            )

        self.assertEqual(result.exit_code, 1)
        self.assertIn(
            "evidence archive is not committed at the referenced SHA",
            result.stdout,
        )
        self.assertIn("github: not mutated", result.stdout)

    def test_refresh_keeps_contract_four_and_repo_relative_offline_handoffs(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = initialized_repo(Path(directory), remote=False)
            write_archive(repo, "contract-four-refresh")
            write_passing_verification(repo)
            closed = run_handoff(repo, "contract-four-refresh")
            commit(repo, "commit contract four evidence")

            result = run_command(
                [
                    "close",
                    "--repo",
                    str(repo),
                    "--change-id",
                    "contract-four-refresh",
                    "--refresh-handoff",
                    "--link-mode",
                    "repo-relative",
                ]
            )
            body = handoff(repo, "contract-four-refresh").read_text(encoding="utf-8")

        self.assertEqual(closed.exit_code, 0)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("local-only", result.stdout)
        self.assertIn(".sdf/evidence/contract-four-refresh/evidence.md", body)
        self.assertNotIn("https://github.com/", body)


def initialized_repo(repo: Path, *, remote: bool = True) -> Path:
    run_git(repo, "init")
    run_git(repo, "checkout", "-b", "feature/publication")
    commit(repo, "initial")
    if remote:
        run_git(repo, "remote", "add", "origin", "git@github.com:acme/sdf-cli.git")
    return repo


def prepared_committed_archive(repo: Path, change_id: str) -> Path:
    repo = initialized_repo(repo)
    write_contract_five_archive(repo, change_id, declared=known_context())
    write_passing_verification(repo)
    closed = run_handoff(repo, change_id)
    if closed.exit_code != 0:
        raise AssertionError(closed.stdout)
    commit(repo, "commit evidence")
    return repo


def write_passing_verification(repo: Path) -> None:
    write_verification_config(
        repo,
        "version: 1\ncommands:\n  - name: ok\n"
        "    command: python3 -c \"print('ok')\"\n",
    )


def handoff(repo: Path, change_id: str) -> Path:
    return repo / ".sdf/handoffs" / change_id / "pr-body.md"


def commit(repo: Path, message: str) -> None:
    run_git(repo, "add", ".")
    run_git(
        repo,
        "-c",
        "user.name=SDF Test",
        "-c",
        "user.email=sdf@example.invalid",
        "commit",
        "--allow-empty",
        "-m",
        message,
    )


def git_output(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
