---
id: OPS-14
title: Twin_Marker_Edit's description is 255 characters or fewer, and a test keeps every marker permission set description within Salesforce's limit
domain: ops
tier: economy
tier_reason: mechanical shorten one XML string and add one length test
status: merged
issue: 93
fixes: []
scope: [starter-kit/connectors/salesforce/force-app/main/default/permissionsets/Twin_Marker_Edit.permissionset-meta.xml, tests/test_salesforce_marker.py]
forbid: []
red_test: python3 -m unittest tests.test_salesforce_marker (the new description-length test fails on the current 338-character description)
gate: test
budget: 2-attempts
spend: 3
---
## Why

The OPS-13 scratch-org dry run showed the marker metadata fails to deploy: Salesforce rejects Twin_Marker_Edit's 338-character description (max 255), and because the deploy is all or nothing, the field and Twin_Marker_Read don't land either. A customer admin following the marker README would hit the same failure.

## Done when

- The <description> in starter-kit/connectors/salesforce/force-app/main/default/permissionsets/Twin_Marker_Edit.permissionset-meta.xml is 255 characters or fewer after stripping surrounding whitespace.
- The new description still says: it grants edit access to Opportunity.Last_Updated_By_Twin__c for the identity the twin writes as; assign it to the integration user when the twin connects through one; with per-user OAuth assign it to the users whose twin writes to opportunities; and it points to the README for why it cannot be limited to the twin alone.
- Nothing else in that XML file changes, and Twin_Marker_Read.permissionset-meta.xml is unchanged.
- tests/test_salesforce_marker.py has a test that fails if the description of any *.permissionset-meta.xml file under the marker's permissionsets folder is longer than 255 characters, with a comment citing the 255 limit as found by the OPS-13 deploy error (starter-kit/connectors/salesforce/wall-test/README.md).
- The new test fails against the old 338-character description and passes after the fix.
- python3 -m unittest discover -s tests passes.

## Review

Attempt 1/2 consistent, next=accept. Checked by hand: 2 files, 12 insertions, both in scope. The description is now exactly 255 characters and keeps all four points (edit access for the identity the twin writes as; integration user; per-user OAuth users; README pointer). The new test covers every permission set in the folder, and the red run failed at 338. 88 tests pass. Not re-deployed to a scratch org: the only error OPS-13 saw in the final run was this description, so deploy success is expected but unconfirmed.
