"""Diagnostic context-budget report for the installed SDF Front Door.

This module is deliberately outside the public ``sdf`` command surface.  It
measures the portable guidance selected by the receiver payload manifest and
reports receiver-owned routed content separately.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from math import ceil
from pathlib import Path
from typing import Iterable

from sdf_cli.config.receiver_playbooks import parse_receiver_playbooks
from sdf_cli.receiver_scaffold_content import PORTABLE_SOURCE_FILES, portable_resource

FRONT_DOOR_START = "<!-- SDF Front Door: start -->"
FRONT_DOOR_END = "<!-- SDF Front Door: end -->"
TOKEN_ESTIMATE_METHOD = "deterministic approximation: ceil(characters / 4)"

BOOTSTRAP = "mandatory bootstrap"
TASK_ROUTED = "task-routed SDF core"
CLOSEOUT = "closeout-only SDF core"


class ContextBudgetError(ValueError):
    """Raised when the supplied repository cannot provide required context."""


@dataclass(frozen=True)
class Metrics:
    """Deterministic text measures for one source."""

    bytes: int
    characters: int
    words: int
    estimated_tokens: int


@dataclass(frozen=True)
class MeasuredSource:
    """One included or excluded source in the report."""

    source: str
    category: str
    ownership: str
    metrics: Metrics


@dataclass(frozen=True)
class ContextBudget:
    """Complete, serializable report for one repository's Front Door."""

    included_sources: tuple[MeasuredSource, ...]
    excluded_receiver_owned_sources: tuple[MeasuredSource, ...]
    excluded_nonstanding_context: tuple[str, ...]
    ambiguities: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        included_totals = {
            BOOTSTRAP: _sum_metrics(
                source.metrics
                for source in self.included_sources
                if source.category == BOOTSTRAP
            ),
            TASK_ROUTED: _sum_metrics(
                source.metrics
                for source in self.included_sources
                if source.category == TASK_ROUTED
            ),
            CLOSEOUT: _sum_metrics(
                source.metrics
                for source in self.included_sources
                if source.category == CLOSEOUT
            ),
        }
        return {
            "schema_version": 1,
            "token_estimate_method": TOKEN_ESTIMATE_METHOD,
            "included_sources": [
                _source_dict(source) for source in self.included_sources
            ],
            "totals": {
                "cold_discovery": _metrics_dict(included_totals[BOOTSTRAP]),
                "governed_change_incremental": _metrics_dict(
                    included_totals[TASK_ROUTED]
                ),
                "closeout_incremental": _metrics_dict(included_totals[CLOSEOUT]),
                "maximum_sdf_owned": _metrics_dict(
                    _sum_metrics(included_totals.values())
                ),
            },
            "excluded_receiver_owned_sources": [
                _source_dict(source) for source in self.excluded_receiver_owned_sources
            ],
            "excluded_receiver_owned_total": _metrics_dict(
                _sum_metrics(
                    source.metrics for source in self.excluded_receiver_owned_sources
                )
            ),
            "excluded_nonstanding_context": list(self.excluded_nonstanding_context),
            "ambiguities": list(self.ambiguities),
        }


def collect_context_budget(repo: Path) -> ContextBudget:
    """Measure installed portable context and separately measure local exclusions."""

    repo = repo.resolve()
    bridge, agents_remainder = _front_door_parts(repo / "AGENTS.md")
    included = [
        _measured("AGENTS.md::SDF Front Door block", BOOTSTRAP, "SDF-owned", bridge),
    ]
    included.extend(_portable_sources())

    excluded = [
        _measured(
            "AGENTS.md::receiver-owned remainder",
            "receiver-owned repository guidance",
            "receiver-owned",
            agents_remainder,
        ),
        _measured_file(
            repo / ".sdf" / "config.yml",
            "receiver-owned routing configuration",
        ),
        _measured_file(
            repo / ".sdf" / "verification.yml",
            "receiver-owned verification boundary",
        ),
    ]
    excluded.extend(_receiver_playbook_sources(repo))
    excluded.extend(_repo_local_portable_extensions(repo))

    return ContextBudget(
        included_sources=tuple(included),
        excluded_receiver_owned_sources=tuple(excluded),
        excluded_nonstanding_context=(
            ".sdf/evidence/** generated current and prior evidence archives",
            ".sdf/work-items/** prior work-item archives",
            "src/sdf_cli/** CLI source and packaged implementation code",
            ".sdf/verification.yml commands, which are executed rather than "
            "loaded as standing prose",
            "external skills, agent-system prompts, and tool documentation",
            "sdf guidance --repo . output, which is live routing metadata "
            "rather than standing guidance text",
        ),
        ambiguities=(
            "The two contracts are conditional in agent instructions: this "
            "report counts the verification contract during ordinary governed "
            "execution and the evidence contract during closeout because the "
            "governed loop directs those phases to them.",
            "The report measures the manifest-backed packaged portable text, "
            "not a receiver's modified copy. This repository's extra "
            "Repo-Local Dogfood Activation section is reported as a "
            "receiver-owned extension.",
            "Agent surfaces can preload AGENTS.md or follow its Front Door "
            "link lazily. The cold-discovery total assumes the marked Front "
            "Door block and portable agent instructions are both consumed.",
        ),
    )


