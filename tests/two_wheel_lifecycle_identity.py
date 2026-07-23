"""Installed-identity checks for the test-only two-wheel rehearsal."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from two_wheel_lifecycle_artifact import (
    LifecycleRehearsalError,
    WheelArtifact,
    is_within,
    key_values,
)


@dataclass(frozen=True)
class LifecycleObservation:
    step: str
    artifact: WheelArtifact
    executable: Path
    import_location: Path


RunCommand = Callable[[str, tuple[str, ...], Path], object]


def assert_identity(
    run: RunCommand,
    step: str,
    artifact: WheelArtifact,
    pip: tuple[str, ...],
    python: Path,
    executable: Path,
    workspace: Path,
) -> LifecycleObservation:
    package_result = run(
        "installed package", (*pip, "show", "software-dark-factory"), workspace
    )
    package = key_values(package_result.stdout)
    version = run("CLI version", (str(executable), "--version"), workspace)
    identity_result = run("CLI identity", (str(executable), "--identity"), workspace)
    identity = key_values(identity_result.stdout)
    imported = run(
        "fresh-shell import location",
        (
            str(python),
            "-c",
            "from pathlib import Path; import sdf_cli; "
            "print(Path(sdf_cli.__file__).resolve().parent)",
        ),
        workspace,
    ).stdout.strip()
    import_location = Path(imported).resolve()
    expected_executable = executable.resolve()

    _expect(
        step, artifact, "package name", "software-dark-factory", package.get("Name")
    )
    _expect(step, artifact, "package version", artifact.version, package.get("Version"))
    _expect(
        step,
        artifact,
        "CLI version",
        f"software-dark-factory {artifact.version}",
        version.stdout.strip(),
    )
    _expect(
        step,
        artifact,
        "identity package version",
        artifact.version,
        identity.get("package_version"),
    )
    _expect(
        step,
        artifact,
        "identity executable path",
        str(expected_executable),
        identity.get("executable_location"),
    )
    _expect(
        step,
        artifact,
        "identity imported package location",
        str(import_location),
        identity.get("imported_package_location"),
    )
    _expect(
        step,
        artifact,
        "identity installation mode",
        "installed",
        identity.get("installation_mode"),
    )
    if not is_within(import_location, python.parent.parent):
        _mismatch(
            step,
            artifact,
            "imported package location",
            "inside temporary venv",
            str(import_location),
        )
    _expect(
        step,
        artifact,
        "installed package location",
        str(import_location.parent),
        package.get("Location"),
    )
    return LifecycleObservation(step, artifact, expected_executable, import_location)


def assert_expected(
    step: str,
    artifact: WheelArtifact,
    field: str,
    expected: str,
    observed: str | None,
) -> None:
    _expect(step, artifact, field, expected, observed)


def _expect(
    step: str,
    artifact: WheelArtifact,
    field: str,
    expected: str,
    observed: str | None,
) -> None:
    if observed != expected:
        _mismatch(step, artifact, field, expected, observed)


def _mismatch(
    step: str,
    artifact: WheelArtifact,
    field: str,
    expected: str,
    observed: str | None,
) -> None:
    raise LifecycleRehearsalError(
        f"Observed identity mismatch during {step}: {field} expected {expected!r} "
        f"from supplied wheel {artifact.path.name}; observed {observed!r}."
    )
