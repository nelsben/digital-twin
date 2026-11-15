# Evals for writing-in-house-style

These are the eval files for the house-style skill in `twin-shared` (#36), written before the skill (they are in an earlier commit than `SKILL.md`). Format: [starter-kit/templates/skill/your-skill-name/evals/](../../../../../templates/skill/your-skill-name/evals/).

## Fixtures are synthetic

Everything under `files/` is invented: companies, people, figures and an email address on a reserved `.example` domain. Each file says so on its first line. Code names reuse the kit's Larch, Birch and Cedar. The customer's skill owner replaces them with redacted real examples of text they would want rewritten, and changes the expectations to match their own rules in `references/house-style.md`.

## Case map

| Case | What it tests | Fixture |
|---|---|---|
| 1 | Rewrite a chatty draft email: ask first, ISO dates, figure labelled, no hype or emoji, says what changed | `larch-update-draft.md` |
| 2 | Draft a note from raw call notes: no invented surname, currency, year or company name | `birch-call-notes.md` |
| 3 | Short summary of a document: figures with unit, currency and period; estimate and calculated figures labelled | `cedar-management-extract.md` |
| 4 | Missing input: asks for the text, writes no draft | none |
| 5 | A role skill's required layout is kept | `brief-template.md`, `birch-facts.md` |
| 6 | Plain question: answered directly, skill not used | none |
| 7 | Rewrite a handover note: ambiguous date and vague period not guessed | `cedar-handover-note.md` |
| 8 | Short chatty message: short result, no emoji, no structure | `chatty-slack-message.md` |

Cases 5 and 6 are the should-not-take-over cases. Case 4 is the missing-data case.

## Trigger evals

`trigger-evals.json` has 10 should-trigger and 12 should-not-trigger queries. The should-not-trigger set includes the deal-team near misses ("company brief for", "one-pager on", "brief me on", "update the CRM", "log my meeting", the pipeline summary) and plain questions that need no writing.

## Results

Run on 2026-11-15 with Sonnet (all subagents). Plugin version 0.2.0. Raw responses, grader prompts and grades are kept outside the repo.

| Arm | Expectations passed | Cases fully passed |
|---|---|---|
| With skill | 50 of 56 (89%) | 3 of 8 (cases 2, 5, 6) |
| Baseline (no skill) | 39 of 56 (70%) | 2 of 8 (cases 5, 6) |

Trigger evals (name and description only, all three kit skills shown, one answer per query, one fresh subagent, queries shuffled): hit rate on should-trigger 10 of 10 (100%); false-trigger rate of this skill on should-not-trigger 0 of 12 (0%). The six deal-team near misses went to the brief or CRM skill, which is the right routing. Query "tidy this up pls" has no text to tidy but did trigger, which is the intended routing; the skill then asks for the text (case 4).

The skill beat the baseline on cases 1, 2, 3, 7 and 8 (11 more expectations passed in total). It did not beat it on cases 4, 5 and 6: both arms tied, and cases 5 and 6 pass in both arms. These two are guards, not gaps the skill fixes.

With-skill failures:

- Case 1: the reply date was left as a bracketed choice between 2026-11-20 and 2026-11-27 (the draft contradicts itself: "end of next week (Fri 27th)"), and the revenue unit stayed a placeholder. The skill chose to flag rather than guess, which its own rules ask for, so these two expectations are arguably too strict.
- Case 3: the 'around a third' customer claim was quoted but not attributed to management.
- Case 4: the reply was well over the 60-word limit.
- Case 7: expectation 3 asks for the surnames Lena Placeholder and Ana Sample, which the handover note does not contain. This is a flaw in the expectation (the baseline failed it too); it should be reworded. Left as run so the numbers match what was graded.
- Case 8: the list of changes was longer than "a line or two".

Baseline failures, which show what the skill adds:

- Case 1: the ask came late and dates were not ISO.
- Case 2: the note did not lead with the decision, the call date was not ISO, Sam's missing surname was not flagged, and the note was long with bold headings.
- Case 3: the summary was longer than five lines and did not open with the headline.
- Case 7: "mid year" was turned into a year the note does not contain.
- Case 8: the ask was not first, the date was not ISO, the message ran longer than three sentences and added facts, and the change summary was long.

How it was run and its limits:

- Each case ran twice, once per arm, each in its own sonnet subagent that was given only the case prompt and fixture files in an opaque run folder. The with-skill arm was also given a copy of `SKILL.md` and `references/` (not the evals). Six spawns were refused on the first try because of a timeout in the spawn check and were re-run unchanged.
- Each run was graded by its own subagent, per expectation, with a one-line reason. The graders were not told which arm they were grading, and the skill name and the phrase "house style" were redacted from with-skill responses. Blinding is imperfect: with-skill replies often end with a list of changes and questions that hint at the skill. The author of the skill did not grade.
- Read-only access was set by instruction, not enforced by the tool set. Subagents may have inherited some session context.
- Graders saw only the response text, not tool calls.
- One run per case and arm, so the pass rates carry no variance estimate. Eight cases is a small set, and several expectations on length or wording are judgement calls that graders applied literally.
- Only sonnet was tested. Haiku and Opus are not covered, and the guide asks for the customer's models.
- The trigger test used one subagent seeing all 22 queries at once, and one answer per query; it is not skill-creator's description-tuning loop and has no held-out set.
