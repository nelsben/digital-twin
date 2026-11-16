Checked 2026-11-16 by the author against the pages listed. Every claim was checked again on 2026-11-16 by a second reader; the results are in the [verification log](../../runbooks/verification-log.md).

# HubSpot marker property: Last updated by twin

## What this is

One custom property on Deal, "Last updated by twin", of type date and time. The twin's CRM-update skill sets it on every write, so HubSpot's own property history can tell a twin edit from a human one. The reason is in [compendium 15](../../../docs/compendium/15-governance-and-performance.md): with per-user sign-in a write by the twin appears under the rep's name. This is the HubSpot copy of the pattern in the [Salesforce marker README](../salesforce/README.md); read that first for the thinking. How the connector is installed and signed in is in the [HubSpot connector runbook](../../runbooks/hubspot-connector.md). Unlike Salesforce there is no deployable file: a HubSpot admin creates the property by hand, and the skill and its eval are the rest of the kit.

Each step ends with the pages it came from, as tags like ([A]) that "Pages used" defines. **⚠ Unverified:** means no page we downloaded states it, and the item says what to confirm.

## Why this marker

HubSpot offers a "Date and time picker" type that "stores a date and time value" ([A]). We use it, and not a checkbox or a date, for the reason the Salesforce field is a DateTime. A checkbox set once stays set, so a second twin write changes nothing and leaves no history. A date-and-time value is new on every write, so each write is a new row. A record's property history gives "Changed to", "Date" and "Source" for each change ([B]). The time also answers "when did the twin last touch this deal?" without a second property. No page says a date-and-time property is left out of property history, but none says it is included, so the first test write in Check it worked settles it. **⚠ Unverified:** that every change to a date-and-time property is kept in history.

Deals come first. The connector lists Contacts, Leads, Companies, Deals, Tickets and custom objects as updatable ([F]); add the same property to any other object the twin writes.

## Create it (the HubSpot admin does this)

1. In HubSpot, click the settings icon, then in the left sidebar menu go to **Properties**, pick the **Deals** object and create a property ([E]). "Edit property settings permissions are required to create properties." ([E])
2. Name it "Last updated by twin", choose the field type **Date and time picker**, and write a description that says the twin sets it and nobody else should. ([A], [E])
3. Do this in a test portal first. HubSpot shows a date-and-time value in the viewer's own time zone ("current time zone is used", [A]), so the skill must write UTC and people must expect local display.

## Limit who can set it

The goal is edit for the twin only. HubSpot can only partly do this.

- **Enterprise.** Property access ("Private to super admins only", "Allow everyone to view", or chosen users and teams) is offered with Marketing, Sales, Service, Data, Content and Revenue Hub Enterprise, and "Super Admin permissions are required to restrict a property" ([D]). Choose "Allow everyone to view": "all users can view but not edit the property's value on a record. Only Super Admins can edit the property's value." ([D])
- **Every edition: it is not a control.** HubSpot says "All users, regardless of access, can set or edit restricted properties via HubSpot's API, or when manually creating a record." ([D]) It also says not to use property restrictions as a security measure ([D]). **⚠ Unverified:** whether a connector write is treated as an API write (and so ignores the restriction) or as the signed-in user's edit (and is blocked for a user who is not a Super Admin). The test below tells you. Safer reading: assume neither side is enforced, and treat the property as a marker, not a security control.
- **Below Enterprise,** the property can be set by anyone who can edit the deal. Record this as a risk with Security.
- The connector acts with the user's own permissions: "Users can access only the data allowed by their existing HubSpot user permissions." ([F]) A user whose twin can write the property can also write it by hand. Cross-check against the governance log in [twin-governance](../../plugins/twin-governance/README.md).

## Make the skill set it

The CRM-update skill writes to deals at autonomy level 2 and above. The connector's write tool is probably `manage_crm_objects` ([G]); the listing does not label tools as read or write. **⚠ Unverified:** that this tool can set a custom property value; no page we downloaded says so, and the write test below is how to find out. The skill must:

