import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from sdf_cli import __version__
from sdf_cli.identity import render_identity
from sdf_cli.main import build_parser, main


class CliFoundationTest(unittest.TestCase):
    def test_package_exposes_public_developer_preview_version(self):
        self.assertEqual(__version__, "0.1.0")

    def test_entrypoint_without_command_prints_top_level_help(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main([])

        self.assertEqual(exit_code, 0)
        help_text = stdout.getvalue()
        self.assertIn("SDF CLI for governed AI-assisted delivery", help_text)
        self.assertIn("First use with the installed sdf command:", help_text)
        self.assertIn("From the repository root:", help_text)
        self.assertIn("1. sdf init", help_text)
        self.assertIn("2. Configure and run sdf verify", help_text)
        self.assertIn(
            "3. Make the normal change, then run sdf close --change-id <change-id>",
            help_text,
        )
        self.assertIn(
            "Use --repo /path/to/receiver only for another checkout.",
            help_text,
        )
        self.assertIn("repository's documentation and release notes", help_text)
        self.assertNotIn("GETTING-STARTED.md", help_text)
        self.assertIn("Local commands:", help_text)
        self.assertIn("Workflow/CI-only commands:", help_text)
        self.assertIn("init", help_text)
        self.assertIn("verify", help_text)
        self.assertIn("start", help_text)
        self.assertIn("close", help_text)
        self.assertIn("publish-open-pr-body", help_text)
        self.assertIn("finalize-merged", help_text)
        self.assertNotIn("\n  closeout", help_text)
        self.assertNotIn("\n  evidence", help_text)
        self.assertNotIn("\n  verification", help_text)
        self.assertNotIn("acceptance", help_text)
        self.assertNotIn("work-item", help_text)

    def test_top_level_help_puts_first_use_orientation_before_commands(self):
        help_text = build_parser().format_help()

        self.assertLess(
            help_text.index("First use with the installed sdf command:"),
            help_text.index("Local commands:"),
        )
        self.assertLess(
            help_text.index("sdf init"),
            help_text.index("sdf verify"),
        )
        self.assertLess(
            help_text.index("sdf verify"),
            help_text.index("sdf close --change-id <change-id>"),
        )

    def test_help_mentions_verify_command(self):
        help_text = build_parser().format_help()

        self.assertIn("SDF CLI for governed AI-assisted delivery", help_text)
        self.assertIn("status", help_text)
        self.assertIn("guidance", help_text)
        self.assertIn("init", help_text)
        self.assertIn("verify", help_text)
        self.assertIn("start", help_text)
        self.assertNotIn("\n  evidence", help_text)
        self.assertNotIn("\n  verification", help_text)
        self.assertIn("close", help_text)
        self.assertIn("publish-open-pr-body", help_text)
        self.assertIn("finalize-merged", help_text)
        self.assertNotIn("\n  closeout", help_text)
        self.assertNotIn("\n  install ", help_text)
        self.assertNotIn("acceptance", help_text)
        self.assertNotIn("work-item", help_text)

    def test_top_level_help_lists_close_after_start(self):
        help_text = build_parser().format_help()

        self.assertIn("Local commands:", help_text)
        self.assertLess(help_text.index("init"), help_text.index("status"))
        self.assertLess(help_text.index("status"), help_text.index("guidance"))
        self.assertLess(help_text.index("guidance"), help_text.index("verify"))
        self.assertLess(help_text.index("verify"), help_text.index("start"))
        self.assertLess(help_text.index("start"), help_text.index("close"))
        self.assertLess(
            help_text.index("close"), help_text.index("publish-open-pr-body")
        )
        self.assertLess(
            help_text.index("publish-open-pr-body"),
            help_text.index("finalize-merged"),
        )
        self.assertNotIn("install manifest", help_text)

    def test_top_level_help_separates_long_command_names_from_descriptions(self):
        help_text = build_parser().format_help()

        self.assertIn(
            "publish-open-pr-body  Workflow/internal: standardize", help_text
        )

    def test_start_help_names_archive_handoff_as_current_path(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as raised:
                main(["start", "--help"])

        self.assertEqual(raised.exception.code, 0)
        help_text = stdout.getvalue()
        self.assertIn("Start the durable .sdf/evidence", help_text)
        self.assertIn("archive path for governed changes", help_text)
        self.assertIn("sdf start --change-id <change-id>", help_text)
        self.assertIn("usage: sdf start", help_text)
        self.assertNotIn("{init,status,guidance,verify,start,close", help_text)
        self.assertIn("Defaults to the current directory.", help_text)
        self.assertIn("Optional declared model name", help_text)
        self.assertIn(
            "literal unknown when genuinely unknown",
            " ".join(help_text.split()),
        )
        self.assertNotIn("legacy compact acceptance", help_text)

    def test_removed_evidence_command_is_not_an_alias(self):
        with self.assertRaises(SystemExit) as raised:
            main(["evidence"])

        self.assertEqual(raised.exception.code, 2)

    def test_verify_help_distinguishes_execution_from_check(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as raised:
                main(["verify", "--help"])

        self.assertEqual(raised.exception.code, 0)
        help_text = stdout.getvalue()
        self.assertIn("Execute configured receiver verification", help_text)
        self.assertIn("Use --check", help_text)
        self.assertIn("--check", help_text)
        self.assertIn("--focused NAME", help_text)
        self.assertIn("Local receiver repository path", help_text)
        self.assertIn("use --repo", help_text)
        self.assertIn("/path/to/receiver", help_text)

    def test_verify_help_describes_execution_and_focused_examples(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as raised:
                main(["verify", "--help"])

        self.assertEqual(raised.exception.code, 0)
        help_text = stdout.getvalue()
        self.assertIn("Execute configured receiver verification", help_text)
        self.assertIn("Examples:", help_text)
        self.assertIn("sdf verify", help_text)
        self.assertIn("sdf verify --focused <name>", help_text)
        self.assertIn("sdf verify --check", help_text)
        self.assertIn("list configured focused verification names", help_text)

    def test_local_command_help_uses_command_local_usage(self):
        for command in ("status", "guidance", "verify"):
            with self.subTest(command=command):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    with self.assertRaises(SystemExit) as raised:
                        main([command, "--help"])

                usage = stdout.getvalue().splitlines()[0]
                self.assertEqual(raised.exception.code, 0)
                self.assertTrue(usage.startswith(f"usage: sdf {command}"))
                self.assertNotIn("{init,status,guidance,verify", usage)

    def test_removed_verification_command_is_not_an_alias(self):
        with self.assertRaises(SystemExit) as raised:
            main(["verification"])

        self.assertEqual(raised.exception.code, 2)

    def test_retired_closeout_composition_paths_are_not_aliases(self):
        for path in (
            ["closeout", "check"],
            ["closeout", "handoff"],
            ["closeout", "pr-body", "write"],
            ["closeout", "pr-body", "check"],
            ["closeout", "pr-body", "finalize-merged"],
        ):
            with self.subTest(path=path), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    main(path)

            self.assertEqual(raised.exception.code, 2)

    def test_version_option_still_reports_package_version(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as raised:
                build_parser().parse_args(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("software-dark-factory 0.1.0", stdout.getvalue())

    def test_identity_option_reports_executing_implementation(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["--identity"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), render_identity() + "\n")


if __name__ == "__main__":
    unittest.main()
