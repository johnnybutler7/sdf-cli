import tempfile
import unittest
from pathlib import Path

from tests.closeout_summary_fixtures import write_archive
from tests.test_closeout_pr_body_github_links import (
    github_blob,
    run_github_check,
    write_pr_body_with_links,
)


class CloseoutPrBodyMalformedLinksTest(unittest.TestCase):
    def test_pr_body_check_rejects_doubled_backticks_around_url(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            change_id = "backticked-github-pr-body"
            write_archive(repo, change_id)
            links = [
                github_blob(change_id, "evidence.md"),
            ]
            links[0] = f"``{links[0]}``"
            write_pr_body_with_links(repo, change_id, links)

            result = run_github_check(repo, change_id)

        self.assertEqual(result.exit_code, 1)
        self.assertIn("missing evidence link: evidence.md", result.stdout)
        self.assertIn("malformed evidence link: ``https://github.com/", result.stdout)


if __name__ == "__main__":
    unittest.main()
