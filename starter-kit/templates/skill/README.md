# Skill template

The starting point for every twin skill. It is built from Anthropic's
[template skill](https://github.com/anthropics/skills/tree/main/template)
(frontmatter with `name` and `description` only, so it works on every
surface) and adds our rules: evals first, guardrails every twin skill needs,
and reference files that load only when needed.

```
your-skill-name/
  SKILL.md                    the skill: frontmatter plus a body under 150 lines
  references/
    example-reference.md      example of a file that loads only when linked
  evals/
    evals.json                3 placeholder cases, in skill-creator's format
    trigger-evals.json        should-trigger and should-not-trigger queries
```

## Copy it

From the repo root, copy into the plugin that will own the skill (for
example `twin-shared`), and use the skill's real name as the folder name:

```
cp -R starter-kit/templates/skill/your-skill-name \
  starter-kit/plugins/<plugin>/skills/<new-skill-name>
```

## Rename it

The folder name and the `name:` line in `SKILL.md` must match, or the
structure test fails. Use lowercase letters, digits and hyphens, at most 64
characters, and no "anthropic" or "claude". In `evals/evals.json`, set
`skill_name` to the same value.

## Fill it in

1. Write the evals first. Replace the `FILL IN` text in `evals/` with cases
   from 3 real examples the skill owner gave you.
2. Replace every `FILL IN` marker in `SKILL.md`, then delete the markers and
   the comment at the top.
3. Keep the three guardrails (twin marker on writes, no web tools for highly
   sensitive data, ask instead of guessing) unless the skill truly does not
   need one.
4. Keep the description under 200 characters: what it does, then
   "Use when ...".
5. Move anything long into `references/` and link it from `SKILL.md`. Delete
   the example reference if you do not need it.
6. Do not add frontmatter keys beyond `name` and `description`. If the
   skill needs Claude Code-only keys, see "CLAUDE_CODE_ONLY" in the guide.
7. Run `python3 -m unittest discover -s tests`.

The full step order, including how to run skill-creator's evals, is in
[../../docs/authoring-skills.md](../../docs/authoring-skills.md).