def _portable_sources() -> list[MeasuredSource]:
    sources: list[MeasuredSource] = []
    for relative_path in PORTABLE_SOURCE_FILES:
        content = portable_resource(relative_path).read_text(encoding="utf-8")
        category = _portable_category(relative_path)
        package_path = (
            "package:sdf_cli/resources/portable_sdf/sdf/"
            + relative_path.removeprefix(".sdf/")
        )
        sources.append(_measured(package_path, category, "SDF-owned", content))
    return sources


def _portable_category(relative_path: str) -> str:
    if relative_path == ".sdf/agent-instructions.md":
        return BOOTSTRAP
    if relative_path == ".sdf/playbooks/governed-change-loop.md":
        return TASK_ROUTED
    if relative_path == ".sdf/contracts/verification-config.md":
        return TASK_ROUTED
    if relative_path in {
        ".sdf/contracts/evidence-archive.md",
        ".sdf/standard-sdf-non-claims.md",
    }:
        return CLOSEOUT
    raise ContextBudgetError(
        "portable manifest path is not classified by the governed routing: "
        f"{relative_path}"
    )


def _front_door_parts(path: Path) -> tuple[str, str]:
    text = _read_text(path)
    start = text.find(FRONT_DOOR_START)
    end = text.find(FRONT_DOOR_END)
    if start < 0 or end < start:
        raise ContextBudgetError(f"missing SDF Front Door markers in {path}")
    end += len(FRONT_DOOR_END)
    bridge = text[start:end]
    remainder = text[:start] + text[end:]
    return bridge, remainder


def _receiver_playbook_sources(repo: Path) -> list[MeasuredSource]:
    config_path = repo / ".sdf" / "config.yml"
    sources: list[MeasuredSource] = []
    for playbook in parse_receiver_playbooks(config_path):
        path = repo / playbook.path
        sources.append(
            _measured_file(
                path,
                "receiver-owned configured playbook "
                f"[{', '.join(playbook.categories)}]",
            )
        )
    return sources


def _repo_local_portable_extensions(repo: Path) -> list[MeasuredSource]:
    sources: list[MeasuredSource] = []
    for relative_path in PORTABLE_SOURCE_FILES:
        live_path = repo / relative_path
        if not live_path.is_file():
            continue
        portable = portable_resource(relative_path).read_text(encoding="utf-8")
        live = _read_text(live_path)
        if live == portable:
            continue
        if live.startswith(portable):
            extension = live[len(portable) :]
        else:
            extension = live
        sources.append(
            _measured(
                f"{relative_path}::receiver-local extension",
                "receiver-owned local override of portable guidance",
                "receiver-owned",
                extension,
            )
        )
    return sources


def _measured_file(path: Path, category: str) -> MeasuredSource:
    return _measured(path.as_posix(), category, "receiver-owned", _read_text(path))


def _measured(source: str, category: str, ownership: str, text: str) -> MeasuredSource:
    return MeasuredSource(
        source=source,
        category=category,
        ownership=ownership,
        metrics=Metrics(
            bytes=len(text.encode("utf-8")),
            characters=len(text),
            words=len(re.findall(r"\S+", text)),
            estimated_tokens=ceil(len(text) / 4),
        ),
    )


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise ContextBudgetError(f"required context source is missing: {path}")
    return path.read_text(encoding="utf-8")


def _sum_metrics(metrics: Iterable[Metrics]) -> Metrics:
    values = tuple(metrics)
    return Metrics(
        bytes=sum(value.bytes for value in values),
        characters=sum(value.characters for value in values),
        words=sum(value.words for value in values),
        estimated_tokens=sum(value.estimated_tokens for value in values),
    )


def _source_dict(source: MeasuredSource) -> dict[str, object]:
    return {
        "source": source.source,
        "category": source.category,
        "ownership": source.ownership,
        **_metrics_dict(source.metrics),
    }


def _metrics_dict(metrics: Metrics) -> dict[str, int]:
    return asdict(metrics)
