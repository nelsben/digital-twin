# Runbook verification log

- **Date checked:** 2026-11-15
- **Checked by:** Claude Opus 5.5 (`claude-opus-5-5`), task SHA-21
- **Updated 2026-11-15 (OPS-24):** rows marked OPS-24 below were added or changed after the review; the summary counts above were not recomputed.
- **Runbooks:** [identity-devices-publishing.md](identity-devices-publishing.md), [salesforce-hosted-mcp.md](salesforce-hosted-mcp.md), [microsoft-365-connector.md](microsoft-365-connector.md)
- **Updated 2026-11-16 (OPS-59):** sections for the four runtime runbooks were added by a second reader, Claude Opus 5.5 (`claude-opus-5-5`); their rows are in the summary table below.

| Runbook | Confirmed | Corrected | Unverified | Total |
|---|---|---|---|---|
| identity-devices-publishing.md | 55 | 16 | 4 | 75 |
| salesforce-hosted-mcp.md | 34 | 11 | 12 | 57 |
| microsoft-365-connector.md | 44 | 8 | 7 | 59 |
| claude-code-scheduled-task.md | 44 | 2 | 6 | 52 |
| claude-tag-routine.md | 37 | 1 | 3 | 41 |
| managed-agents.md | 50 | 5 | 3 | 58 |
| agent-sdk-runner.md | 34 | 3 | 3 | 40 |
| hubspot-connector.md | 39 | 12 | 8 | 59 |

## How the check was done

- Every runbook was treated as untrusted. A source tag did not count as proof. Each numbered step, table row and factual product sentence was checked against the page it cites. Where there was no citation, or the citation did not support the claim, it was checked against the vendor's own docs.
- Accepted vendor domains: code.claude.com, platform.claude.com, claude.com/docs, support.claude.com and support.anthropic.com for Anthropic; help.salesforce.com, developer.salesforce.com and Salesforce's official GitHub for Salesforce; learn.microsoft.com for Microsoft; help.okta.com and developer.okta.com for Okta. Blogs, forums, search snippets and other third-party pages were not counted as confirmation.
- For the four runtime runbooks (OPS-59), the accepted domains were platform.claude.com, code.claude.com, claude.com (docs and connectors pages), support.claude.com, and github.com under the anthropics, anthropic-ai or modelcontextprotocol organisations.
- Exact strings (keys, menu paths, roles, scopes, URLs, IP ranges, file paths, registry keys, CLI commands) were compared character by character with the vendor page.
- Repo statements were checked against the branch: `starter-kit/settings/*.json`, [starter-kit/settings/README.md](../settings/README.md), `.claude-plugin/marketplace.json` and `starter-kit/plugins/twin-governance/hooks/`.
- **States.** Confirmed: the vendor page supports the claim, and the link is kept or added. Corrected: the runbook was changed to match the vendor page, and the link is given. Unverified: no accepted page confirmed it, so the runbook now carries the compendium's `**⚠ Unverified:**` marker ([Conventions](../../docs/compendium/README.md)) and words it as something to confirm at setup. Where two vendor pages disagree, the runbook also carries `**⚠ Conflict:**`.
- Changes are the smallest true change. No step was added, removed or reordered. Besides the rows below, three kinds of edit were made in all three runbooks: each "How sources are marked" sentence now names the `**⚠ Unverified:**` marker and links this log; existing plain **unverified** marks were rewritten to the marker; and new sources were appended to each source list ([S7] to [S14] in the identity runbook, [F] to [H] in the Salesforce runbook, [I] and [J] in the Microsoft 365 runbook).
- Rows that are our own design, not a product claim (for example the wall tests in Salesforce step 9 and Microsoft 365 step 8b, and the hand-over lists), were not counted.

## identity-devices-publishing.md

