"""Smoke-test a packaged install and the installed sdf console script."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path
from typing import Sequence

SDF_SMOKE_COMMANDS = (
    ("sdf help", ("--help",)),
    ("sdf version", ("--version",)),
    ("sdf identity", ("--identity",)),
    ("sdf status", ("status", "--repo", ".")),
    ("sdf guidance", ("guidance", "--repo", ".")),
    ("sdf verify --check", ("verify", "--repo", ".", "--check")),
)

FULL_VERIFICATION_COMMAND = (
    ("sdf verify", ("verify", "--repo", ".")),
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build, install, and verify the packaged sdf console script in a "
            "temporary virtual environment."
        )
    )
    parser.add_argument(
        "--upgrade-pip",
        action="store_true",
        help="deprecated compatibility option; no network upgrade is performed",
    )
    parser.add_argument(
        "--skip-full-verification-run",
        action="store_true",
        help=(
            "skip the installed sdf verify command; use this when "
            "the helper is itself part of the configured verification boundary"
        ),
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="sdf-editable-install-") as temp_dir:
        venv_dir = Path(temp_dir) / "venv"
        print_step(f"Creating temporary venv: {venv_dir}")
        venv.EnvBuilder(with_pip=True, symlinks=True).create(venv_dir)

        python_path = _venv_python(venv_dir)
        sdf_path = _venv_script(venv_dir, "sdf")

        wheels_dir = Path(temp_dir) / "wheels"
        wheels_dir.mkdir()
        build_result = run_command(
            "build package wheel",
            (
                sys.executable,
                "-m",
                "pip",
                "wheel",
                ".",
                "--no-build-isolation",
                "--no-deps",
                "--wheel-dir",
                str(wheels_dir),
            ),
            cwd=repo_root,
        )
        if build_result.returncode != 0:
            return build_result.returncode
        wheel = _single_wheel(wheels_dir)

        commands = [
            ("venv Python version", (str(python_path), "--version")),
            ("venv pip version", (str(python_path), "-m", "pip", "--version")),
            (
                "install packaged wheel",
                (
                    str(python_path),
                    "-m",
                    "pip",
                    "install",
                    "--no-deps",
                    "--force-reinstall",
                    str(wheel),
                ),
            ),
        ]

        for label, command in commands:
            result = run_command(label, command, cwd=repo_root)
            if result.returncode != 0:
                return result.returncode

        for label, sdf_args in _sdf_commands(
            include_full_verification_run=not args.skip_full_verification_run
        ):
            result = run_command(label, (str(sdf_path), *sdf_args), cwd=repo_root)
            if result.returncode != 0:
                return result.returncode

    print()
    print("Packaged install smoke passed.")
    return 0


def run_command(
    label: str, command: Sequence[str], *, cwd: Path
) -> subprocess.CompletedProcess[str]:
    print_step(label)
    print("$ " + " ".join(command))
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
    )
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n")
    return result


def _sdf_commands(
    *, include_full_verification_run: bool
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    if include_full_verification_run:
        return (*SDF_SMOKE_COMMANDS, *FULL_VERIFICATION_COMMAND)
    return SDF_SMOKE_COMMANDS


def print_step(message: str) -> None:
    print()
    print(f"==> {message}")


def _venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _venv_script(venv_dir: Path, name: str) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / f"{name}.exe"
    return venv_dir / "bin" / name


def _single_wheel(directory: Path) -> Path:
    wheels = tuple(directory.glob("software_dark_factory-*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(
            f"expected one software-dark-factory wheel in {directory}, found {wheels}"
        )
    return wheels[0]


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print()
        print("Packaged install smoke interrupted.")
        raise SystemExit(130)
