# Runbook: Set up a task on Managed Agents (hosted, with a self-hosted section)

## What this is

A twin task that runs with no person in the chat (a nightly scan, a reaction to a record change) needs a hosted runtime. This runbook takes our integration engineer and the customer's Director of IT from the engagement's decisions for one task to a working Managed Agents agent: the agent, its environment, its credentials, the thing that starts a run, and a test that proves a read works and a write is refused. Which runtime to pick is already decided; see [05](../../docs/compendium/05-decision-matrix.md). This runbook only sets it up. For a task that stays inside Claude chat or Claude Code, use a client runbook instead.

Roles use the names in [03-stakeholders](../../docs/playbook/03-stakeholders.md):

| Name used here | Role in 03-stakeholders |
|---|---|
| **Console owner** | Technical owner (Director of IT): holds the Claude Console organization, creates the API key, owns spend |
| **Partner integration engineer** | Integration engineer (partner role): builds and tests everything below |
| **Business owner** | Business owner (RevOps manager or the role's leader): confirms the task and its autonomy level |
| **Security** | Security (CISO or security engineer): reviews tools, credentials and the receiver |
| **Compliance** | Compliance / legal: confirms the data class and retention |
| **Source-system admin** | Source-system admins (for example the Salesforce admin): creates the least-privilege account the credential belongs to |

## Read this first

How sources are marked: each numbered step ends with the pages it came from, such as ([B], [C]). **⚠ Unverified:** (the compendium's marker) means no page we read confirmed the sentence; confirm it at set-up, then replace the mark with the page you checked. Where a compendium page already states a fact, this runbook links it and does not repeat it. Managed Agents is in beta ([A]), so re-read the pages before each engagement.

Checked 2026-11-16 by the author against the pages listed. Every claim was checked again on 2026-11-16 by a second reader; the results are in the [verification log](verification-log.md).

Pages used:

- [A] [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview)
- [B] [Agent setup](https://platform.claude.com/docs/en/managed-agents/agent-setup)
- [C] [Permission policies](https://platform.claude.com/docs/en/managed-agents/permission-policies)
- [D] [MCP connector](https://platform.claude.com/docs/en/managed-agents/mcp-connector)
- [E] [Skills](https://platform.claude.com/docs/en/managed-agents/skills)
- [F] [Environments](https://platform.claude.com/docs/en/managed-agents/environments)
- [G] [Vaults](https://platform.claude.com/docs/en/managed-agents/vaults)
- [H] [Sessions](https://platform.claude.com/docs/en/managed-agents/sessions)
- [I] [Events and streaming](https://platform.claude.com/docs/en/managed-agents/events-and-streaming)
- [J] [Session operations](https://platform.claude.com/docs/en/managed-agents/session-operations)
- [K] [Scheduled deployments](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments)
- [L] [Webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks)
- [M] [Memory](https://platform.claude.com/docs/en/managed-agents/memory)
- [N] [Reference](https://platform.claude.com/docs/en/managed-agents/reference)
- [O] [Self-hosted Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/self-hosted)
- [P] [Differences from the hosted service](https://platform.claude.com/docs/en/managed-agents/self-hosted/differences)
- [Q] [Data and access in self-hosted Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/self-hosted-data-and-access)
- [R] [Choosing an agent environment](https://platform.claude.com/docs/en/managed-agents/choosing-an-environment)
- [S] [Budgets](https://platform.claude.com/docs/en/managed-agents/budgets)
- [T] [Session observability](https://platform.claude.com/docs/en/managed-agents/session-observability)
- [U] [Tools](https://platform.claude.com/docs/en/managed-agents/tools)

## Inputs you need

The engagement has already decided these for the task. Do not start without all of them, written in the customer's folder under `engagements/`.

- **Who it runs as.** One Claude API key (held by the Console owner, in a secrets manager) and one vault of credentials per end user or per service account. The task acts as whoever the vault credential belongs to, not as a person in a chat.
- **Autonomy level and ceiling.** The level it starts at and the highest it may reach, from [06](../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation). At level 4 nobody can answer a prompt, so every approval is decided in advance.
- **Data class and retention.** The class Compliance set, and what follows: hosted Managed Agents keeps session transcripts until you delete them and is not eligible for ZDR or HIPAA ([A]). See [10](../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt). If the class needs ZDR or PHI, stop and use the Self-hosted section.
- **Connectors and each tool's permission.** Each MCP server (its URL) and, for each tool, one of: left out, needs approval, or allowed. Include the built-in tools.
- **What starts a run.** An API call from our code, a schedule (cron expression and timezone), or an event from a source system (which event, from which system).
- **Memory on or off.** If on: which stores, and which are read-only reference stores ([02](../../docs/compendium/02-persona.md#memory)).
- **The persona's system-prompt form.** The text that becomes the agent's `system` field, written from the persona template in [02](../../docs/compendium/02-persona.md#a-persona-template-our-recommendation).
- **The skill that holds the task's instructions.** Its folder, already evaluated, ready to upload as a zip.
- **A per-run spending cap**, in US dollars, set by the Console owner.

## Before you start

- A Claude Console workspace for this customer, and an API key that can reach it. Vaults and credentials are workspace-scoped, so any key with workspace access can use them ([G]). (Our recommendation) Give each trust level its own workspace.
- Every Managed Agents request carries the beta header `managed-agents-2026-04-01`; the SDKs add it for you ([A]). The samples below use `curl` and show the headers.
- A place for our own log and our own dedupe store (steps 14 and 16). Decide it with the customer's IT per [15](../../docs/compendium/15-governance-and-performance.md#where-the-log-lives-settle-it-with-each-customer).
- Limits that shape the design: 300 create requests and 1,200 read requests per minute ([N]); up to 20 credentials per vault ([G]); up to 8 memory stores per session ([M]); up to 1,000 scheduled deployments per organization ([K]).

## Steps

### Environment, skill and agent

1. Create the environment with limited networking and list only the hosts the task needs. A create request that omits `networking` gets `unrestricted`, so always set it. ([F])
   ```bash
   curl -fsS https://api.anthropic.com/v1/environments \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2026-10-21" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     -H "content-type: application/json" \
     -d '{"name": "python-dev","config": {"type": "cloud","networking": {"type": "limited", "allow_package_managers": true}}}'
   ```
   Sample from [F]; add `allowed_hosts` and `allow_mcp_servers` as the task needs ([F]).
2. Upload the task's skill as a zip. The response gives the `skill_*` ID. ([E])
   ```bash
   curl -X POST "https://api.anthropic.com/v1/skills" \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2026-10-21" \
     -F "files[]=@example_skill.zip"
   ```
3. Create the agent: pin the model, put the persona text in `system`, attach the skill, and declare the tools and MCP servers. Keep the returned `id` and `version`. ([B], [E])
   ```bash
   curl -fsSL https://api.anthropic.com/v1/agents \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2026-10-21" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     -H "content-type: application/json" \
     -d '{"name": "Coding Assistant","model": "claude-opus-5-5","system": "You are a helpful coding agent.","tools": [{"type": "agent_toolset_20260401"}]}'
   ```
   Sample from [B]. Replace the name, model and `system`; add the skill as `"skills": [{"type": "custom", "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv", "version": "latest"}]` ([E]). (Our recommendation) Give the skill a fixed `version` instead of `"latest"` so a skill edit cannot change a running task; `version` pins a specific version or uses `latest` ([E]).
4. Switch off every built-in tool the task does not need. The agent toolset defaults to `always_allow`, so an unlisted tool runs without asking. ([C], [B])
   ```json
   {"type": "agent_toolset_20260401","default_config": { "enabled": false },"configs": [{ "name": "bash", "enabled": true },{ "name": "read", "enabled": true }]}
   ```
   Sample from [U], cut to two tools; list only the tools the task uses.
5. Add each MCP server in `mcp_servers` and a matching `{"type": "mcp_toolset", "mcp_server_name": "github"}` in `tools`; to allow only some tools, set `"default_config": { "enabled": false }` and enable them one by one in `configs`. Do not put credentials here; they come from the vault (step 8). ([D])
6. Hold each tool at the task's autonomy level with a permission policy; the policies are `always_allow`, `always_ask` and `auto`, so level 1 means the write tool is switched off with `"enabled": false`. ([C], [D])
   - Level 0 or 1: read tools enabled; write tools `"enabled": false`.
   - Level 2: write tools `{"permission_policy": {"type": "always_ask"}}`; the session pauses until someone sends `user.tool_confirmation` with `"allow"` or `"deny"` ([C], [I]).
   - Level 3: allowlisted tools `always_allow`; every other write tool `always_ask`.
   - Level 4: only `always_allow` tools are enabled; anything that would ask is disabled, because an unattended run cannot answer ([C], [06](../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level)). MCP toolsets default to `always_ask`, so each allowed MCP tool needs an explicit `always_allow` ([C]).
   - A fourth setting, `auto`, lets the server judge each call ([C]). **⚠ Unverified:** how it maps to our ladder; do not use it until a page or a test run shows it.
7. Run `GET /v1/agents/$AGENT_ID/versions` and write the version number in the engagement record. The agent's `version` goes up each time an update changes it; an update with no change makes none. ([B])

### Credentials

8. Create a vault for the end user or service account and add one credential per MCP server URL. A credential is keyed by `mcp_server_url`, is unique per vault, and its secret fields are write-only. ([G])
   ```bash
   curl --fail-with-body -sS https://api.anthropic.com/v1/vaults \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2026-10-21" \
     -H "anthropic-beta: managed-agents-2026-04-01" \
     -H "content-type: application/json" \
     -d '{"display_name": "Alice","metadata": {"external_user_id": "usr_abc123"}}'
   ```
   Sample from [G]; use a role-based display name, not a person's name. Then `POST /v1/vaults/$VAULT_ID/credentials` with an `auth` block of type `mcp_oauth` or `static_bearer` ([G]).
9. For a per-user credential, our code runs the source system's own sign-in and posts the resulting token (and, for `mcp_oauth`, a `refresh` block) to the vault; Anthropic then refreshes the token. Map the vault to your user with `metadata`. ([G]) **⚠ Unverified:** whether Anthropic offers a hosted sign-in screen that obtains the first token; no page we read shows one. Ask the Anthropic account team.
10. Subscribe to `vault_credential.refresh_failed` (the webhook endpoint is step 16) so a dead token is noticed before a run fails. ([L], [G])

### Memory, if on

11. Create each memory store and attach it as a session resource. Mark every reference store `"access": "read_only"`; the default is `read_write`, and a prompt injection could write into a writable store. A memory is capped at 100 kB, a store at 10,000 memories; see also [02](../../docs/compendium/02-persona.md#memory). ([M])
    ```json
    {"type": "memory_store","memory_store_id": "'"$store_id"'","access": "read_only","instructions": "..."}
    ```
    Sample from [M]; the `instructions` text tells the agent what the store holds.

### Start a run

12. API call. Create a session with the agent, the environment, the vault and a per-run budget, and send the first message in `initial_events`. To pin the run to one agent version, pass `{"type": "agent", "id": "...", "version": 1}` instead of the ID string. ([H], [S])
    ```bash
    curl -fsSL https://api.anthropic.com/v1/sessions \
      -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2026-10-21" \
      -H "anthropic-beta: managed-agents-2026-04-01" -H "content-type: application/json" \
      -d '{"agent": "'"$AGENT_ID"'","environment_id": "'"$ENVIRONMENT_ID"'","vault_ids": ["'"$VAULT_ID"'"],"title": "..."}'
    ```
    Body from [G]; add `"initial_events": [{"type": "user.message","content": [{"type": "text","text": "..."}]}]` and `"budget": {"type": "limit","max_list_cost": {"amount": "125", "currency": "USD"}}` ([H]). A session that reaches its budget pauses ([S], [L]).
13. Scheduled deployment. Create it with the agent, environment, one initial `user.message` and a `schedule` of type `cron` with an `expression` and a `timezone`. Add `vault_ids` and a `budget`; the budget caps each run, not the total. ([K])
    ```bash
    curl --fail-with-body -sS "https://api.anthropic.com/v1/deployments?beta=true" \
      -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2026-10-21" \
      -H "anthropic-beta: managed-agents-2026-04-01" -H "content-type: application/json" \
      -d '{"name": "Weekly compliance scan","agent": "'"$AGENT_ID"'","environment_id": "'"$ENVIRONMENT_ID"'","initial_events": [{"type": "user.message", "content": [{"type": "text", "text": "Run the weekly compliance scan."}]}],"schedule": {"type": "cron","expression": "0 20 * * 5","timezone": "America/New_York"}}'
    ```
    Sample from [K]. A deployment runs one version of its agent and keeps it when the agent changes; to move it, update the deployment with the agent ID again. Actual start times shift by up to 15 percent of the interval (at least 5 seconds, at most 9 minutes). Missed triggers are not backfilled. Avoid 1 to 3 AM local time. ([K]) Check the next fire times in `schedule.upcoming_runs_at` ([K]).
14. Event. Anthropic offers no event trigger for sessions in the pages we read, so we build a small receiver. It (a) accepts the source system's event over HTTPS and verifies its signature, (b) writes the source event's own ID into our dedupe store with a unique key before doing anything else, (c) if that key already exists, answers 2xx and stops, (d) otherwise calls `POST /v1/sessions` with a `user.message` that carries only the record ID, (e) stores the returned session ID next to the event ID, and (f) deletes the dedupe row if the call failed so a retry can run. ([H], [L]) **⚠ Unverified:** whether session creation accepts an idempotency key; no page we read shows one, so the dedupe store is ours. Keep the message free of record content on private-equity work ([15](../../docs/compendium/15-governance-and-performance.md#one-governance-log-for-all-twins-our-recommendation)).
15. Make the repeat rule hold under a retry. The source system may send one event twice, and Anthropic's own webhooks make up to three delivery attempts with the same `event.id`; dedupe on it ([L]). Add a nightly reconciliation that lists the day's source events and sessions and starts the ones that are missing; a webhook event emitted while no endpoint subscribes to its type is never delivered later, and [06](../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level) says something has to reconcile. ([L])

### Log, versions and limits

16. Write the governance log in our own system, not in Anthropic's. Webhooks give up after three attempts, are not guaranteed to arrive in order, and "aren't a durable log" ([L]); [15](../../docs/compendium/15-governance-and-performance.md#what-each-source-records) says the same. Subscribe a webhook endpoint (HTTPS, port 443) to the session and deployment events, verify the signature, fetch the object by ID, and copy what [15](../../docs/compendium/15-governance-and-performance.md#one-governance-log-for-all-twins-our-recommendation) lists into the log. The live view is the event stream, `GET https://api.anthropic.com/v1/sessions/$SESSION_ID/events/stream?beta=true` with `-H "accept: text/event-stream"` ([I]). Stored session transcripts stay until you delete the session ([A], [J]). ([L], [I])
17. Pin versions. Start every production session from `{"type": "agent", "id": "...", "version": N}`; the plain agent ID string takes the latest version. Update the agent with the `version` you last read, so a second change at the same moment returns 409 instead of overwriting it. ([H], [B])
18. Know the release status. Managed Agents is in beta, "Anthropic might refine behaviors between releases", and the API version header is `anthropic-version: 2026-10-21`. Re-run "Check it worked" after any release you notice. ([A], [B])

## Self-hosted

Use this section only when the data class needs it. When it is required is in [05](../../docs/compendium/05-decision-matrix.md) and [10](../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt); this runbook does not restate it.

1. Get access. Request it through your Anthropic account team; if the customer's Console organization already has it, switch to that organization. The release archive carries an `operator-guide.md` for that version. ([O])
2. Know what runs where. Self-hosted sandboxes keep the service at Anthropic and move only tool execution to the customer. Self-hosted Managed Agents moves the service too: the customer runs `cma-server`, a PostgreSQL 16 or later database, and workers; the model runs at Anthropic or at a provider the customer chooses. ([O], [R])
3. Know what still reaches Anthropic. By default each model call sends the conversation so far, with tool inputs and results, to the Claude API, with the session, agent and environment IDs. The customer's own agreement sets that retention. ([O], [Q])
4. Plan for what the server lacks. It has no scheduled deployments (start sessions from the customer's scheduler), sends no webhooks (poll the event stream), and rejects `mcp_oauth` credentials (store a `static_bearer` token and refresh it yourself). ([P])
5. Repeat steps 1 to 12, 14, 15 and 17 against your own server, whose API is the same apart from [P]'s list. Replace step 13 with the customer's own scheduler and step 16's webhooks with polling the event stream. ([O], [P])

## Check it worked

Run by the **Partner integration engineer**, with the **Business owner** reading the result. About 10 minutes.

1. Start one run through the real trigger, on a test record, asking only for a read: "Read opportunity X and summarize it." Expected: the session ends `idle` with an `end_turn` stop, the summary matches the record, and the governance log has one read row with a record ID and no content. ([I], [J])
2. Start a second run that asks for a write the autonomy level does not allow. Expected at level 0 or 1: the agent says it has no such tool. At level 2: the session pauses with `session.status_idle` and `requires_action`; send `user.tool_confirmation` with `"result": "deny"` and see the source record unchanged. ([I], [C])
3. If the trigger is an event, replay the same source event once. Expected: no second session, and one row in the dedupe store. ([L])
4. Open the session in the Console viewer and confirm the cost is under the cap. ([T], [S])

## Hand over

Record in the customer's folder under `engagements/<customer>/`: the agent ID and pinned version; environment, vault, store and deployment IDs; the autonomy level, ceiling and who may raise it; the API key's owner and rotation date; the cron expression or the event rule; the dedupe store's location; where the governance log lives; the budget; the date of the last check. No secrets go in the folder.

The **Console owner** owns the agent, key, vault and spend after set-up; the **Business owner** owns autonomy promotions; the partner keeps the runbook current until hand-off ends. To stop a run, send `{"type": "user.interrupt"}` and wait for the session to go `idle` ([I], [J]); to pause a schedule, `POST /v1/deployments/$DEPLOYMENT_ID/pause?beta=true` ([K]). To retire the agent: pause or archive the deployment, archive sessions, then `POST /v1/agents/$AGENT_ID/archive`, which stops new sessions while running ones continue; delete the vault to revoke its credentials ([J], [K], [B], [G]).

## What can go wrong

- **A tool ran that nobody approved.** The agent toolset defaults to `always_allow` ([C]). Re-check step 4.
- **A level-4 run never finishes.** It is waiting on an `always_ask` confirmation nobody sent ([C], [I]).
- **The schedule stopped.** A failed trigger with an unrecoverable error pauses the deployment ([K]); check `deployment_runs` with `has_error=true`.
- **Two sessions for one event.** The dedupe row was written after the API call, or the receiver deleted it too early (step 14).
- **A webhook event never arrived.** Events are dropped after three failed attempts, and an endpoint can disable itself ([L]). Reconcile (step 15).
- **A run is cut off.** The budget was reached ([S]), or the create limit of 300 per minute was hit ([N]).
- **The customer needs ZDR or PHI.** Hosted Managed Agents is not eligible ([A]); see the Self-hosted section.
