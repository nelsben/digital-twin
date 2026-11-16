---
id: OPS-23
title: The compendium no longer contradicts itself on ZDR, skills, feedback retention, analytics and autonomy, and every settled fact has a source or the Unverified marker
domain: ops
tier: frontier
tier_reason: Source-checked corrections across ten pages; levelling rules cite these facts, so an error spreads
status: merged
issue: 162
scope: [docs/compendium/**]
forbid: [starter-kit/**, engagements/**, partner-kit/**, docs/playbook/**]
red_test: none
gate: test
budget: 2-attempts
spend: 25
---
## Why

The 2026-11-15 adversarial review found one blocker and seven other faults in docs/compendium, plus two gaps for Team-plan customers. The levelling rules of the persona-card workflow cite these pages, so a wrong or unsourced fact here becomes a wrong build plan for a customer. This card covers issues #162 and #163.

## Done when

- Read the findings first: /Users/bennelsen/Documents/digital-twin/.delegation/reviews/2026-11-15/compendium/findings.md section 2 (F1 to F8), and /Users/bennelsen/Documents/digital-twin/.delegation/reviews/2026-11-15/end-to-end/findings.md findings 1 and 3. Each names page and line. Follow docs/compendium/README.md for the Sources line format and the exact Unverified and Conflict markers. Every fact you add or change carries a source link you fetched in this task, or the Unverified marker. Never state an unconfirmed fact as settled.
- F1 (blocker): pages 05 (lines near 30 and 49), 10 (near 105), 13 (near 54) and 14 (near 71) say the Agent SDK's coverage under ZDR and HIPAA is unverified, in the wording of page 10 line 80. For PHI the decision flow and the data-class matrix give no hosted route until Anthropic confirms one in writing. No line in the compendium presents the Agent SDK as a settled ZDR or HIPAA route.
- F2: README line 46 and page 04 line 74 say which skill routes are outside ZDR and HIPAA cover (skills run through the API and Managed Agents) and say that local skills in Claude Code on a ZDR sign-in are 'available but not covered' as page 10 line 76 has it, marked Unverified where no page confirms it. Page 12's ZDR org row keeps skill development and says the same thing in one clause.
- F3: no page says /feedback transcripts are kept 5 years under ZDR (pages 10 near 50, 15 near 61, 08 decision D10). Page 10 keeps the 5-year figure only for orgs without ZDR, with the code.claude.com data-usage page as source if a fetch confirms it, otherwise marked Unverified. Feedback being off under ZDR is stated once with the ZDR page as source.
- F4: README line 47 and page 08 line 12 say the usage Analytics API is Enterprise-only and a usage dashboard exists on Team, matching page 09. Decision D6 on page 08 lists what a Team customer can measure.
- F5: page 16 line 82 matches page 04 line 13 (claude.ai and a signed-in Claude Code share skills; the API is separate), carries the Conflict marker, and the starter-kit takes on page 16 that relied on the old rule are corrected.
- F6: page 06 says autonomy is enforced per connector tool. A task's level is the strictest setting any of its tools needs, and two tasks that share a tool share that tool's setting in chat and Cowork. If the Claude Code docs confirm that a skill's allowed-tools or a PreToolUse hook can narrow tools per skill, say so with the source link; if you cannot confirm it, say it with the Unverified marker. Line 3 no longer promises 'per task, not per twin' without that mechanism. Pages 01 and 09 agree with page 06.
- F7: each block the finding lists (page 04 lines 72-75, page 09 lines 75-95, all of page 12, page 08 line 51, page 13 lines 47-54) has a Sources line whose links you fetched and that support the text, or the Unverified marker on each unsupported statement. Page 08 line 51 is sourced or struck. docs/compendium/sources.md lists every new source.
- F8: the identity row on page 05 line 9 covers group DMs that include Claude (service account) and a user's own claude.ai connectors used in a channel after the user allows it, with the agent-identity source.
- End-to-end finding 1 (blocker): pages 13 and 15 each have a short section for a Team-plan customer with no device management. It says what such a twin gets on claude.ai web (org-level connector permissions, org-provisioned skills, a usage dashboard) and what it does not get (managed settings, hooks, the governance log, an audit log), and states plainly that such a twin cannot meet a requirement to log every action. Each statement is sourced or marked Unverified.
- End-to-end finding 3: page 12 has a Team-plan variant for a non-regulated role such as customer success (one Team org, no ZDR org), and no longer conflicts with page 09's 'Design twins to work on Team'.
- Page 14 near line 72 gives the surface for highly sensitive deal work as Claude Code on a ZDR sign-in on a managed device, with no Desktop.
- Do not rewrite pages beyond what these items need, and do not copy content between pages: link instead. python3 -m unittest discover -s tests passes. The report lists, per finding, the page and line changed, each URL fetched with what it confirmed, and every statement left Unverified.

## Review

Three attempts, three reviews. Attempt 1 (f693b69): 15 confirmed, 1 refuted (line citations in the hand-back only), 4 unverifiable (quotes from fetched Anthropic pages that the tree cannot check). Attempt 2 (76fc221) reworded "no hosted route" for PHI to "no hosted agent runtime" at the brain's instruction, so pages 05 and 10 no longer read as contradicting page 10's API route; its review refuted one clause as an unlabelled inference. Attempt 3 (f50f134) labels that clause "(our reading of the eligible and blocked lists)": 8 confirmed, 0 refuted, 2 unverifiable. The third attempt went past the budget of two by the brain's choice, to avoid merging an unlabelled claim. Brain read the new sections on pages 05, 06, 10, 12, 13 and 15. Left open: "(Our reading ...)" is used as a label on pages 05, 06, 10 and the README but the README's conventions define only Conflict, Unverified and "(Our recommendation)"; the second adversarial review (#159) decides whether to define it. The quotes from code.claude.com on pages 06, 09, 10 and 16 were fetched by the worker and are not re-checked by any reviewer.
