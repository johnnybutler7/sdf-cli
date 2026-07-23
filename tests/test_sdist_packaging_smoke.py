from __future__ import annotations

import sys
import tarfile
import tempfile
from pathlib import Path

from tests.test_wheel_packaging_smoke import PackagingSmokeTestCase

from sdf_cli import __version__
from sdf_cli.receiver_scaffold_content import PORTABLE_SOURCE_FILES


class SourceDistributionPackagingSmokeTest(PackagingSmokeTestCase):
    """Prove a clean sdist installs and initializes the canonical Front Door."""

    def test_clean_sdist_installs_and_initializes_a_receiver(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            source_export = workspace / "source-export"
            self._export_clean_source(source_export)
            distributions = workspace / "distributions"
            distributions.mkdir()

            sdist = self._build_pep517_sdist(source_export, distributions)
            self._assert_sdist_excludes_repository_only_content(sdist)
            self._assert_installed_sdist_initializes_receiver(sdist, workspace)

    def _assert_sdist_excludes_repository_only_content(self, sdist: Path) -> None:
        with tarfile.open(sdist) as archive:
            contents = archive.getnames()
        self.assertFalse(
            any("/tests/" in name or name.endswith("/tests") for name in contents),
            contents,
        )
        self.assertFalse(
            any("/scripts/" in name or name.endswith("/scripts") for name in contents),
            contents,
        )

    def _build_pep517_sdist(self, source_export: Path, distributions: Path) -> Path:
        self._run(
            (
                sys.executable,
                "-m",
                "build",
                "--sdist",
                "--no-isolation",
                "--outdir",
                str(distributions),
            ),
            cwd=source_export,
        )
        return self._single_sdist(distributions)

    def _assert_installed_sdist_initializes_receiver(
        self, sdist: Path, workspace: Path
    ) -> None:
        environment = workspace / "venv-sdist"
        receiver = workspace / "receiver-sdist"
        receiver.mkdir()
        self._run((sys.executable, "-m", "venv", str(environment)))
        executable = self._venv_executable(environment, "sdf")
        pip = self._venv_executable(environment, "pip")
        self._run((str(pip), "install", "--no-deps", str(sdist)))

        version = self._run((str(executable), "--version")).stdout
        self.assertEqual(f"software-dark-factory {__version__}\n", version)
        identity = self._run((str(executable), "--identity")).stdout
        self.assertIn(f"package_version: {__version__}", identity)
        self.assertIn("installation_mode: installed", identity)
        self.assertIn("usage: sdf", self._run((str(executable), "--help")).stdout)

        self._run((str(executable), "init", "--repo", str(receiver)))
        with tarfile.open(sdist) as archive:
            for receiver_path in PORTABLE_SOURCE_FILES:
                expected = archive.extractfile(
                    f"software_dark_factory-{__version__}/src/sdf_cli/resources/"
                    f"portable_sdf/sdf/{receiver_path.removeprefix('.sdf/')}"
                )
                self.assertIsNotNone(expected, receiver_path)
                with self.subTest(resource=receiver_path):
                    self.assertEqual(
                        expected.read(), (receiver / receiver_path).read_bytes()
                    )

        config = (receiver / ".sdf" / "config.yml").read_text(encoding="utf-8")
        self.assertIn(f'front_door_release: "v{__version__}"', config)
        self.assertIn(
            f'front_door_package: "software-dark-factory {__version__}"', config
        )

    def _single_sdist(self, directory: Path) -> Path:
        sdist = directory / f"software_dark_factory-{__version__}.tar.gz"
        self.assertEqual((sdist,), tuple(directory.glob("*.tar.gz")))
        return sdist
