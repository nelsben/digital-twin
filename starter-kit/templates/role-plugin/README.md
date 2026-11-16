# Role-plugin template

The starting folder for one role plugin: the plugin every person in one role installs, holding that role's skills and persona. Make **one role plugin per role, never per person**. A deal-team associate and a deal-team principal share `twin-pe-deal-team`; two customer-success managers share one customer-success plugin. Rules every role shares go in [twin-shared](../../plugins/twin-shared/README.md), not here.

```
role-plugin/
  twin-your-role/
    .claude-plugin/plugin.json   name, version 0.1.0, a FILL IN description
    README.md                    the plugin's own page: skills table, persona files
    skills/                      empty; one folder per skill, from templates/skill
    output-styles/               empty; the persona's output style goes here
    persona/                     README.md that says to copy templates/persona here
```

## Steps

Do them in this order.

1. **Copy and rename the folder into `starter-kit/plugins/`.** From the repo root, with the role named in the customer's design (for example `twin-customer-success`):

   ```
   cp -R starter-kit/templates/role-plugin/twin-your-role starter-kit/plugins/twin-<role>
   ```

   Then set `name` in `.claude-plugin/plugin.json` to the same text as the folder name, write the `description`, and replace the plugin's `README.md`. The test fails if the name and the folder differ.
2. **Fill the persona.** Follow the [persona template](../persona/README.md): `persona.md` first, then the output style in `output-styles/` and the system prompt in `persona/`. Delete `persona/README.md`, every FILL IN marker and the `.gitkeep` in `output-styles/`.
3. **Add skills from [templates/skill](../skill/README.md)**, once per story, evals first, following [authoring-skills.md](../../docs/authoring-skills.md). Delete the `.gitkeep` in `skills/` with the first skill.
4. **Add the entry to `.claude-plugin/marketplace.json`**, in the `plugins` list at the repo root:

   ```json
   {
     "name": "twin-<role>",
     "source": "./starter-kit/plugins/twin-<role>",
     "description": "Role twin for <role>: one sentence on its skills and output style."
   }
   ```
5. **Run the tests** from the repo root: `python3 -m unittest discover -s tests`. They check the manifest, every skill and its evals, that the marketplace lists the plugin, and that the persona forms match `persona.md`.

The template itself is not in the marketplace and is not a plugin to install. Only the copy in `starter-kit/plugins/` is.
