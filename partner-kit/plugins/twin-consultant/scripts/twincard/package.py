"""Package a customer's role twins and write the deploy checklist (design section 8a).

package(customer_dir) reads every persona's build/build.json under engagements/<customer>/personas/ and
writes, under engagements/<customer>/build/:

- marketplace/: .claude-plugin/marketplace.json (the shape of the repository's own) and plugins/<plugin>/,
  a copy of each persona's role plugin, when every skill in it is evals-passing or above;
- bundles/<persona>/<task>/: each agent, routine, scheduled-task and SDK wrapper at evals-passing or
  above, with its skill folder beside it;
- deploy.md: the deployment tasks already in each persona's backlog.json, in deployment order.

It then records packaged for each artifact it packaged that was evals-passing. With include_drafts it
writes marketplace-draft/ and bundles-draft/ instead, takes drafted artifacts too, prefixes every plugin
description with DRAFT_PREFIX and records nothing. deploy.md is the same either way. The partner kit is
never packaged. Two runs on the same inputs give the same bytes.
"""

import json
import shutil
from pathlib import Path

from . import backlog as _backlog
from . import build as _build
from . import dashboard as _dashboard
from . import validate as _validate

OUT_DIR = "build"
DEPLOY_FILE = "deploy.md"
DRAFT_PREFIX = "DRAFT, not evaluated: "
PARTNER_KIT = "twin-consultant"
TO_REPO = "../../../"  # from engagements/<customer>/build/ to the repository root
WRAPPER_DIRS = ("scheduled", "routines", "agents", "sdk")  # build's wrapper folders (design 8a, kinds)
NO_PACKAGE = "none, a setting, a record or an account in the customer's systems"

# The deploy.md sections, in order, and the task-library templates each one takes from the backlog.
# deploy.md shows only tasks the backlog already has; it never adds a step of its own.
SECTIONS = (
    ("1. Org settings and data policy",
     ("data-policy", "retention-and-feedback-settings", "spend-limits", "zdr-retention", "zdr-retention-agreement-first",
      "settings-deploy", "settings-none", "web-tools-off", "memory-off")),
    ("2. Identity and groups",
     ("identity-scim-groups", "identity-team-members", "credentials-user", "credentials-service-account",
      "credentials-api-key-vault")),
    ("3. Connectors and tool permissions",
     ("connector-review", "connect-salesforce-runbook", "connect-microsoft-365-runbook", "connect-kit-runbook",
      "connect-no-runbook", "connect-own-mcp-server", "twin-marker-salesforce", "twin-marker-hubspot",
      "twin-marker-zendesk", "twin-marker-crm", "tool-always-allow", "tool-needs-approval", "tool-blocked")),
    ("4. Publish the marketplace",
     ("distribute-group", "distribute-everyone", "distribute-manual", "publish-in-role-plugin",
      "publish-in-role-plugin-team")),
    ("5. Hosted agents, routines and scheduled tasks",
     ("setup-managed-agents", "setup-managed-agents-self-hosted", "setup-agent-sdk", "setup-tag-routine",
      "setup-scheduled-task", "start-wiring")),
    ("6. Governance hook",
     ("governance-log-destination", "governance-hook-deploy", "governance-without-hook")),
    ("7. Check it worked and hand over",
     ("settings-verify", "governance-log-check", "source-audit", "wall-test")),
)
CHECK_ANCHORS = ("#check-it-worked", "#hand-over")
HANDOVER = "owner-handover"
SECTION_INTRO = {
    "1. Org settings and data policy": "Settings and decisions in the customer's Claude org, before anyone uses a twin.",
    "2. Identity and groups": "Who the twin's users are, and the accounts its hosted runs use. A credential is "
                              "created in the customer's secret store; this checklist names it, never its value.",
    "3. Connectors and tool permissions": "Each connector the tasks use, and each tool's permission as the levelled "
                                          "plan sets it.",
    "4. Publish the marketplace": "Publish the customer marketplace and the role plugin to the people the plan names.",
    "5. Hosted agents, routines and scheduled tasks": "Each runtime outside the chat, created from its bundle.",
    "6. Governance hook": "Where the governance log goes, and the hook that writes it.",
    "7. Check it worked and hand over": "Each runbook's check-it-worked and hand-over step, then each skill's "
                                        "hand-over to its owner.",
}
DISTRIBUTION = {
    "group-targeted": "Distribution: group-targeted (Enterprise). Publish the marketplace to the role's group only.",
    "everyone": "Distribution: everyone (Team). The plan has no group targeting, so every member gets the role plugin.",
    "manual": "Distribution: manual. Each person installs the role plugin themselves, one install per person.",
}
PACKAGE_NEXT = ("Next: run the evals, record evals-passing for each artifact, then run package again; or run "
                "package --include-drafts to look at a draft")