1. Send the marker in the same update as the change, so the two cannot separate.
2. Use the current time in UTC, ISO 8601, for example `2026-11-16T09:30:00.000Z`. **⚠ Unverified:** the format the tool accepts; write down what the first test accepts.
3. Set it on every write and never on a read; never write a past or future time; never clear it.
4. Fail closed. If HubSpot or the tool rejects the marker, do not retry without it. Stop and tell the user.

**(Our recommendation):** the marker is set on every write, and an eval fails when a write leaves it unset. Put the rules in `SKILL.md` and write the eval first ([authoring-skills.md](../../docs/authoring-skills.md)). Also keep `manage_custom_properties` Blocked for the role: its name suggests it changes property definitions, and the twin should not change this one. ([G])

## Check it worked

In a test portal, with one pilot user who is not a Super Admin:

1. Set the tool to **Needs approval** and ask the twin to change the stage of one named test deal. Approve once.
2. Open the deal, hover the "Last updated by twin" property, and click the view property history icon ([B]). Expect one new row: the new time, its date, and a source. **⚠ Unverified:** whether the row names the person. HubSpot says a person's "profile name and email address" is listed for a "CRM UI" change and that "Integration" is "a connected app" ([C]), so a connector write may show only the source.
3. Open the Audit Log. HubSpot says that for create and update actions "attribution will be recorded in your HubSpot account's Audit Log to both the user and the Claude connector" ([F]). Expect the person and the connector against the same change. If step 2 shows no person, this row is the evidence.
4. Make a second change to the same deal. Expect a second row with a later time.
5. If you restricted the property, repeat once as that non-Super Admin user. Write down whether the marker was set or refused; this settles the Enterprise item above.

Keep the results, the date and the two users in the engagement folder, not here.

## Report on it

- **For RevOps, no code.** Make a segment (HubSpot's new name for a list) of deals whose "Last updated by twin" property has a value: segments "group records based on property values" and are on "All products and plans" ([I]). **⚠ Unverified:** the filter wording for a date-and-time property; use what the editor offers.
- **A report.** Custom reports are available with Professional and Enterprise subscriptions of the hubs ([H]). Build a deal report with the property as a column and the stage and owner beside it.
- Property history for one deal is on the record ([B]). Do not rely on old history for the monthly scorecard; export the figures as [compendium 15](../../../docs/compendium/15-governance-and-performance.md) describes. **⚠ Unverified:** how long property history is kept.

## What can go wrong

| Problem | What to do |
|---|---|
| The tool cannot set the property | The write test shows it. Do not go live at level 2; ask HubSpot, or move the write to a path that can. |
| A write has no marker | The eval should have failed. Fix the skill; the log and the property history show which writes were unmarked. |
| A user changed the marker by hand | Expected below Enterprise, and possible on it. Cross-check the governance log. |
| Time looks wrong on the deal | HubSpot shows the viewer's time zone ([A]). The stored value should be UTC. |
| The connector shows a person nowhere in history | Use the Audit Log ([F]) and the governance log. |

## Pages used

- [A] [Property field types in HubSpot](https://knowledge.hubspot.com/properties/property-field-types-in-hubspot)
- [B] [View a record's property history](https://knowledge.hubspot.com/records/view-record-property-history)
- [C] [HubSpot's change sources](https://knowledge.hubspot.com/properties/hubspots-change-sources)
- [D] [Restrict view and edit access for properties](https://knowledge.hubspot.com/properties/restrict-view-edit-access-for-properties)
- [E] [Create and edit properties](https://knowledge.hubspot.com/properties/create-and-edit-properties)
- [F] [Set up and use the HubSpot connector for Claude](https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude)
- [G] [HubSpot connector listing (Claude connectors directory)](https://claude.com/connectors/hubspot)
- [H] [Create custom reports](https://knowledge.hubspot.com/reports/create-custom-reports)
- [I] [Create active or static segments](https://knowledge.hubspot.com/lists/create-active-or-static-lists)
