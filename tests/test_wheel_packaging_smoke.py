from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from sdf_cli import __version__
from sdf_cli.receiver_scaffold_content import PORTABLE_SOURCE_FILES


class PackagingSmokeTestCase(unittest.TestCase):
    """Shared clean-export and installed-package helpers for packaging smokes."""

    def _export_clean_source(self, destination: Path) -> None:
        shutil.copytree(
            self._source_root(),
            destination,
            ignore=shutil.ignore_patterns(
                ".git",
                ".ruff_cache",
                "__pycache__",
                "*.egg-info",
                "build",
                "dist",
                "*.pyc",
            ),
        )

    def _build_pep517_wheel(self, source_export: Path, wheels: Path) -> Path:
        pep517_wheels = wheels / "pep517"
        pep517_wheels.mkdir()
        self._run(
            (
                sys.executable,
                "-m",
                "pip",
                "wheel",
                ".",
                "--no-build-isolation",
                "--no-deps",
                "--wheel-dir",
                str(pep517_wheels),
            ),
            cwd=source_export,
        )
        return self._single_wheel(pep517_wheels)

    def _assert_wheel_resources(self, wheel: Path) -> None:
        with zipfile.ZipFile(wheel) as archive:
            contents = set(archive.namelist())
        for receiver_path in PORTABLE_SOURCE_FILES:
            resource_path = receiver_path.removeprefix(".sdf/")
            expected = f"sdf_cli/resources/portable_sdf/sdf/{resource_path}"
            with self.subTest(resource=expected):
                self.assertIn(expected, contents)

    def _assert_installed_wheel_initializes_receiver(
        self, wheel: Path, workspace: Path
    ) -> None:
        name = wheel.parent.name or "legacy"
        environment = workspace / f"venv-{name}"
        receiver = workspace / f"receiver-{name}"
        receiver.mkdir()
        self._run((sys.executable, "-m", "venv", str(environment)))
        executable = self._venv_executable(environment, "sdf")
        pip = self._venv_executable(environment, "pip")
        self._run((str(pip), "install", "--no-deps", str(wheel)))

        version = self._run((str(executable), "--version")).stdout
        self.assertEqual(f"software-dark-factory {__version__}\n", version)
        identity = self._run((str(executable), "--identity")).stdout
        self.assertIn(f"package_version: {__version__}", identity)
        self.assertIn("installation_mode: installed", identity)

        self._run((str(executable), "init", "--repo", str(receiver)))
        for receiver_path in PORTABLE_SOURCE_FILES:
            self.assertTrue((receiver / receiver_path).is_file(), receiver_path)
        config = (receiver / ".sdf" / "config.yml").read_text(encoding="utf-8")
        self.assertIn(f'front_door_release: "v{__version__}"', config)
        self.assertIn(
            f'front_door_package: "software-dark-factory {__version__}"', config
        )

    def _single_wheel(self, directory: Path) -> Path:
        wheels = tuple(directory.glob("software_dark_factory-*.whl"))
        self.assertEqual(1, len(wheels), wheels)
        return wheels[0]

    def _source_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def _run(self, command: tuple[str, ...], *, cwd: Path | None = None):
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        completed = subprocess.run(
            command,
            check=False,
            cwd=cwd,
            capture_output=True,
            env=environment,
            text=True,
        )
        if completed.returncode:
            self.fail(
                f"Command failed ({completed.returncode}): {' '.join(command)}\n"
                f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
            )
        return completed

    def _venv_executable(self, environment: Path, name: str) -> Path:
        folder = "Scripts" if os.name == "nt" else "bin"
        return environment / folder / name


class WheelPackagingSmokeTest(PackagingSmokeTestCase):
    """Prove clean wheels contain everything ``sdf init`` reads at runtime."""

    def test_clean_wheels_install_and_initialize_a_receiver(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            source_export = workspace / "source-export"
            self._export_clean_source(source_export)
            wheels = workspace / "wheels"
            wheels.mkdir()

            pep517_wheel = self._build_pep517_wheel(source_export, wheels)

            for wheel in (pep517_wheel,):
                with self.subTest(wheel=wheel.name):
                    self._assert_wheel_resources(wheel)
                    self._assert_installed_wheel_initializes_receiver(wheel, workspace)
