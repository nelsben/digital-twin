---
name: writing-in-house-style
description: Writes or edits internal prose (emails, notes, summaries, memos) to the house rules. Use for "tidy this up", "rewrite this", "draft a note to". Not for tasks a role skill covers.
---

# Writing in house style

## Purpose

Every twin writes the same way: the answer first, plain words, figures that can be checked, sources named. This skill applies those rules when someone asks for prose for an internal reader and no role skill covers the task: an email, a note, a summary, a memo, or a rewrite of text they already have ("tidy this up", "rewrite this", "draft a note to").

It does not replace a role skill's own output format. If a role skill covers the task (a company brief, a CRM update, a pipeline summary), follow that skill's format and sections. If the user supplies a required layout, keep its headings and order. Apply the rules below only inside it, for example ISO dates and full names.

It does not cover plain questions that need an answer, not a piece of writing ("what does EBITDA stand for?"). Answer those directly.

## Inputs

- The text to edit, or the material to write from (notes, a document, a record). Ask for it when it is missing.
- The reader, if the user names one, and what the reader should do. If the writing needs an ask or a decision and none is given, ask for it. Do not invent one.

Required from the user: the text or material. With nothing to write from, say that nothing came with the request and ask for it. Do not write a draft.

## Steps

1. **Read the rules** in [references/house-style.md](references/house-style.md). The customer may have replaced that file with its own rules; always follow the file as it stands, not your memory of the defaults.
2. **Find the point.** Decide what the reader needs to know or do. Put that first.
3. **Draft.** Write from the material only. Do not add facts, figures, names, dates or reasons the material does not hold. Where the material leaves something out that a rule needs (a currency, a period, a surname, a source, an unambiguous date), say it is missing. Do not fill the gap.
4. **Check the draft against the rules**, one by one, using the checklist at the end of the rules file. Fix what fails. Cut length before cutting a source or a label.
5. **Present the draft** as text in the session. Do not send or save it unless the user asks and the twin's autonomy level allows it.
6. **When editing someone's text, say what changed**, in a few lines after the text: what moved, what was cut, what was labelled or flagged. Keep it to the changes that matter to the author. List anything you could not resolve as a question, such as an ambiguous date.

## Output

The edited or drafted text first, then, when you edited existing text, the short list of changes. Match the length to the job: a short message stays short, with no headings or table. Do not add a greeting, a sign-off or a closing offer of more help unless the original had one that the reader needs.

## Guardrails

- **Facts stay as given.** Rewriting changes the words, not the claims. Do not make a figure more precise, turn "around a third" into 33%, or turn a guess into a statement of fact.
- **Ask, do not guess.** An ambiguous date (03/11/2026), a missing currency or period, a first name with no surname, or a vague time ("mid year") is flagged or put to the user. It is never settled by a plausible guess.
- **Names stay exactly as given.** Write each name (a person, a company, a project) exactly as the source gives it. Do not expand it, complete it or correct it from memory.
- **Missing facts are asked for, not looked up.** If a fact is missing, say so and ask the user to supply it. Do not fill it from web search or web fetch.
- **Format of a role skill wins.** See Purpose.
- Writing here is draft only. Nothing is written to a system, so there is no twin marker to add.

## Reference files

- [references/house-style.md](references/house-style.md): the default rules, each with its reason, and the check list. Open it at steps 1 and 4. A customer replaces this one file with its own rules.

## Evals

The cases in [evals/evals.json](evals/evals.json) and [evals/trigger-evals.json](evals/trigger-evals.json) were written before this skill. Re-run them after every change. Results are in [evals/README.md](evals/README.md).
