# Smoke test: the kit's plugins in a real headless session

`smoke.py` runs Claude Code headless (`claude -p`) from the repo root and loads the kit's three plugins ([twin-shared](../plugins/twin-shared/README.md), [twin-pe-deal-team](../plugins/twin-pe-deal-team/README.md) and [twin-governance](../plugins/twin-governance/README.md)) from their folders for that one session. It checks that the plugins load, that both skills trigger from a plain request, that no write, shell or web tool is used, and that the governance log is written and holds no deal content. It is the first end-to-end run of the kit; until now the skills were checked by agents reading `SKILL.md` and the trigger evals were a simulation.

## How to run it

```
python3 starter-kit/smoke/smoke.py
```

Needs Python 3 (standard library only) and a signed-in `claude` on the PATH. Options: `--model` (default `sonnet`), `--timeout` seconds per run (default 600), `--claude` binary, `--keep-logs` to keep the temporary governance logs for inspection (they hold fictional fixture metadata only).

It costs model usage: two sessions, about 0.1 USD each at the time of the run below. For that reason it is not part of the unittest gate (`python3 -m unittest discover -s tests`) and nobody should wire it into CI by default. Run it by hand before a kit release and after a Claude Code upgrade.

Exit code: 0 if every check of both runs passes, 1 if any check fails, 2 if `claude` could not be run (not found, not signed in, timeout, no init event).

## What each run does

- Flags, confirmed against the installed CLI (`claude --help`) and the docs ([headless](https://code.claude.com/docs/en/headless), [plugins reference](https://code.claude.com/docs/en/plugins-reference)): `-p`, `--output-format stream-json --verbose`, `--plugin-dir <folder>` (repeated, this session only), `--model sonnet`, `--tools Read,Glob,Grep,Skill` (limits the built-in tool set), `--allowedTools Read,Glob,Grep,Skill`, `--permission-mode dontAsk`, `--strict-mcp-config` (no MCP config given, so no MCP servers from settings), `--setting-sources ""` (no user, project or local settings files) and `--no-session-persistence` (no transcript written to disk).
- It installs nothing, adds no marketplace and writes nothing under `~/.claude` plugin or settings files. Each run gets a new temporary log outside the repo through `TWIN_GOVERNANCE_LOG`, plus `TWIN_GOVERNANCE_TWIN_ID=twin-pe-deal-team` and a random throwaway `TWIN_GOVERNANCE_SALT`. The temporary folder is deleted at the end.
- Run 1: `Prep a brief on Larch. The deal files are in <abs path to preparing-company-briefs/evals/files>.` Run 2: `Update the CRM for my meeting with Larch. My notes and the opportunity export are in <abs path to drafting-crm-updates/evals/files>.` Neither prompt names a skill.

Differences from the task card: none that change a result. The docs say `--bare` skips plugin hooks, even for a plugin passed with `--plugin-dir`, so the script does not use it (the governance hook would not run).

## The six checks per run

| | Check |
|---|---|
| a | The `system/init` event lists all three plugins (none in `plugin_errors`) and both skills |
| b | The expected skill was invoked: a `Skill` tool call names it, and its result is not an error |
| c | Every tool call in the stream is Read, Glob, Grep or Skill, so no write, shell or web tool ran |
| d | The log has at least one line per tool call, every line is JSON with `schema_version` 2 and `twin_id` `twin-pe-deal-team` |
| e | The log contains none of: Larch (any case), the fixture folder path (absolute or repo-relative), any fixture file name |
| f | Run 1: no sentence claims something was saved. Run 2: a sentence says nothing was written to the CRM |

Check f is a string check on the final answer (negation words next to a write verb, and, for run 2, a CRM word), not a judgement of meaning. A pass means the pattern was found or absent; read the answer if the result matters.

## Results

Run on 2026-11-15, copied from the script's own output. Claude Code 2.1.322, model `claude-sonnet-5-5` (the `sonnet` alias, as reported in the init event).

| Check | Run 1: preparing-company-briefs | Run 2: drafting-crm-updates |
|---|---|---|
| a. init lists all three plugins and both skills | pass | pass |
| b. expected skill was invoked | pass | pass |
| c. no write, shell or web tool was called | pass | pass |
| d. governance log: one valid line per tool call, schema 2, twin_id | pass | pass |
| e. log holds no Larch, fixture path or fixture file name | pass | pass |
| f. final answer says nothing was saved or written | pass | pass |

Tool calls in the stream and log lines matched in both runs (run 1: 8 and 8; run 2: 4 and 4). One run per prompt.

If a check fails on a later run, record the failure here with the evidence. Do not change files outside this folder to make a check pass.

## What this does not prove

- It is not a managed device. No managed settings are in force, and `allowManagedHooksOnly` is not set, so this does not show that the governance hook runs when IT locks hooks down or that a user cannot disable it. (`--setting-sources ""` also means none of the [settings baselines](../settings/README.md) were loaded.)
- The marketplace install path and managed-settings delivery are not exercised. The plugins load from folders with `--plugin-dir`, not from the `digital-twin-kit` marketplace, and nothing is pushed to the machine by IT. Install, update and `enabledPlugins` behavior stay unproven.
- Connectors are not live. The deal data is fixture files read with file tools, so no Salesforce, SharePoint or Teams connector is called and no record ids reach the log (every `record_ids` list is empty). The log's record id handling is covered by unit tests only, not by this run.
- One run per prompt, so there is no measure of variance. A pass shows the skill can trigger, not that it triggers reliably; the trigger evals and a larger sample are still needed for that.
- The final-answer checks are string checks. They do not judge the quality or accuracy of the brief or the CRM draft.
- Isolation is partial. `--setting-sources ""` leaves out the user's settings files, but the CLI can still load plugins that come from the environment instead of settings; one such plugin appeared in the init event of the run above and was not part of the kit. Checks a to e look only at the kit's plugins, tool calls and log, so it did not affect them.
- One platform (macOS) and one Claude Code version.