class PackageError(ValueError):
    """The customer folder cannot be packaged (exit 2)."""


def _rank(status):
    return _build.ORDER.index(status) if status in _build.ORDER else -1


def _copy_tree(src, dst):
    """Copy every file under src to dst, in sorted order; bytes only, so reruns give the same files."""
    for path in sorted(Path(src).rglob("*")):
        if path.is_file():
            target = Path(dst) / path.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())


def _json_bytes(data):
    return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _personas(customer):
    folder = customer / "personas"
    return [p for p in sorted(folder.iterdir()) if p.is_dir() and (p / _validate.CARD_FILE).is_file()]


def _wrapper_files(build_dir, item):
    """[(path inside the bundle folder, source path)] for the artifact's wrapper files (build/<wrapper>/<id>/...)."""
    out = []
    prefix = _build._repo_path(str(build_dir.parent), "")
    for entry in item["files"]:
        if not entry["path"].startswith(prefix):
            continue
        parts = Path(entry["path"][len(prefix):]).parts
        if len(parts) > 2 and parts[0] in WRAPPER_DIRS and parts[1] == item["id"]:
            out.append((Path(*parts[2:]).as_posix(), build_dir.joinpath(*parts)))
    return out


def _plan_persona(customer, persona, include_drafts, notes):
    """What to package from one persona: {persona, plugin, left_out, bundles, packaged, manifest}; None when nothing."""
    manifest = _build.read_manifest(str(persona))
    pid = persona.name
    if manifest is None:
        notes.append("%s: nothing to package: there is no build/build.json. Next: run the build command" % pid)
        return None
    floor = _rank("drafted" if include_drafts else "evals-passing")
    floor_name = "drafted" if include_drafts else "evals-passing"
    build_dir = persona / _build.BUILD_DIR
    items = [a for a in manifest["artifacts"] if a["status"] != "not-built"]
    ready = [a for a in items if _rank(a["status"]) >= floor]
    plugin = manifest["plugin"]["name"]
    in_plugin = [a for a in items if a.get("skill_location") == "plugin"]
    plan = {"persona": pid, "plugin": None, "left_out": [], "bundles": [], "packaged": [], "manifest": manifest}
    if not ready:
        notes.append("%s: nothing to package: no artifact is %s or above (%s). %s"
                     % (pid, floor_name, ", ".join("%s %s" % (a["id"], a["status"]) for a in items) or "none built",
                        PACKAGE_NEXT if not include_drafts else
                        "Next: replace every FILL IN in an artifact's files, then run build, which sets drafted"))
        return None
    if plugin == PARTNER_KIT:
        notes.append("%s: nothing to package: the role plugin is named %s, the partner kit, which is never "
                     "packaged. Next: give the role plugin its own name on the card" % (pid, PARTNER_KIT))
        return None
    if in_plugin:
        below = [a for a in in_plugin if _rank(a["status"]) < floor]
        fill = [p for p in (".claude-plugin/plugin.json", "README.md")
                if _build.FILL_IN in (build_dir / "plugin" / plugin / p).read_text(encoding="utf-8")]
        if include_drafts and len(below) < len(in_plugin):
            plan["plugin"] = plugin
            plan["left_out"] = below
            if below:
                notes.append("%s: the draft of %s leaves out %s (below drafted)"
                             % (pid, plugin, ", ".join("%s %s" % (a["id"], a["status"]) for a in below)))
        elif include_drafts:
            notes.append("%s: the draft leaves out role plugin %s: none of its skills is drafted yet" % (pid, plugin))
        elif not below and not fill:
            plan["plugin"] = plugin
        elif below:
            notes.append("%s: role plugin %s not packaged: every skill in it must be evals-passing or above, and %s. %s"
                         % (pid, plugin, ", ".join("%s is %s" % (a["id"], a["status"]) for a in below), PACKAGE_NEXT))
        else:
            notes.append("%s: role plugin %s not packaged: its %s still say FILL IN. Next: fill them in, then run "
                         "package again" % (pid, plugin, " and ".join(fill)))
    plan["bundles"] = [a for a in ready if a["kind"] not in ("skill", "none")]
    if plan["plugin"]:
        plan["packaged"] += [a for a in in_plugin if not any(a is b for b in plan["left_out"])]
    plan["packaged"] += [a for a in plan["bundles"] if not any(a is b for b in plan["packaged"])]
    if not plan["packaged"]:
        notes.append("%s: nothing to package: the role plugin is left out, for the reason above, and the "
                     "persona has no other artifact" % pid)
        return None
    return plan


