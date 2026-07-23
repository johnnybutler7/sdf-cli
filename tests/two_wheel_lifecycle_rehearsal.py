"""Test-only rehearsal for a supplied local two-wheel SDF CLI lifecycle."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import venv
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from two_wheel_lifecycle_artifact import (
    LifecycleRehearsalError,
    WheelArtifact,
    inspect_wheel,
    yaml_value,
)
from two_wheel_lifecycle_identity import (
    LifecycleObservation,
    assert_expected,
    assert_identity,
)


@dataclass(frozen=True)
class LifecycleResult:
    first: WheelArtifact
    second: WheelArtifact
    observations: tuple[LifecycleObservation, ...]


CommandRunner = Callable[[tuple[str, ...], Path], subprocess.CompletedProcess[str]]
VenvCreator = Callable[[Path], None]


class TwoWheelLifecycleRehearsal:
    """Exercise only caller-supplied local wheels in a temporary workspace."""

    def __init__(
        self,
        *,
        command_runner: CommandRunner | None = None,
        venv_creator: VenvCreator | None = None,
    ) -> None:
        self._command_runner = command_runner or _run_command
        self._venv_creator = venv_creator or _create_venv

    def run(self, first_wheel: str | Path, second_wheel: str | Path) -> LifecycleResult:
        first = inspect_wheel(first_wheel)
        second = inspect_wheel(second_wheel)
        with tempfile.TemporaryDirectory(prefix="sdf-two-wheel-lifecycle-") as root:
            workspace = Path(root)
            environment = workspace / "venv"
            receiver = workspace / "receiver"
            receiver.mkdir()
            self._venv_creator(environment)
            python = _venv_program(environment, "python")
            pip = (str(python), "-m", "pip")
            executable = _venv_program(environment, "sdf")

            observations = [
                self._install_and_observe(
                    "initial install", first, pip, python, executable, workspace
                )
            ]
            self._assert_installed_receiver_resources(
                first, executable, receiver, workspace
            )
            observations.append(
                self._install_and_observe(
                    "upgrade", second, pip, python, executable, workspace
                )
            )
            observations.append(
                self._install_and_observe(
                    "force reinstall", second, pip, python, executable, workspace,
                    force_reinstall=True,
                )
            )
            observations.append(
                self._install_and_observe(
                    "rollback", first, pip, python, executable, workspace,
                    force_reinstall=True,
                )
            )
        return LifecycleResult(first, second, tuple(observations))

    def _install_and_observe(
        self,
        step: str,
        artifact: WheelArtifact,
        pip: tuple[str, ...],
        python: Path,
        executable: Path,
        workspace: Path,
        *,
        force_reinstall: bool = False,
    ) -> LifecycleObservation:
        command = (*pip, "install", "--no-index", "--no-deps", "--upgrade")
        if force_reinstall:
            command = (*command, "--force-reinstall")
        self._run(
            f"{step} local-wheel install", (*command, str(artifact.path)), workspace
        )
        return assert_identity(
            self._run, step, artifact, pip, python, executable, workspace
        )

    def _assert_installed_receiver_resources(
        self,
        artifact: WheelArtifact,
        executable: Path,
        receiver: Path,
        workspace: Path,
    ) -> None:
        self._run(
            "installed receiver scaffold",
            (str(executable), "init", "--repo", str(receiver)),
            workspace,
        )
        inspection = self._run(
            "installed receiver resource check",
            (str(executable), "init", "--check", "--repo", str(receiver)),
            workspace,
        )
        if "Overall: ready" not in inspection.stdout:
            raise LifecycleRehearsalError(
                "Installed receiver resource check did not report ready after "
                f"{artifact.path.name}: {inspection.stdout.strip() or 'no output'}"
            )
        config = receiver / ".sdf" / "config.yml"
        try:
            contents = config.read_text(encoding="utf-8")
        except OSError as error:
            raise LifecycleRehearsalError(
                f"Installed receiver scaffold did not create {config}: {error}"
            ) from error
        assert_expected(
            "initial install", artifact, "receiver Front Door package identity",
            f"software-dark-factory {artifact.version}",
            yaml_value(contents, "front_door_package"),
        )
        assert_expected(
            "initial install", artifact, "receiver Front Door release identity",
            f"v{artifact.version}",
            yaml_value(contents, "front_door_release"),
        )

    def _run(
        self, label: str, command: tuple[str, ...], workspace: Path
    ) -> subprocess.CompletedProcess[str]:
        result = self._command_runner(command, workspace)
        if result.returncode == 0:
            return result
        raise LifecycleRehearsalError(
            f"{label} failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

def _run_command(
    command: tuple[str, ...], workspace: Path
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        cwd=workspace,
        env=environment,
        text=True,
    )


def _create_venv(path: Path) -> None:
    venv.EnvBuilder(with_pip=True).create(path)


def _venv_program(environment: Path, name: str) -> Path:
    if os.name == "nt":
        suffix = ".exe" if name in {"python", "sdf"} else ""
        return environment / "Scripts" / f"{name}{suffix}"
    return environment / "bin" / name


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "first_wheel", help="first supplied local software-dark-factory wheel"
    )
    parser.add_argument(
        "second_wheel", help="second supplied local software-dark-factory wheel"
    )
    args = parser.parse_args(argv)
    try:
        result = TwoWheelLifecycleRehearsal().run(args.first_wheel, args.second_wheel)
    except LifecycleRehearsalError as error:
        print(f"Two-wheel lifecycle rehearsal failed: {error}", file=sys.stderr)
        return 1
    print("Two-wheel lifecycle rehearsal passed.")
    for label, artifact in (("First", result.first), ("Second", result.second)):
        print(f"{label} wheel: {artifact.path.name}")
        print(f"{label} SHA-256: {artifact.sha256}")
    print("Lifecycle: " + " -> ".join(item.step for item in result.observations))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
