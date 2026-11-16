# twin-shared

The common plugin every role twin installs, holding skills that are not role-specific.

Status: in progress (version 0.3.0). One skill is written (`writing-in-house-style`). The account-research skill, hooks and output styles are not written yet.

The private-equity rules that were here (code names, no web lookups for sensitive material) moved to [twin-pe-deal-team](../twin-pe-deal-team/README.md) in 0.3.0. This plugin holds only rules every role can use.

## Skills

| Skill | Issue | What it does |
|---|---|---|
| [writing-in-house-style](skills/writing-in-house-style/SKILL.md) | #36 | Writes or edits internal prose (emails, notes, summaries, memos, rewrites) to one set of rules: answer first, plain words, figures with unit, currency and period, ISO dates, sources named. It does not replace a role skill's own output format. The rules are in one file, `references/house-style.md`, which a customer replaces with its own. |

## Compendium pages

- [01-anatomy.md](../../../docs/compendium/01-anatomy.md)
- [03-skills-authoring.md](../../../docs/compendium/03-skills-authoring.md)

## Filled in by

#36
