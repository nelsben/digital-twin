# digital-twin

A partner playbook and starter kit for delivering role-based digital twins: companion agents with bespoke skills, deployed into customers' Claude orgs. We are Anthropic partners; twins are role templates, not per-person agents. Overview: [README.md](README.md).

## Where things live

- Facts about Claude: [docs/compendium/](docs/compendium/README.md). Sources are listed in [sources.md](docs/compendium/sources.md). For Anthropic's own skills and plugins, start at [page 16](docs/compendium/16-oob-skills-and-references.md).
- How engagements run (phases, discovery, stakeholders, stories): [docs/playbook/](docs/playbook/README.md).
- What we build with (marketplace, plugins, templates, settings, runbooks): [starter-kit/README.md](starter-kit/README.md). Start there.
- The persona-card workflow (interview notes to persona card, levelled plan, backlog and dashboard). Partner-only. Design of record: [partner-kit/docs/design.md](partner-kit/docs/design.md). Start at [partner-kit/README.md](partner-kit/README.md).
- Worked examples of an engagement, both fictional: [engagements/README.md](engagements/README.md) names `sample-pe` and `sample-team-cs`.
- Task cards: [agents/tasks/](agents/tasks/README.md), one file per task.

## Rules

- Every compendium fact carries a source link. If the research did not confirm it, mark it unverified (the compendium README defines the marker). Do not state unconfirmed facts as settled.
- Customer answers and decisions go in that customer's folder under `engagements/`, never in the compendium. The compendium holds defaults; each engagement confirms or overrides them.
- Everything in every `engagements/sample-*` folder is fictional: invented companies, people and numbers. Keep it that way. Never put real customer names or data there.
- The partner kit is never listed in the customer marketplace. A change to the persona-card workflow updates `partner-kit/docs/design.md` in the same pull request.
- Link to existing pages instead of copying their content.

## Workflow

- Work happens on a branch and lands through a pull request. Do not commit to `main`.
- Work is organised as task cards in `agents/tasks/`. Read the card, stay inside its `scope`, and meet its "Done when" list.
- Run the tests before you open a PR: `python3 -m unittest discover -s tests`
