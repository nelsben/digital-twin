---
id: OPS-66
title: A runbook gets Claude Code installed, signed in and checked for a role that does not use it yet
domain: ops
tier: standard
tier_reason: One new runbook from Claude Code's own docs, the same kind of work OPS-50 did on sonnet
status: merged
issue: 231
parent: 228
fixes: []
scope: [starter-kit/runbooks/claude-code-for-a-role.md, starter-kit/README.md, tests/test_runbook_claude_code_for_a_role.py]
forbid: [docs/**, partner-kit/**, engagements/**, starter-kit/runbooks/verification-log.md, starter-kit/runbooks/identity-devices-publishing.md, starter-kit/runbooks/google-workspace-connectors.md, starter-kit/runbooks/microsoft-365-connector.md, CLAUDE.md]
red_test: python3 -m unittest tests.test_runbook_claude_code_for_a_role
gate: test
budget: 3-attempts
spend: 10
---
## Why

When the plan puts a task in Claude Code for a role that does not work in it, the backlog's claude-code-not-in-role task says the kit has no runbook for giving users a Claude Code seat and installing it, and links the identity runbook's role-mapping section. The identity runbook deploys managed settings but never installs Claude Code or checks a sign-in. Issue #231.

## Done when

- READ FIRST. starter-kit/runbooks/identity-devices-publishing.md whole (seats and roles in section 3, the managed-settings rollout in section 4, the device check in section 5, publishing the marketplace in section 6); starter-kit/runbooks/claude-code-scheduled-task.md (the house runbook shape for a runtime); docs/compendium/09-plans-and-it-controls.md and 13-devices.md as they bear on Claude Code seats and managed devices; docs/compendium/README.md (the marker conventions: **⚠ Conflict:**, **⚠ Unverified:**, **(Our recommendation):**, **(Our reading):**; the warning sign appears only inside those two bold labels). You do not change the compendium or the identity runbook; link them.
- SOURCES. Every claim comes from a page you download yourself: curl -sL -m 40 -A 'Mozilla/5.0 (compatible; doc-check)' <url>, saved under .delegation/<this card's id>/pages/ in your worktree, tags stripped with a python3 -I script, and the phrase you quote found in the text. Use code.claude.com/docs pages (add .md for markdown: setup or installation, authentication or sign-in for a Team or Enterprise account, settings and managed settings, plugins and marketplaces) and the Claude help-center articles on support.claude.com about Claude Code seats on Team and Enterprise. Where two sources disagree write **⚠ Conflict:** naming both and take the safer reading. Never confirm a claim from memory or from a summarising fetch. A claim no downloaded page states gets **⚠ Unverified:**.
- THE RUNBOOK. starter-kit/runbooks/claude-code-for-a-role.md has, in this order, the level-2 headings What this is, Read this first, Inputs you need, Before you start, Steps, Check it worked, Hand over, What can go wrong, and a 'Pages used' list that defines every source tag with an https URL; 80 to 220 lines. Its steps, each naming who does it (roles as in docs/playbook/03-stakeholders.md): give each person in the role a seat that includes Claude Code, as the pages say for Team and Enterprise (link identity runbook section 3 for the group-to-role mapping rather than copying it); install Claude Code on a managed device by the method the docs give for macOS and for Windows; sign in with the organization account and confirm in Claude Code that the session belongs to the organization; confirm the managed settings from identity runbook section 4 are in force on that device (link section 5's check, and name the in-product command or file the docs give, if any); add the kit's marketplace and install the role plugin (link identity runbook section 6); run one task from the role plugin as a first-run check. As **(Our recommendation):** do one person first, then the rest of the pilot group. It says in one line what changes when the role's devices are unmanaged, linking compendium page 13. In place of a 'Checked' sentence it says 'Written 2026-11-16 by the author from the pages listed; not yet checked by a second reader.' starter-kit/runbooks/verification-log.md is not changed.
- INDEX. In starter-kit/README.md add one row for the new runbook directly after the identity-devices-publishing.md row, in the same form. Do not change the task library: the brain wires the backlog's link in a later card.
- TEST FIRST. tests/test_runbook_claude_code_for_a_role.py is committed first, alone, failing. It checks the runbook exists; carries the eight headings in order and 'Pages used'; is 80 to 220 lines; names macOS and Windows; links identity-devices-publishing.md sections 3, 4 or 5, and 6 by anchors that exist in that file; links docs/compendium/13-devices.md; contains '(Our recommendation):'; carries the 'not yet checked by a second reader' sentence; defines every [X] source tag it uses with an https URL on code.claude.com, support.claude.com or claude.com; resolves every relative link and anchor; keeps every warning sign inside **⚠ Conflict:** or **⚠ Unverified:**; and that starter-kit/README.md links it. Standard library only.
- GATE AND EVIDENCE. Run tests only through the lease: node /Users/bennelsen/WorkflowBridge/bin/wb lease gate-mac --wait 1800 -- python3 -m unittest <args>, from your worktree. Save the red run's unittest output, and nothing else, to .delegation/<this card's id>/red-1.txt in your worktree. No note file in place of red evidence, no test run on a scratch copy outside the lease. The full gate python3 -m unittest discover -s tests passes. No rebase, no push, no PR.
- HAND-BACK. Each claim with the URL you downloaded and the exact phrase you found; each point marked unverified or conflict and why; anything in the compendium or the identity runbook the pages contradict (listed, not changed); and in the [[report]] line, files= lists every file changed on the branch since origin/main.

## Review

Standard tier, accepted directly. Brain read the 3-file diff and searched every quoted phrase and command in the new runbook against .delegation/OPS-66/pages/: all found. Unverified marks (/status rows for a subscription login, auth status naming the org, MDM install, Desktop reading managed settings) and the Conflict (help center recommends Desktop, setup.md the native install) are appropriate. Noted for a later card, not changed here: compendium 09 shows Claude Code "Y" on Enterprise without the help center's condition that older Enterprise plans need a seat type that includes it.
