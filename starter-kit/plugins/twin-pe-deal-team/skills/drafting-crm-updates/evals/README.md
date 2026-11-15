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

## Results

Run on 2026-11-14 with Sonnet (all subagents). Plugin version 0.2.0. Raw
responses, grader prompts and run inputs are kept outside the repo.

| Arm | Expectations passed | Cases fully passed |
|---|---|---|
| With skill | 44 of 44 (100%) | 8 of 8 |
| Baseline (no skill) | 42 of 44 (95%) | 6 of 8 (cases 1 to 5 and 7) |

Trigger evals (name and description only, two skills shown, one answer per
query): hit rate on should-trigger 8 of 8 (100%); false-trigger rate on
should-not-trigger 0 of 10 (0%). The near miss "Prepare a company brief for
Project Fir before my meeting tomorrow" went to the brief skill, which is the
right routing, not a false trigger.

With-skill failures: none.

Baseline failures, which show what the skill adds:

- Case 6: does not say it cannot save at this autonomy level. It blames a
  read-only session and an unauthorised connector instead.
- Case 8: says it had no web access rather than saying web sources are not used
  for deal work. It did not look the bidder up and invented nothing.

How it was run and its limits:

- Each case ran twice, once per arm, each in its own subagent that was given
  only the case prompt and fixture files. The with-skill arm was given the
  skill folder to read. Run folders had opaque names so the baseline could not
  see the skill name.
- Each run was graded by its own blind grader subagent, per expectation, with a
  one-line reason. Skill names in with-skill responses were redacted in the
  copies the graders saw. Blinding is imperfect: phrases like "Draft only. A
  reviewer checks every brief" still hint at the skill.
- Read-only access was set by instruction, not enforced by the tool set,
  because the Agent tool cannot restrict tools. Subagents also inherited
  session context, and two baseline runs mentioned the Salesforce connector
  from it.
- Graders saw only the response text, not tool calls, so expectations about
  tool use (for example "no write call") were graded as passed by construction.
- One run per case and arm, so the pass rates carry no variance estimate.
- The query "Build the Monday pipeline summary for the partners" is in both
  trigger sets; it was asked once and counted in both.
