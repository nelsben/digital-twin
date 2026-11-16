# twin-pe-deal-team

The role twin for a private equity deal team: its skills and its persona (output style).

Status: in progress (version 0.4.0). Two skills and the persona are written. The private-equity rules moved here from `twin-shared` in 0.4.0: never expand or guess a deal code name, and no web search or web fetch for material that may concern a deal. The persona and both skills state them.

## Skills

| Skill | Story | What it does |
|---|---|---|
| [preparing-company-briefs](skills/preparing-company-briefs/SKILL.md) | T1 (#32) | A one-page company brief from the Salesforce deal record and the SharePoint deal folder, with a source link on every fact, a list of what is missing, and no web tools. Draft only. |
| [drafting-crm-updates](skills/drafting-crm-updates/SKILL.md) | T2 (#34) | Draft activity-log and next-step text for the Salesforce opportunity from meeting notes or a Teams transcript. Draft only at level 1; at level 2 it writes after approval, with the twin marker ([references/level-2-writes.md](skills/drafting-crm-updates/references/level-2-writes.md)). |

## Persona

The deal-team persona is kept once and shipped in two forms, as the [persona template](../../templates/persona/README.md) describes (it also says which form goes on which surface):

| File | What it is | Surface |
|---|---|---|
| [persona/persona.md](persona/persona.md) | The single source. Change it first. | None: it is not loaded |
| [output-styles/pe-deal-team-twin.md](output-styles/pe-deal-team-twin.md) | Output style, with `force-for-plugin: true`, so it applies whenever the plugin is enabled | Claude Code |
| [persona/system-prompt.md](persona/system-prompt.md) | System prompt, in the template's tags | claude.ai Project instructions; hosted agents |

A persona change updates all three files in the same PR; `tests/test_persona.py` fails if the forms drift from `persona.md`. The persona is an instruction, not a guarantee: hard limits (no web tools, no writes at level 1, per-user access) are enforced by settings and connector permissions, not by the persona. The persona has not been evaluated with users or with behavioural evals yet.

## Upstream plugins

`preparing-company-briefs` is a layer on Anthropic's [`private-equity` and `financial-analysis` plugins](https://github.com/anthropics/financial-services), as reviewed in [compendium 17](../../../docs/compendium/17-anthropic-pe-plugins-review.md) (reviewed commit `3e32c2287dcb637c184c01cc0ad82d6af7e9bb0f`). It takes two ideas and depends on no upstream plugin at run time, so **there is nothing to install for it**:

- the deal-facts list and one-page layout, from `deal-screening` (adapt);
- the source ranking and "every number has a citation" rule, from `competitive-analysis` (adapt).

Page 17 finds no upstream skill that writes a brief, so the skill is written here, in our own words, and no upstream text is copied. Do not install `financial-analysis` from the upstream marketplace for this skill: as shipped it registers 12 third-party data connectors that are not acceptable in the private-equity ZDR org. Skills that do build on upstream skills (T4 to T6) will use the reviewed, vendored copy described in page 17, section 5, and this README will say so when they are added.

## Compendium pages

- [01-anatomy.md](../../../docs/compendium/01-anatomy.md)
- [02-persona.md](../../../docs/compendium/02-persona.md)
- [14-private-equity.md](../../../docs/compendium/14-private-equity.md)

## Filled in by

#32, #34, #37
