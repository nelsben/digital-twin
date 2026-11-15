# Runbook: Salesforce hosted MCP connector, per-user OAuth

## What this is

Every deal-team skill reads the CRM through Salesforce's hosted MCP server. This runbook takes the CRM admin, the Claude org Owner and our integration engineer through adding it once, correctly, for a pilot at autonomy level 1 (read only). It is generic: replace every `<placeholder>` with the customer's value.

Roles use the names in [03-stakeholders](../../docs/playbook/03-stakeholders.md):

| Name used here | Role in 03-stakeholders |
|---|---|
| **CRM admin** | Source-system admin (the Salesforce admin) |
| **Claude org Owner** | Technical owner (Director of IT), or the Backup Owner |
| **Partner integration engineer** | Integration engineer (partner role) |

## Read this first

> **Warning: the authentication type cannot be changed after the connector is added.** In Claude, "You can't change authentication settings after you add a connector. That covers OAuth credentials and request headers. To change them, remove the connector and add it again with the new details. Members then need to reconnect." ([Add a connector that isn't in the directory](https://claude.com/docs/connectors/custom/add-unlisted.md)). Settle every value in steps 1 to 4 before step 6. A wrong choice means removing the connector and every member reconnecting.

How sources are marked in this runbook:

- Each step ends with the page it came from.
- **Unverified** means the page did not confirm it. We could not read Salesforce's own developer pages (the fetches returned HTTP 403 on 2026-11-14), so Salesforce-side detail comes from Anthropic's Salesforce page, which relays Salesforce's steps. Confirm every unverified item against Salesforce's current docs before you rely on it, and replace the mark with the page you checked.

Pages used:

- [A] [Connect to Salesforce (Claude Desktop, third-party)](https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md)
- [B] [Add a connector that isn't in the directory](https://claude.com/docs/connectors/custom/add-unlisted.md)
- [C] [Authentication for connectors](https://claude.com/docs/connectors/building/authentication.md)
- [D] Salesforce, [Activate MCP Servers](https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/activate-mcp-servers.html) and [Create an External Client App](https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/create-external-client-app.md). Named by [A] and found by search, **not read** by us (403).
- [E] [Compendium 11, Connectors](../../docs/compendium/11-connectors.md) and [06, Autonomy](../../docs/compendium/06-autonomy.md)

## 1. Prerequisites

| # | Check | Who | Source |
|---|---|---|---|
| 1.1 | The customer's Salesforce edition supports hosted MCP servers. The compendium records Enterprise Edition or higher, from a secondary source. | CRM admin | [E]; **unverified** against Salesforce |
| 1.2 | If the org is on Salesforce Government Cloud, confirm with Salesforce that hosted MCP servers are available there. | CRM admin | [A] |
| 1.3 | The Claude org is Team or Enterprise, and the person adding the connector is an Owner (or, on Enterprise, holds a custom role that manages the organization's libraries). Members without one of these roles cannot add a custom connector. | Claude org Owner | [B] |
| 1.4 | Decide the sandbox-first order: do steps 2 to 7 in a Salesforce sandbox, then repeat in production. | Partner integration engineer | [A] (sandbox values) |
| 1.5 | Name the two pilot test users for step 9 and confirm they sit on opposite sides of a soft wall in Salesforce (different roles or sharing rules, for example). | CRM admin, with the Compliance role | [E] ([14](../../docs/compendium/14-private-equity.md)) |
| 1.6 | Discovery item E6 is answered: can the customer allowlist Anthropic's range `160.79.104.0/21`? Close it before step 6; see step 8. | Claude org Owner, with Security | [C], [playbook discovery](../../docs/playbook/02-discovery.md) |

## 2. Turn on and activate the server in Salesforce

**Who: CRM admin.**

1. In Setup, turn on **Enable MCP Service**.
2. In Setup, enter `MCP Servers` in Quick Find, open **MCP Servers** under **API Catalog**, click the **Salesforce Servers** tab, and activate the **headless-360** server.
3. Until the server is active, Claude cannot connect to it, even when a user's Salesforce sign-in succeeds.

Source: [A] step 1, which points to [D] Activate MCP Servers. Which tools headless-360 exposes, and which of them write, is **unverified**; step 7 lists them from the connector itself.

## 3. Create the External Client App

**Who: CRM admin.** Salesforce's hosted MCP servers use an External Client App, and the playbook names this as the source-system admin's job ([03-stakeholders](../../docs/playbook/03-stakeholders.md)). Use the settings below.

| Setting | Value | Source |
|---|---|---|
| OAuth scopes | `mcp_api` and `refresh_token` | [A] |
| PKCE | Required | [A] |
| Access tokens | Issued as JSON Web Tokens (JWTs) | [A] |
| OAuth policy | Lets users self-authorize (per-user OAuth, no shared integration user) | [A] |
| Callback URL for claude.ai | `https://claude.ai/api/mcp/auth_callback` | [C] |
| Callback URL for Claude Code (only if the pilot uses it with this client) | A loopback redirect on any port, such as `http://localhost/callback` and `http://127.0.0.1/callback`. **Unverified** that Salesforce accepts a port-less loopback entry. | [C] |

Notes:

- [A] gives the callback `http://127.0.0.1:53280/callback` for **Claude Desktop's own managed-configuration route**. That is a different route from the claude.ai connector added in step 6. Use the claude.ai callback above for this runbook. Whether one External Client App may list several callback URLs is **unverified**.
- Copy the app's **Consumer Key**; it is the client ID. [A] says PKCE needs no client secret for Claude Desktop. Whether Salesforce also needs a secret for the claude.ai route is **unverified**; record the answer here.
- Salesforce states that a new External Client App can take up to 30 minutes to become available (third-party summary of [D]; **unverified**). Wait before testing.
- Users need permission to use MCP servers and the External Client App. The exact permission set or profile setting is **unverified**; the CRM admin confirms it in [D].
- The wall: because tokens are per user, each user's twin has only that user's Salesforce permissions. Do not grant the app, or any user, more access than their role has today ([E], [14](../../docs/compendium/14-private-equity.md)).
- Write the Consumer Key in the engagement's secrets record, not in this file or the repo.

## 4. Choose per-user OAuth (the decision you cannot undo)

**Who: Claude org Owner, with the partner integration engineer.** Confirm in writing before step 6.

- Authentication: **Sign in now**, so each user signs in through Salesforce's OAuth flow. Do not choose **No sign-in**, and do not use **Request headers**. Request headers hold one shared credential for everyone, which would make every twin act as one identity and break the wall. ([B], [C])
- OAuth client: **Use your own OAuth client**, with the Consumer Key from step 3. Claude's other options, "Use Claude's published identity" (CIMD) and "Register automatically" (DCR), need the server's authorization server to support them. Whether Salesforce's does is **unverified**, and [A] uses a pre-registered client ID, so this runbook takes that route. ([B], [C], [A])
- Leave the client secret blank unless Salesforce requires one ([B]). Whether it does is **unverified**; see step 3.
- Server URL: `https://api.salesforce.com/platform/mcp/v1/platform/headless-360` for production, and `https://api.salesforce.com/platform/mcp/v1/sandbox/platform/headless-360` for a sandbox ([A]).
- Authorization server: `https://login.salesforce.com` by default, the org's My Domain URL (for example `https://<mydomain>.my.salesforce.com`) to send users to its own login page, or `https://test.salesforce.com` for a sandbox. Exactly one ([A]). The Claude dialog may not show a field named "Authorization server"; the server's metadata normally supplies it. **Unverified** for the claude.ai dialog, because [A] describes the Desktop console.
- Do not use the Claude Desktop route in [A] (the Desktop 3P Connectors page, the `salesforce-h360` name and the Salesforce plugin marketplace) for the pilot unless the customer runs Claude Desktop under managed configuration. It is a separate route; the compendium's per-user, claude.ai-based design uses step 6.

## 5. Plan the tool permissions (autonomy level 1)

**Who: Claude org Owner, with the partner integration engineer.**

At autonomy level 1 ("Draft") the twin prepares work and a person acts. The control is "Write tools Blocked, or left out of the role plugin" ([E], [06](../../docs/compendium/06-autonomy.md)). Claude's three settings per tool are **Always allow**, **Needs approval** and **Blocked** ([B], [E]). For this pilot:

| Tool kind | Setting at level 1 |
|---|---|
| Read tools (query, get, describe) | **Always allow** |
| Any tool that creates, updates or deletes | **Blocked** |
| Anything you cannot classify | **Blocked** until the CRM admin classifies it |

Two defences, not one: the Claude setting hides write tools from the twin, and Salesforce itself should deny writes where the role allows it. Whether the hosted server can be limited to read at the Salesforce side (a read-only scope, or a read-only permission set for pilot users) is **unverified**. `mcp_api` is the only scope [A] lists. Raising a tool to **Needs approval** is a level 2 decision made on scorecard evidence, not in this runbook.

## 6. Add the connector in the Claude org

**Who: Claude org Owner.** Only after steps 2 to 5 are settled and the E6 answer is known.

1. Go to **Organization settings > Connectors**, select **Add**, then **Custom**. If Claude asks for the connector type, choose **Web**.
2. Enter a name (for example `Salesforce`) and the server URL from step 4. Click **Continue** if shown.
3. Set **Authentication** to **Sign in now** and **OAuth client** to **Use your own OAuth client**, with the Consumer Key. Keep any option marked **Detected** unless the server documentation says otherwise.
4. Check every value against step 4 one last time, then click **Add**.

Source: [B]. The exact dialog layout varies by organization ([B]).

## 7. Set tool permissions, then connect

1. **Claude org Owner:** open the connector, list its tools, and set each tool per step 5. The partner integration engineer records the tool list and each setting, with the date, in the engagement's connector plan. Tool lists can change after you approve them, so the Owner reviews this list again at each quarterly access review ([E] review checklist).
2. **Each pilot user:** open **Customize > Connectors**, find the connector with the **Custom** label, click **Connect** and sign in to Salesforce with their own account. ([B])
3. **Partner integration engineer:** confirm the sign-in completes with each user's own identity. If it fails with a callback or "client" error, re-check the callback URL and Consumer Key in step 3 and the 30-minute propagation note. If the connector cannot be reached, go to step 8 and the [connector troubleshooting page](https://claude.com/docs/connectors/building/troubleshooting.md) (not read by us).

## 8. IP allowlist (discovery E6)

**Who: Claude org Owner decides with Security; CRM admin applies it in Salesforce.**

- Anthropic's outbound traffic to a connector server comes from `160.79.104.0/21` ([C]). The compendium says to allow this range on both the server and the authorization server, and nothing broader ([E]). Claude's discovery requests to the authorization server come from the same range, so a firewall or WAF in front of the login host can break sign-in even when the MCP server is reachable ([C]).
- If Salesforce or the External Client App restricts IPs for this app, add `160.79.104.0/21` there. Where the setting lives (the External Client App's OAuth policy IP relaxation, or Setup network access trusted ranges) and whether `api.salesforce.com` needs any change are **unverified**. Confirm in [D] and Salesforce's network access docs.
- Check Anthropic's [published IP address reference](https://platform.claude.com/docs/en/api/ip-addresses) for the current range before entering it ([C] links it).
- If the customer cannot allowlist the range, stop: the remote connector will not work, and the answer to E6 changes the design (see the private-network options in [E]).
- Devices that use the Claude Desktop route in [A] need outbound HTTPS to `github.com`, `api.salesforce.com` and the Salesforce login host ([A]). That is separate from the allowlist above.

## 9. Test: two users on either side of a soft wall

**Who: CRM admin runs the Salesforce checks; partner integration engineer runs the Claude checks; the two test users from step 1.5 sign in.** Run in the sandbox first, then in production.

Setup (CRM admin):

1. Pick record A, visible by Salesforce rules only to user 1's side of the wall, and record B, visible only to user 2's side. Use real or test opportunities with distinct, harmless names.
2. In Salesforce, signed in as each user directly, confirm that user 1 can open A and not B, and user 2 the reverse. If this fails, fix Salesforce sharing first; the connector cannot be stricter than the source system ([E], [14](../../docs/compendium/14-private-equity.md)).

Checks (each user connected as in step 7, in their own Claude session):

| # | Do this | Pass if |
|---|---|---|
| 9.1 | User 1 asks Claude to find record A by name | User 1 sees A |
| 9.2 | User 1 asks Claude to find record B by name and by its id | User 1 sees nothing about B (no record, no field values) |
| 9.3 | User 2 repeats 9.1 and 9.2 with the roles swapped | User 2 sees B and nothing about A |
| 9.4 | Each user asks Claude to list opportunities | Each list contains only that user's own side |
| 9.5 | Each user asks Claude to change a field on a visible record | Claude cannot: write tools are Blocked (step 5) |

Record the date, both users, the records, and each result in the engagement's wall-test notes. The wall test must pass before the pilot starts. A single failure in 9.2 to 9.4 means stop and fix the cause (sharing rules, role hierarchy, or a shared identity somewhere), then repeat the whole table.

## 10. Hand over

**Who: partner integration engineer to CRM admin and Claude org Owner.** Hand over the recorded Consumer Key location, the tool settings from step 7, the E6 answer, the wall-test record, and the list of **unverified** items still open. Offboarding note: a removed user's connector token works until it expires, so the CRM admin also revokes the user's Salesforce session ([E]).

## Open items to verify (all marked unverified above)

1. Salesforce editions and any extra licences for hosted MCP servers.
2. Which tools headless-360 exposes, and which write.
3. Whether the External Client App accepts several callback URLs, and a port-less loopback entry for Claude Code.
4. Whether Salesforce needs a client secret for the claude.ai route, and whether it supports CIMD or DCR.
5. The Salesforce permission a user needs to use MCP servers and the External Client App.
6. Whether read-only can be enforced on the Salesforce side.
7. Where the IP restriction lives in Salesforce and whether `api.salesforce.com` needs a change.
