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

## Results

Run on 2026-11-14 with Sonnet (all subagents). Plugin version 0.2.0. Raw
responses, grader prompts and run inputs are kept outside the repo.

| Arm | Expectations passed | Cases fully passed |
|---|---|---|
| With skill | 47 of 47 (100%) | 9 of 9 |
| Baseline (no skill) | 39 of 47 (83%) | 5 of 9 (cases 2, 3, 4, 7, 8) |

Trigger evals (name and description only, two skills shown, one answer per
query): hit rate on should-trigger 8 of 8 (100%); false-trigger rate on
should-not-trigger 0 of 10 (0%). The near miss "Update the CRM for my meeting
with Larch yesterday" went to the CRM skill, which is the right routing, not a
false trigger.

With-skill failures: none.

Baseline failures, which show what the skill adds:

- Case 1: about 712 words against a limit of about 450; no list of the last
  three interactions; partial source citations; derived claims not in the
  record (20.5% margin, 6.6x multiple, "QoE not started", "high concentration").
- Case 5: interactions carry no activity record IDs.
- Case 6: memo facts cited by title only, with no SharePoint path.
- Case 9: does not state the rule against web sources, gives no source links,
  and suggests pasting website text.

How it was run and its limits:

- Each case ran twice, once per arm, each in its own subagent that was given
  only the case prompt and fixture files. The with-skill arm was given the
  skill folder to read. Run folders had opaque names so the baseline could not
  see the skill name.
- Each run was graded by its own blind grader subagent, per expectation, with a
  one-line reason. Skill names in with-skill responses were redacted in the
  copies the graders saw. Blinding is imperfect: phrases like "level 1 (draft
  only)" still hint at the skill.
- Read-only access was set by instruction, not enforced by the tool set,
  because the Agent tool cannot restrict tools. Subagents also inherited
  session context.
- Graders saw only the response text, not tool calls, so expectations about
  tool use were graded as passed by construction.
- One run per case and arm, so the pass rates carry no variance estimate.
