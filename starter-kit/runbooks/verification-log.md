# Runbook verification log

- **Date checked:** 2026-11-15
- **Checked by:** Claude Opus 5.5 (`claude-opus-5-5`), task SHA-21
- **Runbooks:** [identity-devices-publishing.md](identity-devices-publishing.md), [salesforce-hosted-mcp.md](salesforce-hosted-mcp.md), [microsoft-365-connector.md](microsoft-365-connector.md)

| Runbook | Confirmed | Corrected | Unverified | Total |
|---|---|---|---|---|
| identity-devices-publishing.md | 55 | 16 | 4 | 75 |
| salesforce-hosted-mcp.md | 34 | 11 | 12 | 57 |
| microsoft-365-connector.md | 44 | 8 | 7 | 59 |

## How the check was done

- Every runbook was treated as untrusted. A source tag did not count as proof. Each numbered step, table row and factual product sentence was checked against the page it cites. Where there was no citation, or the citation did not support the claim, it was checked against the vendor's own docs.
- Accepted vendor domains: code.claude.com, platform.claude.com, claude.com/docs, support.claude.com and support.anthropic.com for Anthropic; help.salesforce.com, developer.salesforce.com and Salesforce's official GitHub for Salesforce; learn.microsoft.com for Microsoft; help.okta.com and developer.okta.com for Okta. Blogs, forums, search snippets and other third-party pages were not counted as confirmation.
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
| 9 | Refresh tokens expire after 90 days of inactivity by default | Confirmed | https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide | |
| 9 | Members disconnect in **Customize > Connectors**; Owner removes in **Organization settings > Connectors** | Confirmed | https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector | |

## Sources that could not be read

| URL | How it failed (2026-11-15) |
|---|---|
| https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/activate-mcp-servers.html | HTTP 403 |
| https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/create-external-client-app.html (and `.md`) | HTTP 403 |
| https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/setup-overview.html | HTTP 403 |
| https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/client-connection-overview.html | HTTP 403 |
| developer.salesforce.com Metadata API page for the MCP server External Client App (`meta-mcp-server-eca.html`) | HTTP 403 |
| https://help.salesforce.com/s/articleView?id=sales.what_is_salesforce_in_claude.htm&type=5 (and other help.salesforce.com articleView pages) | Returns a JavaScript shell only; no article text without a browser |
| https://github.com/anthropics/claude-code/tree/main/examples/mdm | Not opened: github.com/anthropics is not on the accepted Anthropic domain list |
| Jamf and Kandji (Iru) documentation | Not read: neither vendor is on the accepted domain list |
| https://support.microsoft.com/en-us/office/edit-permissions-for-a-list-library-or-individual-item-02d770f3-59eb-4910-a608-5f84cc297782 | Read, but support.microsoft.com is not on the accepted Microsoft domain list, so it does not confirm |
