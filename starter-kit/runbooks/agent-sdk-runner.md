# Runbook: Build an Agent SDK runner for a task

## What this is

A twin task that must run in the customer's own container, with a trigger we build, can use the Agent SDK instead of a hosted runtime. The runner is a small program: it starts one SDK session for one trigger, loads the persona's system prompt and the task's skill, allows only the tools the task needs, writes the governance log through hooks, and exits. This runbook takes our integration engineer and the customer's Director of IT from the engagement's decisions to a running, pinned runner and a test that proves a read works and a write is refused. Which runtime to pick is decided in [05](../../docs/compendium/05-decision-matrix.md); for the hosted alternative see the [Managed Agents runbook](managed-agents.md).

Roles use the names in [03-stakeholders](../../docs/playbook/03-stakeholders.md):

| Name used here | Role in 03-stakeholders |
|---|---|
| **Runner owner** | Technical owner (Director of IT): owns the container host, the Claude API key, the secrets manager and the log pipeline |
| **Partner integration engineer** | Integration engineer (partner role): writes and tests the runner |
| **Business owner** | Business owner (RevOps manager or the role's leader): confirms the task and its autonomy level |
| **Security** | Security (CISO or security engineer): reviews tools, credential routing and the network allowlist |
| **Compliance** | Compliance / legal: confirms the data class and retention |
| **Source-system admin** | Source-system admins (for example the Salesforce admin): creates the least-privilege account the credential belongs to |

## Read this first

How sources are marked: each numbered step ends with the pages it came from, such as ([C], [I]). **⚠ Unverified:** (the compendium's marker) means no page we read confirmed the sentence; confirm it at set-up, then replace the mark with the page you checked. Where a compendium page already states a fact, this runbook links it and does not repeat it. Option names below are the Python SDK's; the TypeScript names differ in case (`allowedTools`, `permissionMode`) ([C]).

Checked 2026-11-16 by the author against the pages listed. Every claim was checked again on 2026-11-16 by a second reader; the results are in the [verification log](verification-log.md).

Pages used:

- [A] [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview.md)
- [B] [How the agent loop works](https://code.claude.com/docs/en/agent-sdk/agent-loop.md)
- [C] [Configure permissions](https://code.claude.com/docs/en/agent-sdk/permissions.md)
- [D] [Intercept and control agent behavior with hooks](https://code.claude.com/docs/en/agent-sdk/hooks.md)
- [E] [Agent Skills in the SDK](https://code.claude.com/docs/en/agent-sdk/skills.md)
- [F] [Connect to external tools with MCP](https://code.claude.com/docs/en/agent-sdk/mcp.md)
- [G] [Hosting the Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting.md)
- [H] [Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment.md)
- [I] [Agent SDK reference, Python](https://code.claude.com/docs/en/agent-sdk/python.md)
- [J] [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention.md)
- [K] [Plugins in the SDK](https://code.claude.com/docs/en/agent-sdk/plugins.md)
- [L] [Set up Claude Code (local mode) for a HIPAA-ready organization](https://code.claude.com/docs/en/hipaa-setup.md)

## Inputs you need

The engagement has already decided these for the task. Do not start without all of them, written in the customer's folder under `engagements/`.

- **Who it runs as.** One Claude API key, held by the Runner owner in a secrets manager, plus a credential for each source system the task touches (a service account, or a per-user token fetched for the run). The runner has no vault; where each credential is kept is decided in step 7.
- **Autonomy level and ceiling.** The level it starts at and the highest it may reach, from [06](../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation). At level 4 nobody can answer a prompt.
- **Data class and retention.** The class Compliance set. Hosted agent runtimes are ruled out for some classes ([10](../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt)). **⚠ Unverified:** whether the Agent SDK is covered by ZDR or HIPAA; compendium [05](../../docs/compendium/05-decision-matrix.md) marks it unverified and none of the pages listed below names the Agent SDK in its ZDR or HIPAA text. Ask the Anthropic account team in writing before this runner touches ZDR or PHI data.
- **Connectors and each tool's permission.** Each MCP server (its URL and transport) and, for each tool, one of: left out, needs approval, or allowed. Include the built-in tools such as `Read`, `Write` and `Bash`.
- **What starts a run.** A webhook from a source system, a schedule (cron expression and timezone), or a chat bot message. The customer's IT names who runs the trigger host.
- **Memory on or off.** The SDK pages we read describe no memory store, only `CLAUDE.md` files and auto memory on the container's disk, which a restart loses and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` turns off ([G], [02](../../docs/compendium/02-persona.md#memory)). If on, name where it lives and which parts are read-only.
- **The persona's system-prompt form.** The text, written from the persona template in [02](../../docs/compendium/02-persona.md#a-persona-template-our-recommendation), and whether it replaces or extends the default prompt.
- **The skill that holds the task's instructions.** Its folder, already evaluated.

## Before you start

- Python 3.10 or later for the Python SDK, or Node.js 18.14 or later for the TypeScript SDK ([G]).
- A container image per task, with 1 GiB RAM, 5 GiB disk and 1 CPU per agent as a starting point; measure before you trust it ([G]).
- Outbound HTTPS to `api.anthropic.com` from the container, and to each MCP server the task uses ([G]).
- A place for the governance log, decided with the customer's IT ([15](../../docs/compendium/15-governance-and-performance.md#where-the-log-lives-settle-it-with-each-customer)), and a dedupe store for step 13.
- The Agent SDK spawns a `claude` CLI subprocess that owns a shell, a working directory and session files on disk ([G]). Treat the container as the security boundary ([H]).

## Steps

### Build the runner

1. Pin the SDK package version in the lockfile. The SDK bundles a native Claude Code binary pinned to the package version, so updating the SDK updates the binary; take patch releases, and read the changelog before a minor. Pin the model in the options too (`model=`, a full model name). ([G], [I])
2. Put the task's skill in `.claude/skills/` in the working directory and load it. Setting `setting_sources` without `"user"` and `"project"` stops skills loading. ([E])
   ```python
   options = ClaudeAgentOptions(
       cwd=os.getcwd(),                      # .claude/skills/ here or in a parent directory
       setting_sources=["user", "project"],  # Load skills from filesystem
       skills="all",                         # Let Claude invoke every discovered skill
       allowed_tools=["Read", "Write", "Bash"],
   )
   ```
   Sample from [E]; replace `"all"` with the one skill's name in a list, as in `ClaudeAgentOptions(skills=["pdf", "docx"])` ([E]), and replace `allowed_tools` as in step 4.
3. Pass the persona text as `system_prompt`: a plain string, `{"type": "custom", "prompt": "..."}`, or `{"type": "file", "path": "..."}` for a long prompt; `{"type": "preset", "preset": "claude_code"}` keeps Claude Code's own prompt. ([I])
4. List only the tools the task needs. `allowed_tools` pre-approves; it does not restrict. Unlisted tools fall through to `permission_mode`, so also set `permission_mode="dontAsk"` (deny instead of prompting), and put tools you must hide in `disallowed_tools` by bare name. ([C], [I])
5. Hold each tool at the autonomy level. ([C], [D])
   - Level 0 or 1: only read tools in `allowed_tools`; every write tool in `disallowed_tools`; mode `dontAsk`.
   - Level 2: leave the gated tool out of `allowed_tools` (an allow rule approves a call before `can_use_tool` runs) and pass a `can_use_tool` callback that asks a person; it runs only when the flow falls through to a prompt, never in `dontAsk` ([C], [I]).
   - Level 3: allowlisted tools in `allowed_tools`; the rest go to the callback; a `PreToolUse` hook enforces limits, because a hook deny applies even in `bypassPermissions` and hooks run for pre-approved calls ([C], [D]).
   - Level 4: `allowed_tools` plus `dontAsk` only; nothing may ask. Never use `bypassPermissions`: it approves unlisted tools ([C], [06](../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level)).
6. Declare each MCP server in `mcp_servers` (a URL and `type` of `http` or `sse`, or a command), set `strict_mcp_config=True` so project `.mcp.json` files and claude.ai connectors are ignored, and allow tools by their `mcp__<server>__<tool>` names. ([F], [I])
   ```python
   options = ClaudeAgentOptions(
       mcp_servers={"remote-api": {"type": "sse", "url": "https://api.example.com/mcp/sse",
                                   "headers": {"Authorization": f"Bearer {os.environ['API_TOKEN']}"}}},
       allowed_tools=["mcp__remote-api__*"],
   )
   ```
   Sample from [F]. Use exact tool names for level 2 and 3 instead of `*`.
7. Keep credentials out of the agent. The subprocess reads `ANTHROPIC_API_KEY` from its environment, supplied from the secrets manager; or set `ANTHROPIC_BASE_URL` to a proxy that injects the key outside the container. For source systems, call a tool or MCP server that runs outside the agent's boundary and holds the credential, or route traffic through an egress proxy that injects it and keeps an allowlist. A per-user token is fetched by the runner for this one run and passed in the server's `headers` or `env`. ([G], [H], [F])

### Log and bound the run

8. Write the governance log with hooks. Register `PostToolUse` and `PostToolUseFailure` callbacks; each appends one metadata-only record (when, session, tool, outcome, record IDs) to our log, using the fields in the [twin-governance plugin](../plugins/twin-governance/README.md) and the design in [15](../../docs/compendium/15-governance-and-performance.md#one-governance-log-for-all-twins-our-recommendation). Return `{}` so the call is unchanged. ([D])
   ```python
   options = ClaudeAgentOptions(
       hooks={"PostToolUse": [HookMatcher(hooks=[log_tool_call])]}
   )
   ```
   Pattern from [D] (`hooks={"PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[protect_env_files])]}`); `log_tool_call(input_data, tool_use_id, context)` is ours. A plugin loaded by local path through the `plugins` option brings its hooks, `hooks/hooks.json` included ([K]), so the twin-governance plugin can be loaded instead of the callback; either way confirm one row appears in "Check it worked".
9. Export traces as well. Set `CLAUDE_CODE_ENABLE_TELEMETRY=1`, `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` (needed for traces only), `OTEL_TRACES_EXPORTER=otlp` and the endpoint at container level; prompt text and tool inputs are off by default. ([G])
10. Bound every run. Set `max_turns` (the SDK has no top-level session timeout) and `max_budget_usd`, leave headroom because the cost estimate can pass the cap, and branch on the `ResultMessage` subtype: `success`, `error_max_turns`, `error_max_budget_usd`. Treat anything but `success` as a failed run in our log. ([G], [B], [I])

### Host and trigger

11. One session per container. Build a one-shot entrypoint that reads the task from the `TASK_PROMPT` environment variable, calls the SDK and exits; start a new container for each task. (Our recommendation) Never share a container between customers; if sessions must share one, set `setting_sources=[]`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, a per-tenant `CLAUDE_CONFIG_DIR` and `cwd`. ([G])
12. Isolate the container: egress through a proxy with a domain allowlist, credentials injected outside, requests logged. ([G], [H])
13. Webhook trigger, which we build. The receiver (a) verifies the source system's signature, (b) writes the source event's own ID into our dedupe store with a unique key before doing anything else, (c) if the key exists, answers 2xx and stops, (d) otherwise starts the container with `TASK_PROMPT` holding only the record ID, (e) stores the container or run ID next to the event ID, (f) removes the dedupe row if the start failed so a retry can run. Add a nightly reconciliation, because the SDK pages we read describe no replay of a missed event ([06](../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level)). ([G]) **⚠ Unverified:** the SDK pages describe no built-in dedupe or event intake; confirm by reading the changelogs ([A]).
14. Cron or bot trigger. The scheduler is the customer's own; the SDK pages describe none ([A]). A chat bot dedupes on the platform's message ID with the same rule as step 13. The long-running pattern (`ClaudeSDKClient`) fits a bot; the one-shot pattern fits cron and webhooks. ([G])
15. Know the release status. Compendium [05](../../docs/compendium/05-decision-matrix.md) marks the Agent SDK's release status unverified, and the pages listed here state no release status for it. **⚠ Unverified:** release status; confirm on the SDK changelogs ([A]) and re-read them before each upgrade. The bundled binary moves with the package, so retest after any version change ([G]).

## Check it worked

Run by the **Partner integration engineer**, with the **Business owner** reading the result. About 10 minutes.

1. Start the container through the real trigger on a test record, with the prompt "Read record X and summarize it." Expected: the `ResultMessage` subtype is `success`, the summary matches the record, and the governance log holds one row for the read with a record ID and no content. ([B], [D])
2. Start a second container asking for a write the autonomy level does not allow. Expected at level 0 to 2: no write reaches the source system (under `dontAsk` the call is denied; at level 2 the callback refuses it) and the record is unchanged; the log shows no successful write row. ([C])
3. If the trigger is an event, send the same event again. Expected: no second container and one dedupe row. ([G])
4. Check that the run's cost stayed under `max_budget_usd`. ([B])

## Hand over

Record in the customer's folder under `engagements/<customer>/`: the pinned SDK version and model name; the image name and digest; the skill version; the autonomy level, ceiling and who may raise it; the tool allow and deny lists; where each credential is kept and its rotation date; the trigger rule; the dedupe store; where the governance log lives; the turn and budget caps; the date of the last check. No secrets go in the folder.

The **Runner owner** owns the container, the API key and the log pipeline after set-up; the **Business owner** owns autonomy promotions. To stop a run, stop its container; to stop a trigger, disable the schedule or the receiver; to retire the task, revoke its credentials and delete its API key. ([G])

## What can go wrong

- **A tool ran that nobody approved.** `allowed_tools` does not restrict, and `bypassPermissions` approves unlisted tools ([C]). Re-check steps 4 and 5.
- **The skill is not found.** `setting_sources` omitted `"user"` or `"project"` ([E]).
- **A gated tool never reaches the callback.** It is also in `allowed_tools` ([I]).
- **A run never ends.** There is no session timeout; `max_turns` is unset ([G]).
- **A run stops with no answer.** Its subtype is `error_max_turns` or `error_max_budget_usd`, and the `result` field is empty ([B]).
- **The log has gaps.** A container restart loses local transcripts; send the log to our system, not the container's disk ([G]).
- **Two containers for one event.** The dedupe row was written after the start, or removed too early (step 13).
- **The customer needs ZDR or PHI.** A session on a Claude Console API key is not eligible for the HIPAA configuration (compendium [10](../../docs/compendium/10-sensitive-data.md#what-hipaa-covers)), and the Agent SDK's ZDR cover is unverified (Inputs); the API data-retention page says Claude Code is not covered under HIPAA readiness ([J]), and the HIPAA setup page lists a session on a Claude Console API key, as this runner uses, as not eligible for the HIPAA configuration ([L]); see also [10](../../docs/compendium/10-sensitive-data.md#what-hipaa-covers). Get the answer from Anthropic in writing before the runner touches PHI.
