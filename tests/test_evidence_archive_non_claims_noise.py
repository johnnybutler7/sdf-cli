import tempfile
import unittest
from pathlib import Path

from tests.test_evidence_archive_scaffold_command import run_scaffold


class EvidenceArchiveNonClaimsNoiseTest(unittest.TestCase):
    def test_scaffold_does_not_inject_standard_non_claims_boilerplate(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            result = run_scaffold(
                repo,
                "reduce-non-claims-noise",
            )

            archive = repo / ".sdf" / "evidence" / "reduce-non-claims-noise"
            contents = {
                "evidence.md": (archive / "evidence.md").read_text(encoding="utf-8")
            }
            archive_content = "\n".join(contents.values())

            self.assertEqual(result.exit_code, 0)
            self.assertNotIn("standard-sdf-non-claims.md", archive_content)
            self.assertNotIn("Standard SDF non-claims", contents["evidence.md"])
            self.assertFalse((archive / "verification.md").exists())


if __name__ == "__main__":
    unittest.main()
