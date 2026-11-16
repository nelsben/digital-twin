# Sample engagement: Example Capital Partners

> **All names, people and figures in this folder are invented.** Example Capital Partners is a fictional customer. The folder exists to show the [partner playbook](../../docs/playbook/README.md) applied end to end; copy the structure for a real customer, not the content.

Example Capital Partners is a mid-market private-equity firm with about $4B in assets under management and 65 staff. The first role is the deal team (18 people: partners, principals and associates), with a pilot of 6. The firm runs Claude Enterprise (40 seats) with Okta and SCIM, manages staff laptops with Microsoft Intune, keeps its deal pipeline in Salesforce and its investor relations contacts in HubSpot, and works in SharePoint, OneDrive and Teams. MNPI is present in deal work, so soft walls between the deal team and investor relations are required.

| File | What it is | Status |
|---|---|---|
| [discovery.md](discovery.md) | The completed discovery questionnaire, with candidate tasks and a discovery summary | Done |
| [stakeholders.md](stakeholders.md) | Named people for each customer role, and the RACI | Done |
| [customer-profile.json](customer-profile.json) | The customer profile, built from discovery: plan, identity, devices, compliance, systems, governance. Open discovery items stay open in it, with their owner and due date. | Done; open items as in discovery |
| Role interview notes: [partner](personas/deal-team-associate/interviews/2026-11-10-partner.md), [principal](personas/deal-team-associate/interviews/2026-11-11-principal.md), [associate](personas/deal-team-associate/interviews/2026-11-12-associate.md) | The notes from the three deal-team interviews that [discovery.md](discovery.md) section F summarises | Done |
| [personas/deal-team-associate/card.json](personas/deal-team-associate/card.json) | The persona card: role, voice, four features, six tasks T1 to T6, open questions | Valid; not complete (open discovery and design items) |
| [design.md](design.md) | Org plan, data and device policy, connector plan, wall design, governance-log design | Draft, awaiting sign-off |
| [wall-test-protocol.md](wall-test-protocol.md) | How we test that the soft walls hold | Protocol written. Dry run: #82. Live run needs a customer org. |
| [backlog.md](backlog.md) | The prioritized story backlog | Draft, awaiting sign-off |

## What this sample is for, and when it is done

- This sample is a worked example of the playbook, not a live engagement. Nothing here is delivered to a customer.
- It is done when three things hold:
  - The table above links a file here or in the [starter kit](../../starter-kit/README.md) for every deliverable of phases 1 to 3 in the [engagement model](../../docs/playbook/01-engagement-model.md). Today every deliverable is linked, but the design and the backlog still await sign-off and the persona card is not complete, so the sample is not yet done.
  - The kit parts the sample uses have passed the smoke test (issue #80).
  - The wall-test protocol exists, with a dry run (issues #30 and #82).
- Actions that only the invented customer could take are illustrative: naming pilot users, sign-offs, contract checks with Anthropic, due dates and open discovery answers. They show what a real engagement tracks and are never completed in this repo. The [backlog](backlog.md) marks each one.
