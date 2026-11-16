---
id: OPS-77
title: The backlog and dashboard show build status: each skill, publish and agent-setup task links its artifact and is raised (never lowered) by build.json, and the dashboard gains a Build section
domain: ops
tier: standard
tier_reason: two existing generators read one new file with a fixed mapping
status: merged
issue: 258
parent: 254
fixes: []
scope: [partner-kit/plugins/twin-consultant/scripts/twincard/backlog.py, partner-kit/plugins/twin-consultant/scripts/twincard/dashboard.py, partner-kit/plugins/twin-consultant/README.md, partner-kit/plugins/twin-consultant/skills/building-twin-stories/**, partner-kit/README.md, partner-kit/docs/design.md, README.md, engagements/sample-pe/personas/**, engagements/sample-team-cs/personas/**, tests/test_twincard_build_status.py, tests/test_twincard_backlog.py, tests/test_twincard_dashboard.py, tests/test_twincard_end_to_end.py, tests/fixtures/twincard/**]
forbid: [docs/**, starter-kit/**, .claude-plugin/marketplace.json, CLAUDE.md, agents/tasks/**, partner-kit/plugins/twin-consultant/data/rules.json, partner-kit/plugins/twin-consultant/data/plan-fit.json, partner-kit/plugins/twin-consultant/data/task-library.json, partner-kit/plugins/twin-consultant/scripts/twincard/level.py, partner-kit/plugins/twin-consultant/scripts/twincard/build.py, partner-kit/plugins/twin-consultant/scripts/twincard/package.py, engagements/sample-pe/build/**, engagements/sample-team-cs/build/**]
red_test: python3 -m unittest tests.test_twincard_build_status
gate: test
budget: 3-attempts
spend: 10
---
## Why

After OPS-74 to OPS-76 the build state lives in build.json while the backlog and dashboard, the views the consultant and customer read, still show every build task as todo. This card closes the loop for epic #254 so one dashboard per persona shows plan, build and deployment together.

## Done when

- Read first: partner-kit/docs/design.md sections 8, 8a and 9, backlog.py, dashboard.py, build.py and the build.json of both samples. Read only outside scope.
- BACKLOG LINK. When <persona-dir>/build/build.json exists, backlog.py gives each task story's write-skill, write-evals, trigger-evals, publish-in-role-plugin and runtime setup tasks (the setup-<runtime> template and its wiring tasks) an `artifact` key {id, path, status} for that story's artifact, printed in backlog.md under the task. Status mapping, applied only to raise a task's status and never to lower one a person set: drafted -> write-skill in-progress; evals-passing -> write-skill, write-evals and trigger-evals done; packaged -> publish-in-role-plugin or the setup task in-progress; deployed -> that task done; verified changes nothing here (the owner-handover task stays a person's call). With no build.json, backlog output is byte-identical to today's. backlog.json's source gains build_sha256 only when build.json exists, so the staleness check covers it; design section 8 says so.
- DASHBOARD. dashboard.py gains a Build section after the plan, when build.json exists: one row per artifact with kind, skill name, location (path as text), status, the runbook link as text, and the last history entry's by, pass rate and baseline; and a one-line count per status. No JavaScript; it stays publishable as one static page (design section 9). With no build.json the page is byte-identical to today's.
- `all` keeps its steps; the README and design say the order is all, build, then backlog and dashboard again after any build or record change.
- SAMPLES. Regenerate both fictional samples (all, then backlog and dashboard). The Team sample shows its drafted skill's write-skill task in-progress; nothing else changes status. Completeness lines do not change. Everything stays fictional.
- Docs in the same change: design.md sections 8 and 9; the plugin README; partner-kit/README.md; the top-level README.md flow line if it describes the workflow's end; the building-twin-stories skill if it tells the consultant how to mark build tasks.
- Tests: new tests/test_twincard_build_status.py covers each mapping row, raise-never-lower (a done task stays done when build.json says drafted), the artifact key and its backlog.md line, the staleness check with build.json changed, byte-identical output with no build.json for backlog and dashboard, the dashboard Build section and its counts, and both committed samples matching a fresh run. The whole suite passes: python3 -m unittest discover -s tests.
- Hand-back lists: every sample task whose status changed, before and after; every decision you had to make that this card did not.
- Test runs: the shared Mac test lease may be held by another project for hours. Run tests through `node /Users/bennelsen/WorkflowBridge/bin/wb lease gate-mac --wait 600 -- <command>`; never bypass the hook. Write the red test first and run it red through the lease; never run tests outside the lease. If the lease is not granted within 20 minutes in total, commit the red test alone, then build, commit and hand back with gate=fail and the words 'gate not run: lease blocked'. Do not end your turn while a queued run is pending. files= lists every file changed since origin/main; keep the red output file under 1 MB.

## Review

Verifier consistent at 4bea308 after the brain granted 4 test files (acceptance, dashboard_story_view, hardening, starting_points); no reviewer (next=accept). Brain read the four test edits: each sets only the new Build section aside or copies build/ into the temp sample, and loosens nothing else. All 4 backlog.json fixture copies are byte-identical to their sources. Neither dashboard has a script tag. Nothing under build/ changed. Only the Team S-C1 story (write-skill) and its derived parents moved todo -> in-progress. 1014 tests.
