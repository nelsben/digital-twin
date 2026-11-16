# FILL IN: Reference title (example of progressive disclosure)

This file shows the pattern. `SKILL.md` stays short and always loads when the
skill fires. This file loads only when a step in `SKILL.md` links to it, and
only when Claude needs the detail. Put here whatever is too long or too
specific for the main file: a long checklist, an output template, a glossary,
the customer's naming rules, a worked example.

Rules for reference files:

- Link it directly from `SKILL.md`. Do not link it from another reference
  file, because Claude may read nested files only in part.
- Keep one topic per file, and name the file for its topic
  (`output-template.md`, not `notes.md`).
- If a reference file runs past 100 lines, start it with a table of contents.
- Use forward slashes in paths, and write them relative to the skill folder.

## Example: pre-send checklist

Step 4 of `SKILL.md` points here. FILL IN: replace this with your own checks.

- [ ] Every figure has a source link.
- [ ] Anything the user did not provide is marked "missing", not estimated.
- [ ] The output follows the format in `SKILL.md`.
- [ ] No data above the skill's stated data class appears in the output.
