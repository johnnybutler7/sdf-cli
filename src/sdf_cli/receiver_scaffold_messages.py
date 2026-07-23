"""User-facing text for the receiver initialization command."""

READ_ONLY_BOUNDARY = (
    "This command is read-only.",
    "It reports every canonical manifest entry as missing, matching, or drifted.",
    "It does not create directories or files.",
    (
        "It does not overwrite, repair, migrate, install packages, run "
        "verification, mutate PRs, approve, merge, deploy, or release."
    ),
    (
        "It exits nonzero when a missing entry needs action or a drifted entry "
        "needs acknowledgement."
    ),
)

WRITE_BOUNDARY = (
    "This command creates missing starter receiver files by default.",
    "It creates missing parent directories only for missing starter files.",
    "It creates missing starter receiver files with manifest-approved content.",
    "It never overwrites existing files.",
    "It reports canonical manifest drift without repairing conflicting files.",
    "The shared .gitattributes entry retains its manifest-approved append-only rule.",
    "It does not inspect CI, tests, package scripts, language, or framework metadata.",
    (
        "It does not repair, migrate, install packages, run verification, mutate "
        "PRs, approve, merge, deploy, or release."
    ),
    "Pass --check for a fully read-only canonical-manifest inspection.",
)

VERIFICATION_HANDOFF = (
    "The scaffolded verification placeholder fails intentionally.",
    "Inspect the receiver's own test, lint, build, or verification commands.",
    "Replace the placeholder in .sdf/verification.yml with receiver-owned commands.",
    "Then run:",
    "  sdf verify --repo <receiver>",
)

PRODUCT_DIRECTION_HANDOFF = (
    "Receiver product direction is customer-owned.",
    "Declare it in receiver-owned docs or configured receiver playbooks when ready.",
)
