import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from sdf_cli.commands.status import StatusResult
from sdf_cli.commands.status_rendering import render_status
from sdf_cli.main import main
from sdf_cli.receiver_cli_identity import (
    CLI_IDENTITY_UNAVAILABLE,
    MATCH,
    MISMATCH,
    RECEIVER_IDENTITY_UNAVAILABLE,
    compare_identity_values,
)


class ReceiverCliIdentityTest(unittest.TestCase):
    def test_equivalent_supported_identity_forms_match(self):
        for receiver_release in (
            "v0.1.0",
            "0.1.0",
            "software-dark-factory 0.1.0",
        ):
            for cli_version in (
                "v0.1.0",
                "0.1.0",
                "software-dark-factory 0.1.0",
            ):
                with self.subTest(
                    receiver_release=receiver_release,
                    cli_version=cli_version,
                ):
                    comparison = compare_identity_values(receiver_release, cli_version)

                    self.assertEqual(comparison.result, MATCH)

    def test_mismatching_versions_mismatch(self):
        comparison = compare_identity_values("v0.0.14", "0.1.0")

        self.assertEqual(comparison.result, MISMATCH)

    def test_missing_receiver_identity_is_explicit(self):
        comparison = compare_identity_values(None, "0.1.0")

        self.assertEqual(comparison.result, RECEIVER_IDENTITY_UNAVAILABLE)

    def test_malformed_or_unavailable_cli_identity_is_explicit(self):
        malformed = compare_identity_values("v0.1.0", "not-a-version")
        unavailable = compare_identity_values("v0.1.0", None)
        embedded_version = compare_identity_values(
            "v0.1.0", "other-software-dark-factory 0.1.0"
        )

        self.assertEqual(malformed.result, CLI_IDENTITY_UNAVAILABLE)
        self.assertEqual(unavailable.result, CLI_IDENTITY_UNAVAILABLE)
        self.assertEqual(embedded_version.result, CLI_IDENTITY_UNAVAILABLE)

    def test_malformed_identity_is_not_a_match_in_rendered_status(self):
        comparison = compare_identity_values("v0.1.0", "not-a-version")
        result = StatusResult(
            repo_label="receiver",
            repo_path=Path("receiver"),
            files=(),
            identity_comparison=comparison,
        )

        output = render_status(result)

        self.assertIn("Executing CLI version: not-a-version", output)
        self.assertIn(
            "Receiver/operator identity: CLI identity unavailable or unparsable",
            output,
        )
        self.assertNotIn("Receiver/operator identity: match", output)

    def test_status_renders_mismatch_without_blocking_read_only_inspection(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            self._write_release(repo, "v0.0.14")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["status", "--repo", str(repo)])

        self.assertEqual(exit_code, 1)
        self.assertIn(
            "Receiver-declared Front Door release: v0.0.14", stdout.getvalue()
        )
        self.assertIn("Executing CLI version: 0.1.0", stdout.getvalue())
        self.assertIn("Receiver/operator identity: mismatch", stdout.getvalue())

    def test_start_refuses_mismatch_before_writing_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            self._write_release(repo, "v0.0.14")
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    main(["start", "--repo", str(repo), "--change-id", "blocked"])

            self.assertEqual(raised.exception.code, 2)
            self.assertIn(
                "receiver declares Front Door release v0.0.14", stderr.getvalue()
            )
            self.assertIn("executing CLI version is 0.1.0", stderr.getvalue())
            self.assertIn("Align the operator CLI with the receiver", stderr.getvalue())
            self.assertEqual(self._receiver_files(repo), self._mismatched_files())

    def test_close_refuses_mismatch_before_creating_late_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            self._write_release(repo, "v0.0.14")
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    main(["close", "--repo", str(repo), "--change-id", "blocked"])

            self.assertEqual(raised.exception.code, 2)
            self.assertIn("receiver/operator identity mismatch", stderr.getvalue())
            self.assertEqual(self._receiver_files(repo), self._mismatched_files())

    def test_matching_receiver_starts_normally(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            self._write_release(repo, "v0.1.0")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    ["start", "--repo", str(repo), "--change-id", "matching"]
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue((repo / ".sdf" / "evidence" / "matching").is_dir())

    def _write_release(self, repo: Path, release: str) -> None:
        config = repo / ".sdf" / "config.yml"
        config.parent.mkdir(parents=True)
        config.write_text(f'front_door_release: "{release}"\n', encoding="utf-8")

    def _receiver_files(self, repo: Path) -> dict[str, bytes]:
        return {
            path.relative_to(repo).as_posix(): path.read_bytes()
            for path in repo.rglob("*")
            if path.is_file()
        }

    def _mismatched_files(self) -> dict[str, bytes]:
        return {".sdf/config.yml": b'front_door_release: "v0.0.14"\n'}
