# House style: default rules

**These are the starter kit's defaults.** They are a sensible starting set, not the customer's own rules. The customer's skill owner replaces this one file with the firm's rules. To do that:

1. Keep the file at `references/house-style.md` in this skill folder. `SKILL.md` links to that path and does not need to change.
2. Keep one section per rule, each with a one-line reason. Claude follows a rule better when it knows why, and can apply it to cases the rule does not name.
3. Keep the check list at the end in step with the rules, so the draft is checked against the same list.
4. Re-run the evals in `evals/` and change any expectation that no longer matches the new rules (for example a date format that is not ISO 8601).

The examples below are invented.

## 1. Lead with the answer or the ask

Open with what the reader needs to know or do, and the date they need to do it by. Background comes after, only as much as the reader needs.

Reason: internal readers decide from the first lines. A reader who stops after one sentence should still have the point.

Example: "Please confirm by 2026-11-27 whether the 2026-12-03 committee slot works." Not: "Following our recent discussions, I wanted to reach out about next steps."

## 2. Plain words and short sentences

Use everyday words and sentences of about 20 words or fewer. Say the thing once. Cut hype ("amazing", "game-changer"), filler ("touch base", "just wanted to", "as per", "in order to") and jargon that has a plain equivalent ("use", not "leverage"). Keep a figure or a fact that is real; cut an adjective that only adds feeling.

Reason: hype and filler hide the facts and make readers trust the text less. Short sentences are checked faster.

## 3. Numbers with unit, currency and period

Write every figure with its unit (thousand, million), its currency (USD, EUR, or the symbol with the code on first use) and its period (the financial year or date range). Example: "revenue of EUR 66.0 million for the year ending 2025-12-31". If the source does not give one of these, say it is not stated. Do not supply it. Do not make a figure more precise than the source: "around a third" stays "around a third".

Reason: a bare "18" or "up 10%" cannot be checked or compared, and a guessed currency or year turns into a wrong number downstream.

## 4. Dates in ISO 8601

Write dates as YYYY-MM-DD (2026-12-03), and times in 24-hour form with the time zone when it matters (15:00 CET). Turn relative dates ("next Friday", "end of the month") into ISO dates when the text gives a date to count from (the date written, or today's date given to you). If a date is ambiguous (03/11/2026 could be 3 November or 11 March) or too vague ("mid year"), flag it or ask. Do not pick one.

Reason: one format cannot be misread across regions, and sorts correctly. A relative date goes stale the moment the message is forwarded.

## 5. Name the source of every fact taken from a system or document

When a fact comes from a system or a document (a CRM record, a data-room file, a memo, a presentation), name it: the system and record, or the file name and page. Label what is not firm: write "unaudited", "management-provided" or "management estimate" for those figures, and "calculated" or "inferred" for a figure you derived (a growth rate, a margin) or a conclusion not in the source. Never present an inferred figure as if the source said it.

Reason: readers act on what they believe is checked. The label tells them how far to trust a figure, and the source tells them where to check it.

## 6. People by full name on first mention

Give a person's full name the first time they appear, and the role if the reader may not know it. After that, the first name is fine. If you only have a first name, use it as given and note that the surname is missing. Do not guess one.

Reason: first names are ambiguous in a firm with several people of the same name, and a guessed surname puts the wrong person on a record.

## 7. Headings and tables only when they help

A short message (a note, an email, a summary of a few lines) has no headings and no table. Use a heading when a text has several parts a reader will want to jump between, and a table when there are three or more items with the same attributes. A short list is fine for steps or parallel items.

Reason: structure on a short text adds weight and hides the point. Structure on a long text is how readers find their part.

## 8. No emoji

Do not use emoji or emoticons, and keep exclamation marks to none, or at most one. When editing someone's text, remove them.

Reason: emoji read as informal in business writing, can be misread, and render differently across systems.

## Check list

Before presenting a draft, check each line.

- The first line is the answer or the ask, with its date.
- No hype, filler or sentence over about 20 words.
- Every figure has unit, currency and period, or says which is not stated.
- Every date is ISO 8601; ambiguous or vague dates are flagged.
- Every fact from a system or document names its source; unaudited, management-provided, calculated and inferred items are labelled.
- Each person has a full name on first mention, or the missing surname is noted.
- Headings and tables appear only where they help; a short text has none.
- No emoji.
- Nothing is stated that the material does not support.
