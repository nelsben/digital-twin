# Authoring a twin skill

For consultants. A twin skill is one `SKILL.md` folder that turns a story into repeatable work. Every skill starts from the template in [../templates/skill/](../templates/skill/README.md), and every skill is evaluated before it ships. Background and the reasons are in [compendium 03](../../docs/compendium/03-skills-authoring.md); the choice of tools is in [compendium 16](../../docs/compendium/16-oob-skills-and-references.md).

## Step order

Do the steps in this order. Writing evals before the skill is the rule that matters most: Anthropic's method is to find where Claude falls short without a skill, write the cases from those gaps, then write the minimum instructions that fix them ([best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

1. **Collect 3 real examples from the skill owner.** Real inputs and the output the owner would accept, not invented ones. This is also the story's definition of ready ([04-stories](../../docs/playbook/04-stories.md)). One example should have something missing or messy, and one should be a request that sounds similar but is a different task.
2. **Write the evals.** Copy the template (see its [README](../templates/skill/README.md)), then fill in `evals/evals.json` and `evals/trigger-evals.json` from the examples. Run the task once without the skill and note where Claude falls short.
3. **Write the skill.** Fill in `SKILL.md`: the least text that fixes the failures you saw. Keep the body under 150 lines, put detail in `references/`, and keep the three guardrails (twin marker on writes, no web tools for highly sensitive data, ask instead of guessing).
4. **Run skill-creator's eval and description-tuning loop.** Install skill-creator (see below). It runs each case with and without the skill, grades the `expectations`, and shows results in a viewer. Then it tunes the description against `trigger-evals.json`, holding some queries back to avoid overfitting. Both are described in the [skill-creator source](https://github.com/anthropics/skills/tree/main/skills/skill-creator) and in the Claude Code docs section "Run evals with skill-creator" ([Claude Code skills](https://code.claude.com/docs/en/skills)). Run its loop with the model ID the session uses, so the triggering test matches what users see.
5. **Test on the models the customer uses.** A skill that works on one model may not work on another, so run the evals on each model the customer has enabled ([best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)). Record the pass rate per model in the story.
6. **Run the repo tests.** `python3 -m unittest discover -s tests`. The structure tests check the name (and that it matches the folder), the description limit, the body length and the frontmatter keys. The limits come from the [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview). Our own limits are stricter: descriptions under 200 characters, bodies under 150 lines (compendium 03).
7. **Get a reviewer who is not the author.** This is in the story's definition of done ([04-stories](../../docs/playbook/04-stories.md)). The reviewer reads the skill and runs the evals.

## The eval files

The template follows skill-creator's own formats, so its tooling reads them without conversion.

- `evals/evals.json` is skill-creator's functional eval file (location and fields as given in its [`references/schemas.md`](https://github.com/anthropics/skills/blob/main/skills/skill-creator/references/schemas.md)). Fields: `skill_name`, and for each case `id`, `prompt`, `expected_output`, `files` and `expectations` (a list of checkable statements).
- `evals/trigger-evals.json` is the input to skill-creator's description-tuning loop (`scripts.run_loop --eval-set`): a list of `{"query": ..., "should_trigger": true|false}`. Skill-creator keeps it out of `evals.json`, so we do too. Its guidance: realistic, detailed queries, and near-miss negatives rather than obviously unrelated ones.

One wrinkle: skill-creator's `SKILL.md` calls the per-case checks "assertions" in places, while its schema file names the field `expectations`. We follow the schema file. If a later version of skill-creator renames the field, follow the installed version and change the template.

## Mapping a story's acceptance criteria to evals

The story template in [04-stories](../../docs/playbook/04-stories.md) lists acceptance criteria "(evals)". Turn each one into a case or an expectation:

| In the story | In the skill's evals |
|---|---|
| A criterion about a real example ("for the 3 example deals, the brief contains...") | One case in `evals.json` per example. The criterion's contents become `expectations`. |
| A criterion about missing data ("if the deal folder is empty, the brief says what is missing") | A missing-data case: the input is absent, and the expectations say the skill names the gap and asks. |
| "The skill triggers on `<phrases>`" | `should_trigger: true` entries in `trigger-evals.json`, using the owner's own words. |
| A task the owner says people confuse with this one | A `should_trigger: false` entry, and a should-not-trigger case in `evals.json`. |
| "Every write carries the twin marker" | An expectation on any case that writes. |
| "No web tools (if MNPI)" | An expectation such as "No web search or fetch was used". Also enforce it in settings, not only in the skill. |
| "A user without access gets no data" or "the governance log shows record IDs only" | Not skill evals. These test connectors, permissions and hooks. Test them as spike or task work, and tick them off in the story's definition of done ([04-stories](../../docs/playbook/04-stories.md)). |

The three placeholder cases in the template (normal, missing data, should not trigger) are the minimum. Add a case for every failure found later.

## When to use the CLAUDE_CODE_ONLY marker

Default: frontmatter holds `name` and `description` only. That is the safe set on every surface; claude.ai and the Skills API accept a short list of keys and reject others at upload ([compendium 03](../../docs/compendium/03-skills-authoring.md), from the [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)), while Claude Code accepts many more ([Claude Code skills](https://code.claude.com/docs/en/skills)).

Add an empty file named `CLAUDE_CODE_ONLY` to the skill folder only when the skill needs Claude Code-only frontmatter (for example `allowed-tools`, `disable-model-invocation`, `context`, `paths`, `hooks` or `model`) and the customer runs it in Claude Code alone. The structure test then allows any keys in that skill. Rules:

- Say why in the story, and keep a separate variant; never put these keys in the shared master copy.
- The skill must not be uploaded to claude.ai or the API, so list it only in plugins installed through Claude Code.
- Prefer a hook or a managed setting for a rule that must hold every time ([hooks](https://code.claude.com/docs/en/hooks)).

## Install skill-creator

In Claude Code, from the official marketplace ([Anthropic's marketplaces](https://code.claude.com/docs/en/plugins/anthropic-marketplaces), [install plugins](https://code.claude.com/docs/en/plugins/install)):

```
/plugin install skill-creator@claude-plugins-official
```

Shell form: `claude plugin install skill-creator@claude-plugins-official`. The official marketplace is added automatically the first time you start an interactive session. Alternatively, copy the folder from [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/skill-creator); it is licensed Apache 2.0 per its own `LICENSE.txt` (compendium 16). Anthropic describes these skills as demonstration material, so test it on your own machine before relying on it in an engagement.

Once a role is packaged as a plugin, `claude plugin eval` can run the suites in CI ([plugin evals](https://code.claude.com/docs/en/plugin-evals)). Whether skill-creator works inside claude.ai is unverified; run the eval loop in Claude Code.

## Links

- [Skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Defining success criteria and test cases](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Anthropic's template skill](https://github.com/anthropics/skills/tree/main/template)
