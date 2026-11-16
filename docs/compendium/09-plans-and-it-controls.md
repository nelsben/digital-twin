# 09 — Plans, features and what IT can control

Our users are spread across every Claude plan. Some are on Team, some on Enterprise, and some bought individual licenses (Free, Pro, Max, Ultra) outside any company plan. This page shows what each plan gives you and what an IT team can control on each.

**The short version:**

- **Individual plans** are outside IT's reach. They run on consumer terms, which allow training on your data unless the user opts out and carry no confidentiality clause.
- **Team** gives central control over plugins, connectors and settings, but has no audit logs and can't absorb existing personal accounts.
- **Enterprise** is the only plan with group targeting, audit and compliance tooling, custom retention, ZDR, HIPAA and domain capture.

## Feature matrix

Y = yes, N = no, L = limited. Free, Pro, Max and Ultra share one column; where Free differs, the cell says so.

| Feature | Individual (Free / Pro / Max / Ultra) | Team | Enterprise |
|---|---|---|---|
| **Terms** | Consumer | Commercial | Commercial |
| **Used for model training by default** | **Yes, unless the user opts out** | No | No |
| Custom skills (personal) | Y on Pro and up. ⚠ Conflict for Free | Y (an Owner must turn on code execution) | Y |
| Org-provisioned skills and plugins | N | Y | Y |
| Targeting skills and plugins at groups | N | N | **Y** (via SCIM groups) |
| Connectors | Y, the user adds them (Free: 1 custom) | L: only an Owner adds custom connectors; members sign in | L: Owner, or a custom role with the Libraries permission |
| Per-tool connector permission (Allow / Approve / Block); the only autonomy control in chat and Cowork, set per tool, not per skill or task ([06](06-autonomy.md)) | User | Owner | Owner |
| Desktop extensions | Y | Y; allowlist or block via MDM | Y |
| Claude Code | Pro and up | Y | Y |
| Cowork | Pro and up | Y (cloud sessions on by default) | Y (cloud sessions off until turned on) |
| Claude Tag (Slack) | N | Y (beta) | Y (beta) |
| Claude Code scheduled tasks | Pro and up | Y; Owner can turn off | Y; Owner can turn off |
| Memory | User-controlled | Org-wide on/off only; admins can't view memories | Same, plus audit events |
| SSO / SAML | N | **⚠ Conflict:** the pricing page says Y, the roles article says Enterprise-only | Y |
| SCIM provisioning | N | N | Y |
| Domain verification / capture | N | Verify and block *new* sign-ups only | **Capture and migrate existing accounts** |
| Audit logs | N | N | Y (180 days) |
| Compliance API | N | N | Y |
| Usage analytics | N | Dashboard; adoption per plugin | Dashboard plus Analytics API |
| Custom data retention | N (training toggle only) | N | Y (minimum 30 days) |
| Zero data retention (ZDR) | N | N | L: qualified orgs, Claude Code only |
| HIPAA / BAA | N | N | Y (**permanent once on**) |
| Customer-managed encryption keys (CMEK) | N | N | L: eligible orgs |
| Spend controls | N | Y | Y, including per-user limits |
| Roles | None | User, Admin, Owner, Primary Owner | The same four, plus custom roles for groups |

**The API / Console** is a separate product with commercial terms. It offers SSO, tenant restrictions, HIPAA readiness and ZDR by arrangement, plus `inference_geo` for US-only processing. Claude Code running with a Console API key **bypasses claude.ai's server-managed settings**.

**Not in the matrix: hooks, the governance log and the agent runtimes.**

