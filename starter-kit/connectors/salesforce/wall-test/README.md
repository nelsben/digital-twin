# Wall test: scratch-org dry run (Salesforce)

A throwaway Salesforce scratch org with two roles, one test user in each, and invented records on each side. `wall_test.py` replays the API-level cases of the [wall-test protocol](../../../../engagements/sample-pe/wall-test-protocol.md) (WT-01 to WT-16, the cases marked "can be dry-run at the API level") as each user, deploys the kit's [twin-marker metadata](../README.md), runs the `UserRecordAccess` `HasEditAccess` check from the CRM-update skill's [level-2-writes.md](../../../plugins/twin-pe-deal-team/skills/drafting-crm-updates/references/level-2-writes.md), prints a pass or fail table, and deletes the org.

All data is invented (WALLTEST- names, Project Larch, example.com addresses).

## Status

Run once on 2026-11-15 (results below). The first attempt, earlier the same day, stopped at scratch-org creation with `STORAGE_LIMIT_EXCEEDED: storage limit exceeded` because the Dev Hub had no data storage left; it ran after space was freed. The 16 record-access cases pass. **The kit's marker metadata does not deploy as it stands** (see Results).

## What you need

- Python 3 and the Salesforce CLI (`sf`).
- A Dev Hub you are logged in to, with a free scratch org and some data storage. Pass its alias as the only required argument. The script never stores it.
- No default org is used. Every `sf` call except the scratch-org create and `sf org list` must name the scratch org (`twin-wall-test`) or one of the two test-user aliases (`twin-wall-d`, `twin-wall-i`); the script refuses any other target before the CLI runs.

## Run it

```
python3 wall_test.py <dev-hub-alias>
```

| Option | Effect |
|---|---|
| `--keep-org` | Skip the delete stage, so you can look at the org. Delete it yourself: `sf org delete scratch --target-org twin-wall-test --no-prompt` |
| `--stages setup,cases,marker,delete` | Run some stages only. Setup is safe to repeat: it reuses the org, redeploys, and reseeds. |
| `--search-wait <seconds>` | How long a search control waits for the search index (default 240). A pair whose control never passes is reported NOT RUN |

Stages: create the org (Enterprise, 3 days), deploy the metadata, create the two users and seed the records; run WT-01 to WT-16; deploy the marker and run the access check; delete the org and confirm it is gone from `sf org list`. Exit code 0 means every row passed.

## What is in this folder

| Path | What it is |
|---|---|
| `config/project-scratch-def.json` | The scratch-org definition (Enterprise) |
| `force-app/main/default/roles/` | Roles Deal Team and Investor Relations, both at the top of the hierarchy, neither above the other |
| `force-app/main/default/objects/` | Sharing: Opportunity and Account private, Contact controlled by parent |
| `optional/enable-opportunity-history/` | Turns on Opportunity history. Used only if the marker deploy fails without it |
| `wall_test.py` | The script |
| `sfdx-project.json` | Makes this folder an SFDX project |

## How the cases map

The users are two Standard User accounts with no Modify All Data or View All Data (the script checks this). Every seeded record on a side is owned by that side's user. Content tokens are `ZD` or `ZI` plus 6 characters, made at seed time and read back by the script as admin.

| Protocol cases | API call, as the user the case names |
|---|---|
| WT-01 to WT-04 | SOQL for the four records by name, then by id (with `FOR VIEW`) |
| WT-05 to WT-08 | SOSL `FIND {WALLTEST*}` over opportunities, accounts, contacts and tasks, plus a search for the other side's token |
| WT-09 to WT-12 | SOQL over all opportunities, accounts and contacts, `RecentlyViewed`, and every list view the user has on those three objects, read through the REST API |
| WT-13 to WT-16 | `COUNT()`, and a grouped count by owner |

A blocked case passes only when nothing of the other side comes back (name, token, record id), the call reached the API, and its control passed. This is stricter than the protocol's leak rule, which excludes names the actor typed. A control that fails marks its pair NOT RUN.

## Results

