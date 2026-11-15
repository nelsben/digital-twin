---
id: SHA-6
title: starter-kit/README.md is the front door to the kit: what it is, how a consultant uses it with Claude on an engagement, and links to Anthropic's docs
domain: shared
tier: standard
tier_reason: docs index from existing pages
effort: low
effort_reason: docs-only; every fact is already in the repo
status: merged
issue: 22
parent: 10
scope: [starter-kit/README.md, README.md]
forbid: []
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

The kit now has a marketplace, three plugins, skill and persona templates, settings baselines, a governance hook, tests and a sample engagement, but no entry point. A new consultant (and Claude itself, when pointed at the repo) needs one page that says what each part is, the order to use them in, and where Anthropic's guidance lives.

## Done when

- Before writing, the worker reads the root README.md, every README under starter-kit/, starter-kit/docs/authoring-skills.md, .claude-plugin/marketplace.json, docs/playbook/README.md and 01-engagement-model.md, docs/compendium/README.md and 16-oob-skills-and-references.md, and engagements/sample-pe/README.md. Every path it names exists on main
- starter-kit/README.md, under 150 lines, has these sections: What this is (two or three sentences); What's inside (a table of every part: marketplace, the three plugins, templates/skill, templates/persona, settings, docs/authoring-skills.md, the tests, engagements/sample-pe as the worked example, each with a one-line purpose and a link); Using it on an engagement (the playbook phases 1-6 mapped to which kit parts are used in each, linking docs/playbook/01-engagement-model.md); Start a new customer (a numbered list: copy engagements/sample-pe as the folder layout, fork or copy the marketplace into the customer's repo, fill the persona, copy the skill template per story, pick a settings baseline per org, deploy the governance plugin through the managed marketplace); Reuse before you build (the six decisions from compendium 16, linked); Working with Claude on this repo (how to install the marketplace locally with the exact commands from the plugin docs, run the tests, and use skill-creator; plus a note that Claude reads this README and the compendium first); Anthropic references (8-12 of the most-used links from compendium 16 section 4, each with a one-line purpose, and a pointer to the full list)
- Every Anthropic link is copied from compendium 16 section 4; no new URLs
- The root README.md gains one line linking starter-kit/README.md, and nothing else in it changes
- python3 -m unittest discover -s tests passes

## Review

Brain review: 97 lines, all seven sections, links copied from page 16, paths exist. Gap: 'Claude should read this README first' is advice only, because Claude Code loads CLAUDE.md, not README. Follow-up: add a root CLAUDE.md so Claude picks up the defaults and sources automatically.