| Line or step | Claim | State | Source URL | Old wording → new wording (corrections) |
|---|---|---|---|---|
| 0.1 | SCIM needs Enterprise or Console; Team uses JIT | Corrected | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | Added: "or on Console organizations joined to a Team plan's parent organization" |
| 0.2 | SSO, including domain verification, comes before SCIM | Confirmed | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | |
| 0.3 | Baseline per data class is chosen from the settings README | Confirmed | repo: starter-kit/settings/README.md | |
| 0.4 | Placeholder list; `REPLACE-WITH-GITHUB-ORG` appears twice per file, under `strictKnownMarketplaces` and `extraKnownMarketplaces`; pe-zdr has two MCP host placeholders | Confirmed | repo: starter-kit/settings/*.json | |
| 0.4 | Org ID comes from claude.ai admin settings; a wrong value makes Claude Code exit at startup | Confirmed | https://code.claude.com/docs/en/authentication#restrict-login-to-your-organization | Link [S11] added |
| 0.5 | An Owner outside a mapped Owner group can be removed by the next sync | Confirmed | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | |
| 1.1 | Okta menu path to create the app | Corrected | https://help.okta.com/en-us/content/topics/apps/apps_app_integration_wizard_saml.htm | "go to **Applications > Applications** and select **Create App Integration**" → "go to **Applications and Resources > Applications**, select **Create App Integration**, then **Classic experience**, and choose **SAML 2.0**"; notes that Anthropic's guide shows the older name |
| 1.1 | App named `Claude`; Anthropic recommends SAML over OIDC | Confirmed | https://support.claude.com/en/articles/13917894-sso-setup-okta | |
| 1.2 | Name ID format EmailAddress; attribute `email` = `user.email` | Confirmed | https://support.claude.com/en/articles/13917894-sso-setup-okta | Added "Application username to Email" from the same page |
| 1.2 | ACS URL and Entity ID come from the Claude side | Confirmed | https://support.claude.com/en/articles/13917894-sso-setup-okta | "values **unverified** here" removed; now "copy them from the WorkOS setup flow in the Claude **Identity and access** settings" |
| 1.3 | A `groups` attribute statement is needed for group mappings; attribute name | Confirmed | https://support.claude.com/en/articles/13917894-sso-setup-okta | "attribute name **unverified**" removed; name `groups` and the filter requirement added |
| 1.3 | Where the group attribute statement lives in Okta | Corrected | https://help.okta.com/en-us/content/topics/apps/define-group-attribute-statements.htm | Added: **Sign On** tab, **Attribute Statements** > **Show legacy configuration**; Okta's newer alternative is custom claims |
| 1.4 | "On the **Provisioning** tab, select **Configure API Integration**" | Corrected | https://help.okta.com/en-us/content/topics/apps/apps_app_integration_wizard_scim.htm | For an app made with Create App Integration: **General** tab, **App Settings**, set **Provisioning** to **SCIM**; then **Provisioning** tab, **Settings > Integration**, **Edit**. Notes that "Configure API Integration" is the catalog-app label Anthropic's guide uses |
| 1.4 | Enable Create Users, Update User Attributes, Deactivate Users | Confirmed | https://help.okta.com/en-us/content/topics/provisioning/lcm/lcm-provision-application.htm | Added "under **To App**, click **Edit**" |
| 1.4 | SCIM base URL and token come from the WorkOS flow | Confirmed | https://support.claude.com/en/articles/13917894-sso-setup-okta | "WorkOS values **unverified** (guide not read)" removed |
| 1.5 | SAML and SCIM email must be the same Okta attribute | Confirmed | https://support.claude.com/en/articles/13917894-sso-setup-okta | |
| 1.6 | One group per role and seat type; prefix `anthropic-claude-` recommended, not required | Confirmed | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | |
| 1.7 | "**Choice: see the Choices list.**" (no Choices section exists in the file; defect reported by the OPS-11 worker) | Corrected | repo: this runbook; marker from docs/compendium/README.md | "**Choice: see the Choices list. The docs do not describe pilot groups.**" → "**(Our recommendation): the docs do not describe pilot groups.**" |
| 1.7 | Pilot-group design | Unverified | | "pilot design is **unverified**" → "**⚠ Unverified:** confirm the pilot design at setup" |
| 1.7 | A pilot group alone gives no role | Confirmed | https://support.claude.com/en/articles/14499648-how-scim-sync-works-for-enterprise-organizations | |
| 1.8 | Users not assigned when the provisioning mode is saved are removed | Confirmed | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | |
| 1.8 | "Check the assignment list before step 2.5" | Corrected | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | Saving happens in step 2.4: "before step 2.5" → "before step 2.4, which saves it" |
| 2 (header) | "Only an Admin or Owner can do this" | Corrected | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | → "The docs require the Owner role in a Claude organization, or Admin in a Console organization" |
| 2.1 | **Setup SCIM** / **Manage SCIM** in **User provisioning** | Confirmed | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | Added the path **Organization settings > Organization and access** |
| 2.2 | Modes Invite only, Just-in-time (JIT), SCIM directory sync | Confirmed | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | |
| 2.3 | Change preview shows the removal count | Confirmed | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | Added "and cancel if more users would be removed than you expect" from the same page |
| 2.4 | **Save changes** triggers the first provisioning | Confirmed | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | |
| 2.5 | Groups appear only after the first sync | Confirmed | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | |
| 3.1 | **Enable group mappings** | Confirmed | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | |
| 3.2 | **Add** per role; a user without a role group is removed | Confirmed | https://support.claude.com/en/articles/14499648-how-scim-sync-works-for-enterprise-organizations | |
| 3.3 | Seat tiers: existing users keep their seat; new users get the highest seat type with an unassigned seat | Confirmed | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | |
| 3.4 | Owner and Admin not exempt; Primary Owner exempt and not set by mappings; set it under **Organization settings > Members** first | Confirmed | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | |
| 3.5 | "run **Sync now** under **Directory sync (SCIM)**" | Corrected | https://support.claude.com/en/articles/14499648-how-scim-sync-works-for-enterprise-organizations | The two Anthropic pages name different buttons (**Sync**, **Sync now**, **Check for updates**); now a `**⚠ Conflict:**` naming each, and states that existing members are not resynced after a seat-tier or role mapping change |
| 3.6 | Custom-role sequence; users in a custom-mapped group have no permissions until attached | Confirmed | https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning | Added "click **Check for updates** in **Organization settings > Groups**" from [S2] |
| 3 (removal) | Removed when group access is revoked; sync takes minutes, sometimes hours | Confirmed | https://support.claude.com/en/articles/14499648-how-scim-sync-works-for-enterprise-organizations | |
| 4 (table) | macOS path `/Library/Application Support/ClaudeCode/managed-settings.json`; domain `com.anthropic.claudecode`; nested settings as dictionaries, lists as plist arrays | Confirmed | https://code.claude.com/docs/en/managed-settings | |
| 4 (table) | Windows path `C:\Program Files\ClaudeCode\managed-settings.json`; `Settings` value (REG_SZ or REG_EXPAND_SZ) under `HKLM\SOFTWARE\Policies\ClaudeCode` | Confirmed | https://code.claude.com/docs/en/managed-settings | |
| 4 (table) | Linux and WSL `/etc/claude-code/managed-settings.json`, file only | Confirmed | https://code.claude.com/docs/en/managed-settings | |
| 4 | Legacy `C:\ProgramData\ClaudeCode\managed-settings.json` is not read | Confirmed | https://code.claude.com/docs/en/managed-settings | |
| 4 | Precedence: server-managed, then MDM plist or HKLM, then file; `managedSourcesBehavior` | Confirmed | https://code.claude.com/docs/en/plugins/org | |
| 4 Intune | Intune blade names and OMA-URI or script setup | Unverified | | Reworded to the marker |
| 4 Intune | MDM examples repository has an Intune template | Confirmed | https://code.claude.com/docs/en/managed-settings | Repository itself not opened |
| 4 Intune | "Intune delivers to devices, not to users" | Corrected | https://learn.microsoft.com/en-us/intune/device-management/tools/management-extension-windows | → "Intune can assign scripts and apps to user groups or device groups [S14]. The file and the HKLM value are machine-wide, so assign them to device groups **(Our recommendation)**" |
| 4 Jamf | Profile in `com.anthropic.claudecode`, or the file, from Jamf | Confirmed | https://code.claude.com/docs/en/managed-settings | |
| 4 Jamf | Jamf UI steps | Unverified | | Reworded to the marker. No Jamf page is on the accepted list |
| 4 Kandji | "Anthropic's docs name Jamf, Iru and Intune as the MDM examples" | Corrected | https://code.claude.com/docs/en/managed-settings | → "Jamf, Iru, Intune and Group Policy as the MDM starter templates" |
| 4 Kandji | The repo README mentions Kandji | Confirmed | repo: starter-kit/settings/README.md | |
| 4 Kandji | Kandji and Iru are the same product with the same steps | Unverified | | Reworded to the marker |
| 4 (check) | Malformed JSON or plist makes Claude Code refuse to start and names the source | Confirmed | https://code.claude.com/docs/en/managed-settings | |
| 4 (check) | Wrong org UUID exits at startup | Confirmed | https://code.claude.com/docs/en/authentication#restrict-login-to-your-organization | Link [S11] added |
| 4 (check) | "A missing or unreadable file is not a failure. Claude Code runs without that source." | Corrected | https://code.claude.com/docs/en/managed-settings | Missing file: no policy. Read denied by the OS: session starts without it, and `/status` and `claude doctor` record it. Other read errors (for example I/O): Claude Code exits at startup |
| 5.1 | `/status` **Setting sources** shows `Enterprise managed settings` with `(plist)`, `(HKLM)` or `(file)` | Confirmed | https://code.claude.com/docs/en/managed-settings | Added `(remote)` for server-managed settings |
| 5.2 | "`claude doctor` ... **Organization policy** line ... names where the policy loaded from" | Corrected | https://code.claude.com/docs/en/managed-settings | The Organization policy line (v2.1.261+) is about the claude.ai organization policy (Remote Control and cloud sessions), not the managed-settings file. Now: `claude doctor` lists each dropped managed-settings entry with its source and field; the Organization policy line is described separately |
| 5.3 | pe-zdr denies WebFetch and WebSearch; "Run a read that the policy blocks. The read is refused." | Corrected | https://code.claude.com/docs/en/permissions | A bare tool name in `deny` removes the tool from Claude's context, so there is no refusal to see; `Read(**/.env)` matches only at or under the current directory. Now: fetch a web page (Claude has no web tool), and read a `.env` in the project folder (refused) |
| 5.4 | `/plugin` lists the marketplace and the group's plugins | Confirmed | https://code.claude.com/docs/en/plugins/org | |
| 5.5 | `Setting sources` names the source used | Confirmed | https://code.claude.com/docs/en/managed-settings | Added the `Skipped sources` line (v2.1.242+) |
| 6 (kit) | Marketplace `digital-twin-kit` in `.claude-plugin/marketplace.json` | Confirmed | repo: .claude-plugin/marketplace.json | |
| 6 (kit) | Three plugins: `twin-shared`, `twin-pe-deal-team`, `twin-governance` | Confirmed | repo: .claude-plugin/marketplace.json | |
| 6 (kit) | Every baseline has the allowlist and registration entries with `REPLACE-WITH-GITHUB-ORG/digital-twin-kit` | Confirmed | repo: starter-kit/settings/*.json | |
| 6 (kit) | `twin-shared` in every baseline, `twin-governance` in three; no role plugin | Confirmed | repo: starter-kit/settings/*.json | |
| 6 (groups) | Plugin keys apply to every user who receives the settings; no per-user or per-group key | Confirmed | https://code.claude.com/docs/en/plugins/org | |
| 6 (groups) | Device groups: the file or profile applies to the whole machine | Confirmed | https://code.claude.com/docs/en/managed-settings | |
| 6 (groups) | Server-managed group configurations: Enterprise, Owner role | Corrected | https://code.claude.com/docs/en/server-managed-settings#give-groups-different-settings | "Requires the Owner role" → "Owner or Primary Owner"; added **Add configuration**, that the group must already exist (SCIM-synced or custom), that configurations do not merge, and that they are not yet available with HIPAA enabled |
| 6 (groups) | Cloud sessions read only server-managed settings | Confirmed | https://code.claude.com/docs/en/plugins/org | |
| 6 (groups) | "SCIM groups ... do not decide which plugins a device gets" | Corrected | https://code.claude.com/docs/en/server-managed-settings#give-groups-different-settings | True for the device-group path only. On the server-managed path the configuration is chosen by Claude group, so a SCIM-synced group can carry a plugin set; use an IdP-synced group |
| 6.1 | Private repo needs read access per user; a seed for users without git-host accounts | Confirmed | https://code.claude.com/docs/en/plugins/org | |
| 6.2 | "the mapping itself is a **choice** (see Choices)" (no Choices section; OPS-11 defect) | Corrected | repo: this runbook; marker from docs/compendium/README.md | → "the mapping itself is **(Our recommendation)**" |
| 6.3 | `enabledPlugins` shape `"<plugin>@<marketplace>": true` | Confirmed | https://code.claude.com/docs/en/plugins/org | |
| 6.3 | `TWIN_GOVERNANCE_TWIN_ID` and `TWIN_GOVERNANCE_LOG` are set per group in `env` | Confirmed | repo: starter-kit/settings/README.md | |
| 6.5 | Under `allowManagedHooksOnly`, hooks from plugins force-enabled by managed settings still run | Confirmed | https://code.claude.com/docs/en/settings-reference#what-runs-under-allowmanagedhooksonly | |
| 6.5 | Hook files `governance_log.py` and `hooks.json` ship in `hooks/` | Confirmed | repo: starter-kit/plugins/twin-governance/hooks/ | |
| 6.6 | `/plugin`; `claude -p --output-format stream-json --verbose` lists `plugins` in the `init` event | Confirmed | https://code.claude.com/docs/en/plugins/org | |
| 6.7 | A source outside the allowlist fails with `blocked by enterprise policy`; `disableSideloadFlags` | Confirmed | https://code.claude.com/docs/en/plugins/org | |
| 6.8 | **Organization settings > Plugins & skills**; reaches Claude Code as synced plugins | Confirmed | https://code.claude.com/docs/en/plugins/org | |
| 6 (hook) | `PostToolUse` and `PostToolUseFailure` hook; one metadata-only line; never blocks | Confirmed | repo: starter-kit/plugins/twin-governance/hooks/ | |

## salesforce-hosted-mcp.md

| Line or step | Claim | State | Source URL | Old wording → new wording (corrections) |
|---|---|---|---|---|
| Read this first | Warning quote on authentication settings | Confirmed | https://claude.com/docs/connectors/custom/add-unlisted.md | Verbatim match |
| Read this first | Salesforce developer pages return 403 (2026-11-14) | Corrected | https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/activate-mcp-servers.html | Still 403 on 2026-11-15; help.salesforce.com renders no content; Salesforce's official GitHub [G] added as a source |
| Pages [D] | [D] not read (403) | Confirmed | see "Sources that could not be read" | |
| 1.1 | Enterprise Edition or higher supports hosted MCP servers | Unverified | | Reworded to the marker; no Salesforce page could be read |
| 1.2 | Confirm Government Cloud availability with Salesforce | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | |
| 1.3 | Team or Enterprise; Owner, or on Enterprise a custom role that manages the organization's libraries | Confirmed | https://claude.com/docs/connectors/custom/add-unlisted.md | |
| 1.4 | Sandbox values exist; do the work in a sandbox first | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | Order marked **(Our recommendation)** |
| 1.5 | Two test users across a soft wall | Confirmed | repo: docs/compendium/14-private-equity.md | |
| 1.6 | Allowlist Anthropic's range `160.79.104.0/21` | Corrected | https://platform.claude.com/docs/en/api/ip-addresses | → "Anthropic's outbound ranges (`160.79.104.0/21` and `153.61.208.0/20` on 2026-11-15)" |
| 2.1 | Setup: **Enable MCP Service** | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | |
| 2.2 | Quick Find `MCP Servers`, **MCP Servers** under **API Catalog**, **Salesforce Servers** tab, activate **headless-360** | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | |
| 2.3 | Claude cannot connect until the server is active | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | [A] states it for Claude Desktop |
| 2 (source) | "Which tools headless-360 exposes, and which of them write, is **unverified**" | Corrected | https://github.com/salesforce/salesforce-skills/blob/claude-prod/salesforce-for-sales/.mcp.json | Now lists `discover`, `describe`, `dispatch`, `dispatch_readonly`, `display_widget`; `dispatch` writes; [G] marks `discover`, `describe`, `dispatch` "should be blocked". Live list kept as `**⚠ Unverified:**` to confirm at setup |
| 3 | OAuth scopes `mcp_api` and `refresh_token` | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | |
| 3 | PKCE required | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | |
| 3 | Access tokens issued as JWTs | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | |
| 3 | OAuth policy lets users self-authorize | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | |
| 3 | claude.ai callback `https://claude.ai/api/mcp/auth_callback` | Confirmed | https://claude.com/docs/connectors/building/authentication.md | |
| 3 | Claude Code uses port-agnostic `http://localhost/callback` and `http://127.0.0.1/callback` | Confirmed | https://claude.com/docs/connectors/building/authentication.md | |
| 3 | Salesforce accepts a port-less loopback entry | Unverified | | Reworded to the marker |
| 3 notes | Desktop route callback `http://127.0.0.1:53280/callback` | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | |
| 3 notes | One External Client App may list several callback URLs | Unverified | | Reworded to the marker |
| 3 notes | Consumer Key is the client ID; with PKCE, Claude Desktop needs no secret | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | |
| 3 notes | Salesforce needs a secret for the claude.ai route | Unverified | | Reworded to the marker |
| 3 notes | A new External Client App can take up to 30 minutes | Unverified | | Only a third-party summary supports it; reworded to the marker |
| 3 notes | Users need a permission to use MCP servers and the app | Corrected | https://github.com/salesforce/salesforce-skills/blob/claude-prod/salesforce-for-sales/SETUP.md | Added: Salesforce's guide says to create a permission set for those users ("optional but recommended") |
| 3 notes | Exact permissions in that permission set | Unverified | | Reworded to the marker |
| 3 notes | Per-user tokens carry only that user's Salesforce permissions | Confirmed | https://claude.com/docs/connectors/building/authentication.md | |
| 4 | **Sign in now** / **No sign-in** / **Request headers**; headers are one shared credential | Confirmed | https://claude.com/docs/connectors/custom/add-unlisted.md | |
| 4 | OAuth client options: "Use Claude's published identity" (CIMD), "Register automatically" (DCR), **Use your own OAuth client** | Confirmed | https://claude.com/docs/connectors/custom/add-unlisted.md | |
| 4 | Salesforce's authorization server supports CIMD or DCR | Unverified | | Reworded to the marker |
| 4 | Leave the secret blank unless the server requires one | Confirmed | https://claude.com/docs/connectors/custom/add-unlisted.md | |
| 4 | Salesforce requires a secret | Unverified | | Reworded to the marker |
| 4 | Server URLs `https://api.salesforce.com/platform/mcp/v1/platform/headless-360` and `.../v1/sandbox/platform/headless-360` | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | |
| 4 | Authorization server `https://login.salesforce.com`, My Domain, or `https://test.salesforce.com`; exactly one | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | [C] also says Claude uses only the first `authorization_servers` entry |
| 4 | The claude.ai dialog may have no "Authorization server" field | Unverified | | Reworded to the marker |
| 4 | Desktop route: Desktop 3P Connectors page, `salesforce-h360` | Confirmed | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | |
| 5 | Level 1 control "Write tools Blocked, or left out of the role plugin" | Confirmed | repo: docs/compendium/06-autonomy.md | |
| 5 | Per-tool settings **Always allow**, **Needs approval**, **Blocked** | Confirmed | https://claude.com/docs/connectors/getting-started.md | |
| 5 table | Read tools such as describe set to **Always allow** | Corrected | https://github.com/salesforce/salesforce-skills/blob/claude-prod/salesforce-for-sales/.mcp.json | Added: Salesforce says to keep the beta read-only and marks `discover`, `describe` and `dispatch` "should be blocked"; set those to **Blocked** |
| 5 | "the Claude setting hides write tools" | Corrected | https://claude.com/docs/connectors/getting-started.md | "hides" → "blocks" (the setting is **Blocked**) |
| 5 | Salesforce-side read-only enforcement | Unverified | | Reworded to the marker |
| 5 | "`mcp_api` is the only scope [A] lists" | Corrected | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | [A] lists two scopes → "`mcp_api` is the only access scope [A] lists, besides `refresh_token`" |
| 4 (pe-zdr, OPS-24) | Host `api.salesforce.com` replaces `REPLACE-WITH-SALESFORCE-HOSTED-MCP-HOST`; `https://api.salesforce.com/*` matches both server URLs on port 443; no port means 443 only; a pattern with a path wildcard matches every path | Confirmed | https://code.claude.com/docs/en/managed-mcp | Host taken from the server URLs in https://github.com/salesforce/salesforce-skills/blob/claude-prod/salesforce-for-sales/.mcp.json. Added [I] |
| 5 (OPS-24) | The five tool names `discover`, `describe`, `dispatch`, `dispatch_readonly`, `display_widget`; `discover`, `describe`, `dispatch` marked "should be blocked"; `dispatch_readonly` listed beside `dispatch` | Confirmed | https://github.com/salesforce/salesforce-skills/blob/claude-prod/salesforce-for-sales/.mcp.json | Table rewritten to one row per tool; the row for `query`, `get` removed |
| 5 (OPS-24) | `dispatch_readonly` cannot create or update | Unverified | | The description text is ambiguous about writes; marker added |
| 5 (OPS-24) | The model can find a read call through `dispatch_readonly` with `discover` and `describe` Blocked | Unverified | | Marker added; our choice is Always allow for both **(Our recommendation)** |
| Move to level 2 (OPS-24) | Per-tool settings Always allow, Needs approval, Blocked; the user is asked before a tool runs, with **Allow once** or **Always allow** | Confirmed | https://claude.com/docs/connectors/getting-started.md | |
| Move to level 2 (OPS-24) | A member cannot choose **Always allow** over an Owner's Needs approval for a custom connector | Unverified | | Marker added |
| Move to level 2 (OPS-24) | `dispatch` can run any REST call including sObject delete | Confirmed | https://github.com/salesforce/salesforce-skills/blob/claude-prod/salesforce-for-sales/.mcp.json | |
| 6 | **Organization settings > Connectors**, **Add**, **Custom**, **Web** | Confirmed | https://claude.com/docs/connectors/custom/add-unlisted.md | |
| 6 | **Continue**; keep **Detected**; **Add**; layout varies | Confirmed | https://claude.com/docs/connectors/custom/add-unlisted.md | |
| 7.1 | The Owner sets each tool's permission for the whole organization | Unverified | https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities | Help center says org-wide tool permissions apply to everyone and members can't override them, but not whether this covers custom connectors; marker added |
| 7.1 | Tool lists can change after approval | Confirmed | repo: docs/compendium/11-connectors.md | |
| 7.2 | Member: **Customize > Connectors**, **Custom** label, **Connect** | Confirmed | https://claude.com/docs/connectors/custom/add-unlisted.md | |
| 7.3 | Troubleshooting page "(not read by us)" | Corrected | https://claude.com/docs/connectors/building/troubleshooting.md | Page read on 2026-11-15; "(not read by us)" removed |
| 8 | Outbound traffic comes from `160.79.104.0/21`, "nothing broader" | Corrected | https://platform.claude.com/docs/en/api/ip-addresses | `**⚠ Conflict:**` added: [C] names one range, the IP reference lists `160.79.104.0/21` and `153.61.208.0/20`; allow every outbound range on the reference |
| 8 | Discovery requests use the same range; a WAF can break sign-in | Confirmed | https://claude.com/docs/connectors/building/authentication.md | |
| 8 | "add `160.79.104.0/21` there" | Corrected | https://platform.claude.com/docs/en/api/ip-addresses | → "add the outbound ranges from [F] there" |
| 8 | Where the Salesforce IP setting lives; `api.salesforce.com` change | Unverified | | Reworded to the marker |
| 8 | Check the IP reference before entering ranges | Confirmed | https://claude.com/docs/connectors/building/authentication.md | Wording now "outbound ranges" |
| 8 | Without the allowlist the remote connector will not work | Confirmed | https://claude.com/docs/connectors/building/authentication.md | |
| 8 | Desktop route needs outbound HTTPS to `github.com`, `api.salesforce.com`, login host | Corrected | https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md | Added "and git installed" from the same page |
| 10 | A removed user's token works until it expires | Confirmed | repo: docs/compendium/11-connectors.md | |

