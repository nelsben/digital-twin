# Salesforce marker field: Last updated by twin

## What this is

One custom field on Opportunity, `Last_Updated_By_Twin__c`, with Field History tracking on, plus two permission sets. The twin's CRM-update skill sets the field on every write, so the CRM's own history can tell a twin edit from a human one. The reason is in [compendium 15](../../../docs/compendium/15-governance-and-performance.md): with per-user OAuth a Salesforce update by the twin appears under the rep's name, and the RevOps manager needs a way to report on it.

| File | What it is |
|---|---|
| [`force-app/main/default/objects/Opportunity/fields/Last_Updated_By_Twin__c.field-meta.xml`](force-app/main/default/objects/Opportunity/fields/Last_Updated_By_Twin__c.field-meta.xml) | The field: DateTime, not required, history tracked, with a description and help text |
| [`force-app/main/default/permissionsets/Twin_Marker_Read.permissionset-meta.xml`](force-app/main/default/permissionsets/Twin_Marker_Read.permissionset-meta.xml) | Read-only access to the field, for everyone |
| [`force-app/main/default/permissionsets/Twin_Marker_Edit.permissionset-meta.xml`](force-app/main/default/permissionsets/Twin_Marker_Edit.permissionset-meta.xml) | Edit access to the field, for the identity the twin writes as |
| [`sfdx-project.json`](sfdx-project.json) | Makes this folder an SFDX project, so the Salesforce CLI can deploy it |

## Why a DateTime field and not a checkbox

The field is a DateTime. A checkbox set to true on the first twin write stays true, so a second twin write changes nothing in that field and leaves no history row. A DateTime holds a new value on every twin write, so each write adds a row to Field History. Each row gives the time and the user the twin acted as. The time also answers the question RevOps asks most, "when did the twin last touch this deal?", without a second field.

## Deploy it (the Salesforce admin does this)

Prerequisites: the [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli) (`sf`), and an org you have logged in to (`sf org login web --alias <alias>`). Deploy to a sandbox first.

1. **Turn on history for Opportunity, once.** Setup, Object Manager, Opportunity, Fields & Relationships, Set History Tracking, tick Enable Opportunity History. Check that a tracked-field slot is free. **⚠ Unverified:** the 20 tracked fields per object limit; Salesforce's pages returned HTTP 403 on 2026-11-15, so confirm the limit for the customer's edition. The field's `trackHistory` setting only works when object-level history is on.
2. **Validate, then deploy.** From this folder:

   ```
   sf project deploy start --source-dir force-app --target-org <alias> --dry-run
   sf project deploy start --source-dir force-app --target-org <alias>
   ```

   The first command checks the deploy without changing the org. Run the second only when the first passes.
3. **Assign the permission sets** (Setup, Permission Sets, Manage Assignments, or `sf org assign permset --name Twin_Marker_Read --target-org <alias>`):
   - `Twin_Marker_Read` to everyone who should see the field, including RevOps managers. A permission set group of the sales roles is the usual way.
   - `Twin_Marker_Edit` to the identity the twin writes as. See the next section.
4. **Add the field to the Opportunity page layout** (or the Lightning record page) if people should see it on the record. Reports and the history list work without this.

A custom field is invisible to every profile until a permission set or profile grants it, so a deploy without step 3 is not visible and not writable.

## Who can edit the field

The goal is edit for the twin only and read for everyone else. How much of that Salesforce can do depends on how the twin connects.

- **Integration user (a shared identity, such as the one a Claude Tag setup uses).** Edit can be limited to the twin. Assign `Twin_Marker_Edit` to the integration user and `Twin_Marker_Read` to everyone else. No human holds edit.
- **Per-user OAuth (the default for regulated and walled teams, such as private equity; see [compendium 14](../../../docs/compendium/14-private-equity.md)).** Edit cannot be limited to the twin. With per-user OAuth through an External Client App, the twin acts as the user and has that user's permissions. Field-level security belongs to the user and not to the client, so a user whose twin can write the field can also write it by hand. Salesforce has no setting that gives edit to a user only when the call comes from the twin. In this mode:
  - Assign `Twin_Marker_Edit` to the users whose twin writes to opportunities, and `Twin_Marker_Read` to everyone else.
  - Treat the field as a marker, not a security control. It makes the twin's writes visible and reportable. It does not stop a user editing it on purpose.
  - Cross-check against the governance log from [twin-governance](../../plugins/twin-governance/README.md), which records the Salesforce record id of each twin call and sits outside Salesforce.

## How the CRM-update skill sets it

The CRM-update skill is the twin skill that writes to opportunities at autonomy level 2 and above ([compendium 06](../../../docs/compendium/06-autonomy.md)). It must:

1. **Include the marker in the same update as the change.** Send `Last_Updated_By_Twin__c` in the same update call that carries the other field changes, so the two cannot separate and the history rows share a timestamp.
2. **Use the current time in UTC, ISO 8601.** For example `2026-11-14T09:30:00.000Z`. Salesforce stores DateTime in UTC.
3. **Set it on every write**, including writes that change one field, and never on a read.
4. **Fail closed.** If Salesforce rejects the marker (the user lacks `Twin_Marker_Edit`, or the field is not deployed), do not retry the update without it. Stop and tell the user the marker is missing, so no unmarked twin write reaches the CRM.
5. **Never write a past or future time**, and never clear the field.

Put these rules in the skill's `SKILL.md` and add an eval that fails when an update is sent without the marker. See [authoring-skills.md](../../docs/authoring-skills.md).

## Report on twin-written changes

With tracking on, every change to the marker is a row in `OpportunityFieldHistory`, next to the rows for the fields the twin changed in the same update. Both rows should have the same `CreatedById` (the user the twin acted as) and the same `CreatedDate`. **⚠ Unverified:** the marker has not been deployed to an org yet (see the [wall-test README](wall-test/README.md)), so this has not been observed; confirm it on the first test write.

**Which opportunities the twin touched, and when**, in the Developer Console query editor or `sf data query`:

```
SELECT OpportunityId, CreatedById, CreatedDate, NewValue
FROM OpportunityFieldHistory
WHERE Field = 'Last_Updated_By_Twin__c'
ORDER BY CreatedDate DESC
```

**What the twin changed.** Take the same opportunity and `CreatedDate` as a marker row, and read every other history row there:

```
SELECT Field, OldValue, NewValue, CreatedById, CreatedDate
FROM OpportunityFieldHistory
WHERE OpportunityId = '<opportunity id>'
ORDER BY CreatedDate DESC
```

Rows that share a `CreatedDate` with a marker row are the twin's. Rows with no marker row beside them are human edits. This is why the skill must send the marker in the same update.

**For RevOps managers, no code.** Build a report from the standard Opportunity Field History report type and filter on Field equals "Last updated by twin". Show Opportunity Name, Edited By, Date Edited and New Value. Salesforce shows history rows for a limited time (**⚠ Unverified:** the retention period; confirm it for the customer's edition), so export the monthly scorecard figures rather than relying on old history rows. The scorecard is described in [compendium 15](../../../docs/compendium/15-governance-and-performance.md).

## Limits

- The marker records that the twin wrote, not that a person approved the write. Approval is the job of the autonomy level and the skill's confirmation step.
- The marker is on Opportunity only. Other objects the twin writes to, such as Account or Contact, need the same field and the same rule; copy the field file into `objects/<Object>/fields/`, change the permission-set field names, and turn on history for that object.
- Field History is not the same as the governance log. History lives in Salesforce, under the customer's retention rules. The log lives with the customer's IT and holds metadata only.
