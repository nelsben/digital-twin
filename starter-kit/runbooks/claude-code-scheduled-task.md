# Runbook: set up a Claude Code scheduled task for a twin's task

## What this is

A Claude Code scheduled task (called a routine until recently) is a saved prompt, one or more repositories and a set of connectors that runs on its own, in Anthropic's cloud or in the customer's self-hosted environment, while the employee's laptop is closed. ([A]) Its release status is research preview: behaviour, limits and the API surface may change. ([A]) This runbook takes the engagement's decisions for one task (see "Inputs you need") and turns them into a working scheduled task that runs as one named employee. It is generic: replace every `<placeholder>` with the customer's value.

Roles use the names in [03-stakeholders](../../docs/playbook/03-stakeholders.md):

| Name used here | Role in 03-stakeholders |
|---|---|
| **Task owner** | Pilot user: the employee whose claude.ai account owns the task and whose identity the task runs under |
| **Claude org Owner** | Technical owner (Director of IT), or the Backup Owner |
| **Business owner** | Business owner: confirms what the task should produce and the autonomy level |
| **Skill owner** | Skill owners: keep the skill that holds the task's instructions |
| **Source-system admin** | Source-system admins: confirm each connected account is as narrow as the autonomy level needs |
| **Security** | Security (CISO or security engineer) |
| **Compliance** | Compliance / legal: confirms the data class |
| **Partner skill engineer** | Skill engineer (partner role) |
| **Partner integration engineer** | Integration engineer (partner role) |

## Read this first

