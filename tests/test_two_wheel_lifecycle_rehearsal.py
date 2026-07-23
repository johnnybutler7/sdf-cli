from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from two_wheel_lifecycle_rehearsal import (
    LifecycleRehearsalError,
    TwoWheelLifecycleRehearsal,
    inspect_wheel,
)


class TwoWheelLifecycleRehearsalTest(unittest.TestCase):
    def test_rehearsal_records_digests_and_lifecycle_in_no_index_order(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = self._wheel(root / "sdf_cli-1.0.0.whl", "1.0.0")
            second = self._wheel(root / "sdf_cli-2.0.0.whl", "2.0.0")
            runner = _LifecycleRunner({first: "1.0.0", second: "2.0.0"})

            result = TwoWheelLifecycleRehearsal(
                command_runner=runner, venv_creator=_fake_venv
            ).run(first, second)

            self.assertEqual(
                hashlib.sha256(first.read_bytes()).hexdigest(), result.first.sha256
            )
            self.assertEqual(
                hashlib.sha256(second.read_bytes()).hexdigest(), result.second.sha256
            )
            self.assertEqual(
                ["initial install", "upgrade", "force reinstall", "rollback"],
                [item.step for item in result.observations],
            )
            self.assertEqual(
                ["1.0.0", "2.0.0", "2.0.0", "1.0.0"], runner.observed_versions
            )
            self.assertEqual([first, second, second, first], runner.installed_wheels)
            for command in runner.install_commands:
                self.assertIn("--no-index", command)
                self.assertIn("--no-deps", command)
                self.assertIn("--upgrade", command)
                self.assertNotIn("--find-links", command)
            self.assertNotIn("--force-reinstall", runner.install_commands[0])
            self.assertNotIn("--force-reinstall", runner.install_commands[1])
            self.assertIn("--force-reinstall", runner.install_commands[2])
            self.assertIn("--force-reinstall", runner.install_commands[3])
            self.assertTrue(runner.scaffold_checked)

    def test_reports_clear_identity_failure_for_supplied_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = self._wheel(root / "sdf_cli-1.0.0.whl", "1.0.0")
            second = self._wheel(root / "sdf_cli-2.0.0.whl", "2.0.0")
            runner = _LifecycleRunner(
                {first: "1.0.0", second: "2.0.0"}, wrong_cli_version="2.0.0"
            )

            with self.assertRaisesRegex(
                LifecycleRehearsalError,
                (
                    "Observed identity mismatch during upgrade: CLI version.*"
                    "sdf_cli-2.0.0.whl"
                ),
            ):
                TwoWheelLifecycleRehearsal(
                    command_runner=runner, venv_creator=_fake_venv
                ).run(first, second)

    def test_rejects_a_non_sdf_local_wheel(self):
        with tempfile.TemporaryDirectory() as directory:
            wheel = Path(directory) / "other-1.0.0.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr(
                    "other-1.0.0.dist-info/METADATA",
                    "Name: other\nVersion: 1.0.0\n",
                )

            with self.assertRaisesRegex(
                LifecycleRehearsalError, "not a software-dark-factory wheel"
            ):
                inspect_wheel(wheel)

    def _wheel(self, path: Path, version: str) -> Path:
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(
                f"sdf_cli-{version}.dist-info/METADATA",
                f"Name: software-dark-factory\nVersion: {version}\n",
            )
        return path.resolve()


class _LifecycleRunner:
    def __init__(self, versions: dict[Path, str], wrong_cli_version: str | None = None):
        self.versions = versions
        self.wrong_cli_version = wrong_cli_version
        self.current_version = ""
        self.installed_wheels: list[Path] = []
        self.install_commands: list[tuple[str, ...]] = []
        self.observed_versions: list[str] = []
        self.scaffold_checked = False

    def __call__(self, command: tuple[str, ...], _workspace: Path):
        if command[1:4] == ("-m", "pip", "install"):
            wheel = Path(command[-1]).resolve()
            self.current_version = self.versions[wheel]
            self.installed_wheels.append(wheel)
            self.install_commands.append(command)
            return _completed(command)
        if command[1:4] == ("-m", "pip", "show"):
            self.observed_versions.append(self.current_version)
            package_location = _package_location(command[0])
            return _completed(
                command,
                "Name: software-dark-factory\n"
                f"Version: {self.current_version}\n"
                f"Location: {package_location}\n",
            )
        if command[-1] == "--version":
            version = self.current_version
            if version == self.wrong_cli_version:
                version = "unexpected"
            return _completed(command, f"software-dark-factory {version}\n")
        if command[-1] == "--identity":
            executable = Path(command[0]).resolve()
            package_location = _package_location(command[0]) / "sdf_cli"
            return _completed(
                command,
                "SDF CLI identity\n"
                f"package_version: {self.current_version}\n"
                f"executable_location: {executable}\n"
                f"imported_package_location: {package_location}\n"
                "installation_mode: installed\n",
            )
        if command[-1].startswith("from pathlib"):
            return _completed(command, f"{_package_location(command[0]) / 'sdf_cli'}\n")
        if command[1] == "init" and "--check" not in command:
            receiver = Path(command[-1])
            config = receiver / ".sdf" / "config.yml"
            config.parent.mkdir(parents=True)
            config.write_text(
                f'front_door_release: "v{self.current_version}"\n'
                f'front_door_package: "software-dark-factory {self.current_version}"\n',
                encoding="utf-8",
            )
            return _completed(command, "SDF init\nOverall: ready\n")
        if command[1] == "init" and "--check" in command:
            self.scaffold_checked = True
            return _completed(command, "SDF init check\nOverall: ready\n")
        raise AssertionError(command)


def _fake_venv(path: Path) -> None:
    (path / "bin").mkdir(parents=True)


def _completed(command: tuple[str, ...], stdout: str = ""):
    return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")


def _package_location(program: str) -> Path:
    return Path(program).resolve().parent.parent / "site-packages"
