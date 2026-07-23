import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Optional

from sdf_cli.main import main
from sdf_cli.pr_body import render_pr_body_write_result, write_pr_body_artifact
from sdf_cli.pr_body_check import check_pr_body_artifact, render_pr_body_check
from sdf_cli.pr_body_github_context import resolve_pr_body_link_options
from sdf_cli.pr_body_links import validate_pr_body_link_options


class CommandResult:
    def __init__(self, exit_code: int, stdout: str, stderr: str = "") -> None:
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


def run_pr_body_write(
    repo: Path,
    change_id: str,
    *,
    overwrite: bool = False,
    link_mode: Optional[str] = None,
    github_repo: Optional[str] = None,
    github_ref: Optional[str] = None,
) -> CommandResult:
    options = _link_options(repo, change_id, link_mode, github_repo, github_ref)
    if isinstance(options, CommandResult):
        return options
    result = write_pr_body_artifact(
        repo=str(repo),
        change_id=change_id,
        overwrite=overwrite,
        link_mode=options.link_mode,
        github_repo=options.github_repo,
        github_ref=options.github_ref,
    )
    return CommandResult(result.exit_code, render_pr_body_write_result(result))


def run_pr_body_check(
    repo: Path,
    change_id: str,
    *,
    link_mode: Optional[str] = None,
    github_repo: Optional[str] = None,
    github_ref: Optional[str] = None,
) -> CommandResult:
    options = _link_options(repo, change_id, link_mode, github_repo, github_ref)
    if isinstance(options, CommandResult):
        return options
    result = check_pr_body_artifact(
        repo=str(repo),
        change_id=change_id,
        link_mode=options.link_mode,
        github_repo=options.github_repo,
        github_ref=options.github_ref,
    )
    return CommandResult(result.exit_code, render_pr_body_check(result))


def _link_options(
    repo: Path,
    change_id: str,
    link_mode: Optional[str],
    github_repo: Optional[str],
    github_ref: Optional[str],
):
    options = resolve_pr_body_link_options(
        repo=str(repo),
        link_mode=link_mode,
        github_repo=github_repo,
        github_ref=github_ref,
        change_id=change_id,
    )
    errors = validate_pr_body_link_options(
        link_mode=options.link_mode,
        github_repo=options.github_repo,
        github_ref=options.github_ref,
    )
    if errors:
        return CommandResult(2, "", "; ".join(errors))
    return options


def run_handoff(
    repo: Path,
    change_id: str,
    *,
    overwrite: bool = False,
    surface: Optional[str] = None,
    model: Optional[str] = None,
    reasoning: Optional[str] = None,
    speed: Optional[str] = None,
    link_mode: Optional[str] = None,
    github_repo: Optional[str] = None,
    github_ref: Optional[str] = None,
) -> CommandResult:
    argv = [
        "close",
        "--repo",
        str(repo),
        "--change-id",
        change_id,
    ]
    if overwrite:
        argv.append("--overwrite")
    if surface:
        argv.extend(["--surface", surface])
    if model:
        argv.extend(["--model", model])
    if reasoning:
        argv.extend(["--reasoning", reasoning])
    if speed:
        argv.extend(["--speed", speed])
    if link_mode:
        argv.extend(["--link-mode", link_mode])
    if github_repo:
        argv.extend(["--github-repo", github_repo])
    if github_ref:
        argv.extend(["--github-ref", github_ref])
    return run_command(argv)


def run_command(argv: list[str]) -> CommandResult:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            exit_code = main(argv)
        except SystemExit as raised:
            exit_code = int(raised.code)
    return CommandResult(
        exit_code=exit_code,
        stdout=stdout.getvalue(),
        stderr=stderr.getvalue(),
    )
