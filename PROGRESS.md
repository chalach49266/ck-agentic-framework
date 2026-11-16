# PC import progress

Done: required guides and caveats read; sanitized imports created; Windows installer rewired to core/ and setup/common/; bundled skills copy replaces remote clone; Herdr look and keyboard bindings included with original-backup logic; Claude settings deep merge included; smoke script includes explicit live race mode. Isolated install, repeat, installed CLI, settings merge and smoke-argument checks pass. Logs are under verification/ and ignored by git.

Done: full offline suite passes (verification/offline-suite-final.log); source completeness and Git-HEAD provenance pass (verification/source-check.log); requested and extended privacy scans pass across staged files including hidden files and archives (verification/privacy-grep.log). The optional whitespace check retains only inherited blank endings and Markdown hard-break spaces. Repository content is ready for the requested local commit.

Remaining: no implementation work. The final action of this run commits this tree locally and writes the required outbox result.md followed by summary.md. Those completion details are recorded in the outbox and ignored verification logs.

The root documentation, docs/, setup/mac/ and platform/mac/ remain placeholders reserved for the next workers. Source repositories are unchanged. Native Windows batch execution, plugin downloads and real agent launches are UNVERIFIED; this Linux environment has no cmd.exe. No remote is configured.

# Step 2 progress (docs + Mac draft, ask A-1115-21)

Done: facts read (setup/windows, setup/common, v4.md, platform READMEs, GROKBOT.md, ck-mode, verification logs, archive Mac line).
Remaining: write README.md, AGENT_SETUP.md, docs/*.md, setup/mac/README.md, core/ck-dispatch/platform/mac/README.md;
path + command check; privacy grep; one local commit. Update this list as each file lands.
Done (step 2): README.md, AGENT_SETUP.md, docs/ARCHITECTURE.md, docs/HOW_TO_USE.md, docs/PHONE.md, docs/TROUBLESHOOTING.md.
Remaining (step 2): docs/MAC_HANDOFF.md, docs/HISTORY.md, docs/README.md, setup/mac/README.md, platform/mac/README.md, checks, commit.
Done (step 2): docs/MAC_HANDOFF.md, docs/HISTORY.md, docs/README.md, setup/mac/README.md, core/ck-dispatch/platform/mac/README.md.
Done (step 2): path check (missing only Mac-owned setup/mac/setup.sh and docs/CHANGES_FROM_MAC.md), ck-run flag check, privacy grep clean (allowed hit: the public Tailscale range in docs/PHONE.md).
Remaining (step 2): nothing after the local commit. Next plan steps: 3 review, 5 push (CK), Mac part (docs/MAC_HANDOFF.md).

# Review fix progress (ask A-1115-21)

Done: required guides and review read; Windows prompts and explicit path forwarding, noninteractive stop, missing-project warning, exact archive symlink, machine placeholder and setup docs fixed.
Done: real PTY and noninteractive dry runs, isolated HOME install and unchanged repeat, missing/restored project checks with an offline plugin recorder, archive symlink check and privacy grep pass. Evidence: verification/A-1115-21-fix-checks.log and verification/A-1115-21-fix-privacy.log.
Done: full offline suite passes (verification/A-1115-21-fix-offline-suite.log); Python, JSON, shell syntax and final diff checks pass (verification/A-1115-21-fix-static.log).
Remaining: no implementation or verification work. Finalization is the requested local commit and outbox reports; completion evidence is in verification/A-1115-21-fix-commit.log and the run outbox. Native Windows execution remains UNVERIFIED; no cmd.exe is available. No remote was added; nothing was pushed.
