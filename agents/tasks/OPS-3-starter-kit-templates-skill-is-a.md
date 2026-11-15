---
id: OPS-3
title: starter-kit/templates/skill is a copyable skill template with evals, built from Anthropic's template-skill and skill-creator's eval format, plus an authoring guide
domain: ops
tier: standard
tier_reason: template plus guide; must match skill-creator's real eval format
status: merged
issue: 17
parent: 16
scope: [starter-kit/templates/skill/**, starter-kit/docs/authoring-skills.md]
forbid: []
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

Every twin skill in every engagement starts from this template, so it must encode our rules (evals before the skill, cross-surface frontmatter, progressive disclosure) and reuse Anthropic's own tooling rather than inventing a parallel format. Compendium page 16 decided: seed from anthropics/skills template-skill and evaluate with skill-creator.

## Done when

- Before writing, the worker reads docs/compendium/03-skills-authoring.md, docs/compendium/16-oob-skills-and-references.md, tests/test_kit_structure.py, the template at https://github.com/anthropics/skills/tree/main/template (or wherever page 16 says it lives), and skill-creator's SKILL.md and its eval file format at https://github.com/anthropics/skills/tree/main/skills/skill-creator. Where skill-creator defines an eval file (name, location, JSON shape), the template uses exactly that format, and the report says which file and fields it followed
- The template lives at starter-kit/templates/skill/your-skill-name/ so it passes the structure tests as-is: SKILL.md frontmatter has only name: your-skill-name and a description under 200 characters written as a fill-in pattern (what it does, then 'Use when ...')
- SKILL.md body is under 150 lines and has clearly marked fill-in sections: purpose, inputs and the connectors it reads (with data class), steps, output format, guardrails (twin marker on writes, no web tools for MNPI, ask instead of guessing on missing data), and links to reference files; it points to Anthropic's skill best-practices URL from page 16
- The folder has a references/ subfolder with one example reference file showing progressive disclosure, and an evals file in skill-creator's format with 3 placeholder cases (a normal case, a missing-data case, and a should-not-trigger case)
- starter-kit/templates/skill/README.md explains in under 60 lines how to copy the template into a plugin's skills/ folder, rename it (folder and name must match), and fill it in
- starter-kit/docs/authoring-skills.md is the authoring guide for consultants: the step order (collect 3 real examples from the skill owner, write evals, write the skill, run skill-creator's eval and description-tuning loop, test on the models the customer uses, run python3 -m unittest discover -s tests, get a reviewer who is not the author), how a story's acceptance criteria in docs/playbook/04-stories.md map to eval cases, when to use the CLAUDE_CODE_ONLY marker, and the install command for skill-creator from page 16. Every Anthropic claim links a URL from page 16 section 4
- python3 -m unittest discover -s tests passes, and the worker's report confirms the template's SKILL.md was picked up by the skill tests (not skipped)

## Review

Brain review: template passes the structure tests as a real skill; evals follow skill-creator's references/schemas.md (evals/evals.json with expectations) plus a trigger-evals.json for description tuning. Noted skill-creator's own assertions/expectations wording drift; the guide says follow the installed version.
