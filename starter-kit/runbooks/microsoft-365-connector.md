# Runbook: Microsoft 365 connector, tenant consent and a SharePoint access check

## What this is

Deal-team skills read documents in SharePoint (and OneDrive and Teams) through Claude's Microsoft 365 connector. This runbook takes the Microsoft 365 admin, the Claude org Owner and our integration engineer through tenant admin consent, then proves the deal-team libraries are not readable by investor relations or any other walled group, before any twin reads a deal folder. It is generic: replace every `<placeholder>` with the customer's value.

Roles use the names in [03-stakeholders](../../docs/playbook/03-stakeholders.md):

| Name used here | Role in 03-stakeholders |
|---|---|
| **Microsoft 365 admin** | Source-system admin (M365 admin). The person who signs in as Global Administrator in step 3 holds that Microsoft Entra role; if the Microsoft 365 admin does not, the **Director of IT** arranges one. |
| **Claude org Owner** | Technical owner (Director of IT), or the Backup Owner |
| **Security** | Security (CISO or security engineer) |
| **Compliance** | Compliance / legal; confirms which groups are walled |
| **Partner integration engineer** | Integration engineer (partner role) |

## Read this first

How sources are marked: each step ends with the page it came from. **⚠ Unverified:** (the compendium's marker) means the pages we read did not confirm it. Confirm each unverified item at setup before relying on it, then replace the mark with the page you checked. Pages were read on 2026-11-14, and every claim was checked again on 2026-11-15; the results are in the [verification log](verification-log.md).

Pages used:

- [A] [Microsoft 365 connector (Claude docs)](https://claude.com/docs/connectors/microsoft/365.md)
- [B] [Set up the Microsoft 365 connector (Claude help center)](https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector)
- [C] [Microsoft 365 connector security guide (Claude help center)](https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide)
- [D] [Grant tenant-wide admin consent to an application (Microsoft Learn)](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/grant-admin-consent)
- [E] [Sharing & permissions in the SharePoint modern experience (Microsoft Learn)](https://learn.microsoft.com/en-us/sharepoint/modern-experience-sharing-permissions)
- [F] [Edit permissions for a list, library or individual item (Microsoft Support)](https://support.microsoft.com/en-us/office/edit-permissions-for-a-list-library-or-individual-item-02d770f3-59eb-4910-a608-5f84cc297782)
- [G] [List who has access to a file, driveItem permissions (Microsoft Graph)](https://learn.microsoft.com/en-us/graph/api/driveitem-list-permissions?view=graph-rest-1.0)
- [H] [Compendium 11, Connectors](../../docs/compendium/11-connectors.md) and [14, Private equity](../../docs/compendium/14-private-equity.md)
- [I] [Anthropic IP addresses](https://platform.claude.com/docs/en/api/ip-addresses)
- [J] [Search the audit log (Microsoft Purview, Microsoft Learn)](https://learn.microsoft.com/en-us/purview/audit-search)
- [K] [Control MCP server access for your organization](https://code.claude.com/docs/en/managed-mcp)

## What access the connector gets (read this before consent)

- **Per user, delegated.** Claude acts as the signed-in user and can reach only what that user's Microsoft 365 account can already reach. Service-principal (application-only) authentication is not supported. ([A], [C])
- **SharePoint sharing is not bypassed.** The connector does not bypass SharePoint sharing settings or folder permissions. ([C])
- **Read by default.** Write scopes are requested in the consent set but are used only when write tools are enabled. ([B], [C]) At autonomy level 1 (Draft: write tools blocked, [06](../../docs/compendium/06-autonomy.md)), keep write tools off; see step 6.
- **Scopes for documents:** `Files.Read`, `Files.Read.All` and `Sites.Read.All` (read); `Files.ReadWrite.All` (write). `Sites.Read.All` is needed for SharePoint search. Other scopes cover Outlook mail and calendar, Teams chat and channels, and meetings (see [B] for the full list). ([B], [C])
- **No site-level narrowing.** SharePoint search is tenant-wide, and site-specific `*.Selected` permissions are not supported. Limiting the connector to chosen sites in Entra is not an option. ([C]; [B] says "Site-specific search restriction isn't supported.") So the wall rests entirely on SharePoint permissions, which is why step 8 exists.
- **Audit.** Every Graph call the connector makes appears in the organization's Microsoft 365 audit log (timestamp, user, operation, resource). ([C])
- **Not in scope:** personal Microsoft accounts (no tenant consent, no SharePoint), Claude Desktop on third-party inference, US government deployments, and the Claude Desktop local connector (it uses its own app registration). Each has its own page. ([A])

## 1. Prerequisites

| # | Check | Who | Source |
|---|---|---|---|
| 1.1 | The customer's Claude org is Team or Enterprise, with the Owner or Primary Owner role held by the person who will add the connector. | Claude org Owner | [A] |
| 1.2 | Users have work or school accounts on a Microsoft Entra tenant, with active Microsoft 365 licences. Team and Enterprise plans support work or school accounts only. | Microsoft 365 admin | [A], [B] |
| 1.3 | A Microsoft Entra Global Administrator is available for step 3. | Microsoft 365 admin, or Director of IT | [A], [B] |
| 1.4 | Name two pilot test users for step 8 who sit on opposite sides of a wall: one on the deal team, one in investor relations (or another walled group). Compliance names the groups. | Compliance, with the Microsoft 365 admin | [H] |
| 1.5 | Name the Claude group or groups that will use the connector: the deal-team group only. | Claude org Owner, with Compliance | [H] |
| 1.6 | Check whether the customer's Entra tenant restricts third-party app consent or uses Conditional Access that could block the connector. Claude's security guide says group-based access, MFA and device compliance policies are supported (device compliance is checked against the device the member connected from; keep such a policy assigned to the Claude applications). Location and network policies, and sign-in frequency policies, are not supported: the connector's server-side requests come from Anthropic's IP ranges, so such a policy blocks the connector for every member. For those, exclude Anthropic's ranges as in step 1.7. **⚠ Unverified:** confirm at setup whether app-consent settings block it. | Security | [C]; [B] |
| 1.7 | Network: Microsoft 365 is a public cloud service, so the compendium expects no tunnel ([H]). But if a Conditional Access location or sign-in frequency policy covers the connector, create a named location under **Conditional Access > Named locations** with every current IPv4 range from Anthropic's outbound IP list (`160.79.104.0/21` and `153.61.208.0/20` on 2026-11-15, [I]), leave **Mark as trusted location** unchecked, and add it under the policy's **Conditions > Locations > Exclude**. Excluding the two Claude applications is not enough on its own. Do not use this exclusion for a device compliance policy. Record the answer against discovery item E6 ([playbook discovery](../../docs/playbook/02-discovery.md)). | Claude org Owner, with Security | [B]; [C]; [I] |

## 2. Decide what to approve before consent

**Who: Security with the Director of IT; Compliance consulted.**

- Consent is tenant-wide. By default it lets every user in the tenant use the app unless you restrict it, and Microsoft warns that tenant-wide consent is a sensitive operation: review the permissions first. ([D])
- Decide whether to revoke any write scopes after consent (the paragraph "To list or revoke a permission later" at the end of step 3), based on autonomy level 1. Re-running consent later re-grants the full current set, including writes, so any revocation must be repeated. ([B])
- Record the decision in the engagement's connector plan.

## 3. Grant tenant admin consent

**Who: Microsoft 365 admin signing in as Global Administrator.** **⚠ Conflict:** Microsoft's own page says a Privileged Role Administrator can grant consent for any permission, and a Cloud Application Administrator, AI Administrator or Application Administrator for any permission except Microsoft Graph app roles ([D]), but Claude's pages name the Global Administrator for the first consent ([A], [B]). Use a Global Administrator unless Claude confirms otherwise. **⚠ Unverified:** whether a lesser role is enough for the first consent; confirm with Anthropic at setup.

First, the Claude org Owner adds the connector: **Organization settings > Connectors**, **Add**, **All available**, find **Microsoft 365**, **Add to your team**. ([A], [B])

Then pick one consent route. ([B])

| Route | When | Steps |
|---|---|---|
| **Through Claude** | The Global Administrator has a Claude account | Go to **Customize > Connectors**, **Connect** on Microsoft 365, choose **Work or school account**, sign in, accept the permissions, and tick the box to grant access on behalf of the whole organization. |
| **Manual in Entra** | No Claude account, or troubleshooting | 1. Add both service principals in Microsoft Graph Explorer with `POST https://graph.microsoft.com/v1.0/servicePrincipals`: **M365 MCP Client for Claude** (appId `08ad6f98-a4f8-4635-bb8d-f1a3044760f0`) and **M365 MCP Server for Claude** (appId `07c030f6-5743-41b7-ba00-0a6e85f37c17`). 2. In a browser, open `https://login.microsoftonline.com/<tenant-id>/adminconsent?client_id=<appId>` once for each appId. |

The admin consent URL format is `https://login.microsoftonline.com/{organization}/adminconsent?client_id={client-id}`, where `{organization}` is the tenant ID or a verified domain. ([D]) A successful approval ends on a page whose address contains `admin_consent=True`. ([A])

For the pe-zdr managed-settings file: the value to paste over `REPLACE-WITH-MICROSOFT-365-MCP-HOST` in `starter-kit/settings/pe-zdr.managed-settings.json` is the host of the Microsoft 365 connector's server URL, so the entry reads `https://<that host>/*` ([K] describes the matching). **⚠ Unverified:** the host. Neither Claude's connector page [A] nor the help-center pages [B] and [C] name it. Where to read it is also unverified. The Claude org Owner tries the Microsoft 365 connector entry (**Organization settings > Connectors**, or the entry's server URL in Claude Code's `/mcp` list once a user is connected), and the Partner integration engineer pastes only that value, then runs `claude mcp list` on a managed machine to check the server loads. Do not guess a host. Until it is confirmed, the pe-zdr allowlist matches no Microsoft 365 server.

Check: in the Entra admin center, **Enterprise applications**, remove the application-type filter, open **M365 MCP Server for Claude** and **Permissions**; the approved permissions are listed. ([A], [B]) Confirm the list matches the decision in step 2.

If Anthropic adds a permission after your tenant consented, the feature that needs it fails with a permission error, and reconnecting does not fix it. A Global Administrator or Application Administrator re-opens the admin consent link for the connector's Application ID (`07c030f6-5743-41b7-ba00-0a6e85f37c17` for claude.ai; use the ID on the enterprise application's **Overview** page if it differs) and accepts the list. ([A]) Review this at each quarterly access review.

To list or revoke a permission later: **Enterprise applications > M365 MCP Server for Claude > Permissions > Admin consent** tab, then "..." next to the permission and **Revoke permission**. A call that needs it then returns "Failed to call tool". ([B])

## 4. Enable the connector for the right group (Entra side)

**Who: Microsoft 365 admin, with the group named by Compliance in step 1.5.**

Consent alone lets all users in the tenant use the connector. To limit it to the deal team: ([B], [D])

1. In the Entra admin center, open the **M365 MCP Server for Claude** enterprise application, **Properties**, and set **Assignment required?** to **Yes**.
2. Under **Users and groups**, add the deal-team users or group.
3. Repeat both actions for **M365 MCP Client for Claude**. [B] says both apps must be restricted to the same set of people.

Claude's own article describes restriction through Entra app assignment, not through Claude roles. ([B])

## 5. Enable the connector for the right Claude group

**Who: Claude org Owner.**

- Adding the connector in step 3 makes it available to the org; each member then connects their own account. ([A])
- **⚠ Unverified:** whether Claude Enterprise can show the Microsoft 365 connector to only one Claude group, as the compendium's plugin design assumes for other tools. [B] describes restriction only through Entra. Ask Anthropic before relying on a Claude-side group control, and until then treat step 4 as the control.
- Each pilot user opens **Customize > Connectors**, selects **Connect** on Microsoft 365, chooses **Work or school account**, and signs in with their own account. The button then reads **Disconnect**. ([A])

## 6. Keep write tools off (autonomy level 1)

**Who: Claude org Owner, with the Partner integration engineer.**

- Write actions for a work or school account are controlled by administrators in the connector's permissions in Entra and in the connector configuration under **Organization settings > Connectors**. ([A])
- In the connector configuration, open **Tool permission restrictions**. A per-tool restriction overrides the **Default restriction** row. ([A]) Set every tool that sends, creates, updates or deletes (mail, calendar, files, Teams messages) to blocked, and record the tool list and each setting with the date in the engagement's connector plan.
- Enterprise plans can enable write tools for a subset of users through custom roles (beta). That is a level 2 decision made on scorecard evidence, not in this runbook. ([A], [B])
- Whether the Claude-side restriction is enough, or the write scopes should also be revoked in Entra (step 3), is a Security call. Revoking removes the capability at the source. ([B])

## 7. Plan the SharePoint wall before testing

**Who: Compliance names the walled groups; Microsoft 365 admin owns the SharePoint settings.**

Because the connector uses each user's own permissions ([C]), the connector can never be stricter than SharePoint. Before step 8:

1. List the deal-team sites and libraries, and the groups that must **not** read them (investor relations, other deal teams, and any others Compliance names).
2. For each site, note its type, because it decides where permissions are managed ([E]):
   - Team site (group-connected): permissions follow the Microsoft 365 group or Teams team; group owners become site owners and members become site members. Site permissions can also be managed separately through SharePoint groups, so check those too.
   - Channel site (private or shared channel): permissions are managed in Teams only and show read-only in SharePoint.
   - Communication site: the Owners, Members and Visitors groups.
3. Note sharing links. *Anyone* links give access without sign-in and cannot be audited; *People in your organization* links work for anyone inside the organization who has the link. Both defeat a wall. ([E])
4. Note external sharing settings. Confidential sites should have external sharing off. ([E])

## 8. Check that deal-team libraries are not readable by walled groups

**Who: Microsoft 365 admin runs the SharePoint checks; Partner integration engineer runs the Claude checks; the two test users from step 1.4 sign in. Compliance reviews the record.** Do this before any twin reads a deal folder.

### 8a. List the permissions on each library

Do all three; each catches things the others miss.

**Library permissions page** (Microsoft 365 admin; needs administrator or owner of the library): open the library, **Settings** (gear), **Library settings** (or **More library settings**), then under **Permissions and Management** select **Permissions for this document library**. ([F]) **⚠ Unverified:** [F] is a Microsoft Support page, not one of the Microsoft Learn pages this runbook accepts as confirmation; confirm the menu names and messages in this list at setup.

- "This library inherits permissions from its parent" means the library uses the site's permissions. ([F])
- A message that some items have permissions not controlled from this page: select **Show these items** to see the exceptions. These are folders or files whose permissions differ from the library's. ([F])
- **Show users** under limited access lists people who were shared a single item. Unsharing an item does not remove their limited access. ([F])
- Do not use **Stop Inheriting Permissions** or **Delete unique permissions** as part of a check: they change access. Make changes only through the customer's change process. ([F])

**Site level** (Microsoft 365 admin): the people with access to a site are the members of its Owners, Members and Visitors groups, or of the connected Microsoft 365 group or Teams team ([E]). Open the site permissions and expand every group, including any nested security group, and compare membership with the walled groups from step 7. Nested security groups are not recommended because they can cause performance issues ([E]). The exact menu path to the site permissions page and a "check permissions for a named user" control were not confirmed by the pages we read. **⚠ Unverified:** confirm them at setup in the SharePoint admin documentation.

**Scripted listing** (Partner integration engineer, only with the customer's written approval): Microsoft Graph lists effective sharing permissions on a driveItem with `GET /drives/{drive-id}/items/{item-id}/permissions` (PowerShell: `Get-MgDriveItemPermission -DriveId <id> -DriveItemId <id>`), including permissions inherited from an ancestor (`inheritedFrom`). ([G]) Limits to know:

- It returns **sharing** permissions. For a caller who is not the item's owner it returns only the permissions that apply to that caller, so it can be incomplete; the item's owner (including co-owners) sees all sharing permissions. ([G])
- **⚠ Unverified:** whether it lists SharePoint site-group membership ([G] is silent); use the site-level check above for group membership.
- Read scopes needed: `Files.Read` at least; `Sites.Read.All` or `Files.Read.All` for higher. ([G])

Record for each library: who has access (users and groups), how (inheritance, unique permissions, sharing links), and any walled group found. Any walled group, an *Anyone* link, an organization-wide link or an unexpected guest is a **fail**: the Microsoft 365 admin removes it through the customer's change process, then repeat 8a.

### 8b. Test with two users

Setup (Microsoft 365 admin): pick library A, intended for the deal team only, with a harmless test file named `wall-test-A`. Pick user 1 (deal team) and user 2 (investor relations or another walled group). Pick library B on user 2's own side, with a harmless test file named `wall-test-B` that user 2 can open and user 1 is not required to.

First, signed in to SharePoint directly as each user, confirm user 1 can open the file and user 2 cannot. If this fails, fix SharePoint first; the connector cannot be stricter than the source system. ([C], [H])

Test setup: for the duration of this test, add user 2 to the Entra app assignment from step 4 on both apps (**M365 MCP Server for Claude** and **M365 MCP Client for Claude**). Without it, step 4 stops user 2 from using the connector at all, and 8.2 and 8.3 would pass for that reason and not because of SharePoint permissions. Remove user 2 afterwards unless Compliance says otherwise, and record both changes.

Then, each user connected as in step 5, in their own Claude session (Partner integration engineer observing):

| # | Do this | Pass if |
|---|---|---|
| 8.1 | User 1 asks Claude to find `wall-test-A` in the named deal-team SharePoint site | User 1 sees it |
| 8.1b | Control: user 2 asks Claude to find a file in a library on user 2's own side (a harmless test file, for example `wall-test-B`, that user 2 can open in SharePoint) | User 2 sees it. If not, user 2 is not connected or not assigned: fix that, because 8.2 and 8.3 prove nothing until this passes |
| 8.2 | User 2 asks Claude to find `wall-test-A` by exact filename, then by words from inside it | User 2 sees nothing about it (no name, no content) |
| 8.3 | User 2 asks Claude to list or summarise what is in the deal-team site | Nothing from library A appears |
| 8.4 | User 1 asks Claude to change or create a file in the library | Claude cannot: write tools are blocked (step 6) |

Search tips from [A]: results can lag for new uploads, and naming the specific SharePoint site helps. Allow for indexing delay before concluding that a file is hidden or missing.

### 8c. Confirm in the audit log

**Who: Security** (needs the Audit Logs or View-Only Audit Logs role). After 8b, search the audit log in the Microsoft Purview portal (**Audit** solution, **Search**), filtering by **Users** and by **File, folder, or site** for library A ([J]). Records for core services are typically available 60 to 90 minutes after the event, so wait before you search ([J]). Entries show timestamp, user, operation and resource. ([C]) Confirm user 2 has no access events on library A. **⚠ Unverified:** confirm at setup the exact audit search filters for the connector's app.

Record the date, both users, the libraries, and each result in the engagement's wall-test notes. These 8.x checks are a pre-check. The gate before the pilot is the full protocol, [wall-test-protocol.md](../../engagements/sample-pe/wall-test-protocol.md) (the worked example of the protocol, on invented records seeded in the live systems): no pilot user connects until every case in it passes. A single failure in 8.2 or 8.3 means stop and fix the cause (a group on the site, an inherited or unique permission, a sharing link, a guest), then repeat 8a and 8b in full.

## 9. Hand over

**Who: Partner integration engineer to the Microsoft 365 admin, the Claude org Owner and Security.** Hand over the consent decision and who consented (step 3), the Entra assignment list (step 4), the tool settings (step 6), the library permission listings and wall-test record (step 8), and the unverified items still open. Offboarding: remove the user from the Entra app assignment (step 4) and revoke their Microsoft 365 sessions through the customer's identity process **⚠ Unverified:** Claude's pages do not say that removing a user from Claude also removes the Entra assignment or revokes the Microsoft 365 session, so do both by hand; refresh tokens expire after 90 days of inactivity by default ([C]). Members can disconnect themselves in **Customize > Connectors**, and an Owner can remove the connector for the org in **Organization settings > Connectors**. ([B])

## Open items to verify (all marked unverified above)

1. The host of the Microsoft 365 connector's server URL, for the pe-zdr allowlist (step 3).
2. Whether a role below Global Administrator is enough for the first consent.
3. Whether app-consent policies at the customer can block the connector's apps (Conditional Access behaviour is now confirmed in step 1.6).
4. Whether the Microsoft 365 connector can be limited to one Claude group on the Claude side.
5. The library permissions menu names and messages in 8a, which rest on a Microsoft Support page, not a Microsoft Learn page.
6. The site permissions page path and a per-user "check permissions" control in SharePoint.
7. Whether the Graph permissions listing includes SharePoint site-group membership.
8. Audit-log search filters for the connector.
9. Whether removing a user from Claude also removes the Entra assignment and revokes the Microsoft 365 session (step 9).