Run on 2026-11-15, API version 68.0 (the scratch org's), Enterprise edition, copied from the script's output. The users and records were checked first: both users are Standard User, in the role named for their side, with no Modify All Data or View All Data (ID-D, ID-I: pass).

| Case | Actor | Result | What the output showed |
|---|---|---|---|
| WT-01 | DT | pass | own 4 records by name and by id, all 4 tokens |
| WT-02 | DT | pass | 0 rows from the other side; no leak |
| WT-03 | IR | pass | own 4 records by name and by id, all 4 tokens |
| WT-04 | IR | pass | 0 rows from the other side; no leak |
| WT-05 | DT | pass | search found 5 of 5 own-side ids (5 items) |
| WT-06 | DT | pass | 5 items; no leak; a search for the other side's token returned 0 records |
| WT-07 | IR | pass | search found 5 of 5 own-side ids (5 items) |
| WT-08 | IR | pass | 5 items; no leak; a search for the other side's token returned 0 records |
| WT-09 | DT | pass | own opportunity, account and contact ids in the lists |
| WT-10 | DT | pass | no leak; 4 recently viewed rows; 1 list view read |
| WT-11 | IR | pass | own opportunity, account and contact ids in the lists |
| WT-12 | IR | pass | no leak; 3 recently viewed rows; 1 list view read |
| WT-13 | DT | pass | count 2 |
| WT-14 | DT | pass | grouped total 2, one owner (`WALLTEST-D-USER`); other side's count 0 |
| WT-15 | IR | pass | count 2 |
| WT-16 | IR | pass | grouped total 2, one owner (`WALLTEST-I-USER`); other side's count 0 |

The search index caught up within the script's wait, so no pair was NOT RUN.

**Marker metadata (`../force-app`): fails to deploy.** Two findings, both with the Salesforce error text:

- **Twin_Marker_Edit has a description that is too long.** Validate and deploy both fail with `Twin_Marker_Edit`: `Description: data value too large: Edit access to Opportunity.Last_Updated_By_Twin__c, for the identity the twin writes as. ... (max length=255)`. The file's description is 338 characters; `Twin_Marker_Read`'s is 186 and was not named in any error. Nothing was changed here (the file is outside this folder). The fix is to shorten that description to 255 characters or fewer.
- The Twin_Marker_Edit description was shortened to 255 characters after this run (#93, PR #94). The marker has not been re-deployed to a scratch org since.
- **Opportunity history must be on first.** In a run on the same org before history was enabled, validate also failed with `Opportunity.Last_Updated_By_Twin__c`: `The entity: Opportunity does not have history tracking enabled`. This confirms step 1 of the [marker README](../README.md#deploy-it-the-salesforce-admin-does-this). The script turns history on from `optional/enable-opportunity-history/` and retries; that step passed. In the final run history was already on, so only the description error showed.

Because the deploy is all or nothing, the field and `Twin_Marker_Read` are not in the org either, and the marker's permission sets were not assigned.

**Edit-access check (`UserRecordAccess`, as in level-2-writes.md step 2).** It behaves as the skill assumes. Each user asked about their own `UserId` and one opportunity on each side:

| As | Own-side opportunity | Other-side opportunity |
|---|---|---|
| DT | HasReadAccess true, HasEditAccess true | HasReadAccess false, HasEditAccess false |
| IR | HasReadAccess true, HasEditAccess true | HasReadAccess false, HasEditAccess false |

All four answers matched what the skill needs (ACCESS-DD, -DI, -ID, -II: pass). Only the answers were compared; the script did not try the write.

**Other things the run showed.** Salesforce stores the contact's email in lower case, so the script matches tokens without regard to case. A role's description is limited to 80 characters. After the script logged out the two test-user aliases, `sf org delete scratch` reported `NamedOrgNotFoundError` for a test user's auth, yet the org showed as Deleted in `sf org list --all` and the Dev Hub's active scratch org count returned to 3 of 3 free. The script now trusts the listing over that exit status.

The scratch org was deleted at the end, and `sf org list` no longer shows `twin-wall-test`.

## What this does not prove

- Calls were made through the Salesforce API as each user, not through the Salesforce Hosted MCP connector or Claude. Nothing here shows what the connector's tools expose or how Claude uses them.
- A scratch org's sharing model is not the customer's. The roles, the private defaults and the standard profile here are a stand-in; the live run must test the customer's own roles, sharing rules and permission sets.
- SharePoint and HubSpot are not covered, and neither are the skill, Project, memory and shared-file routes (WT-17 to WT-53).
- Salesforce audit, the governance log and Event Monitoring are not checked.
- The search cases wait for the index for minutes, not the 24 hours the protocol asks for.
- It shows the cases run and the rules apply, as the protocol says; it does not show a customer's wall holds.
