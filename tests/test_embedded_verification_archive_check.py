import tempfile
import unittest
from pathlib import Path

from tests.evidence_archive_helpers import write_current_archive

from sdf_cli.evidence_archive_check import check_evidence_archive


class EmbeddedVerificationArchiveCheckTest(unittest.TestCase):
    def test_new_contract_four_archive_uses_embedded_machine_record(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            write_current_archive(repo, "embedded-verification")

            result = check_evidence_archive(str(repo), "embedded-verification")

        self.assertTrue(result.passed)
        self.assertEqual(result.exit_code, 0)
        filenames = tuple(file.filename for file in result.files)
        self.assertEqual(filenames, ("evidence.md",))
