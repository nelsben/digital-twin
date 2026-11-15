# Evals for drafting-crm-updates (T2)

These are the eval files for the CRM-update skill, written before the skill
(#34). The acceptance criteria are in
[engagements/sample-pe/backlog.md](../../../../../../engagements/sample-pe/backlog.md),
story T2. Format: [starter-kit/templates/skill/your-skill-name/evals/](../../../../../templates/skill/your-skill-name/evals/).

## Fixtures are synthetic

Everything under `files/` is **synthetic and obviously fictional**: invented
companies, people, record IDs and figures. Each file says so on its first line.
They exist so the eval cases can run today and so the expectations are checkable.

**The customer's skill owners replace them with 3 redacted real examples**
(F3 gives one sample CRM update; ask Beatriz Halloran for two more, one from a
transcript and one with no next step), as the story's definition of ready
requires. When replacing, keep the same shape: one file per connector result,
so the cases keep working, and keep the expectations in step with the real facts.

The files stand in for what the Salesforce and Microsoft 365 connectors would
return. Each prompt says so, because the connectors are not live yet.

## Case map

| Case | Backlog criterion | Fixture |
|---|---|---|
| 1 | 1, sample update from notes | `larch-meeting-notes.md`, `larch-salesforce-opportunity.md` |
| 2 | 2, transcript input | `larch-teams-transcript.md` |
| 3 | 3, no next step | `larch-meeting-notes-no-next-step.md` |
| 4 | 4, wrong opportunity | Larch notes with `cedar-salesforce-opportunity.md` |
| 5 | 5, no access | `larch-no-access-result.md` |
| 6 | 6, level 1 holds | Case 1 files, with "go ahead and save it" |
| 7 | Missing material: empty notes, no transcript | `larch-meeting-notes-empty.md` |
| 8 | "Plus": no web tools | Case 1 files |

Case 7 is the T2 counterpart of T1's empty-deal-folder case: the backlog has
no separate criterion for it, so it is added here.

## Not covered here

"Every write carries the twin marker" is not an eval at level 1, because the
skill makes no writes. The `Last updated by twin` field in the Salesforce
fixture is empty for that reason; at level 2 the cases change (see the
backlog). "Governance log shows record IDs only" and connector-level access
are tested as spike #30 and task #21 work (see
[authoring-skills.md](../../../../../docs/authoring-skills.md)). Case 5 checks
only that the skill reports no access and invents nothing.

## Trigger evals

`trigger-evals.json` has 8 should-trigger and 10 should-not-trigger queries.
The should-not-trigger set includes the near miss named in the story (email
drafting), and the other deal-team tasks.
