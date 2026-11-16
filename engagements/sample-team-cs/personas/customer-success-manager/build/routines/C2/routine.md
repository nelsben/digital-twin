# Claude Tag routine: C2, Weekly renewal-risk digest

A fill-in sheet for setting up this task as a Claude Tag routine. Fill it in, then follow the runbook's steps.

Runbook: [starter-kit/runbooks/claude-tag-routine.md#steps](../../../../../../../starter-kit/runbooks/claude-tag-routine.md#steps). Runtime: claude-tag-routine (levelled `tasks.C2.runtime`, rule runtime-team-slack-tag-routine; cite docs/compendium/05-decision-matrix.md#decision-flow-our-recommendation).

## Inputs you need

One line per input in the runbook. Replace each FILL IN with what the engagement decided; a hint names the field it came from.

- **Runs as:** FILL IN. Levelled `tasks.C2.identity`: service-account.
- **Autonomy level:** FILL IN. Levelled `tasks.C2.autonomy`: start 1, ceiling 2.
- **Data class:** FILL IN. Card `tasks.C2.data_class`: confidential; levelled `tasks.C2.data_controls.retention`: standard.
- **Connectors:** FILL IN. Levelled `tools` for C2: hubspot read (always-allow), usage-db read (always-allow), slack send (blocked).
- **Schedule or trigger:** FILL IN. Card `tasks.C2.trigger`: schedule-team.
- **Memory:** FILL IN. Levelled `tasks.C2.memory`: off.
- **Skill:** FILL IN. The build scaffolded weekly-renewal-risk-digest in the role plugin twin-customer-success-manager, at build/plugin/twin-customer-success-manager/skills/weekly-renewal-risk-digest/.
