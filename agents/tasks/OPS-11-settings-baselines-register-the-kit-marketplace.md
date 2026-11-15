---
id: OPS-11
title: Settings baselines register the kit marketplace and enable the governance plugin, and the settings README and identity runbook describe them truthfully
domain: ops
tier: standard
tier_reason: config keys must match the current Claude Code docs exactly; small change with tests
status: merged
issue: 78
parent: 23
fixes: [OPS-4, SHA-11]
scope: [starter-kit/settings/**, tests/test_settings.py, starter-kit/runbooks/identity-devices-publishing.md]
forbid: []
red_test: python3 -c "import json;d=json.load(open('starter-kit/settings/pe-zdr.managed-settings.json'));assert d['enabledPlugins']['twin-governance@digital-twin-kit'] is True and 'extraKnownMarketplaces' in d"
gate: test
budget: 2-attempts
spend: 10
---
## Why

A device that receives one of the four managed-settings baselines as shipped gets no marketplace, no plugins and no governance log, because the files only allowlist the marketplace and never register it or enable a plugin. Two documents describe the files wrongly: the identity runbook says the registration exists, and the settings README still says the governance hook is an unwired placeholder (it was delivered in #21). The baselines must be deployable as written and the documents must match the files.

## Done when

- Before changing any file, the worker reads the current Claude Code docs for these keys and follows their exact names and shapes: https://code.claude.com/docs/en/plugins/org , https://code.claude.com/docs/en/settings-reference , https://code.claude.com/docs/en/plugin-marketplaces and the allowManagedHooksOnly entry (settings reference or https://code.claude.com/docs/en/hooks). Where the docs differ from this card, the docs win and the report lists each difference
- All four baselines (general, confidential, pe-zdr, hipaa) have an extraKnownMarketplaces entry that registers the marketplace named digital-twin-kit from the same github source as the existing strictKnownMarketplaces entry, with the repo placeholder REPLACE-WITH-GITHUB-ORG/digital-twin-kit unchanged
- All four baselines have enabledPlugins with "twin-shared@digital-twin-kit": true. The confidential, pe-zdr and hipaa baselines also have "twin-governance@digital-twin-kit": true. The general baseline does not enable twin-governance. No baseline enables twin-pe-deal-team or any other role plugin: role plugins stay a per-group step in the runbook
- The confidential, pe-zdr and hipaa baselines have an env block that sets TWIN_GOVERNANCE_ORG_LABEL (values confidential, pe-zdr, hipaa) and TWIN_GOVERNANCE_SALT with the placeholder REPLACE-WITH-GOVERNANCE-SALT, if the docs confirm env is honoured in managed settings. TWIN_GOVERNANCE_TWIN_ID and TWIN_GOVERNANCE_LOG are not set in the baselines (they vary per role and per customer); the README says where to set them
- The pe-zdr baseline sets forceLoginMethod to the same value the hipaa baseline uses, because engagements/sample-pe/design.md section 3 says the private-equity settings set it
- The settings README states, with a link to the doc page that says it, whether a plugin's hooks run under allowManagedHooksOnly when the plugin is enabled through managed-settings enabledPlugins. If the docs do not confirm it, the README marks the point with the compendium's unverified marker (docs/compendium/README.md, Conventions) and says it must be checked on one managed device before rollout. The worker does not state it as settled without a source
- The 'Governance hook (placeholder)' section and its TODO comment are removed from starter-kit/settings/README.md and replaced by a short section saying how the hook reaches a device (the enabledPlugins entry in the three sensitive baselines) with a link to starter-kit/plugins/twin-governance/README.md. The Keys table gains a row for each new key, the placeholder list names REPLACE-WITH-GOVERNANCE-SALT, and the README stays under 80 lines (a test enforces this)
- In starter-kit/runbooks/identity-devices-publishing.md the bullet at about line 143 and steps 0.4, 6.1, 6.3 and 6.5 match the baselines as changed: the baselines register the marketplace and enable twin-shared and (for three classes) twin-governance; step 6.3 is about adding the role plugin for each group. The sentence 'The shipped baselines do not contain enabledPlugins' is corrected
- The worker checks every statement in that runbook that is cited as [repo file] or [repo files], or that names a path in this repo, against the file on its branch, corrects any that are false, and lists each statement checked in its report as pass or fixed
- tests/test_settings.py asserts the new keys: marketplace registered in all four files, twin-shared enabled in all four, twin-governance enabled in exactly the three sensitive files, no role plugin enabled anywhere, the salt placeholder present where env is set, and the top-level key allowlist updated. Existing tests still pass
- No real org id, repo owner, salt or host name is written anywhere; placeholders only
- The gate passes: python3 -m unittest discover -s tests

## Review

Brain review: all four baselines now register digital-twin-kit and enable twin-shared (plus twin-governance in confidential, pe-zdr, hipaa); env carries org label and salt placeholder; pe-zdr gains forceLoginMethod claudeai. Settings README placeholder section replaced; runbook step 6.5 hook statement corrected. Tests 70 -> 77. Noted for SHA-21: runbook steps 1.7 and 6.2 point at a "Choices list" that does not exist.
