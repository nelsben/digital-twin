# Evals for preparing-company-briefs (T1)

These are the eval files for the company-brief skill, written before the skill
(#32). The acceptance criteria are in
[engagements/sample-pe/backlog.md](../../../../../../engagements/sample-pe/backlog.md),
story T1. Format: [starter-kit/templates/skill/your-skill-name/evals/](../../../../../templates/skill/your-skill-name/evals/).

## Fixtures are synthetic

Everything under `files/` is **synthetic and obviously fictional**: invented
companies, people, record IDs and figures. Each file says so on its first line.
They exist so the eval cases can run today and so the expectations are checkable.

**The customer's skill owners replace them with 3 redacted real examples**
(F3: two briefs, one good and one weak, plus a third from Callum Nwosu), as
the story's definition of ready requires. When replacing, keep the same
shape: one file per connector result, so the cases keep working, and keep the
expectations in step with the real facts.

The files stand in for what the Salesforce and Microsoft 365 connectors would
return. Each prompt says so, because the connectors are not live yet.

## Case map

| Case | Backlog criterion | Fixture |
|---|---|---|
| 1 | 1, good example | Project Larch (`larch-*`) |
| 2 | 2, missing material (empty deal folder) | Project Birch (`birch-*`) |
| 3 | 3, no access | Project Cedar (`cedar-no-access-result.md`) |
| 4 | 4, closed record | Project Dune (`dune-closed-opportunity.md`) |
| 5 | 4, stage changed last week | Project Elm (`elm-stage-changed-opportunity.md`) |
| 6 | 5, unsupported claim (weak example) | Project Fir (`fir-conflicting-sources.md`) |
| 7 | 6, level 1 holds: save to the deal folder | Project Larch |
| 8 | 6, level 1 holds: update the stage | Project Larch |
| 9 | "Plus": no web tools | Project Larch |

Criterion 4 has two inputs in the backlog, so it is two cases (4 and 5).
Criterion 6 has two requests, so it is two cases (7 and 8).

## Not covered here

"Governance log shows record IDs only" and "a user without access gets no
data" at the connector level are tested as spike #30 and task #21 work, not
as skill evals (see [authoring-skills.md](../../../../../docs/authoring-skills.md)).
Case 3 checks only that the skill reports no access and invents nothing.

## Trigger evals

`trigger-evals.json` has 8 should-trigger and 10 should-not-trigger queries.
The should-not-trigger set includes the near miss named in the story
(pitch-book drafting) and the other deal-team tasks (T3 to T6) and the CRM update (T2).
