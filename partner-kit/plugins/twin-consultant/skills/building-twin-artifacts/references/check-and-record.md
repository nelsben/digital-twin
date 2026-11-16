# check and record

What the two commands test and read. The design of record is section 8a of
`partner-kit/docs/design.md`; this page is the working summary for step 7.

## check

`cli.py check <persona-dir> [<task-id>]` writes nothing. It prints one line
per problem, `<file>: <problem>. Next: <fix>.`, then a count. Exit 0 means no
problem; 1 means at least one, or that `levelled.json` is stale. It skips
not-built artifacts.

For every artifact:

- No FILL IN is left in any file the manifest lists, nor in any file under
  the artifact's `SKILL.md` folder (an added file counts too). A missing file
  is a problem.

For the `SKILL.md` folder:

- The frontmatter has only `name` and `description` (compendium 16).
- `name` equals the folder name and meets compendium 03's name rule: 64
  characters at most, lowercase letters, numbers and hyphens, no "anthropic"
  or "claude".
- `description` is under 200 characters (compendium 03's Conflict line: the
  platform docs allow 1,024, the claude.ai help article says 200).
- The body is under 500 lines (compendium 03).
- Every file `SKILL.md` links exists, inside the folder and one level deep
  (`references/x.md`, never `references/a/x.md` or `../x.md`).
- `evals/evals.json` is in `skill-creator`'s shape: a `skill_name` equal to
  the name and an `evals` list of at least 3 cases, each with a `prompt` and
  at least one `expectations` entry.
- `evals/trigger-evals.json` is a list of `{"query", "should_trigger"}` with
  at least one true entry and one false entry.
- Every system the levelled plan's `tools` gives the task appears in the
  first table under the Inputs heading.

For a hosted agent (`agents/<task-id>/`): `agent.json` and
`environment.json` parse; `model` and `system` are set; `skills` names a
`skill_id`; the `SKILL.md` folder exists; `config.networking.type` is
`limited`. For a routine, scheduled task or SDK runner sheet: no FILL IN.

## record

`cli.py record <persona-dir> <task-id> --status evals-passing --evidence <file> --by <name> [--pass-mark <percent> --approved-by <name>]`

It moves one status at a time, never backwards, and writes nothing on a
refusal (exit 1, a line ending "Next: ..."). It sets evals-passing only, from
drafted. It appends `{status, by, evidence, pass_rate, baseline_rate,
pass_mark, approved_by}` to the artifact's `history` in `build.json`; build
keeps the history.

The evidence must sit under `build/evidence/<task-id>/` and be one of:

| Tool | Pass rate | Baseline |
|---|---|---|
| `skill-creator` benchmark (`benchmark.json`) | `run_summary.with_skill.pass_rate.mean` | `run_summary.without_skill.pass_rate.mean`, with runs whose `configuration` is `without_skill` |
| `claude plugin eval` JSON result (`--json`, `schemaVersion` 1) | mean of `cases[].aggregates.score` | mean of score minus `cases[].aggregates.delta` |

It also refuses when:

- check reports a problem for the artifact;
- the benchmark's `metadata.skill_name` is another name, or a case in
  `evals/evals.json` has no `with_skill` run;
- the plugin eval result is `partial`, or a run has `skippedPaidGraders`;
- the pass rate is below the pass mark (default 100);
- the pass mark is below 100 and `--approved-by` is missing;
- the status asked for is packaged: only the package command sets it;
- the status asked for is deployed or verified before the package command
  has set packaged.

## Deployed and verified

After `package` has set packaged and the customer's admin has worked through
`build/deploy.md`, record moves the artifact on a text note under
`build/evidence/<task-id>/` in the customer's copy:

- `--status deployed --by <admin's name> --evidence <note>`: the note says
  where it was published or created (the surface, and the group or
  channel). A hosted agent is named by a placeholder such as `<agent-id>`.
- `--status verified --evidence <note>`: the note gives the result of the
  runbook's check-it-worked step.

It refuses a note that is empty, or that holds what looks like a key, a
token, a password, an org, tenant, agent or vault id, or a URL. The history
entry keeps the note's path and leaves the rates and the pass mark null.
