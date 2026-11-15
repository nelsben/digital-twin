---
id: OPS-2
title: tests/test_kit_structure.py validates every plugin, skill and marketplace entry in the starter kit
domain: ops
tier: standard
tier_reason: straightforward stdlib tests with stated limits
status: merged
issue: 15
parent: 13
scope: [tests/test_kit_structure.py]
forbid: [.claude-plugin/marketplace.json, starter-kit/plugins/**]
red_test: none (test-only)
gate: test
budget: 2-attempts
spend: 10
---
## Why

Skills and plugins are written by many hands across engagements, and a broken frontmatter or manifest silently stops a skill from triggering on some Claude surfaces. A structure test in the repo gate catches that before any merge, and later skill stories rely on it.

## Done when

- tests/test_kit_structure.py uses only the Python standard library (unittest, json, pathlib, re); no PyYAML. Frontmatter is parsed with a small helper that reads the block between the first two '---' lines as simple 'key: value' pairs (folded or quoted values on one line are enough)
- Test: .claude-plugin/marketplace.json parses, has name, owner and a non-empty plugins list; every plugin entry's source path exists and contains .claude-plugin/plugin.json
- Test: every plugin.json parses, has name equal to its folder name, a semver version and a description
- Test: every plugin folder under starter-kit/plugins is listed in the marketplace (no orphan plugins)
- Test: every SKILL.md under starter-kit/** (zero is allowed today) has frontmatter with name and description; name is lowercase letters, digits and hyphens, at most 64 characters, matches its folder name, and does not contain 'anthropic' or 'claude'; description is non-empty and at most 1024 characters
- Test: SKILL.md frontmatter uses only the cross-surface keys name and description, unless the skill folder holds a file named CLAUDE_CODE_ONLY (then any keys are allowed); this enforces the portability rule in docs/compendium/03-skills-authoring.md
- Test: SKILL.md bodies are under 500 lines
- Each limit is a named constant at the top of the file with a comment linking the Anthropic doc it comes from (https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview and https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices; use the URL that currently loads if those redirect)
- The tests are written so that they pass on main once the marketplace and plugin skeletons from card OPS-1 are merged, and fail with a clear message if marketplace.json is missing
- python3 -m unittest discover -s tests passes

## Review

Brain review: 15 stdlib tests pass; red run shown on a copy without marketplace.json. Accepted: cross-surface keys limited to name+description, a strict subset of what claude.ai accepts (license, compatibility, metadata, allowed-tools), so any passing skill uploads everywhere. Widen later if a skill needs license.