## microsoft-365-connector.md

| Line or step | Claim | State | Source URL | Old wording → new wording (corrections) |
|---|---|---|---|---|
| Access | Per user, delegated; no service-principal authentication | Confirmed | https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide | |
| Access | Does not bypass SharePoint sharing or folder permissions | Confirmed | https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide | |
| Access | Write scopes used only when write tools are enabled | Confirmed | https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide | |
| Access | Scopes `Files.Read`, `Files.Read.All`, `Sites.Read.All`, `Files.ReadWrite.All`; `Sites.Read.All` for SharePoint search | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |
| Access | Tenant-wide search; `*.Selected` not supported; "Site-specific search restriction isn't supported." | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |
| Access | Audit log records timestamp, user, operation, resource | Confirmed | https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide | |
| Access | Personal accounts, 3P Desktop, US government and the Desktop local connector have their own setup | Confirmed | https://claude.com/docs/connectors/microsoft/365.md | |
| 1.1 | Team or Enterprise; Owner or Primary Owner | Confirmed | https://claude.com/docs/connectors/microsoft/365.md | |
| 1.2 | Work or school accounts with active Microsoft 365 accounts | Confirmed | https://claude.com/docs/connectors/microsoft/365.md | |
| 1.3 | Global Administrator needed | Confirmed | https://claude.com/docs/connectors/microsoft/365.md | |
| 1.4, 1.5 | Pilot users across a wall; deal-team group | Confirmed | repo: docs/compendium/14-private-equity.md | |
| 1.6 | "the exact policies that could block it are **unverified**" | Corrected | https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide | Now states: group-based, MFA and device compliance policies are supported (keep device policy assigned to the Claude apps); location, network and sign-in frequency policies block the connector for every member |
| 1.6 | App-consent settings could block the connector | Unverified | | Reworded to the marker |
| 1.7 | "whether Anthropic's range `160.79.104.0/21` needs allowlisting for Microsoft 365 is **unverified**" | Corrected | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | Now: for a location or sign-in frequency policy, create a named location with every outbound IPv4 range (`160.79.104.0/21` and `153.61.208.0/20`, from https://platform.claude.com/docs/en/api/ip-addresses), leave **Mark as trusted location** unchecked, add it under **Conditions > Locations > Exclude**; excluding the two apps alone is not enough; not for device compliance policies |
| 2 | Consent is tenant-wide, lets every user use the app unless restricted, and is a sensitive operation | Confirmed | https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/grant-admin-consent | |
| 2 | Repeating consent re-grants the full current set | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |
| 3 (header) | Microsoft roles "can grant consent for delegated Graph permissions" | Corrected | https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/grant-admin-consent | → Privileged Role Administrator for any permission; Cloud Application, AI or Application Administrator for any permission except Microsoft Graph app roles; marked `**⚠ Conflict:**` against Claude's Global Administrator requirement |
| 3 (header) | A role below Global Administrator is enough for the first consent | Unverified | | Reworded to the marker |
| 3 | **Organization settings > Connectors**, **Add**, **All available**, **Microsoft 365**, **Add to your team** | Confirmed | https://claude.com/docs/connectors/microsoft/365.md | |
| 3 route 1 | Consent through Claude: **Customize > Connectors**, **Connect**, **Work or school account**, consent on behalf of the organization | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |
| 3 route 2 | `POST https://graph.microsoft.com/v1.0/servicePrincipals`; M365 MCP Client for Claude `08ad6f98-a4f8-4635-bb8d-f1a3044760f0`; M365 MCP Server for Claude `07c030f6-5743-41b7-ba00-0a6e85f37c17` | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |
| 3 route 2 | Open the adminconsent URL once per appId | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |
| 3 | URL format `https://login.microsoftonline.com/{organization}/adminconsent?client_id={client-id}` | Confirmed | https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/grant-admin-consent | |
| 3 | Success address contains `admin_consent=True` | Confirmed | https://claude.com/docs/connectors/microsoft/365.md | |
| 3 | Check: **Enterprise applications**, remove the filter, **M365 MCP Server for Claude**, **Permissions** | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |
| 3 | Added permissions: Global Administrator or Application Administrator re-opens the consent link; ID on **Overview** | Confirmed | https://claude.com/docs/connectors/microsoft/365.md | |
| 3 | Revoke: **Admin consent** tab, "...", **Revoke permission**; error "Failed to call tool" | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |
| 4 | Consent alone lets all users use the app | Confirmed | https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/grant-admin-consent | |
| 4 | **Assignment required?** **Yes**, **Users and groups**, on both apps | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |
| 4 | Claude's article restricts through Entra assignment | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |
| 5 | Adding makes it available; each member connects | Confirmed | https://claude.com/docs/connectors/microsoft/365.md | |
| 5 | Claude-side restriction to one Claude group | Unverified | | Reworded to the marker |
| 5 | Member connect flow; button reads **Disconnect** | Confirmed | https://claude.com/docs/connectors/microsoft/365.md | |
| 6 | Write actions controlled in Entra and **Organization settings > Connectors** | Confirmed | https://claude.com/docs/connectors/microsoft/365.md | |
| 6 | **Tool permission restrictions**; per-tool overrides **Default restriction** | Confirmed | https://claude.com/docs/connectors/microsoft/365.md | |
| 6 | Enterprise custom roles (beta) for a subset of users | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |
| 6 | Revoking write scopes in Entra removes the capability | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |
| 7 | Connector uses each user's own permissions | Confirmed | https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide | |
| 7.2 | Team site: group owners become site owners, members become site members | Corrected | https://learn.microsoft.com/en-us/sharepoint/modern-experience-sharing-permissions | Added: "Site permissions can also be managed separately through SharePoint groups, so check those too" |
| 7.2 | Channel sites managed in Teams, read-only in SharePoint | Confirmed | https://learn.microsoft.com/en-us/sharepoint/modern-experience-sharing-permissions | |
| 7.2 | Communication site: Owners, Members, Visitors | Confirmed | https://learn.microsoft.com/en-us/sharepoint/modern-experience-sharing-permissions | |
| 7.3 | *Anyone* links need no sign-in and cannot be audited | Confirmed | https://learn.microsoft.com/en-us/sharepoint/modern-experience-sharing-permissions | |
| 7.3 | *People in your organization* links "open the item to everyone in the tenant" | Corrected | https://learn.microsoft.com/en-us/sharepoint/modern-experience-sharing-permissions | → "work for anyone inside the organization who has the link" |
| 7.4 | Confidential sites: external sharing off | Confirmed | https://learn.microsoft.com/en-us/sharepoint/modern-experience-sharing-permissions | |
| 8a | Library permissions path, inheritance message, **Show these items**, **Show users**, unsharing keeps limited access, **Stop Inheriting Permissions** / **Delete unique permissions** | Unverified | https://support.microsoft.com/en-us/office/edit-permissions-for-a-list-library-or-individual-item-02d770f3-59eb-4910-a608-5f84cc297782 | The Microsoft Support page matches every string, but support.microsoft.com is not on the accepted list; one marker added to the paragraph |
| 8a site | Site access = Owners, Members, Visitors, or the connected group | Confirmed | https://learn.microsoft.com/en-us/sharepoint/modern-experience-sharing-permissions | |
| 8a site | "Nested security groups are discouraged because they cause performance issues and hide membership" | Corrected | https://learn.microsoft.com/en-us/sharepoint/modern-experience-sharing-permissions | → "are not recommended because they can cause performance issues" ("hide membership" is not on the page) |
| 8a site | Site permissions menu path and a per-user check control | Unverified | | Reworded to the marker |
| 8a script | `GET /drives/{drive-id}/items/{item-id}/permissions`; `Get-MgDriveItemPermission -DriveId -DriveItemId`; `inheritedFrom` | Confirmed | https://learn.microsoft.com/en-us/graph/api/driveitem-list-permissions?view=graph-rest-1.0 | |
| 8a script | "a library owner or admin account sees more" | Corrected | https://learn.microsoft.com/en-us/graph/api/driveitem-list-permissions?view=graph-rest-1.0 | → "the item's owner (including co-owners) sees all sharing permissions" |
| 8a script | Lists SharePoint site-group membership | Unverified | | Reworded to the marker |
| 8a script | `Files.Read` least privileged; `Files.Read.All`, `Sites.Read.All` higher | Confirmed | https://learn.microsoft.com/en-us/graph/api/driveitem-list-permissions?view=graph-rest-1.0 | |
| 8b | New uploads lag; naming the site helps | Confirmed | https://claude.com/docs/connectors/microsoft/365.md | |
| 8b | The connector cannot be stricter than SharePoint | Confirmed | https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide | |
| 8c | "search the Microsoft 365 audit log (Compliance Center)" | Corrected | https://learn.microsoft.com/en-us/purview/audit-search | → Microsoft Purview portal, **Audit** solution, **Search**; filter by **Users** and **File, folder, or site**; needs the Audit Logs or View-Only Audit Logs role; records typically appear 60 to 90 minutes after the event |
| 8c | Audit fields | Confirmed | https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide | |
| 8c | Filters for the connector's app | Unverified | | Reworded to the marker |
| 3 (pe-zdr, OPS-24) | The host of the Microsoft 365 connector's server URL for `REPLACE-WITH-MICROSOFT-365-MCP-HOST`, and where an admin reads it | Unverified | | https://claude.com/docs/connectors/microsoft/365.md, https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector and https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide name no host (page 1 re-read 2026-11-15). Matching rules from https://code.claude.com/docs/en/managed-mcp. Marker added |
| 8b (OPS-24) | Step 4 assignment stops an unassigned user from using the connector, so user 2 is added for the test | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | Consent alone lets all users in; assignment required limits it ([D] too). Setup line and control row 8.1b added |
| 9 (OPS-24) | Removing a user from Claude also removes the Entra app assignment and revokes the Microsoft 365 session | Unverified | | Old wording stated it as fact; now the admin does both by hand, marker added |
| 9 | Refresh tokens expire after 90 days of inactivity by default | Confirmed | https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide | |
| 9 | Members disconnect in **Customize > Connectors**; Owner removes in **Organization settings > Connectors** | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |

## starter-kit/connectors/salesforce/README.md (OPS-24)

| Line or step | Claim | State | Source URL | Old wording → new wording (corrections) |
|---|---|---|---|---|
| Deploy 1 | Salesforce allows 20 tracked fields per object | Unverified | | developer.salesforce.com returned HTTP 403 on 2026-11-15; stated as fact before; marker added |
| Report | The marker row and the changed-field rows share `CreatedById` and `CreatedDate` | Unverified | | Never observed: the marker has not deployed to an org yet; marker added |
| Report (RevOps) | Retention period of Field History rows | Unverified | | "(⚠ confirm the retention ...)" → the compendium's marker |

## claude-code-scheduled-task.md (OPS-59)

| Line or step | Claim | State | Source URL | Old wording → new wording (corrections) |
|---|---|---|---|---|
| What this is | A saved prompt, repositories and connectors that runs on its own, in Anthropic's cloud or a self-hosted environment, with the laptop closed | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| What this is | Release status is research preview | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Inputs: Runs as | A task belongs to the owner's claude.ai account, is not shared with teammates, and acts through their connectors as them | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Inputs: Autonomy | Pilots start at level 1; an unwatched run is level 4 | Confirmed | repo: docs/compendium/06-autonomy.md |  |
| Inputs: Data class | Cloud sessions are off under ZDR, the HIPAA configuration and CMEK | Confirmed | https://code.claude.com/docs/en/claude-code-on-the-web.md |  |
| Inputs: Connectors | All the employee's connected connectors are included by default | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Inputs: Memory | The repository's CLAUDE.md is part of the clone | Confirmed | https://code.claude.com/docs/en/cloud-environments.md |  |
| Inputs: Memory | Whether auto memory is on in an Anthropic-hosted scheduled run | Unverified |  | Retried: memory.md says auto memory is machine-local; the self-hosted page covers self-hosted only; marker kept |
| Before you start 1 | Plans: Pro, Max, Ultra, Team or Enterprise | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Before you start 2 | Toggle **Scheduled tasks (Was Routines)** or **Routines** at **Organization settings > Capabilities > Remote sessions**; off stops existing tasks and blocks new ones | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Before you start 3 | Custom roles: the permission sits in the role's **Remote sessions** section at **Organization settings > Roles** | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Before you start 4 | Policy message `Cloud sessions are disabled by your organization's policy` | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Before you start 5 | A Console API key or a cloud provider login hides `/schedule` | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Before you start 6 | On Team and Enterprise an Owner turns on the GitHub connection method | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Step 1 | Anthropic-managed cloud is the default place a task runs; self-hosted when routed there | Confirmed | https://code.claude.com/docs/en/scheduled-tasks.md |  |
| Step 2 | Each run is a fresh cloud session that does not read `~/.claude/skills/`; the repository's `.claude/skills/` is part of the clone | Confirmed | https://code.claude.com/docs/en/skills.md |  |
| Step 2 | Account skills versus [G]: skills.md says cloud sessions load account skills and that some self-hosted sessions do not; [G]'s sentence sits in the self-hosted page's session-config section, so the two pages do not disagree | Corrected | https://code.claude.com/docs/en/skills.md | **⚠ Conflict:** [D] says cloud sessions also load skills enabled on the claude.ai account, while [G] says a cloud scheduled task run does not get its owner's skills; follow the committed copy, and → Cloud sessions also load skills enabled on the claude.ai account, but in a self-hosted environment a cloud scheduled task run does not get its owner's skills, so follow the committed copy; |
| Step 2 | A skill committed to `.claude/skills/` is not available to cloud threads in a project | Confirmed | https://code.claude.com/docs/en/skills.md |  |
| Step 3 | claude.ai/code/routines, **New task** or **New routine** (full-page form), the **New scheduled task** dialog, `/schedule` in the CLI | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Step 4 | The saved prompt is not live user input and cannot act as approval | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Step 4 | Whether a prompt that is only `/<skill-name>` invokes the skill | Unverified |  | Retried on routines.md and skills.md; neither says; marker kept |
| Step 5 | Presets in local time; five-field cron in UTC; `CRON_TZ=` prefix; more often than hourly rejected; 9:07 to avoid a late start on the hour | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Step 5 | **Custom** cron is set in the edit dialog of an existing task, not when the task is created | Corrected | https://code.claude.com/docs/en/routines.md | or **Custom** with a cron expression such as `0 */2 * * *`; → or, once the task exists, **Custom** in its edit dialog with a cron expression such as `0 */2 * * *`; |
| Step 5 | Minimum interval one hour | Confirmed | https://code.claude.com/docs/en/scheduled-tasks.md |  |
| Step 6 | **Advanced settings**, **Repository** on the **General** tab; cloned each run; `claude/`-prefixed branches | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Step 6 | **Default** environment: **Limited** network with **Allow package managers**; connectors go through Anthropic's servers | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Step 7 | Model and effort are chosen in the prompt input's model selector | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Step 8 | **Connectors** tab; included connectors can be used during a run, including writes | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Step 9 | A cloud run begins in auto mode, stops for an ask rule and after repeated blocks | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Step 9 | Repository `.claude/settings.json` permission rules apply in a session with one repository | Confirmed | https://code.claude.com/docs/en/cloud-environments.md |  |
| Step 9 | Server-managed settings reach cloud sessions | Confirmed | https://code.claude.com/docs/en/server-managed-settings.md |  |
| Step 9 | `allowManagedPermissionRulesOnly` makes the repository's rules ignored | Confirmed | https://code.claude.com/docs/en/claude-code-on-the-web.md |  |
| Step 9 | Whether a connector tool set to Blocked or Needs approval holds in a scheduled run | Unverified |  | Retried on routines.md; not stated; marker kept |
| Step 10 | Endpoint-managed settings do not reach Anthropic-hosted cloud sessions | Confirmed | https://code.claude.com/docs/en/server-managed-settings.md |  |
| Step 10 | Plugins declared in a repository's `.claude/settings.json` do not load in cloud sessions | Confirmed | https://code.claude.com/docs/en/cloud-environments.md |  |
| Step 10 | The starter kit delivers `twin-governance` through managed `enabledPlugins` | Confirmed | repo: starter-kit/settings/README.md |  |
| Step 10 | Whether the governance hook runs in a scheduled run and where its log lives | Unverified |  | Retried; no page says; marker kept |
| Step 11 | **Create** opens the detail page; the task runs at the next trigger; **Run now** on the detail page | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Step 12 | 100 runs per hour per account; Run now, API fires and one-off re-runs share 30 per hour per task; no overage; usage credits | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Step 13 | On/off switch, **Edit** and **Delete** in the name menu, `/schedule list`, `/schedule update`, `/schedule run` | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Check 1 | History rows end with **Error** or **Cancelled** | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Check 2 | Succeeded only means the session ended | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Check 4 | Default log `~/.claude/twin-governance/log.jsonl` via `TWIN_GOVERNANCE_LOG` | Confirmed | repo: starter-kit/plugins/twin-governance/README.md |  |
| Check 5 | Paused tasks keep their configuration and run again when switched on | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Hand over | What happens to the task when its owner leaves | Unverified |  | Retried on routines.md; not stated; marker kept |
| Can go wrong 1 | Causes of `/schedule` Unknown command (API key, cloud provider, signed out, cloud session, toggle off, custom role) | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Can go wrong 2 | A missing GitHub connection skips runs for up to 72 hours, then the task turns off | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Can go wrong 4 | Warnings beginning "The last run" explain runs that did not start | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Can go wrong 4 | Whether a missed run is replayed | Unverified |  | Retried on routines.md and scheduled-tasks.md; not stated; marker kept |
| Can go wrong 5 | A skill only in `~/.claude/skills/` is reported as not found | Confirmed | https://code.claude.com/docs/en/skills.md |  |
| Can go wrong 6 | A host outside the allowlist fails with `403` or `ENOTFOUND` | Confirmed | https://code.claude.com/docs/en/routines.md |  |
| Can go wrong 8 | A toggle turned off or a paused subscription stops the task | Confirmed | https://code.claude.com/docs/en/routines.md |  |

## claude-tag-routine.md (OPS-59)

| Line or step | Claim | State | Source URL | Old wording → new wording (corrections) |
|---|---|---|---|---|
| What this is | Routine kinds: a scheduled job, a channel watch, a subscription to one pull request | Confirmed | https://claude.com/docs/claude-tag/users/proactivity.md |  |
| What this is | Runs on the channel's connections with a typed request's permissions; keeps running when its creator leaves | Confirmed | https://claude.com/docs/claude-tag/users/proactivity.md |  |
| What this is | Claude Tag is in public beta | Confirmed | https://claude.com/docs/claude-tag/users/proactivity.md |  |
| Inputs: Runs as | Channels and group DMs run as Claude's service accounts; a one-to-one DM runs on the person's own account | Confirmed | https://claude.com/docs/claude-tag/concepts/agent-identity.md |  |
| Inputs: Data class | Not available with ZDR, CMEK or the HIPAA configuration | Confirmed | https://claude.com/docs/claude-tag/admins/setup-overview |  |
| Inputs: Memory | Memory is per channel and anyone in the channel can read and change it | Confirmed | https://claude.com/docs/claude-tag/users/memory.md |  |
| Inputs: Memory | Workspace notes: from a public channel Claude also saves notes it reads in every channel | Corrected | https://claude.com/docs/claude-tag/users/memory.md | Memory is per channel and anyone in the channel can read and change it. → Memory is per channel and anyone in the channel can read and change it; from a public channel Claude can also save workspace notes, which it reads in every channel, private ones included. |
| Before you start 1 | Team or Enterprise plan on Anthropic's first-party service | Confirmed | https://claude.com/docs/claude-tag/overview.md |  |
| Before you start 2 | **Organization settings > Capabilities > Remote sessions > Routines**; while off, Claude answers that it is unavailable | Confirmed | https://claude.com/docs/claude-tag/admins/setup-overview |  |
| Before you start 3 | Owner role, a Slack workspace admin, usage credits on a Team plan | Confirmed | https://claude.com/docs/claude-tag/admins/setup-overview |  |
| Step 1 | `claude.ai/admin-settings/claude-tag`, **Start setup**, claude.com/claude-for-slack, `/invite @Claude`, `@Claude connect`, 15-minute code, **Paste the pairing code**, **Pair workspace**, **Launch Claude Tag** | Confirmed | https://claude.com/docs/claude-tag/admins/setup-overview |  |
| Step 2 | Guests off by default; **How should Claude work in channels with guests**; **Restrict** posts no notice; guests can read posts; no routines in Slack Connect | Confirmed | https://claude.com/docs/claude-tag/admins/restrict-access.md |  |
| Step 2 | The Slack menu path to list a channel's members and guests | Unverified |  | Retried; no accepted page gives it (slack.com is not on this card's list); marker kept |
| Step 3 | Anyone in a channel where a connector applies can use it; Claude can never exceed what the key allows | Confirmed | https://claude.com/docs/claude-tag/admins/add-connections.md |  |
| Step 4 | **Organization settings > Claude Tag**, **Connectors** tab, **Add**, **Custom connector**, **Advanced** tab, **Allowed websites**, **Connect** | Confirmed | https://claude.com/docs/claude-tag/admins/add-connections.md |  |
| Step 5 | A first credential is on everywhere; **Slack** row under **Assign access**, **Add place**, **Save changes**; **Bundles** tab and **Where it applies** | Confirmed | https://claude.com/docs/claude-tag/admins/add-connections.md |  |
| Step 6 | Plugin plus credential; remote server only, not stdio; a cloned repository's `.mcp.json` is not loaded | Confirmed | https://claude.com/docs/claude-tag/admins/connections/custom.md |  |
| Step 7 | The **Credential type** list, nine entries, character for character | Confirmed | https://claude.com/docs/claude-tag/admins/connections/custom.md |  |
| Step 8 | **Skills and plugins** tab, **What's in it**, **Plugin**; changes apply to new threads only | Confirmed | https://claude.com/docs/claude-tag/admins/add-connections.md |  |
| Step 9 | Schedules run in UTC; Slack-profile time zone when none is named; at most once an hour | Confirmed | https://claude.com/docs/claude-tag/users/proactivity.md |  |
| Step 10 | Watch and pull-request subscription syntax; a subscription is the only GitHub event trigger | Confirmed | https://claude.com/docs/claude-tag/users/proactivity.md |  |
| Step 10 | A watch of another channel needs Claude to be a member of it | Confirmed | https://claude.com/docs/claude-tag/concepts/how-it-works.md |  |
| Step 11 | Thread reporting; a top-level routine announces each run and works in the thread under it | Confirmed | https://claude.com/docs/claude-tag/users/proactivity.md |  |
| Step 12 | `@Claude remember for this channel:` syntax; keep it short; members can list, change or forget; Owner edits under **Activity**, **Memory** tab | Confirmed | https://claude.com/docs/claude-tag/users/memory.md |  |
| Step 12 | A setting that turns channel memory off | Unverified |  | Retried on memory.md, settings-map.md and audit.md; none shown; marker kept |
| Step 13 | Routines never use personal connectors | Confirmed | https://claude.com/docs/claude-tag/concepts/personal-connectors.md |  |
| Step 13 | **Tools and access** tab of the **Configure** page; **Auto mode allow rules** per scope | Confirmed | https://claude.com/docs/claude-tag/concepts/settings-map.md |  |
| Step 14 | **Scheduled work** tab at `claude.ai/admin-settings/claude-tag/audit`; service-account logs; Compliance API transcripts on Enterprise | Confirmed | https://claude.com/docs/claude-tag/admins/audit.md |  |
| Step 15 | `@Claude !scheduled` lists routines in UTC; changes by plain request | Confirmed | https://claude.com/docs/claude-tag/users/proactivity.md |  |
| Step 15 | **Pause**, **Resume**, **Delete** in a row's **⋮** menu | Confirmed | https://claude.com/docs/claude-tag/admins/audit.md |  |
| Check 3 | **View details** shows **Created by** | Confirmed | https://claude.com/docs/claude-tag/admins/audit.md |  |
| Hand over | A channel's routines survive their creator leaving; anyone in the channel can disable them | Confirmed | https://claude.com/docs/claude-tag/users/proactivity.md |  |
| Hand over | A one-to-one DM routine is turned off when its owner is removed from the organization | Confirmed | https://claude.com/docs/claude-tag/users/proactivity.md |  |
| Can go wrong 2 | Fixed UTC time; daylight saving shifts the local time | Confirmed | https://claude.com/docs/claude-tag/users/proactivity.md |  |
| Can go wrong 3 | Slack Connect: no routines, earlier routines do not run | Confirmed | https://claude.com/docs/claude-tag/admins/restrict-access.md |  |
| Can go wrong 4 | Output boundaries; a group DM routine posts only there | Confirmed | https://claude.com/docs/claude-tag/users/proactivity.md |  |
| Can go wrong 5 | **Access from** table, **Not enabled**, **Enable** | Confirmed | https://claude.com/docs/claude-tag/admins/add-connections.md |  |
| Can go wrong 5 | A host no allow layer covers is blocked | Confirmed | https://claude.com/docs/claude-tag/concepts/agent-identity.md |  |
| Can go wrong 6 | A running thread keeps the plugins it began with | Confirmed | https://claude.com/docs/claude-tag/admins/add-connections.md |  |
| Can go wrong 8 | Failure notice to the creator when their Slack account is connected | Confirmed | https://claude.com/docs/claude-tag/users/proactivity.md |  |
| Can go wrong 8 | Whether a run missed while Claude Tag was down is replayed | Unverified |  | Retried on proactivity.md and audit.md; not stated; marker kept |

## managed-agents.md (OPS-59)

| Line or step | Claim | State | Source URL | Old wording → new wording (corrections) |
|---|---|---|---|---|
| Read this first | Managed Agents is in beta | Confirmed | https://platform.claude.com/docs/en/managed-agents/overview |  |
| Inputs: Data class | Hosted transcripts persist until you delete them; not eligible for ZDR or HIPAA | Confirmed | https://platform.claude.com/docs/en/managed-agents/overview |  |
| Before you start 1 | Vaults and credentials are workspace-scoped; any key with workspace access can use them | Confirmed | https://platform.claude.com/docs/en/managed-agents/vaults |  |
| Before you start 2 | Beta header `managed-agents-2026-04-01` on every request; the SDKs set it | Confirmed | https://platform.claude.com/docs/en/managed-agents/overview |  |
| Before you start 4 | 300 create and 1,200 read requests per minute | Confirmed | https://platform.claude.com/docs/en/managed-agents/reference |  |
| Before you start 4 | Maximum 20 credentials per vault | Confirmed | https://platform.claude.com/docs/en/managed-agents/vaults |  |
| Before you start 4 | Maximum 8 memory stores per session | Confirmed | https://platform.claude.com/docs/en/managed-agents/memory |  |
| Before you start 4 | Maximum 1,000 scheduled deployments per organization | Confirmed | https://platform.claude.com/docs/en/managed-agents/scheduled-deployments |  |
| Step 1 | A create request that omits `networking` gets `unrestricted` | Confirmed | https://platform.claude.com/docs/en/managed-agents/environments |  |
| Step 1 | Environment sample: curl flags | Corrected | https://platform.claude.com/docs/en/managed-agents/environments | `curl -fsSL https://api.anthropic.com/v1/environments` → `curl -fsS https://api.anthropic.com/v1/environments` (the page's sample) |
| Step 1 | Sample body `python-dev`, `limited`, `allow_package_managers`; `allowed_hosts` and `allow_mcp_servers` exist | Confirmed | https://platform.claude.com/docs/en/managed-agents/environments |  |
| Step 2 | Skill upload: `curl -X POST "https://api.anthropic.com/v1/skills"`, `anthropic-version: 2026-10-21`, `files[]=@example_skill.zip`; returns the `skill_*` ID | Confirmed | https://platform.claude.com/docs/en/managed-agents/skills |  |
| Step 3 | Agent sample: `curl -fsSL`, `Coding Assistant`, `claude-opus-5-5`, `agent_toolset_20260401`; response has `id` and `version` | Confirmed | https://platform.claude.com/docs/en/managed-agents/agent-setup |  |
| Step 3 | Skill attachment `{"type": "custom", "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv", "version": "latest"}` | Confirmed | https://platform.claude.com/docs/en/managed-agents/skills |  |
| Step 3 | A fixed skill `version` is accepted: "Pin to a specific version or use `latest`" | Corrected | https://platform.claude.com/docs/en/managed-agents/skills | **⚠ Unverified:** [E] shows `"latest"` only; confirm that a numbered version is accepted. → `version` pins a specific version or uses `latest` ([E]). |
| Step 4 | The agent toolset defaults to `always_allow` | Confirmed | https://platform.claude.com/docs/en/managed-agents/agent-setup |  |
| Step 4 | The `default_config: { enabled: false }` sample with `bash` and `read` comes from the Tools page, not [B] | Corrected | https://platform.claude.com/docs/en/managed-agents/tools | Sample from [B]; → Sample from [U], cut to two tools; (and [U] Tools added to Pages used) |
| Step 5 | `mcp_servers` plus a matching `{"type": "mcp_toolset", "mcp_server_name": "github"}`; `default_config` and `configs` on the toolset; credentials come from a vault | Confirmed | https://platform.claude.com/docs/en/managed-agents/mcp-connector |  |
| Step 6 | Policies are `always_allow`, `always_ask` and `auto` | Confirmed | https://platform.claude.com/docs/en/managed-agents/permission-policies |  |
| Step 6 | `always_ask` pauses until `user.tool_confirmation` with `"allow"` or `"deny"` | Confirmed | https://platform.claude.com/docs/en/managed-agents/permission-policies |  |
| Step 6 | MCP toolsets default to `always_ask` | Confirmed | https://platform.claude.com/docs/en/managed-agents/permission-policies |  |
| Step 6 | How `auto` maps to our autonomy ladder | Unverified |  | Retried: the page explains `auto` (runs, denies or pauses) but not our ladder; marker kept |
| Step 7 | `GET /v1/agents/$AGENT_ID/versions`; `version` increments on a change; no-op updates create none | Confirmed | https://platform.claude.com/docs/en/managed-agents/agent-setup |  |
| Step 8 | Credentials keyed by `mcp_server_url`, unique per vault, secret fields write-only | Confirmed | https://platform.claude.com/docs/en/managed-agents/vaults |  |
| Step 8 | Vault sample `curl --fail-with-body -sS`, `Alice`, `external_user_id`; auth types `mcp_oauth` and `static_bearer` | Confirmed | https://platform.claude.com/docs/en/managed-agents/vaults |  |
| Step 9 | With a `refresh` block Anthropic refreshes the token; `metadata` maps the vault to your user | Confirmed | https://platform.claude.com/docs/en/managed-agents/vaults |  |
| Step 9 | Whether Anthropic offers a hosted sign-in screen for the first token | Unverified |  | Retried on vaults and mcp-connector; none shown; marker kept |
| Step 10 | Webhook event `vault_credential.refresh_failed` | Confirmed | https://platform.claude.com/docs/en/managed-agents/webhooks |  |
| Step 11 | `access` defaults to `read_write`; `read_only` supported; prompt-injection warning; 100 kB per memory, 10,000 per store | Confirmed | https://platform.claude.com/docs/en/managed-agents/memory |  |
| Step 12 | Agent ID string takes the latest version; `{"type": "agent", "id": ..., "version": 1}` pins one; `initial_events` with `user.message` | Confirmed | https://platform.claude.com/docs/en/managed-agents/sessions |  |
| Step 12 | The session body with `vault_ids` and `title` is the Vaults page's sample | Corrected | https://platform.claude.com/docs/en/managed-agents/vaults | Body from [H]; → Body from [G]; |
| Step 12 | Budget `{"type": "limit", "max_list_cost": {"amount": "125", "currency": "USD"}}`; a session at its budget pauses | Confirmed | https://platform.claude.com/docs/en/managed-agents/budgets |  |
| Step 13 | Deployment sample: `?beta=true` URL, `Weekly compliance scan`, `0 20 * * 5`, `America/New_York` | Confirmed | https://platform.claude.com/docs/en/managed-agents/scheduled-deployments |  |
| Step 13 | The budget bounds every run separately, not the total | Confirmed | https://platform.claude.com/docs/en/managed-agents/scheduled-deployments |  |
| Step 13 | A deployment keeps its agent version; update it with the agent ID to move | Confirmed | https://platform.claude.com/docs/en/managed-agents/scheduled-deployments |  |
| Step 13 | Jitter up to 15 percent, at least 5 seconds, at most 9 minutes; missed triggers not backfilled; avoid 1 to 3 AM; `schedule.upcoming_runs_at` | Confirmed | https://platform.claude.com/docs/en/managed-agents/scheduled-deployments |  |
| Step 14 | Whether session creation accepts an idempotency key | Unverified |  | Retried: no Managed Agents page read mentions one; marker kept |
| Step 15 | Webhook delivery attempts | Corrected | https://platform.claude.com/docs/en/managed-agents/webhooks | Anthropic's own webhooks retry up to three times with the same `event.id` → Anthropic's own webhooks make up to three delivery attempts with the same `event.id` |
| Step 15 | Duplicates carry the same `event.id`; an event emitted while no endpoint subscribes is never delivered | Confirmed | https://platform.claude.com/docs/en/managed-agents/webhooks |  |
| Step 16 | Dropped after three attempts; no ordering guarantee; "aren't a durable log"; HTTPS on port 443; fetch the object by ID | Confirmed | https://platform.claude.com/docs/en/managed-agents/webhooks |  |
| Step 16 | Stream `GET .../sessions/$SESSION_ID/events/stream?beta=true` with `accept: text/event-stream` | Confirmed | https://platform.claude.com/docs/en/managed-agents/events-and-streaming |  |
| Step 17 | Update with the last-read `version`, or the request returns 409 | Confirmed | https://platform.claude.com/docs/en/managed-agents/agent-setup |  |
| Step 18 | "Anthropic might refine behaviors between releases" | Confirmed | https://platform.claude.com/docs/en/managed-agents/overview |  |
| Step 18 | Header `anthropic-version: 2026-10-21` | Confirmed | https://platform.claude.com/docs/en/managed-agents/agent-setup |  |
| Self-hosted 1 | Access through the account team or by switching organization; `operator-guide.md` in each release archive | Confirmed | https://platform.claude.com/docs/en/managed-agents/self-hosted |  |
| Self-hosted 2 | `cma-server`, PostgreSQL 16 or later, workers; model at Anthropic or a chosen provider | Confirmed | https://platform.claude.com/docs/en/managed-agents/self-hosted |  |
| Self-hosted 2 | Self-hosted sandboxes keep the service at Anthropic and move tool execution only | Confirmed | https://platform.claude.com/docs/en/managed-agents/choosing-an-environment |  |
| Self-hosted 3 | Each model call carries the conversation, tool inputs and results, and session, agent and environment IDs; the agreement's retention applies | Confirmed | https://platform.claude.com/docs/en/managed-agents/self-hosted-data-and-access |  |
| Self-hosted 4 | No scheduled deployments, no webhooks, `mcp_oauth` rejected | Confirmed | https://platform.claude.com/docs/en/managed-agents/self-hosted/differences |  |
| Check 1 | A finished turn idles with `end_turn` | Confirmed | https://platform.claude.com/docs/en/managed-agents/events-and-streaming |  |
| Check 2 | `session.status_idle` with `requires_action`; `user.tool_confirmation` with `"result": "deny"` | Confirmed | https://platform.claude.com/docs/en/managed-agents/permission-policies |  |
| Check 4 | The Console session viewer shows cost and spend against the budget | Confirmed | https://platform.claude.com/docs/en/managed-agents/session-observability |  |
| Hand over | `{"type": "user.interrupt"}` ends the turn with `session.status_idle` | Confirmed | https://platform.claude.com/docs/en/managed-agents/events-and-streaming |  |
| Hand over | `POST /v1/deployments/$DEPLOYMENT_ID/pause?beta=true` | Confirmed | https://platform.claude.com/docs/en/managed-agents/scheduled-deployments |  |
| Hand over | `POST /v1/agents/$AGENT_ID/archive`: new sessions stop, running ones continue | Confirmed | https://platform.claude.com/docs/en/managed-agents/agent-setup |  |
| Hand over | Deleting the vault revokes its credentials | Confirmed | https://platform.claude.com/docs/en/managed-agents/vaults |  |
| Can go wrong 3 | An unrecoverable trigger error pauses the deployment; `deployment_runs` with `has_error=true` | Confirmed | https://platform.claude.com/docs/en/managed-agents/scheduled-deployments |  |
| Can go wrong 5 | A 3xx disables an endpoint | Confirmed | https://platform.claude.com/docs/en/managed-agents/webhooks |  |

## agent-sdk-runner.md (OPS-59)

| Line or step | Claim | State | Source URL | Old wording → new wording (corrections) |
|---|---|---|---|---|
| Read this first | TypeScript names differ in case (`allowedTools`, `permissionMode`) | Confirmed | https://code.claude.com/docs/en/agent-sdk/permissions.md |  |
| Inputs: Data class | Whether the Agent SDK is covered by ZDR or HIPAA | Unverified |  | Retried on api-and-data-retention and the SDK overview; neither names the Agent SDK; marker kept |
| Inputs: Memory | What the SDK keeps as memory: `CLAUDE.md` files and auto memory on the container's disk, lost on restart, off with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` | Corrected | https://code.claude.com/docs/en/agent-sdk/hosting.md | The SDK pages we read describe no memory store ([02]). → The SDK pages we read describe no memory store, only `CLAUDE.md` files and auto memory on the container's disk, which a restart loses and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` turns off ([G], [02]). |
| Before you start 1 | Python 3.10 or later, or Node.js 18.14 or later | Confirmed | https://code.claude.com/docs/en/agent-sdk/hosting.md |  |
| Before you start 2 | 1 GiB RAM, 5 GiB disk and 1 CPU per agent as a starting point | Confirmed | https://code.claude.com/docs/en/agent-sdk/hosting.md |  |
| Before you start 3 | Outbound HTTPS to `api.anthropic.com` and to each MCP server | Confirmed | https://code.claude.com/docs/en/agent-sdk/hosting.md |  |
| Before you start 5 | The SDK spawns a `claude` CLI subprocess that owns a shell, a working directory and session files | Confirmed | https://code.claude.com/docs/en/agent-sdk/hosting.md |  |
| Before you start 5 | The agent runs inside the container's isolation boundary | Confirmed | https://code.claude.com/docs/en/agent-sdk/secure-deployment.md |  |
| Step 1 | The bundled native binary is pinned to the package version; semver; patch releases, read the changelog before a minor | Confirmed | https://code.claude.com/docs/en/agent-sdk/hosting.md |  |
| Step 1 | `model` takes an alias or a full model name | Confirmed | https://code.claude.com/docs/en/agent-sdk/python.md |  |
| Step 2 | The skills sample (`cwd`, `setting_sources=["user", "project"]`, `skills="all"`, `allowed_tools`) and comments, character for character | Confirmed | https://code.claude.com/docs/en/agent-sdk/skills.md |  |
| Step 2 | Setting `setting_sources` without `user` and `project` stops skills loading; `ClaudeAgentOptions(skills=["pdf", "docx"])` | Confirmed | https://code.claude.com/docs/en/agent-sdk/skills.md |  |
| Step 3 | `system_prompt` forms: string, custom object, file object, `claude_code` preset | Confirmed | https://code.claude.com/docs/en/agent-sdk/python.md |  |
| Step 4 | `allowed_tools` auto-approves and does not restrict | Confirmed | https://code.claude.com/docs/en/agent-sdk/python.md |  |
| Step 4 | In `dontAsk` the callback step is skipped and the call is denied; a bare name in `disallowed_tools` removes the tool | Confirmed | https://code.claude.com/docs/en/agent-sdk/permissions.md |  |
| Step 5 | `can_use_tool` runs only when the flow falls through to a prompt, not for calls an allow rule approved | Confirmed | https://code.claude.com/docs/en/agent-sdk/python.md |  |
| Step 5 | Hooks run first, can deny outright, before the mode step that `bypassPermissions` uses | Confirmed | https://code.claude.com/docs/en/agent-sdk/permissions.md |  |
| Step 5 | `bypassPermissions` approves each call that reaches the mode step | Confirmed | https://code.claude.com/docs/en/agent-sdk/permissions.md |  |
| Step 6 | `strict_mcp_config=True` ignores project `.mcp.json` and claude.ai connectors | Confirmed | https://code.claude.com/docs/en/agent-sdk/python.md |  |
| Step 6 | MCP sample `remote-api`, `sse`, `headers`, `mcp__remote-api__*`; names `mcp__<server-name>__<tool-name>` | Confirmed | https://code.claude.com/docs/en/agent-sdk/mcp.md |  |
| Step 7 | `ANTHROPIC_API_KEY` from the environment, or `ANTHROPIC_BASE_URL` to a key-injecting proxy | Confirmed | https://code.claude.com/docs/en/agent-sdk/hosting.md |  |
| Step 7 | Credentials outside the boundary via an MCP server or tool, or a proxy that injects them and keeps an allowlist | Confirmed | https://code.claude.com/docs/en/agent-sdk/secure-deployment.md |  |
| Step 7 | Per-run credentials passed in an MCP server's `headers` or `env` | Confirmed | https://code.claude.com/docs/en/agent-sdk/mcp.md |  |
| Step 8 | `PostToolUse` and `PostToolUseFailure` hooks; return `{}` to allow; the `protect_env_files(input_data, tool_use_id, context)` pattern | Confirmed | https://code.claude.com/docs/en/agent-sdk/hooks.md |  |
| Step 8 | An SDK plugin loaded by local path brings its hooks (`hooks/hooks.json`) | Corrected | https://code.claude.com/docs/en/agent-sdk/plugins.md | **⚠ Unverified:** whether the twin-governance plugin's own `hooks.json` fires inside an SDK session; write the callback yourself and confirm ... → A plugin loaded by local path through the `plugins` option brings its hooks, `hooks/hooks.json` included ([K]), so the twin-governance plugin can be loaded instead of the callback; either way confirm ... ([K] added to Pages used) |
| Step 9 | `CLAUDE_CODE_ENABLE_TELEMETRY=1`, `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` for traces only, `OTEL_TRACES_EXPORTER=otlp`; prompt text and tool inputs off by default | Confirmed | https://code.claude.com/docs/en/agent-sdk/hosting.md |  |
| Step 10 | No top-level session timeout; set `max_turns` | Confirmed | https://code.claude.com/docs/en/agent-sdk/hosting.md |  |
| Step 10 | `max_budget_usd`; the estimate can pass the cap, leave headroom | Confirmed | https://code.claude.com/docs/en/agent-sdk/python.md |  |
| Step 10 | `ResultMessage` subtypes include `success`, `error_max_turns`, `error_max_budget_usd` | Confirmed | https://code.claude.com/docs/en/agent-sdk/python.md |  |
| Step 11 | One-shot entrypoint reading `TASK_PROMPT`, calls the SDK and exits | Confirmed | https://code.claude.com/docs/en/agent-sdk/hosting.md |  |
| Step 11 | Shared container: `setting_sources=[]`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, per-tenant `CLAUDE_CONFIG_DIR` and `cwd` | Confirmed | https://code.claude.com/docs/en/agent-sdk/hosting.md |  |
| Step 12 | Proxy that enforces domain allowlists, injects credentials and logs all traffic | Confirmed | https://code.claude.com/docs/en/agent-sdk/secure-deployment.md |  |
| Step 13 | Built-in dedupe or event intake in the SDK | Unverified |  | Retried on the overview and hosting pages; none described; marker kept |
| Step 14 | `ClaudeSDKClient` holds a session open across turns | Confirmed | https://code.claude.com/docs/en/agent-sdk/hosting.md |  |
| Step 15 | Agent SDK release status | Unverified |  | Retried on the overview; no status stated; marker kept |
| Check 1 | A finished task returns subtype `success` | Confirmed | https://code.claude.com/docs/en/agent-sdk/agent-loop.md |  |
| Can go wrong 5 | Error subtypes carry no `result` field | Confirmed | https://code.claude.com/docs/en/agent-sdk/agent-loop.md |  |
| Can go wrong 6 | Container-local state does not survive a restart | Confirmed | https://code.claude.com/docs/en/agent-sdk/hosting.md |  |
| Can go wrong 8 | "Claude Code is not covered under HIPAA readiness" | Confirmed | https://platform.claude.com/docs/en/manage-claude/api-and-data-retention.md |  |
| Can go wrong 8 | The other vendor page: a Console API key session is not eligible for the HIPAA configuration, so it does not disagree for this runner | Corrected | https://code.claude.com/docs/en/hipaa-setup.md | but other vendor pages disagree (see [10]). → and the HIPAA setup page lists a session on a Claude Console API key, as this runner uses, as not eligible for the HIPAA configuration ([L]); see also [10]. ([L] added to Pages used) |

## hubspot-connector.md (OPS-60)

| Line or step | Claim | State | Source URL | Old wording → new wording (corrections) |
|---|---|---|---|---|
| What this is | HubSpot publishes the connector; the listing carries "Anthropic verified" ("Made by HubSpot") | Confirmed | https://claude.com/connectors/hubspot |  |
| What this is | The listing says "Added November 2025" | Confirmed | https://claude.com/connectors/hubspot |  |
| What this is | Quote and quote-template create and update, HubSpot Work projects and HubSpot Work tables are labelled beta | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| What this is | Whether the connector as a whole is generally available | Unverified |  | Retried on [A], [B], [F] and [G]; none states a release status; marker kept |
| Roles table | "Super Admins and users with App Marketplace Access permissions can connect … without prior app approval. For all other users to connect, a Super Admin must first approve the connector" | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Inputs: identity | Each user acts under their own HubSpot account: "users will only see in Claude the CRM data they're allowed to access in HubSpot" | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Inputs: surfaces | Covers web, desktop and mobile | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Inputs: surfaces | The `hubspot` entry in the plugin points to `https://mcp.hubspot.com/anthropic`; the listing's "Connector URL" is the same | Confirmed | https://claude.com/connectors/hubspot |  |
| Inputs: surfaces | Connectors added in claude.ai are available in Claude Code when signed in with a Claude account | Confirmed | https://claude.com/docs/connectors/getting-started.md |  |
| Inputs: Sensitive Data | "with it on, Claude cannot access any engagement data" | Corrected | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude | It decides whether the twin can use engagement data at all: with it on, Claude cannot access any engagement data ([A]) → With it on, the connector reaches Sensitive Data properties and engagements only if a Super Admin grants it read-only access to them during installation or reauthentication, and the user also needs the matching HubSpot permissions ([A]). Page: "a Super Admin can grant the connector read-only access to Sensitive Data properties and engagements during installation or reauthentication" |
| Before you start 1 | Paid tiers Pro, Max, Team or Enterprise; web, desktop and mobile | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Before you start 2 | "All products and plans"; an active HubSpot user account and an active Claude account | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Before you start 3 | "On Team and Enterprise plans, an Owner adds a connector for the organization, and members then connect with their own account" | Confirmed | https://claude.com/docs/connectors/getting-started.md |  |
| Before you start 4 | Super Admin or App Marketplace Access user available; others need approval first | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Step 1 | Who connects without approval, and that a Super Admin approves for everyone else and picks the optional data permissions | Corrected | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude | and chooses which optional data permissions it may access. → and chooses which optional data permissions it may access and who in the account is allowed to install it. Page: "you can also select which optional data permissions the connector can access and who in the account is allowed to install it" |
| Step 2 | Settings icon > **Integrations** > **Connected Apps** > **Approved apps** tab > HubSpot Connector for Claude > **Manage access**; tabs **Installed Permissions** and **Data permissions** | Confirmed | https://knowledge.hubspot.com/integrations/set-up-enterprise-managed-authentication-in-claude |  |
| Step 2 | Older path "Connected Apps > HubSpot connector for Claude > Give users access" | Confirmed | https://developers.hubspot.com/changelog/claude-connector-additional-objects-and-admin-controls |  |
| Step 2 | New objects need a Super Admin to update data permissions, then each user reconnects | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Step 2 | What each tab offers for restricting a pilot group (was unverified) | Corrected | https://knowledge.hubspot.com/integrations/set-up-enterprise-managed-authentication-in-claude | **⚠ Unverified:** what each tab offers for restricting a pilot group; neither page lists it. Confirm on screen and record it. → **Installed Permissions** sets who can connect to the app (HubSpot users and teams) …; **Data permissions** sets the data and APIs it can access, applies to all users, including admins, and required permissions can't be turned off. ([F]) Page: "HubSpot install permissions: Which HubSpot users and teams are allowed to connect to the app"; "HubSpot's app data permissions apply to all users, including admins. Required permissions can't be turned off." |
| Step 3 | **Organization settings > Connectors**, **Browse connectors**, select, **Add to your team**; adding grants no access, each person authenticates | Confirmed | https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities |  |
| Step 3 | "The directory page names the same two places for an Owner" | Corrected | https://claude.com/docs/connectors/directory.md | The directory page names the same two places for an Owner. → The directory page also names **Organization settings > Connectors** as the Owner's way in. Page: "Organization settings > Connectors for Team and Enterprise Owners" |
| Step 4 | Whether a Team plan can show the connector to one Claude group | Unverified |  | Retried on [C], [D], [E] and [H]; the role article covers Enterprise only and no page describes Team-plan scoping; marker kept |
| Step 4 | Enterprise: **Organization settings > Roles**, open the role, **Connectors** tab, dropdown **Always allow**, **Needs approval**, **Blocked** or **Custom** | Confirmed | https://support.claude.com/en/articles/13930458-set-up-role-based-permissions-on-enterprise-plans |  |
| Step 4 | "A newly created role defaults to "Needs approval" on every connector" | Confirmed | https://support.claude.com/en/articles/13930458-set-up-role-based-permissions-on-enterprise-plans |  |
| Step 4 | **Custom** sets each tool individually | Confirmed | https://support.claude.com/en/articles/13930458-set-up-role-based-permissions-on-enterprise-plans |  |
| Step 4 | Org-wide tool setting is a ceiling; roles narrow and cannot widen: "role grants narrow within it and can't widen past it" | Confirmed | https://support.claude.com/en/articles/13930458-set-up-role-based-permissions-on-enterprise-plans |  |
| Step 4 | Narrowing "the other roles here" holds only for a member with one role | Corrected | https://support.claude.com/en/articles/13930458-set-up-role-based-permissions-on-enterprise-plans | and narrow the other roles here. → and narrow the other roles here; grants add up across roles, so a member who holds two roles gets the more permissive one ([E]). Page: "connector permissions are additive across roles … the most permissive grant is the one that applies" |
| Step 4 | The HubSpot-side restriction is "the only candidate control, and it is unconfirmed" | Corrected | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude | the HubSpot-side restriction in step 2 is the only candidate control, and it is unconfirmed (its options are marked unverified there). → the HubSpot-side install permissions in step 2 are the only control ([A], [F]). Page: "During approval, Super Admins select which data permissions the connector can access and who in the account can install it" |
| Step 5 | **Customize > Connectors**, **Tool permissions**, **Always allow**, **Needs approval** or **Blocked** per category or tool; org-wide, users cannot override | Confirmed | https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities |  |
| Step 5 | The listing names 24 tools and "Show all 36 tools" | Corrected | https://claude.com/connectors/hubspot | the page says "Show all 36 tools" but lists 24. → then "Show all 36 tools"; the other 12 in the page's data are `read_campaign_data`, `render_asset`, `search_conversations`, `search_crm_objects`, `search_intent_signals`, `search_owners`, `search_properties`, `show_feedback_form`, `tool_guidance`, `update_task`, `ask_breeze` and `discover_hubspot_schema`. The 24 names were compared character by character with the page |
| Step 5 | Which tools are read and which write | Unverified |  | Retried: the listing gives names only, and [A] lists objects, not tools; marker kept |
| Step 6 | HubSpot recommends "set Write tools to Needs Approval"; "If you set the connector to Always allow, edits may occur without asking for approval" | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Step 6 | Whether the screen groups tools as "Write tools" | Unverified |  | Retried: Claude's help center says "The permissions will be categorized by type (for example, read-only tools, write/delete tools)", which does not name HubSpot's group; marker kept, that sentence added before it ([D]) |
| Step 6 | Create and update on contacts, leads, companies, deals, tickets, custom objects and activable objects, no delete; engagements read, create, update; conversations read-only; at most 10 records at a time | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Step 6 | The writes listed are all the connector supports | Corrected | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude | conversations are read-only. At most 10 records → conversations are read-only. The article lists more writes, among them line items, products, pipelines, landing pages, website pages, blog posts, marketing emails, segments and social posts. At most 10 records |
| Step 7 | "Go to **Customize > Connectors** and select **Connect** on HubSpot. ([C])" | Corrected | https://claude.com/docs/connectors/getting-started.md | select **Connect** on HubSpot → select **Discover**, find HubSpot and select **Connect to Claude**. Page: "Select **Discover** to browse the directory"; "Select **Connect to Claude**" |
| Step 7 | profile icon > **Settings** > **Connectors** > **Browse**, search, **Connect**; "Connecting HubSpot Connector for Claude to HubSpot" page; **Connect app** | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Step 7 | Which permissions the connect screen lists | Unverified |  | Retried on [A] and [F]; [A] says to select them and names none; marker kept |
| Step 8 | **+** > **Connectors**, toggle HubSpot on | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Step 9 | Each tool's **Tool permissions** setting is read at **Customize > Connectors** | Confirmed | https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities |  |
| Read test | The connector runs under the user's own HubSpot permissions | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Read test | "If Sensitive Data is on, an engagement question should fail" | Corrected | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude | should fail: with it on, Claude cannot access any engagement data. → should fail unless a Super Admin granted the connector read-only access to Sensitive Data properties and engagements. |
| Write test | **Needs approval**: **Allow once** to continue | Confirmed | https://claude.com/docs/connectors/getting-started.md |  |
| Write test | HubSpot has you "type Yes to confirm them or type No to cancel" | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Write test | **Blocked**: the note is not created, tagged [C] | Corrected | https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities | The note is not created. ([C]) → The note is not created. ([D]). [C] only names the option; [D]: "you can allow a connector to read data from a service while preventing it from writing any changes back" |
| Write test | The exact message Claude shows for a blocked tool | Unverified |  | Retried: the role article gives "I don't have a tool for that" for a tool a role does not grant, not for the org-wide **Blocked** setting; marker kept |
| Write test | Audit Log attribution to the user and the connector; Super Admins see connections and all create and update actions | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Write test | The connector cannot delete | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Hand over | User disconnect: profile icon > **Settings** > **Connectors** > **HubSpot** > **Disconnect** at the top right | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Hand over | An Owner removes a connector for the organization from **Organization settings > Connectors** | Confirmed | https://claude.com/docs/connectors/getting-started.md |  |
| Hand over | HubSpot-side revocation of one user's connection | Unverified |  | Retried on [A] and [F]; [F] says "review the Install Permissions tab to change who is allowed to connect to the app" and that issued tokens "can remain usable until it expires or is revoked", but no page describes revoking one connection; marker kept, wording now names the **Install Permissions** tab ([F]) |
| Can go wrong 1 | Connect fails for a user who is not a Super Admin or App Marketplace Access user; on Team and Enterprise the Owner must add it | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Can go wrong 2 | Write access and engagement visibility need a disconnect and reauthentication | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Can go wrong 3 | Sensitive Data on: no engagement data, custom Sensitive Data properties not accessible | Corrected | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude | HubSpot's Sensitive Data setting is on; Claude cannot access any engagement data, and custom Sensitive Data properties are not accessible. → HubSpot's Sensitive Data setting is on and a Super Admin has not granted the connector read-only access to Sensitive Data properties and engagements. Grant it during reauthentication. |
| Can go wrong 4 | **Always allow** lets writes run with no prompt; the org-wide setting cannot be overridden by users | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Can go wrong 5 | At most 10 records at a time | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Can go wrong 6 | Reference the Partner Client Object (PCO) explicitly | Confirmed | https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude |  |
| Can go wrong 7 | After an endpoint change the old connection keeps working and shows under **Custom**; remove and re-add | Confirmed | https://claude.com/docs/connectors/directory.md |  |
| Can go wrong 8 | Team-plan group scoping | Unverified |  | Same retry as step 4; marker kept |

## Sources that could not be read

| URL | How it failed (2026-11-15) |
|---|---|
| https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/activate-mcp-servers.html | HTTP 403 |
| https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/create-external-client-app.html (and `.md`) | HTTP 403 |
| https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_opportunityfieldhistory.htm | HTTP 403 |
| https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/setup-overview.html | HTTP 403 |
| https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/client-connection-overview.html | HTTP 403 |
| developer.salesforce.com Metadata API page for the MCP server External Client App (`meta-mcp-server-eca.html`) | HTTP 403 |
| https://help.salesforce.com/s/articleView?id=sales.what_is_salesforce_in_claude.htm&type=5 (and other help.salesforce.com articleView pages) | Returns a JavaScript shell only; no article text without a browser |
| https://github.com/anthropics/claude-code/tree/main/examples/mdm | Not opened: github.com/anthropics is not on the accepted Anthropic domain list |
| Jamf and Kandji (Iru) documentation | Not read: neither vendor is on the accepted domain list |
| https://support.microsoft.com/en-us/office/edit-permissions-for-a-list-library-or-individual-item-02d770f3-59eb-4910-a608-5f84cc297782 | Read, but support.microsoft.com is not on the accepted Microsoft domain list, so it does not confirm |
