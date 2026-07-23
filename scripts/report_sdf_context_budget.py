#!/usr/bin/env python3
"""Print a deterministic diagnostic budget for installed SDF guidance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

def main(argv: list[str] | None = None) -> int:
    from scripts.sdf_context_budget import ContextBudgetError, collect_context_budget

    parser = argparse.ArgumentParser(
        description="Measure portable SDF context without changing the receiver."
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Receiver repository to inspect (defaults to the current directory).",
    )
    args = parser.parse_args(argv)
    try:
        report = collect_context_budget(Path(args.repo))
    except ContextBudgetError as error:
        parser.error(str(error))
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