How sources are marked: each numbered step and each product fact ends with the pages it came from, as tags like ([A], [B]) that the list below defines. **⚠ Unverified:** (the compendium's marker) means the pages we read did not confirm it; the item says what would confirm it. Confirm each one at setup, then replace the mark with the page you checked. Menu paths, setting names, limits and commands are copied from the pages as read on 2026-11-16.

Checked 2026-11-16 by the author against the pages listed. Not yet independently verified: verification-log.md has no rows for this runbook.

Pages used:

- [A] [Automate work with scheduled tasks](https://code.claude.com/docs/en/routines.md)
- [B] [Compare scheduling options](https://code.claude.com/docs/en/scheduled-tasks.md)
- [C] [Cloud environments](https://code.claude.com/docs/en/cloud-environments.md)
- [D] [Skills: use skills in Cowork and cloud sessions](https://code.claude.com/docs/en/skills.md)
- [E] [Settings: settings in cloud sessions](https://code.claude.com/docs/en/settings.md)
- [F] [Server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md)
- [G] [Self-hosted environments: configuration](https://code.claude.com/docs/en/self-hosted-environments-configuration.md)
- [H] [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web.md)
- [I] [Compendium 05, hosted agent or client skill](../../docs/compendium/05-decision-matrix.md)
- [J] [Compendium 06, autonomy](../../docs/compendium/06-autonomy.md)
- [K] [Compendium 10, sensitive data](../../docs/compendium/10-sensitive-data.md)
- [L] [Compendium 15, governance and performance](../../docs/compendium/15-governance-and-performance.md)
- [M] [twin-governance plugin README](../plugins/twin-governance/README.md)
- [N] [Managed-settings baselines README](../settings/README.md)

## Inputs you need

The engagement has already decided these for the task. The steps consume them; if one is missing, stop and ask the Business owner.

- **Runs as:** one named employee, the task owner. A scheduled task belongs to that person's claude.ai account, is not shared with teammates, and anything it does through their connectors appears as them. ([A]) Compendium [05](../../docs/compendium/05-decision-matrix.md) explains why this differs from a Claude Tag routine.
- **Autonomy level:** the level it starts at and its ceiling, from [06](../../docs/compendium/06-autonomy.md). Pilots start at level 1 (draft); a run that nobody watches is level 4 in that ladder. ([J])
- **Data class:** the class and what follows from it: which surfaces are allowed and what retention applies, per the matrix in [10](../../docs/compendium/10-sensitive-data.md). Cloud sessions, and so scheduled tasks, are off under Zero Data Retention, the HIPAA configuration and customer-managed encryption keys. ([H], [K])
- **Connectors:** each connector the task uses and, for each, whether it may read or may also write. All of the employee's connectors are included by default, so the list is also what to remove. ([A])
- **Schedule or trigger:** the cadence and time zone, or the API or GitHub trigger, and the repository the run works in. ([A])
- **Memory:** on or off. Instructions that must carry across runs go in the skill or in the repo's `CLAUDE.md`, which are part of the clone. ([C]) **⚠ Unverified:** whether auto memory is on in an Anthropic-hosted scheduled run; [G] says auto memory is off by default in a self-hosted environment. Confirm in a test run by asking Claude what it remembers from the last run.
- **Skill:** the name of the skill that holds the task's instructions, and the repository it is committed to. ([D])

## Before you start

- The plan is Pro, Max, Ultra, Team or Enterprise. ([A])
- Team and Enterprise: an Owner has left the **Scheduled tasks (Was Routines)** or **Routines** toggle on at **Organization settings > Capabilities > Remote sessions**. When it is off, existing tasks stop and nobody can create new ones. ([A])
- Enterprise with custom roles: the task owner's role includes the scheduled tasks permission, added by an Owner in the role's **Remote sessions** section at **Organization settings > Roles**. ([A])
- Cloud sessions are not turned off by policy (`Cloud sessions are disabled by your organization's policy`), and the organization is not on ZDR, HIPAA or CMEK. ([A], [H])
- The task owner signs in to Claude Code with a claude.ai subscription login: a Console API key or a cloud provider login hides `/schedule`. ([A])
- The repository is reachable: on Team and Enterprise an Owner has turned on the GitHub connection method the task owner will use. ([A])
- The skill from "Inputs you need" is already committed to that repository and has passed its evals. ([D])

## Steps

1. **Who: Technical owner with Compliance.** Choose the place it runs, using the data class: Anthropic-managed cloud is the default, or your organization's self-hosted environment when it is routed there; do not restate the matrix, follow [10](../../docs/compendium/10-sensitive-data.md) and [05](../../docs/compendium/05-decision-matrix.md). ([A], [B], [K], [I])
2. **Who: Partner skill engineer.** Commit the skill to the repository at `.claude/skills/<skill-name>/SKILL.md`; each run is a fresh cloud session that does not read `~/.claude/skills/` on the employee's machine, and the repository's `.claude/skills/` is part of the clone. **⚠ Conflict:** [D] says cloud sessions also load skills enabled on the claude.ai account, while [G] says a cloud scheduled task run does not get its owner's skills; follow the committed copy, and a skill committed to `.claude/skills/` is not available to cloud threads in a project. ([C], [D], [G])
3. **Who: Task owner.** Go to claude.ai/code/routines and click **New task** (**New routine** in some accounts, which opens a full-page form) to open the **New scheduled task** dialog; `/schedule` in the CLI does the same conversationally. ([A])
4. **Who: Task owner.** Give the task a descriptive name and write the prompt: self-contained, naming the skill, the output and what success looks like, because the task runs autonomously and the saved prompt is not live user input and cannot act as approval. **⚠ Unverified:** whether a prompt that is only `/<skill-name>` invokes the skill; the page says only that the session uses skills. Confirm with the run in "Check it worked", and until then write "Use the <skill-name> skill to ...". ([A])
5. **Who: Task owner.** In the **Trigger** row choose **Schedule** and a preset frequency (time in local time zone), or **Custom** with a cron expression such as `0 */2 * * *`; five fields alone are read in UTC, a `CRON_TZ=` prefix sets the zone, and anything more often than once per hour is rejected; pick a few minutes past the hour (for example 9:07), because a run exactly on the hour can start several minutes late. ([A], [B])
6. **Who: Task owner.** Expand **Advanced settings**, and under **Repository** on the **General** tab select the repository (cloned on every run; changes go to `claude/`-prefixed branches), then pick the **Cloud environment**: the **Default** has **Limited** network access with **Allow package managers** checked, and connectors reach their services through Anthropic's servers without allowlist changes. ([A])
7. **Who: Task owner.** Select the model, and the effort level if the model offers one, in the prompt box's model selector. ([A])
8. **Who: Task owner with the Source-system admin.** Open the **Connectors** tab of **Advanced settings** and remove every connector the task does not need: all connected connectors are included by default, and Claude can use an included connector during a run, including writes. ([A])
9. **Who: Security.** Hold the task to its autonomy level, using what the pages confirm. A cloud run begins in auto mode, where a classifier allows or blocks actions, and still stops for an ask rule and after repeated blocks; permission rules in the repository's `.claude/settings.json` apply in a session with one repository; Owners can deliver rules and `allowManagedPermissionRulesOnly` through server-managed settings, which reach cloud sessions and make the repository's rules ignored. The level is then the narrowest connector set, account scope and rules together ([06](../../docs/compendium/06-autonomy.md)). **⚠ Unverified:** whether a connector tool set to Blocked or Needs approval on the account holds in a scheduled run; confirm with test 3 in "Check it worked". ([A], [C], [E], [F], [H])
10. **Who: Partner integration engineer.** Decide what records the run, because the governance hook may not. Endpoint-managed settings (MDM, managed settings files) do not reach Anthropic-hosted cloud sessions, server-managed settings do, and plugins declared in a repository's `.claude/settings.json` do not load there; the starter kit delivers `twin-governance` through managed `enabledPlugins` and logs to a local file. **⚠ Unverified:** whether that hook runs in a scheduled run and where its log would live on a throwaway VM; confirm with test 4 in "Check it worked". Until confirmed, treat the run transcript and each source system's audit log as the record. ([C], [F], [M], [N], [L])
11. **Who: Task owner.** Click **Create**; the task's detail page opens and the task runs at the next trigger. Click **Run now** on the detail page for the first run. ([A])
12. **Who: Task owner.** Note the limits the task now lives under: 100 scheduled runs per hour per account; **Run now**, API fires and re-running a one-off share 30 per hour per task; none of these has overage. Runs draw down subscription usage, and without usage credits extra runs are rejected until the window resets. ([A])
13. **Who: Task owner.** Record how to pause and remove it: the on/off switch at the top of the detail page pauses and resumes the schedule; the menu next to the task's name has **Edit** and **Delete**; `/schedule list`, `/schedule update` and `/schedule run` manage it from the CLI. ([A])

## Check it worked

**Who: Task owner, with the Partner skill engineer watching. About ten minutes.** Use a harmless test input agreed with the Business owner.

| # | Do this | Pass if |
|---|---|---|
| 1 | On the detail page click **Run now**, then open the run from **History** | The run opens as a session and its transcript shows the skill being used. The row shows neither **Error** nor **Cancelled**. ([A]) |
| 2 | Read the transcript against the task's expected output | The output is what the Business owner expects. "Succeeded" only says the session ended, so this reading is the real check. ([A], [J]) |
| 3 | Add to a copy of the prompt: attempt one write that the level forbids, using a connector tool | The write does not happen without a person's approval, or the run stops waiting. If it succeeds, remove that connector or narrow the account and repeat. ([A]) |
| 4 | In a run, ask Claude to show the last line of the governance log file named in [M] (default `TWIN_GOVERNANCE_LOG`, `~/.claude/twin-governance/log.jsonl`) | A log line appears, so the hook ran. If not, the record is the transcript and the source-system audit logs (step 10). ([M]) |
| 5 | Switch the task off at the top of the detail page, then on again | Paused tasks keep their configuration and run again when switched on. ([A]) |

## Hand over

**Who: Partner skill engineer to the Task owner, the Business owner and the Claude org Owner.** In the customer's folder under `engagements/<customer>/`, record: the task name and its page at claude.ai/code/routines; the task owner; the place it runs and why (data class); the repository and environment; the connector list and read or write for each; the autonomy level now and its ceiling; the schedule in UTC and local time; the skill name and the commit it was checked in at; the date and result of each check above; and the unverified items still open.

After set-up the **Task owner** owns it, because it belongs to their account and is not shared. ([A]) The Business owner owns what it produces and any move up an autonomy level ([06](../../docs/compendium/06-autonomy.md)); the Claude org Owner owns the toggle and the roles. **⚠ Unverified:** what happens to the task when its owner leaves; compendium [05](../../docs/compendium/05-decision-matrix.md) says it stops, and the pages read here do not say. Confirm by asking Anthropic or testing with a spare account, and plan a named replacement owner before the pilot.

## What can go wrong

- **`/schedule` says "Unknown command".** The CLI hides it with a Console API key, a cloud provider login, a signed-out session, a cloud session, an Owner-disabled toggle, or a custom role without the scheduled tasks permission; create the task on the web instead. ([A])
- **Runs are skipped.** A missing or expired GitHub connection skips runs for up to 72 hours, then the task turns off and you turn it back on after reconnecting. ([A])
- **A run is late or waiting.** A run on the hour can start late, and the hourly limits make a run wait or an action fail until the limit resets. ([A])
- **A missed or failed run.** The row ends with **Error** if the run failed and **Cancelled** if its session was archived; a warning beginning "The last run" explains runs that did not start. **⚠ Unverified:** whether a run missed while nothing was wrong is replayed; the page does not say, so plan for a reconcile check ([06](../../docs/compendium/06-autonomy.md)). ([A])
- **The skill is not found.** A skill that exists only in `~/.claude/skills/` is reported as not found; commit it to the repository. ([D])
- **A host is blocked.** A request to a host outside the environment's allowlist fails with a `403` or `ENOTFOUND`; edit the environment's network access. ([A])
- **A run waits for an answer.** Auto mode still prompts for ask rules and repeated blocks; open the run from the detail page. ([A])
- **The task stops running.** An Owner turning off the toggle, a paused subscription, or an exhausted usage window each stop it. ([A])
- **The research preview changes.** Re-read [A] before each new engagement. ([A])
