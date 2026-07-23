import os
import subprocess
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sdf_cli.open_pr_github import observed_pull_request


class PublishOpenPrBodyWorkflowTest(unittest.TestCase):
    def test_workflow_is_manual_and_runs_only_trusted_default_branch_code(self):
        workflow = Path(
            ".github/workflows/publish-open-pr-body.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("pull_request_target:", workflow)
        self.assertNotIn("pull_request:", workflow)
        self.assertIn("pull-requests: write", workflow)
        self.assertIn("ref: ${{ github.event.repository.default_branch }}", workflow)
        self.assertIn("path: trusted-base", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("PYTHONPATH: ${{ github.workspace }}/trusted-base/src", workflow)
        self.assertNotIn("github.event.pull_request.head.sha", workflow)
        self.assertIn("publish-open-pr-body", workflow)
        self.assertIn("PR_NUMBER: ${{ inputs.pr_number }}", workflow)
        self.assertNotIn("${{", self._run_script(workflow))

    def test_malicious_dispatch_input_cannot_become_shell_syntax(self):
        workflow = Path(
            ".github/workflows/publish-open-pr-body.yml"
        ).read_text(encoding="utf-8")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            cli_marker = root / "cli-invoked"
            malicious_marker = root / "shell-injected"
            python = bin_dir / "python3"
            python.write_text(
                '#!/bin/sh\ntouch "$CLI_MARKER"\n', encoding="utf-8"
            )
            python.chmod(0o755)
            environment = os.environ.copy()
            environment.update(
                {
                    "PR_NUMBER": '41"; touch "$MALICIOUS_MARKER"; echo "',
                    "GITHUB_REPOSITORY": "example/sdf-cli",
                    "DEFAULT_BRANCH": "main",
                    "PYTHONPATH": "src",
                    "CLI_MARKER": str(cli_marker),
                    "MALICIOUS_MARKER": str(malicious_marker),
                    "PATH": f"{bin_dir}:{environment['PATH']}",
                }
            )

            result = subprocess.run(
                ["bash", "-c", self._run_script(workflow)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("positive integer", result.stderr)
            self.assertFalse(cli_marker.exists())
            self.assertFalse(malicious_marker.exists())

    def test_positive_dispatch_number_is_passed_as_one_cli_argument(self):
        workflow = Path(
            ".github/workflows/publish-open-pr-body.yml"
        ).read_text(encoding="utf-8")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            arguments_file = root / "arguments"
            python = bin_dir / "python3"
            python.write_text(
                '#!/bin/sh\nprintf \'%s\\n\' "$@" > "$CLI_ARGUMENTS"\n',
                encoding="utf-8",
            )
            python.chmod(0o755)
            environment = os.environ.copy()
            environment.update(
                {
                    "PR_NUMBER": "41",
                    "GITHUB_REPOSITORY": "example/sdf-cli",
                    "DEFAULT_BRANCH": "main",
                    "PYTHONPATH": "src",
                    "CLI_ARGUMENTS": str(arguments_file),
                    "PATH": f"{bin_dir}:{environment['PATH']}",
                }
            )

            result = subprocess.run(
                ["bash", "-c", self._run_script(workflow)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                arguments_file.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "sdf_cli.main",
                    "publish-open-pr-body",
                    "--pr-number",
                    "41",
                    "--github-repo",
                    "example/sdf-cli",
                    "--base-branch",
                    "main",
                ],
            )

    def test_github_payload_is_the_source_of_current_head_and_state(self):
        observed = observed_pull_request(
            {
                "number": 41,
                "state": "open",
                "draft": True,
                "body": "Native summary",
                "head": {
                    "sha": "0123456789abcdef0123456789abcdef01234567",
                    "ref": "ignored-provider-branch",
                    "repo": {"full_name": "example/sdf-cli"},
                },
                "base": {"ref": "main"},
            }
        )

        self.assertEqual(
            observed.head_sha, "0123456789abcdef0123456789abcdef01234567"
        )
        self.assertEqual(observed.state, "open")
        self.assertEqual(observed.base_ref, "main")
        self.assertFalse(hasattr(observed, "head_ref"))

    @staticmethod
    def _run_script(workflow: str) -> str:
        marker = "        run: |\n"
        _, found, script = workflow.partition(marker)
        if not found:
            raise AssertionError("workflow run script is missing")
        return textwrap.dedent(script)


if __name__ == "__main__":
    unittest.main()
