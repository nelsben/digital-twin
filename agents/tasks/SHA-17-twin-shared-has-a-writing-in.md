---
id: SHA-17
title: twin-shared has a writing-in-house-style skill, written evals-first and graded by an independent grader against a no-skill baseline
domain: shared
tier: standard
tier_reason: one small skill from an existing template, with an eval run
status: merged
issue: 36
parent: 35
fixes: []
scope: [starter-kit/plugins/twin-shared/**]
forbid: []
red_test: test -f starter-kit/plugins/twin-shared/skills/writing-in-house-style/SKILL.md
gate: test
budget: 2-attempts
spend: 10
---
## Why

The shared plugin that every role twin installs is still an empty skeleton, and a common voice was one of the first things the user asked for. A house-style skill gives every twin the same writing rules, in one file a customer can replace with its own.

## Done when

- The worker follows starter-kit/docs/authoring-skills.md and copies starter-kit/templates/skill as the starting folder. It reads docs/compendium/03-skills-authoring.md first
- Evals come first: skills/writing-in-house-style/evals/evals.json (at least 6 cases, each with checkable expectations) and evals/trigger-evals.json (at least 8 should-trigger and at least 8 should-not-trigger queries) are committed in a commit before the commit that adds SKILL.md
- The should-not-trigger set includes near misses that belong to the deal-team skills: 'company brief for', 'one-pager on', 'brief me on', 'update the CRM', 'log my meeting', and plain questions that need no writing
- The skill is for writing or editing prose for internal readers when no role skill covers the task: emails, notes, summaries, memos, rewrites ('tidy this up', 'rewrite this', 'draft a note to'). It says it does not replace a role skill's own output format
- The rules live in skills/writing-in-house-style/references/house-style.md so a customer can replace that one file; SKILL.md holds the method (read the rules, draft, check the draft against the rules, say what was changed when editing someone's text). The default rules cover these categories, each with its reason: lead with the answer or the ask; plain words and short sentences, no hype or filler; numbers with unit, currency and period; dates in ISO 8601; every fact taken from a system or document names its source, and unaudited, management-provided or inferred figures are labelled as such; people by full name on first mention; deal code names used exactly as given and never expanded or guessed; headings and tables only when they help; no emoji. The worker chooses the wording and lists its choices in the report
- The top of references/house-style.md says these are the kit's defaults and tells the customer's skill owner how to replace them
- Frontmatter has only name (writing-in-house-style, matching the folder) and description; the description is in the third person, under 200 characters, and names trigger phrases. The body is within the limits tests/test_kit_structure.py enforces
- The skill, its references and its eval fixtures contain no customer or deal data and no real company or person. Invented names only; reuse the kit's existing invented names (Larch, Birch, Cedar) where a name is needed
- The evals are run after the skill is written, using the method recorded in starter-kit/plugins/twin-pe-deal-team/skills/preparing-company-briefs/evals/README.md (read it for the method only): each case once with the skill and once without, each in its own subagent on sonnet, and each answer graded per expectation by a separate grader subagent that is not told which arm it is. The worker does not grade its own skill. Trigger queries are checked by showing a fresh subagent the names and descriptions of all three kit skills and counting hits and false triggers
- skills/writing-in-house-style/evals/README.md records the results (with-skill and baseline pass counts, trigger hit and false-trigger rates, date, model) and the limits of the run, in the same shape as the deal-team eval READMEs. If the worker cannot spawn subagents, it records 'not run' with the reason and does not grade the skill itself
- If the with-skill arm does not beat the baseline on any case, the README says so plainly
- starter-kit/plugins/twin-shared/README.md is updated: status line, a Skills table with this skill and issue #36, and the placeholder wording removed. plugin.json version becomes 0.2.0. skills/.gitkeep is deleted
- The gate passes: python3 -m unittest discover -s tests

## Review

Sonnet, attempt 1, verifier consistent. The brain read the top of SKILL.md: the description is short, it defers to role skills and to layouts the user supplies, and it asks for any missing input. All names in the fixtures are invented. The redact grep found nothing. Evals were written before the skill. With the skill 50 of 56 expectations passed; without it, 39 of 56. Trigger evals: 10 of 10 hits, 0 of 12 false triggers. Known flaw, left as it was run: case 7 expectation 3 expects the surnames Placeholder and Sample, but the handover note has only "Lena" and "Ana". The expectation is wrong, and should be reworded in a follow-up.
