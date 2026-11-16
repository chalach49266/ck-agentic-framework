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

## Mac build

Done: read worker brief, repo-work playbook, full task, Mac contract, both inventories, workspace rules and live Mac host/settings sources. No required guide is missing.

Plan: preserve the shared runner; route the Mac AppleScript protocol through a Mac adapter based on the live Herdr module. Render Mac config at install time. Keep Windows adapters unchanged.

Done: Mac installer and native iTerm/Herdr adapter, portable Mac preferences and detailed setup/phone/troubleshooting docs. Dry-run, temp-home install and identical repeat, installed CLI, backups, hooks, symlink refusal and Mac fixture checks passed. Publishable-tree privacy scan has only permitted code/public-range hits. Required read-only inventories and ignored logs still match the literal whole-folder grep; retain and disclose them.

Done: final shared suite and Mac host suite pass. Initial shared-suite environment failures were fixed before the final passing rerun. Evidence and remaining UNVERIFIED items are recorded in verification/build/RESULTS.md.

Finalization: local commit on mac-part, then result.md and summary.md last in the assigned outbox. No implementation or test work remains. Commit completion and the privacy-scope question are recorded in the outbox.

Scope: repository only, plus the named result and summary outbox files. Live install stays read only. No push, PR, network setup, live agent race, or phone action.

## Mac review fixes

Done: worker guide, bug-fix playbook, review, original task, wiki routing and workspace rules read. Required guides present.
Remaining: reproduce lost edits in a temporary home; replace owner-name comments; preserve existing Herdr files and timestamp other replacements; document Herdr installation and Remote Login; rerun requested checks; commit locally; write outbox result then summary.
Scope: Mac installer, requested documentation, regression test and this progress entry. Protected paths stay untouched. No push or live install.

Done: old installer reproduced loss of a later edit; regression failed before the fix and passes after it. Owner-name comments replaced. Existing Herdr files now print `kept yours` and stay untouched; other changed files get timestamped, collision-safe backups. Herdr vendor install options and Remote Login requirement documented.
Done: isolated install/repeat, installed CLI, empty/existing-home dry runs, installer regression and Mac host tests pass. Logs: verification/fix1/. Protected paths unchanged.
Remaining: full shared suite is running; then final committed-tree privacy check, local commit and required outbox completion files.

Done: full shared suite passes; see verification/fix1/offline-suite.log. Mac host and installer regression suites, old-code failure reproduction, temp-home install/repeat/CLI/dry runs and protected-path checks all pass.
Done: full staged-tree privacy scan uses the correct complete owner-name pattern and only permits the public CIDR. The privacy recipe uses equivalent bracketed token prefixes so it does not flag itself.
Remaining: no implementation or test work. Finalization records the new local mac-part commit, final HEAD privacy proof and clean status in verification/fix1/RESULTS.md, then writes the assigned outbox result.md followed by summary.md. No push.
