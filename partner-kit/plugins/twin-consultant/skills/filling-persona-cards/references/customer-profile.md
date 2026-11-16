# Creating a missing customer profile

Step 1 of `SKILL.md` points here. Every persona card needs the customer
profile at `engagements/<customer>/customer-profile.json`; the validator
reads it from `../../customer-profile.json` beside the persona folder.

## When it is missing

1. Say that the file is missing and that the card cannot be validated
   without it.
2. Look for the engagement's discovery answers (`discovery.md` in the
   customer folder, or answers the consultant pastes). Say whether you
   found any.
3. If there is no `discovery.md`, offer to create it from
   `templates/discovery.md` in this plugin, and write the pasted answers in
   its rows (answer, status, and owner and due for an open row). The profile
   then cites those rows.
4. Offer to create the profile from `templates/customer-profile.json` in
   this plugin and those answers. Wait for the consultant to agree.

## Filling it

- Each answer comes from the discovery question the catalogue's
  `asked_by` names for that field (plan from B1 and B2, identity from D1,
  devices from D2 and D3, compliance from C1 to C5, systems from E1 to E6,
  governance from G1 to G4, owners from A1, C3 and G4). Its entry is
  `{"status": "answered", "source": "discovery.md#B1"}`. An answer always
  cites a row of `discovery.md`. An answer
  that two rows give together cites both: `"discovery.md#D2; discovery.md#D3"`.
- A pack's `compliance_defaults` entry fills its field with
  `{"status": "default", "source": "data/industry-packs/<id>.json"}` until
  the customer confirms or overrides it.
- **Never guess** the plan, identity, devices or compliance. With no
  discovery answer, the value is empty (`null`, `""` or `[]`; `false` is a
  value) and the entry is `open` with an owner and a due date from the
  consultant. A working guess, such as "no PHI today" while compliance has
  not ruled, keeps its value and is `assumed`, with an owner.
- `customer` is a kebab-case id; `display_name` is the customer's name.
- Under `engagements/sample-*`, set `fictional` to `true` and use invented
  names only. Anywhere else, never copy a real person's name from a source
  the consultant did not give you.

## After writing

Run the validate command from `SKILL.md` step 6 on the persona folder. It
checks the profile and the card together.