- **Managed settings and hooks:** server-managed settings "are available for Claude for Teams and Claude for Enterprise customers"; on Team they "apply uniformly to all users in the organization", and group configurations "require an Enterprise plan" ([Server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md)). **⚠ Unverified:** no page read gives a per-plan value for hooks themselves, or for a managed settings file delivered by MDM; the [hooks page](https://code.claude.com/docs/en/hooks) names surfaces, not plans.
- **The governance action log:** **⚠ Unverified:** no page read gives a per-plan value; it is our own build, resting on a Claude Code hook or a hosted agent's server log ([15](15-governance-and-performance.md#one-governance-log-for-all-twins-our-recommendation)).
- **Hosted Managed Agents:** configured through the Claude API, not a claude.ai plan ([Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview.md), [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview), beta). **⚠ Unverified:** no page read ties it to Free, Pro, Max, Ultra, Team or Enterprise.
- **Self-hosted Managed Agents:** by request: "To request access to self-hosted Claude Managed Agents, contact your Anthropic account team" ([Self-hosted Managed Agents](https://platform.claude.com/docs/en/managed-agents/self-hosted)). **⚠ Unverified:** no page read gives a per-plan value.
- **Agent SDK:** API key authentication, not a claude.ai plan: "Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK" ([Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview.md)). **⚠ Unverified:** no page read gives a per-plan value.

Sources: [Pricing](https://claude.com/pricing), [Skills](https://claude.com/docs/skills/overview.md), [Plugins admin](https://claude.com/docs/plugins/admin.md), [Connectors](https://claude.com/docs/connectors/getting-started.md), [Desktop policies](https://support.claude.com/en/articles/12622667), [Domain capture](https://support.claude.com/en/articles/14625619-claim-and-migrate-accounts-on-your-domain), [Roles](https://support.claude.com/en/articles/9267276), [Audit logs](https://support.claude.com/en/articles/9970975), [Compliance API](https://platform.claude.com/docs/manage-claude/compliance-api), [ZDR](https://code.claude.com/docs/en/zero-data-retention.md), [HIPAA](https://support.claude.com/en/articles/13296973), [CMEK](https://support.claude.com/en/articles/15505325), [Memory](https://support.claude.com/en/articles/11817273), [Claude Tag](https://claude.com/docs/claude-tag/overview.md), [Scheduled tasks](https://code.claude.com/docs/en/routines.md).

## What IT can do on each plan

| Lever | Individual | Team | Enterprise |
|---|---|---|---|
| Publish role plugins and skills to users | ✗ (users install them by hand) | ✓ to everyone | ✓ per group |
| Control which connectors exist, and per-tool permissions | ✗ | ✓ | ✓ |
| Lock Claude Code settings (allowed marketplaces, forced plugins, sandbox, deny rules) | Only via MDM on managed devices | ✓ server-managed settings, plus MDM | ✓ also per group (not yet in HIPAA orgs) |
| Lock Claude Desktop (extensions, Claude Code, Cowork, folders) | Only via MDM on managed devices | ✓ MDM keys | ✓ |
| Force sign-in to *our* org (`forceLoginOrgUUID`) | Only via MDM on managed devices | ✓ via MDM | ✓ via MDM |
| Stop new personal accounts on our domain | ✗ | ✓ verify the domain, then "Restrict organization creation" | ✓ |
| Absorb existing personal accounts | ✗ | ✗ | ✓ domain capture (users migrate within 30 days, or the account is deleted) |
| Block other Claude orgs on the corporate network | ✗ | ✗ | ✓ tenant restrictions, through a TLS-inspecting proxy |
| See who did what | ✗ | Usage dashboard | Audit logs, Compliance API |
| Offboard | ✗ | Remove the member | SCIM removal; Support for permanent deletion |

Sources: [Server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md), [Claude Code org plugins](https://code.claude.com/docs/en/plugins/org.md), [Authentication](https://code.claude.com/docs/en/authentication.md), [SSO and domain](https://support.claude.com/en/articles/13132885), [Tenant restrictions](https://support.claude.com/en/articles/13198485).

## What this means for the rollout (our recommendation)

1. **Make Team the minimum for anyone who uses a twin on company data.** Individual plans give IT no control, use consumer terms and train on data by default.
2. **Use Enterprise for the HIPAA and private-equity roles,** and wherever you need group targeting, audit or domain capture.
3. **Mixed estate: a migration path.**
   - Verify the domain and block new personal sign-ups.
   - Move people with individual licenses onto the company plan.
   - On Enterprise, use domain capture, but plan it: it's a one-way step, and accounts not migrated within 30 days are deleted.
4. **Design twins to work on Team.** Then they work on Enterprise too. Use Enterprise-only features (group targeting, the Compliance API) as extras, not dependencies.
5. **Users who stay on individual plans** can install the shared plugin by hand from a marketplace URL. They should not use twins that touch customer, deal or patient data.

## Traps IT directors don't know to ask about

- **Server-managed settings aren't a security boundary.** Anthropic calls them "client-side control". Users can step around them by:
  - signing in to a personal or other org
  - using a Console API key or a custom `ANTHROPIC_BASE_URL`
  - running an old or modified binary.

  Cowork in Desktop never fetches them. (Our recommendation) Deliver the org lock through MDM, and pair it with tenant restrictions.
- **The Admin role can't manage Plugins & skills.** Only Owners and Primary Owners can, or an Enterprise custom role with the Libraries permission.
- **Two separate plugin control planes.** claude.ai plugin policy and Claude Code managed settings are configured separately.
- **Plugins can run code on the user's machine:** agents, hooks and local connectors. Anthropic says it "does not control what MCP servers, files, or other software are included in plugins and cannot verify that they will work as intended".
- **Claude Tag spends the org's balance.** By default, anyone in the paired Slack workspace can tag @Claude and use the org's usage balance. Restrict it to org members.
- **Departing users leave things behind.**
  - Plugins they shared keep working until someone selects "Stop sharing".
  - Memory survives deleting conversations.
  - **⚠ Unverified:** local Cowork history can't be wiped centrally (not re-checked in this pass).
- **Two one-way doors:** domain capture (Enterprise; it "can't be reversed", and personal accounts not migrated within 30 days are closed), and turning on HIPAA readiness.
- **Tenant restrictions work only on the corporate network.** The company's proxy adds a header to requests to Claude, so networks it doesn't control are out of reach. Tenant restrictions are on Enterprise and Console orgs.
- **Raise with the Anthropic account team:**
  - SSO on Team (conflicting docs).
  - Skills on Free (conflicting docs).
  - Data residency for claude.ai (no page found).

Sources: [Server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md), [Plugins admin](https://claude.com/docs/plugins/admin) (Admin role, separate control planes, Stop sharing), [Plugin security](https://code.claude.com/docs/en/plugins/security.md), [Claude Tag access](https://claude.com/docs/claude-tag/admins/restrict-access.md) (anyone in the workspace by default; group DMs and DMs from members without a Claude account bill to the org), [Memory](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context) (memory isn't removed when conversations are deleted), [Domain capture](https://support.claude.com/en/articles/14625619-claim-and-migrate-accounts-on-your-domain), [API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) (HIPAA readiness is permanent), [Tenant restrictions](https://support.claude.com/en/articles/13198485).
