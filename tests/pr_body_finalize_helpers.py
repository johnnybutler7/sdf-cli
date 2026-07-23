from sdf_cli.pr_body_finalize_merged import FinalizeMergedPrBodyOptions

SHA = "0123456789abcdef0123456789abcdef01234567"
OTHER_SHA = "abcdef0123456789abcdef0123456789abcdef01"
GITHUB_REPO = "example/sdf-cli"


class FakeGithubPrBoundary:
    def __init__(self, body: str) -> None:
        self.body = body
        self.updated_body: str | None = None
        self.read_calls: list[tuple[str, str]] = []
        self.update_calls: list[tuple[str, str]] = []

    def read_pr_body(self, pr_number: str, github_repo: str) -> str:
        self.read_calls.append((pr_number, github_repo))
        return self.body

    def update_pr_body(self, pr_number: str, github_repo: str, body: str) -> None:
        self.update_calls.append((pr_number, github_repo))
        self.updated_body = body


def options() -> FinalizeMergedPrBodyOptions:
    return FinalizeMergedPrBodyOptions(
        pr_number="197",
        github_repo=GITHUB_REPO,
        merge_sha=OTHER_SHA,
    )


def body_with_branch_links(extra_line: str = "") -> str:
    extra = f"{extra_line}\n" if extra_line else ""
    return (
        "# What you are reviewing\n\n"
        f"{extra}"
        "[Evidence notes](https://github.com/example/sdf-cli/blob/"
        "feature-branch/.sdf/evidence/finalise-links/evidence.md)\n"
        "[Review notes](.sdf/evidence/historical-links/review.md#review-focus)\n"
    )
