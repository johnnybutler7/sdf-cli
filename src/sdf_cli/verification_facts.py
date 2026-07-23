"""Opt-in structured facts supplied by verification executors."""

from __future__ import annotations

from subprocess import CompletedProcess

from sdf_cli.verification_results import VerificationFactValue


def structured_facts(
    completed: CompletedProcess[str],
) -> tuple[tuple[str, VerificationFactValue], ...]:
    """Read facts supplied by a structured executor, never command output."""
    facts = getattr(completed, "verification_facts", ())
    if not isinstance(facts, tuple):
        return ()
    accepted: list[tuple[str, VerificationFactValue]] = []
    for fact in facts:
        if (
            not isinstance(fact, tuple)
            or len(fact) != 2
            or not isinstance(fact[0], str)
            or not fact[0]
            or not isinstance(fact[1], (str, int, float, bool))
        ):
            continue
        accepted.append((fact[0], fact[1]))
    return tuple(accepted)
