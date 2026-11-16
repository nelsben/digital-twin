---
id: OPS-25
title: The kit's tests enforce the limits its docs state, a preflight script rejects unreplaced placeholders, and eval files are checked
domain: ops
tier: standard
tier_reason: Small script, tests and doc edits with every decision in the card
status: merged
issue: 168
scope: [tests/test_kit_structure.py, tests/test_preflight.py, starter-kit/settings/preflight.py, .claude-plugin/marketplace.json, starter-kit/plugins/twin-shared/.claude-plugin/plugin.json, starter-kit/docs/authoring-skills.md, starter-kit/templates/skill/README.md, starter-kit/templates/skill/your-skill-name/evals/**]
forbid: [starter-kit/settings/README.md, starter-kit/settings/*.json, starter-kit/README.md, starter-kit/runbooks/**, starter-kit/plugins/twin-pe-deal-team/**, starter-kit/plugins/twin-shared/skills/**, engagements/**, docs/**, partner-kit/**]
red_test: python3 -m unittest tests.test_preflight tests.test_kit_structure
gate: test
budget: 2-attempts
spend: 10
---
## Why

The 2026-11-15 adversarial review found that the starter kit's docs promise limits the tests do not enforce, that a settings file with placeholders still in it can be deployed with nothing to stop it, and that the marketplace advertises a skill that does not exist. The generated backlog will send consultants to these parts.

## Done when

- Read the findings first: /Users/bennelsen/Documents/digital-twin/.delegation/reviews/2026-11-15/starter-kit/findings.md section 2, findings 2, 3, 5, 9 and 10. Each names file and line. Findings 1, 4, 6, 7 and 8 belong to other cards: leave them, and do not edit starter-kit/settings/README.md or starter-kit/README.md.
- Finding 3: tests/test_kit_structure.py sets SKILL_DESCRIPTION_MAX_CHARS to 200 and SKILL_BODY_MAX_LINES to 150, and its own unit cases for those limits are adjusted to match. The three built skills still pass. The docs already state 200 and 150 and stay as they are.
- Finding 2: starter-kit/settings/preflight.py exists, Python 3.9+ standard library only. Run as 'python3 starter-kit/settings/preflight.py <file>...' it prints one line per value that still contains REPLACE-WITH-, giving the file and the JSON path of the value, and exits 1; it exits 0 with a one-line OK when none is left; it exits 2 with a message for a missing file or invalid JSON. The four shipped baselines keep their placeholders (they are templates) and tests/test_settings.py keeps asserting that.
- tests/test_preflight.py covers: each shipped baseline fails with every one of its placeholders listed; a temporary copy with every placeholder replaced passes; a missing file and an invalid JSON file exit 2; a placeholder nested inside a list or object is found.
- Finding 5: starter-kit/docs/authoring-skills.md says that skill-creator and Anthropic's own plugins are installed on the consultant's own unmanaged machine, because each settings baseline's strictKnownMarketplaces allows only the kit marketplace on managed devices, and that anything the customer needs from them is copied into the kit marketplace after review. starter-kit/templates/skill/README.md says the same in one sentence where it mentions skill-creator, or links to that section.
- Finding 9: the twin-shared description in .claude-plugin/marketplace.json and in starter-kit/plugins/twin-shared/.claude-plugin/plugin.json names only what exists (house style), with no account research.
- Finding 10: a test in tests/test_kit_structure.py checks, for every skill under starter-kit/plugins and for the skill template, that evals/evals.json and evals/trigger-evals.json exist and parse, that skill_name where present equals the skill folder name, and that every path listed under a files key exists. If the template uses placeholder values that cannot meet a check, the test names that exception in a comment. Report any eval file the new test showed to be broken and fix it only if it sits in scope.
- python3 -m unittest discover -s tests passes. The report lists, per finding, the file and line changed.

## Review

Brain read the full diff at c454e52. Findings 2, 3, 5, 9 and 10 of the starter-kit lane are met as the card states. One nit left: the docs say descriptions are "under 200 characters" and the test accepts exactly 200. The settings README does not call preflight.py yet; that line belongs to the Team deploy path card (#166).