def _marketplace_path(plugin, skill):
    return "build/marketplace/plugins/%s/skills/%s/" % (plugin, skill)


def _bundle_path(pid, tid):
    return "build/bundles/%s/%s/" % (pid, tid)


def _artifact_path(manifest, pid, item):
    """The package path deploy.md shows for an artifact (the evaluated output, never the draft folders)."""
    if item is None:
        return "not built yet. Next: run the build command"
    if item["kind"] == "none":
        return "none: the task has no runtime, so nothing is built"
    if item["kind"] == "skill":
        return _marketplace_path(manifest["plugin"]["name"], item["skill_name"])
    return _bundle_path(pid, item["id"])


def package(customer_dir, include_drafts=False):
    """Package the customer's twins; {notes, plugins, bundles, recorded, marketplace, deploy}. PackageError on bad input."""
    customer = Path(customer_dir)
    profile_path = customer / _validate.PROFILE_FILE
    if not customer.is_dir():
        raise PackageError("no such customer folder: %s. Next: give engagements/<customer>, the folder that holds "
                           "customer-profile.json and personas/" % customer)
    if not profile_path.is_file() or not (customer / "personas").is_dir():
        raise PackageError("%s holds no customer-profile.json and personas/ folder, so it is not a customer folder. "
                           "Next: give engagements/<customer>, not a persona folder" % customer)
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except ValueError:
        raise PackageError("%s is not JSON. Next: fix it, then run package again" % profile_path)
    notes, plans = [], []
    for persona in _personas(customer):
        plan = _plan_persona(customer, persona, include_drafts, notes)
        if plan:
            plans.append(plan)
    out = customer / OUT_DIR
    market = out / ("marketplace-draft" if include_drafts else "marketplace")
    bundles = out / ("bundles-draft" if include_drafts else "bundles")
    for folder in (market, bundles):
        if folder.exists():
            shutil.rmtree(str(folder))
    entries, written_bundles, recorded = [], [], []
    repo_customer = "engagements/%s" % customer.resolve().name
    for plan in plans:
        persona = customer / "personas" / plan["persona"]
        build_dir = persona / _build.BUILD_DIR
        manifest = plan["manifest"]
        if plan["plugin"]:
            name = plan["plugin"]
            dst = market / "plugins" / name
            _copy_tree(build_dir / "plugin" / name, dst)
            for item in plan["left_out"]:
                shutil.rmtree(str(dst / "skills" / item["skill_name"]), ignore_errors=True)
            meta_path = dst / ".claude-plugin" / "plugin.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            description = meta.get("description") or ""
            if include_drafts:
                description = DRAFT_PREFIX + description
                meta["description"] = description
                meta_path.write_bytes(_json_bytes(meta))
            entries.append({"name": name, "source": "./plugins/%s" % name, "description": description})
        for item in plan["bundles"]:
            dst = bundles / plan["persona"] / item["id"]
            folder = _build.skill_folder(manifest, item)
            for rel, src in _wrapper_files(build_dir, item):
                target = dst / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(src.read_bytes())
            if folder:
                _copy_tree(build_dir / folder, dst / item["skill_name"])
            written_bundles.append("%s/%s" % (plan["persona"], item["id"]))
        if include_drafts:
            continue
        for item in plan["packaged"]:
            if item["status"] != "evals-passing":
                continue
            where = _bundle_path(plan["persona"], item["id"]) if item in plan["bundles"] else \
                _marketplace_path(plan["plugin"], item["skill_name"])
            entry = {"status": "packaged", "by": "package", "evidence": "%s/%s" % (repo_customer, where),
                     "pass_rate": None, "baseline_rate": None, "pass_mark": None, "approved_by": None}
            _build.write_status(str(persona), _build.read_manifest(str(persona)), item["id"], "packaged", entry)
            recorded.append("%s %s" % (plan["persona"], item["id"]))
    if entries:
        name = profile.get("marketplace_name")
        name = name if isinstance(name, str) and name.strip() else "%s-twins" % profile.get("customer")
        display = profile.get("display_name") or profile.get("customer")
        description = "Role twins for %s." % display
        if include_drafts:
            name, description = name + "-draft", DRAFT_PREFIX + description
        data = {"name": name, "description": description, "owner": {"name": display},
                "plugins": sorted(entries, key=lambda e: e["name"])}
        target = market / ".claude-plugin" / "marketplace.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(_json_bytes(data))
    deploy = render_deploy(customer, profile, notes)
    out.mkdir(parents=True, exist_ok=True)
    (out / DEPLOY_FILE).write_bytes(deploy.encode("utf-8"))
    return {"notes": notes, "plugins": [e["name"] for e in entries], "bundles": written_bundles,
            "recorded": recorded, "marketplace": market if entries else None, "deploy": out / DEPLOY_FILE}


