# Level 2: writing to Salesforce with approval

Open this only when the user's role setup puts this task at autonomy level 2 and the Salesforce update tool is set to Needs approval. At level 1 none of it applies. The marker field is described in [starter-kit/connectors/salesforce/README.md](../../../../../connectors/salesforce/README.md).

Contents: before the write, the write, if it fails, after the write.

## Before the write

1. Finish steps 1 to 6 of `SKILL.md` and show the draft. The user must approve the exact text and say which opportunity it is for. An earlier "save it" does not count: approve after seeing the final text.
2. Confirm the user can edit this record, not only read it. Ask Salesforce for the user's edit access on the opportunity (for example the `UserRecordAccess` record for the user and the opportunity, field `HasEditAccess`). If it says no, or cannot be checked, do not write. Show the draft for the user to paste and say why.
3. Confirm the opportunity is the one read in step 1 of `SKILL.md`, by record ID.

## The write

Send one update call to the opportunity that carries:

- the activity log text and the next-step text, exactly as approved;
- `Last_Updated_By_Twin__c` set to the current time in UTC, ISO 8601, for example `2026-11-14T09:30:00.000Z`.

Rules:

- The marker goes in the same call as the field changes, so the history rows share a timestamp. If only one field changes, the marker is still sent.
- Never a past or future time. Never clear the marker. Never set it on a read.
- Change only the fields the user approved.

## If it fails

If Salesforce rejects the call because of the marker (the user lacks `Twin_Marker_Edit`, or the field is not deployed), do not retry without it. Stop, tell the user the marker is missing, and show the draft for the user to paste. No unmarked twin write may reach Salesforce. Other failures (record locked, validation rule): report the error text, do not retry with different content, and show the draft.

## After the write

Tell the user what was written, to which record ID, and that the marker was set. Do not claim more than the tool's reply confirms.
