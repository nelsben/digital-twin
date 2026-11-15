# twin-pe-deal-team

The role twin for a private equity deal team: its skills and its persona (output style).

Status: in progress (version 0.1.0). One skill is written (`preparing-company-briefs`); the other skills, hooks and the output style are placeholders kept with `.gitkeep`.

## Skills

| Skill | Story | What it does |
|---|---|---|
| [preparing-company-briefs](skills/preparing-company-briefs/SKILL.md) | T1 (#32) | A one-page company brief from the Salesforce deal record and the SharePoint deal folder, with a source link on every fact, a list of what is missing, and no web tools. Draft only. |

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
