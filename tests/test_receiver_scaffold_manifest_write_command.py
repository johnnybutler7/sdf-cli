import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sdf_cli.main import main
from sdf_cli.receiver_payload_manifest import RECEIVER_PAYLOAD_MANIFEST
from sdf_cli.receiver_scaffold_content import PORTABLE_SOURCE_FILES, starter_content


class InitManifestWriteCommandTest(unittest.TestCase):
    def test_init_creates_the_unchanged_manifest_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            with redirect_stdout(io.StringIO()):
                exit_code = main(["init", "--repo", str(repo)])

            self.assertEqual(exit_code, 0)
            for entry in RECEIVER_PAYLOAD_MANIFEST:
                with self.subTest(path=entry.path):
                    self.assertTrue((repo / entry.path).is_file())
            for relative_path in PORTABLE_SOURCE_FILES:
                with self.subTest(path=relative_path):
                    self.assertEqual(
                        starter_content(relative_path),
                        (repo / relative_path).read_text(encoding="utf-8"),
                    )

    def test_init_keeps_excluded_sdf_runtime_directories_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            with redirect_stdout(io.StringIO()):
                exit_code = main(["init", "--repo", str(repo)])

            self.assertEqual(exit_code, 0)
            for path in (".sdf/evidence", ".sdf/work-items", ".sdf/local"):
                with self.subTest(path=path):
                    self.assertFalse((repo / path).exists())

    def test_init_creates_the_intentionally_failing_verification_placeholder(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            with redirect_stdout(io.StringIO()):
                exit_code = main(["init", "--repo", str(repo)])

            verification_content = (repo / ".sdf" / "verification.yml").read_text(
                encoding="utf-8"
            )
            self.assertEqual(exit_code, 0)
            self.assertIn("configure-receiver-verification", verification_content)
            self.assertIn("&& exit 1", verification_content)
            self.assertIn("required: true", verification_content)


if __name__ == "__main__":
    unittest.main()
