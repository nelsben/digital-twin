---
id: OPS-48
title: The persona template's steps put the output in the customer's delivery repo, and its web rule's reason is a FILL IN
domain: ops
tier: standard
tier_reason: two short doc edits and one small text test, every decision made in the card
status: merged
issue: 197
parent: 158
fixes: []
scope: [starter-kit/templates/persona/README.md, starter-kit/templates/persona/persona.md, tests/test_persona_template.py]
forbid: [starter-kit/plugins/**, starter-kit/README.md, partner-kit/**, engagements/**, docs/**, CLAUDE.md, agents/**, tests/test_persona.py, tests/test_role_plugin_template.py]
red_test: python3 -m unittest tests.test_persona_template
gate: test
budget: 2-attempts
spend: 10
---
## Why

The consultant-walk lane of the second adversarial review (OPS-44, findings 9 and 14) followed the persona template for an invented insurance customer. Step 3 of the template README sent the customer's output style into this repo's starter-kit/plugins folder and step 6 told the consultant to run this repo's tests; the template's web rule gave every customer a private-equity reason ("a query can reveal deal intent").

## Done when

- starter-kit/templates/persona/README.md keeps its headings '## Which form goes where', '## Fill it in' and '## The rule' with exactly those words (the partner kit's backlog links to #which-form-goes-where, #fill-it-in and #the-rule).
- In 'Fill it in', step 1 tells the reader to copy the folder into the role plugin in the customer's delivery repo as that plugin's persona/ folder (the layout starter-kit/plugins/twin-pe-deal-team uses: persona/persona.md, persona/system-prompt.md, and the output style in the plugin's output-styles/ folder). The first mention of 'the customer's delivery repo' links to ../../README.md#start-a-new-customer (step 2 there is where that repo gets its copy of the plugins) instead of describing the repo again.
- Step 3 says to put the finished output style in that role plugin's output-styles/ folder in the customer's delivery repo. The string 'starter-kit/plugins/<role-plugin>' no longer appears in the file as a destination.
- Step 6 no longer tells the reader to run 'python3 -m unittest discover -s tests'. It says: check that both forms match persona.md section by section; this kit's tests/test_persona.py makes that check for the plugins kept in this repo, and can be copied into the delivery repo to run there. One or two sentences, no new section.
- The 'Which form goes where' table and 'The rule' section are unchanged in meaning. Nothing else in the README is rewritten.
- In starter-kit/templates/persona/persona.md section 10, the web rule sentence keeps the rule ('Do not use web search or web fetch on highly sensitive tasks') and its last sentence ('If a task needs outside facts, ask the user to supply them.'), and the reason becomes a FILL IN marker that asks for the reason in this customer's words and gives the private-equity reason as the example, in the form: because FILL IN: the reason for this customer (for a private-equity deal team: a query can reveal deal intent).
- starter-kit/plugins/twin-pe-deal-team/** is not changed: the PE plugin's own persona keeps its deal-intent reason.
- A new test file tests/test_persona_template.py (standard library only, same style as tests/test_persona.py) checks: the three headings exist in the template README; the README does not contain 'starter-kit/plugins/<role-plugin>' or 'discover -s tests'; the README links to the starter-kit README's #start-a-new-customer anchor and that anchor's heading exists there; the persona.md line that holds 'Do not use web search or web fetch' also holds 'FILL IN'. It fails before the change and passes after.
- python3 -m unittest discover -s tests passes, and the hand-back gives the test count (main has 439 before this card unless another card merged first).
- The hand-back quotes the changed lines of both files before and after.

## Review

Brain read the whole diff (3 files, 61 added lines, 4 removed). Every done-when line is met: the three headings are unchanged, step 1 links the customer's delivery repo to the starter-kit README's "Start a new customer" section, step 3 names the role plugin's output-styles folder in that repo, step 6 no longer tells the reader to run this repo's suite, and the web rule's reason is a FILL IN with the private-equity reason as the example. No reviewer ran (verdict next=accept). The worker reported 448 tests where the card expected 443; the difference was not investigated beyond the gate passing.
