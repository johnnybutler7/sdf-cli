import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.check_python_module_size import audit_paths, main, render_audit


class PythonModuleSizeAuditTest(unittest.TestCase):
    def test_no_findings_exits_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_python_file(root / "small.py", 2)

            audit = audit_paths([root], warn_threshold=3, fail_threshold=5)

        self.assertEqual(audit.exit_code, 0)
        self.assertEqual(audit.warnings, ())
        self.assertEqual(audit.failures, ())
        self.assertIn("Warnings:\n- none", render_audit(audit))
        self.assertIn("Failures:\n- none", render_audit(audit))
        self.assertIn("Overall: passed", render_audit(audit))

    def test_warn_threshold_reports_warning_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module = root / "warning.py"
            self._write_python_file(module, 3)

            audit = audit_paths([root], warn_threshold=3, fail_threshold=5)

        self.assertEqual(audit.exit_code, 0)
        self.assertEqual(audit.warnings[0].path, module.as_posix())
        self.assertEqual(audit.warnings[0].lines, 3)
        self.assertEqual(audit.failures, ())
        self.assertIn(f"- {module.as_posix()}: 3 lines", render_audit(audit))

    def test_fail_threshold_reports_failure_and_exits_one(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module = root / "failure.py"
            self._write_python_file(module, 5)

            audit = audit_paths([root], warn_threshold=3, fail_threshold=5)

        self.assertEqual(audit.exit_code, 1)
        self.assertEqual(audit.warnings, ())
        self.assertEqual(audit.failures[0].path, module.as_posix())
        self.assertEqual(audit.failures[0].lines, 5)
        self.assertIn("Overall: failed", render_audit(audit))

    def test_ignored_folders_are_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_python_file(root / ".venv" / "large.py", 5)
            self._write_python_file(root / "__pycache__" / "cached.py", 5)
            self._write_python_file(root / ".ruff_cache" / "cached.py", 5)

            audit = audit_paths([root], warn_threshold=3, fail_threshold=5)

        self.assertEqual(audit.exit_code, 0)
        self.assertEqual(audit.warnings, ())
        self.assertEqual(audit.failures, ())

    def test_findings_are_deterministically_ordered(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            second = root / "zeta.py"
            first = root / "alpha.py"
            self._write_python_file(second, 3)
            self._write_python_file(first, 3)

            audit = audit_paths([root], warn_threshold=3, fail_threshold=5)

        self.assertEqual(
            [finding.path for finding in audit.warnings],
            [first.as_posix(), second.as_posix()],
        )

    def test_main_prints_report_and_returns_audit_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_python_file(root / "small.py", 1)
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main([str(root)])

        self.assertEqual(exit_code, 0)
        self.assertIn("Python module-size audit", stdout.getvalue())
        self.assertIn("Warn threshold: 150 lines", stdout.getvalue())
        self.assertIn("Fail threshold: 250 lines", stdout.getvalue())

    def _write_python_file(self, path: Path, line_count: int) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("print('x')\n" * line_count, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
