---
id: OPS-15
title: The sample engagement and the wall-test README no longer call existing files "coming" or a fixed deploy failure open
domain: ops
tier: economy
tier_reason: mechanical doc edits at named lines
status: merged
fixes: []
scope: [engagements/sample-pe/design.md, engagements/sample-pe/backlog.md, starter-kit/connectors/salesforce/wall-test/README.md]
forbid: []
red_test: none
gate: test
budget: 2-attempts
spend: 3
---
## Why

Under epic #23, only illustrative customer actions (#57, #58) and blocked Scale items (#59, #60) are left, and none of them is worker work. What remains is stale text. design.md still calls backlog.md and wall-test-protocol.md "coming", the backlog's #30 row doesn't link the protocol or give its status, and the wall-test README reports a marker deploy failure that #94 has since fixed.

## Done when

- engagements/sample-pe/design.md line 7: the text "(`backlog.md`, coming)" becomes a markdown link to backlog.md with no "coming"; the rest of the sentence is unchanged.
- engagements/sample-pe/design.md around line 214: "produces `wall-test-protocol.md` (coming)" becomes "produces [wall-test-protocol.md](wall-test-protocol.md)"; the outline that follows it is not changed.
- Any other occurrence of the word "coming" in engagements/sample-pe/*.md that refers to a file that now exists in that folder is fixed the same way (link, no "coming"); occurrences that refer to things that do not exist yet are left alone. The worker lists every occurrence it found and what it did with each.
- engagements/sample-pe/backlog.md, row #30: `wall-test-protocol.md` becomes a link to wall-test-protocol.md, and the row adds this status in one short sentence: the protocol is written, a scratch-org dry run passed the API-level cases (#82), and the live run needs the customer's org. The row still says it must pass before any pilot user connects.
- starter-kit/connectors/salesforce/wall-test/README.md: directly after the bullet about the Twin_Marker_Edit description being too long, a single new line says that the description was shortened to 255 characters after this run (#93, PR #94) and that the marker has not been re-deployed to a scratch org since. The dated results above it are not edited.
- No other lines in these files change; no file outside the scope changes.
- python3 -m unittest discover -s tests passes.

## Review

Attempt 1/2 consistent, next=accept. Checked by hand: 4 files, 6 insertions, 5 deletions, all at the named lines. Every link target exists. The scope amend for discovery.md is justified: the card's own Done-when covered every "coming" in engagements/sample-pe/*.md, but its scope left that file out, which was the brain's mistake. Both discovery.md edits turn "(coming, #26)" into a link to stakeholders.md and nothing more.
