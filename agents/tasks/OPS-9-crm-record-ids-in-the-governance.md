---
id: OPS-9
title: CRM record ids in the governance log must pass the 18-character checksum or contain a digit (15-character)
domain: ops
tier: standard
status: merged
issue: 63
parent: 19
fixes: [OPS-7]
scope: [starter-kit/plugins/twin-governance/hooks/governance_log.py, starter-kit/plugins/twin-governance/README.md, tests/test_governance_hook.py]
forbid: []
red_test: python3 -m unittest tests.test_governance_hook
gate: test
budget: 2-attempts
spend: 10
---
## Why

OPS-7 accepts any 15 or 18 alphanumeric characters as a CRM id, so an 18-letter code name such as FalconAcquisitions under a record_id key is still logged. Real 18-character ids end in a 3-character checksum of the first 15, and real ids carry digits. Issue #63.

## Done when

- An 18-character value is kept only if its last 3 characters equal the checksum computed from its first 15 (the documented algorithm: for each 5-character chunk, a bitmask of which characters are uppercase A-Z, mapped through ABCDEFGHIJKLMNOPQRSTUVWXYZ012345)
- A 15-character value is kept only if it contains at least one digit
- Tests: FalconAcquisitions and ProjectFalconXYZ (15 letters, no digit) are dropped; a real-shaped 18-character id with a correct checksum is kept and the same id with a wrong last character is dropped; a 15-character id with digits is kept
- Existing tests that used 18-character ids are updated to valid checksums
- The twin-governance README's allowlist description is updated in one or two lines
- The gate passes: python3 -m unittest discover -s tests

## Review

Brain review: checksum matches a hand-computed id (0015000000Gv7qJ -> AAR); FalconAcquisitions dropped; 53 tests pass. Accepted choices: no digit rule for 18-character ids, helpers in governance_log.py.
