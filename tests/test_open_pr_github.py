import json
import subprocess
import unittest
from unittest.mock import patch

from tests.open_pr_body_helpers import observed_pr

from sdf_cli.open_pr_github import GhOpenPrBoundary


class GhOpenPrBoundaryTest(unittest.TestCase):
    def test_observation_captures_github_etag_with_complete_state(self):
        payload = {
            "number": 41,
            "state": "open",
            "draft": True,
            "body": "Native summary",
            "head": {
                "sha": "0123456789abcdef0123456789abcdef01234567",
                "repo": {"full_name": "example/sdf-cli"},
            },
            "base": {"ref": "main"},
        }
        response = _response(200, etag='W/"state-one"', body=json.dumps(payload))
        completed = subprocess.CompletedProcess([], 0, stdout=response)

        with patch("sdf_cli.open_pr_github.subprocess.run", return_value=completed):
            observed = GhOpenPrBoundary().observe_pull_request(
                "example/sdf-cli", "41"
            )

        self.assertEqual(observed.etag, 'W/"state-one"')
        self.assertEqual(observed.body, "Native summary")
        self.assertEqual(observed.head_repository, "example/sdf-cli")

    def test_body_patch_requires_etag_not_modified_response(self):
        freshness = subprocess.CompletedProcess(
            [],
            1,
            stdout=_response(304, etag='"state-one"'),
            stderr="gh: HTTP 304\n",
        )
        mutation = subprocess.CompletedProcess([], 0)

        with patch(
            "sdf_cli.open_pr_github.subprocess.run",
            side_effect=(freshness, mutation),
        ) as run:
            updated = GhOpenPrBoundary().update_pr_body_if_current(
                "41",
                "example/sdf-cli",
                observed_pr(etag='W/"state-one"'),
                "Rendered body",
            )

        self.assertTrue(updated)
        self.assertIn("If-None-Match: W/\"state-one\"", run.call_args_list[0].args[0])
        mutation_call = run.call_args_list[1]
        self.assertIn("PATCH", mutation_call.args[0])
        self.assertEqual(
            json.loads(mutation_call.kwargs["input"]), {"body": "Rendered body"}
        )

    def test_changed_etag_refuses_without_patch(self):
        changed = subprocess.CompletedProcess(
            [],
            0,
            stdout=_response(200, etag='W/"state-two"', body="{}"),
            stderr="",
        )

        with patch(
            "sdf_cli.open_pr_github.subprocess.run", return_value=changed
        ) as run:
            updated = GhOpenPrBoundary().update_pr_body_if_current(
                "41",
                "example/sdf-cli",
                observed_pr(etag='W/"state-one"'),
                "Rendered body",
            )

        self.assertFalse(updated)
        self.assertEqual(run.call_count, 1)


def _response(status: int, *, etag: str, body: str = "") -> str:
    reason = "OK" if status == 200 else "Not Modified"
    return f"HTTP/2.0 {status} {reason}\r\nEtag: {etag}\r\n\r\n{body}"


if __name__ == "__main__":
    unittest.main()
