import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from sdf_cli.main import main


class InitWriteSafetyTest(unittest.TestCase):
    def test_init_never_overwrites_an_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            config_path = repo / ".sdf" / "config.yml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("receiver-owned: true\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                exit_code = main(["init", "--repo", str(repo)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                "receiver-owned: true\n", config_path.read_text(encoding="utf-8")
            )

    def test_init_retains_the_shared_gitattributes_append_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            attributes_path = repo / ".gitattributes"
            attributes_path.write_text("*.png binary\n", encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["init", "--repo", str(repo)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                "*.png binary\n.sdf/evidence/** linguist-generated=true\n",
                attributes_path.read_text(encoding="utf-8"),
            )
            self.assertIn("1 shared rules updated", stdout.getvalue())

    def test_init_creates_handoff_ignore_rule_for_fresh_receiver(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["init", "--repo", str(repo)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                ".sdf/handoffs/\n",
                (repo / ".gitignore").read_text(encoding="utf-8"),
            )
            self.assertIn("11 created", stdout.getvalue())

    def test_init_preserves_gitignore_content_when_appending_handoff_rule(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            ignore_path = repo / ".gitignore"
            ignore_path.write_text("build/\n.env\n", encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["init", "--repo", str(repo)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                "build/\n.env\n.sdf/handoffs/\n",
                ignore_path.read_text(encoding="utf-8"),
            )
            self.assertIn("1 shared rules updated", stdout.getvalue())

    def test_repeated_init_does_not_duplicate_handoff_ignore_rule(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            with redirect_stdout(io.StringIO()):
                first_exit = main(["init", "--repo", str(repo)])
                second_exit = main(["init", "--repo", str(repo)])

            self.assertEqual(first_exit, 0)
            self.assertEqual(second_exit, 0)
            self.assertEqual(
                ".sdf/handoffs/\n",
                (repo / ".gitignore").read_text(encoding="utf-8"),
            )

    def test_existing_equivalent_handoff_ignore_rule_is_left_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            ignore_path = repo / ".gitignore"
            original = "build/\n/.sdf/handoffs/**\n"
            ignore_path.write_text(original, encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["init", "--repo", str(repo)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(original, ignore_path.read_text(encoding="utf-8"))
            self.assertIn("1 existing files unchanged", stdout.getvalue())

    def test_init_write_failure_exits_nonzero_with_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / ".sdf" / "config.yml").mkdir(parents=True)
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    main(["init", "--repo", str(repo)])

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("init: failed to create .sdf/config.yml", stderr.getvalue())

    def test_missing_packaged_resource_fails_before_creating_a_receiver(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            stderr = io.StringIO()

            with patch(
                "sdf_cli.receiver_scaffold.starter_content",
                side_effect=FileNotFoundError("packaged resource missing"),
            ), redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    main(["init", "--repo", str(repo)])

            self.assertFalse((repo / ".sdf").exists())

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("required packaged resource unavailable", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