# --- deploy.md -----------------------------------------------------------------------------------------------

def _owner(task):
    text = task["owner_role"]
    if task.get("owner_name"):
        text += ", %s" % task["owner_name"]
    elif task.get("acting_owner"):
        text += ", acting: %s" % task["acting_owner"]
    else:
        text += ", not named yet"
    return text


def _link(links):
    """(label, link) for the first runbook link, else the first kit link, else the first link."""
    for test in (lambda l: l.startswith("starter-kit/runbooks/"), lambda l: l.startswith("starter-kit/"),
                 lambda l: True):
        for link in links:
            if link and test(link):
                return ("Runbook" if link.startswith("starter-kit/runbooks/") else "Guide"), link
    return None, None


def _item(task_id, template):
    rest = task_id.split(".", 1)[1]
    return rest[len(template) + 1:] if rest.startswith(template + ".") else None


def _gates(story):
    return [("%s %s" % (g.get("kind"), g.get("id"))) + (" (spike %s)" % g["spike"] if g.get("spike") else "")
            for g in story.get("gated_by") or []]


class _Step(object):
    def __init__(self, text, link, package_path):
        self.text, self.link, self.package_path = text, link, package_path
        self.tasks = []  # [(story, task)]


def _steps_for(backlog, manifest, pid):
    """{section heading: [steps]} for one persona, in section order, from its backlog."""
    stories, task_story = [], set()
    for feature in backlog["epic"]["features"]:
        for story in feature["stories"]:
            stories.append(story)
            if feature.get("kind") != "foundation":
                task_story.add(story["id"])
    by_tid = dict((a["id"], a) for a in (manifest or {}).get("artifacts", []))
    out = dict((name, []) for name, _ in SECTIONS)
    index = {}

    def path_for(story, template):
        if template.startswith("distribute-"):
            return "build/marketplace/"
        if story["id"] not in task_story:
            return NO_PACKAGE
        item = by_tid.get(story["id"][2:] if story["id"].startswith("S-") else story["id"])
        if template.startswith(("publish-in-role-plugin", "setup-")) or template == HANDOVER:
            return _artifact_path(manifest, pid, item)
        if template.startswith("credentials-") or template == "start-wiring":
            return _bundle_path(pid, item["id"]) if item and item["kind"] not in ("skill", "none") else NO_PACKAGE
        return NO_PACKAGE

    def add(section, key, text, link, package_path, story, task):
        if key not in index:
            index[key] = _Step(text, link, package_path)
            out[section].append(index[key])
        index[key].tasks.append((story, task))

    checks = []
    for section, templates in SECTIONS:
        for template in templates:
            for story in stories:
                for task in story["tasks"]:
                    if task["template"] != template:
                        continue
                    links = [h.get("link") for h in task.get("how") or []]
                    label, link = _link(links)
                    package_path = path_for(story, template)
                    add(section, (section, template, _item(task["id"], template), package_path), task["title"],
                        (label, link), package_path, story, task)
                    if section.startswith("7."):
                        continue
                    for how in task.get("how") or []:
                        target = how.get("link") or ""
                        if any(target.endswith(a) for a in CHECK_ANCHORS):
                            checks.append((("check", template, _item(task["id"], template), package_path,
                                            how["text"]), how["text"], target, package_path, story, task))
    last = "7. Check it worked and hand over"
    for key, text, target, package_path, story, task in checks:
        add(last, key, text, ("Runbook" if target.startswith("starter-kit/runbooks/") else "Guide", target),
            package_path, story, task)
    for story in stories:
        for task in story["tasks"]:
            if task["template"] == HANDOVER:
                label, link = _link([h.get("link") for h in task.get("how") or []])
                package_path = path_for(story, HANDOVER)
                add(last, (last, HANDOVER, story["id"]), task["title"], (label, link), package_path, story, task)
    return out


