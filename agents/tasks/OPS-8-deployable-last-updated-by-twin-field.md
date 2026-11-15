---
id: OPS-8
title: Deployable 'Last updated by twin' field on Opportunity, with a test that checks the metadata
domain: ops
tier: standard
status: merged
issue: 54
parent: 33
scope: [starter-kit/connectors/salesforce/**, tests/test_salesforce_marker.py]
forbid: []
red_test: python3 -m unittest tests.test_salesforce_marker
gate: test
budget: 2-attempts
spend: 10
---
## Why

At autonomy level 2 the CRM-update skill writes to opportunities, and twin writes must be told apart from human edits in the source system's field history. This ships the marker field as source metadata the CRM admin can deploy. Issue #54.

## Done when

- starter-kit/connectors/salesforce/ holds SFDX source-format metadata for a custom field on Opportunity (API name Last_Updated_By_Twin__c, type DateTime or Checkbox plus DateTime, worker states which and why), with Field History tracking enabled and a description
- A permission set grants edit on the field only to the twin's integration path and read to everyone else, or the README explains why that is not possible with per-user OAuth
- starter-kit/connectors/salesforce/README.md explains how the admin deploys it (sf project deploy start), how the CRM-update skill sets it, and how to report on twin-written changes
- tests/test_salesforce_marker.py checks the XML parses, the field API name and object are right, and history tracking is on
- The gate passes: python3 -m unittest discover -s tests

## Review

Brain review: DateTime field with history tracking and two single-field permission sets match the card; 67 tests pass. Accepted choices: DateTime over Checkbox (each write leaves a history row), object-level history as an admin prerequisite rather than shipping Opportunity.object-meta.xml, per-user OAuth limit explained in the README.
