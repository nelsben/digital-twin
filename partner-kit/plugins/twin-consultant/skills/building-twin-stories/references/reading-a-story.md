# Reading a task story

What the generated fields of a task story in `backlog.json` mean while you
build. The rules that make them are in
[design section 8](../../../../../docs/design.md#statement-target-ready-and-done).

## Statement

`statement` reads "As a <role>, I want my twin to <want> so that
<benefit>." `statement_source` says where the words came from:

- `card`: the card's `story_want` and `story_benefit`, in the
  interviewee's words. Use it as it stands.
- `drafted`: the kit wrote one half or both, from the task's output and its
  minutes, because the notes did not say. `backlog.md` marks it. Tell the
  consultant to confirm the wording with the interviewee and to fill in
  `story_want` and `story_benefit` through `planning-a-twin`. Never reword
  the statement yourself.

## Target

`target` comes from the card's `outcome.scorecard_targets`, with the task's
frequency, minutes and users today. When `set` is false there is no number
yet: say the sponsor must agree the scorecard targets before the pilot
starts, and invent none. `backlog.md` counts the stories with no target.

## Ready

`ready` lists the definition-of-ready checks, in this order, each with `met`
and a `note` that says what is missing:

| Check | Met when |
|---|---|
| `fields` | the task's data class, surface, autonomy start and ceiling and identity are decided |
| `examples` | at least 3 examples are counted on the card |
| `connectors` | every system the task uses has a decided connector, identity and permission, and no blocker names it |
| `compliance-sign-off` | only for a highly sensitive or PHI task: its `compliance-sign-off` task is done |

Build a story only when every check is met; `backlog.md` says
`Ready to build: yes` or `no` with the unmet checks. The work that meets a
check is a task of its own (`collect-examples`, `compliance-sign-off`) or a
change to the card through `planning-a-twin`.

## Writing the skill

A task story's `write-skill` task is where the twin's instructions are
written, for a client skill and for a hosted or scheduled agent alike.
When the card task names Anthropic skills to build on (`starts_from`),
the task's title names them and its first steps read
`Start from <name> (<where>): <what the pack says about it>`, each linked
to the compendium page the pack cites. A step marked `⚠ Unverified` means
the pack is not sure of that fact: read the page before building on it.
Without those steps the skill starts from the kit's template.

## Foundation stories

`S-connectors-and-identity` may carry `data_providers`: the data providers
the industry pack knows, shown in `backlog.md` as a table headed
`Data providers the pack knows (none is on by default)`. Listing one does
not allow it. The `data-providers-decide` task has compliance decide each
provider (allowed, not allowed or later, with who approved it and why),
and the decision is written in the customer's engagement folder.

`S-guardrails-and-settings` has `retention-and-feedback-settings` (set the
org's retention and feedback settings to the data policy and record them)
and, on Team and Enterprise, `spend-limits` (set the org and per-user
spend limits and name who watches them; its owner is the profile's spend
owner when one is named). Both are admin work: hand the steps over.

## Gates and spikes

`gated_by` lists what holds the story: a `blocker`, an `open-question`
(its `spike` names the spike that answers it) or, until the
`compliance-sign-off` task is done, a `sign-off` from compliance.

The backlog's `spikes` are the card's open questions, each with an id
`SP-<n>`, a title, an owner, a due date and the story ids it `blocks`.
`backlog.md` lists them in its `Spikes` section. A spike is not build
work: the people it names answer it, and the answer goes onto the card
through `planning-a-twin`. Change a spike's `status` in `backlog.json` the
way you change a task's, only forward; a spike the card no longer has moves
to `retired`.

## Done

Every story with a runtime ends with its `owner-handover` task: the skill
owner learns where the skill lives, how to change it with an eval case, and
who reviews a change, then makes one change while the engineer watches. The
map from the playbook's definition of done to the tasks is in the design
section linked above.