def _render_step(step):
    ids = []
    for _, task in step.tasks:
        if task["id"] not in ids:
            ids.append(task["id"])
    done = all(task.get("status") == "done" for _, task in step.tasks)
    lines = ["- [%s] %s: %s" % ("x" if done else " ", ", ".join("`%s`" % i for i in ids), step.text)]
    owners = []
    for _, task in step.tasks:
        if _owner(task) not in owners:
            owners.append(_owner(task))
    lines.append("  - Owner: %s" % "; ".join(owners))
    label, link = step.link
    if link:
        lines.append("  - %s: [%s](%s%s)" % (label, link, TO_REPO, link))
    lines.append("  - Package: %s" % ("`%s`" % step.package_path if step.package_path.startswith("build/")
                                      else step.package_path))
    gated = []
    for story, _ in step.tasks:
        gates = _gates(story)
        if gates and story["id"] not in [s for s, _ in gated]:
            gated.append((story["id"], gates))
    if gated:
        groups = []
        for sid, gates in gated:
            for group in groups:
                if group[1] == gates:
                    group[0].append(sid)
                    break
            else:
                groups.append(([sid], gates))
        for sids, gates in groups:
            lines.append("  - Gated (%s) by: %s" % (", ".join(sids), ", ".join(gates)))
    return lines


def render_deploy(customer, profile, notes):
    """deploy.md for the customer: the backlog's deployment tasks in deployment order, per persona."""
    display = profile.get("display_name") or profile.get("customer")
    personas = []
    for persona in _personas(customer):
        try:
            inputs = _dashboard.load_inputs(str(persona))
        except (_dashboard.DashboardError, _dashboard.UsageError, _backlog.UsageError) as exc:
            notes.append("%s: deploy.md has no steps for this persona: %s" % (persona.name, str(exc).split("\n")[0]))
            continue
        manifest = _build.read_manifest(str(persona))
        distribution = inputs["levelled"]["persona_plan"]["distribution"]["value"]
        personas.append((persona.name, _steps_for(inputs["backlog"], manifest, persona.name), distribution))
    lines = [
        "# Deploy checklist: %s" % display,
        "",
        "Written by `cli.py package` from each persona's backlog.json; do not edit it by hand. Change the backlog, "
        "then run package again.",
        "",
        "The customer's admin works through it in the customer's Claude org, in order. Each step names the backlog "
        "task or tasks it comes from, the owner, the runbook section, and the package path it uses under this "
        "folder. A ticked box means every task in the step is done in backlog.json. A gated step waits on the "
        "open question, spike or sign-off it names.",
        "",
        "Credentials live in the customer's secret store. This checklist and every note recorded from it name an "
        "environment variable or a placeholder at most, never a key, token, password, org id or instance URL.",
        "",
        "When an artifact is live, the consultant records it with `cli.py record <persona-dir> <task-id> --status "
        "deployed --by <admin> --evidence <note>`, then `--status verified` with the runbook's check-it-worked "
        "result.",
    ]
    for heading, _ in SECTIONS:
        lines += ["", "## %s" % heading, "", SECTION_INTRO[heading]]
        for pid, steps, distribution in personas:
            lines += ["", "### %s" % pid, ""]
            if heading.startswith("4."):
                lines += [DISTRIBUTION.get(distribution, "Distribution: %s." % distribution), ""]
            if not steps[heading]:
                lines.append("No backlog task for this section.")
                continue
            for step in steps[heading]:
                lines += _render_step(step)
    return "\n".join(lines) + "\n"
