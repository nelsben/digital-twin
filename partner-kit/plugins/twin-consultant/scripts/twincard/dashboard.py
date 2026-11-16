"""Render a persona's dashboard: one self-contained dashboard.html from the card, the levelled plan and the backlog.

render(persona_dir, date) validates the card, checks that levelled.json and backlog.json exist, were
made from the files on disk, and are what level and backlog give now (it levels and builds the backlog
again in memory and compares the parsed files; whitespace and key order are not a difference), and
returns the page as a string; it never writes. write_dashboard(persona_dir,
date) does the same and writes <persona_dir>/dashboard.html:

    {"ok": bool,                  # False on validation errors or a missing or stale input
     "validation": {...},         # the validate() result
     "error": str or None,        # why nothing was written, naming the file and the command to run next
     "path": str or None,         # the file written
     "summary": {...} or None}    # completeness, blockers, warnings and backlog counts for the command line

The page is a rendering only: every value comes from card.json, the customer profile, levelled.json,
backlog.json or the completeness figures from validate. It has no JavaScript and makes no external
request; cites are shown as text. The generated date is the only date the renderer adds, so the same
inputs and the same date give the same bytes. Design of record: partner-kit/docs/design.md, section 9.
"""

import datetime
import hashlib
import html
import json
import re
from pathlib import Path

from . import backlog as _backlog
from . import fields as _fields
from . import level as _level
from . import packs as _packs
from . import validate as _validate

DASHBOARD_FILE = "dashboard.html"

# The seven sections, in order: (data-section, id).
SECTIONS = (
    ("Header", "header"),
    ("Anatomy grid", "anatomy-grid"),
    ("Feature list", "feature-list"),
    ("Blockers and warnings", "blockers-and-warnings"),
    ("Backlog", "backlog"),
    ("Open questions", "open-questions"),
    ("Where each answer came from", "where-each-answer-came-from"),
)

# The anatomy panels: which decisions and fields sit in which panel (design section 9). Each item is
# rendered by the function of the same name in PANEL_ITEMS below.
PANELS = (
    ("A1", "Persona", ("persona.plugin_name", "role.team", "voice.serves", "voice.tone", "voice.never",
                       "voice.escalate_to")),
    ("A2", "Skills", ("tasks.client_skills", "tasks.skill_owner", "persona.starting_points")),
    ("A3", "Connectors", ("tools", "systems")),
    ("A4", "Runtime", ("tasks.runtime", "role.works_in", "runtime_preferences.self_hosting_required")),
    ("A5", "Identity", ("tasks.identity", "connectors.identity", "identity.sign_in")),
    ("A6", "Memory", ("memory.personal_memory_wanted", "tasks.memory", "memory.notes")),
    ("A7", "Guardrails", ("persona.settings_baseline", "tasks.web_tools", "tasks.autonomy", "tasks.data_class",
                          "devices", "compliance")),
    ("A8", "Evaluation", ("tasks.examples", "outcome.scorecard_targets")),
    ("A9", "Distribution and governance", ("persona.distribution", "governance.log", "governance.profile",
                                           "tasks.plan_fit")),
)

# The task decisions shown in the feature list, named as in tests/fixtures/twincard/expectations.json.
TASK_DECISIONS = ("runtime", "identity", "autonomy.start", "autonomy.ceiling", "data_controls", "memory",
                  "plan_fit", "connectors")
DECISION_LABELS = {
    "runtime": "Runtime", "identity": "Identity", "data_controls": "Data controls", "memory": "Memory",
    "plan_fit": "Plan fit", "connectors": "Connectors",
}
PERSONA_DECISIONS = ("plugin_name", "distribution", "settings_baseline")
PROVENANCE_STATUSES = ("answered", "default", "assumed", "open")
STATUS_WORDS = {"todo": "[ ] todo", "in-progress": "[~] in progress", "done": "[x] done"}
DATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
DATE_NEXT = "Next: give the date as YYYY-MM-DD, for example 2026-11-15."
NULL_IS_A_VALUE = ("settings_baseline",)


class DashboardError(ValueError):
    """Nothing can be rendered: validation errors, or levelled.json or backlog.json missing or out of date."""

    def __init__(self, message, validation=None):
        ValueError.__init__(self, message)
        self.validation = validation


class UsageError(ValueError):
    """A date that is not a real calendar date in YYYY-MM-DD form, or a backlog.json that cannot be used."""


# --- Inputs -----------------------------------------------------------------------------------------------

def parse_date(value=None):
    """The generated date as YYYY-MM-DD: today when value is None; UsageError for anything not a real date."""
    if value is None:
        return datetime.date.today().isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    text = str(value)
    if not DATE_PATTERN.match(text):
        raise UsageError("--date must be a calendar date in YYYY-MM-DD form, in ASCII digits; got %s. %s"
                         % (json.dumps(text), DATE_NEXT))
    try:
        return datetime.date(int(text[:4]), int(text[5:7]), int(text[8:])).isoformat()
    except ValueError:
        raise UsageError("--date %s is not a real calendar date. %s" % (text, DATE_NEXT))


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _json(data):
    try:
        loaded = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def load_inputs(persona_dir):
    """Validate and read the four records; DashboardError names the file at fault and the next command."""
    catalogue = _fields.load_catalogue()
    validation = _validate.validate(str(persona_dir), catalogue)
    if not validation["ok"]:
        raise DashboardError("card.json or customer-profile.json has validation errors. Next: fix them, then run "
                             "the level, backlog and dashboard commands again.", validation)
    persona = Path(persona_dir)
    card_path = persona / _validate.CARD_FILE
    profile_path = (persona / ".." / ".." / _validate.PROFILE_FILE).resolve()
    levelled_path = persona / _level.LEVELLED_FILE
    backlog_path = persona / _backlog.BACKLOG_JSON
    card_bytes, profile_bytes = card_path.read_bytes(), profile_path.read_bytes()

    if not levelled_path.is_file():
        raise DashboardError("levelled.json is missing. Next: run the level command, then the backlog command.",
                             validation)
    levelled = _json(levelled_path.read_bytes())
    source = (levelled or {}).get("source") or {}
    stale = source.get("card_sha256") != _sha(card_bytes) or source.get("profile_sha256") != _sha(profile_bytes)
    if not stale:
        # Level again in memory: the plan must be what level gives now for the current inputs and kit data.
        fresh = _level.level(str(persona))
        stale = not fresh["ok"] or _level.canonical(fresh["levelled"]) != _level.canonical(levelled)
    if stale:
        raise DashboardError("levelled.json is out of date: it is not what level gives for the current card.json, "
                             "customer-profile.json and kit data. Next: run the level command, then the backlog "
                             "command.", validation)
    levelled = fresh["levelled"]
    if not backlog_path.is_file():
        raise DashboardError("backlog.json is missing. Next: run the backlog command.", validation)
    try:
        _backlog.read_statuses(persona)
    except _backlog.UsageError as exc:
        raise UsageError(str(exc))
    backlog = _json(backlog_path.read_bytes())
    source = (backlog or {}).get("source") or {}
    stale = source.get("card_sha256") != _sha(card_bytes) or \
        source.get("levelled_sha256") != _sha(_level.render(levelled).encode("utf-8"))
    if not stale:
        # Build the backlog again in memory, with backlog.json's statuses carried over, and compare.
        built = _backlog.assemble(persona, validation, json.loads(card_bytes.decode("utf-8")),
                                  json.loads(profile_bytes.decode("utf-8")), levelled)
        stale = _level.canonical(built["backlog"]) != _level.canonical(backlog)
    if stale:
        raise DashboardError("backlog.json is out of date: it is not what backlog gives for the current card.json, "
                             "levelled.json and task library. Next: run the backlog command.", validation)
    return {
        "card": json.loads(card_bytes.decode("utf-8")),
        "profile": json.loads(profile_bytes.decode("utf-8")),
        "levelled": levelled,
        "backlog": built["backlog"],
        "validation": validation,
        "catalogue": catalogue,
    }


def field_counts(card, profile, catalogue):
    """{part: [satisfied, required]} over the required fields of both records, as validate counts them."""
    complete = catalogue["provenance"]["counts_as_complete"]
    counts = {}
    for record, data in (("profile", profile), ("card", card)):
        required, provenance, values = _validate._check_record(data, record, catalogue, _validate._Report())
        part_of = {}
        for entry in _fields.fields_for(record, catalogue):
            for path, _ in values.get(entry["path"], []):
                part_of[path] = entry["part"]
        for path in required:
            prov = provenance.get(path)
            done = isinstance(prov, dict) and prov.get("status") in complete
            pair = counts.setdefault(part_of.get(path, "context"), [0, 0])
            pair[0] += 1 if done else 0
            pair[1] += 1
    return counts


def backlog_tasks(backlog):
    return [task for feature in backlog["epic"]["features"] for story in feature["stories"]
            for task in story["tasks"]]


def summary(inputs):
    """The figures the command line prints and the header leads with."""
    card, levelled, backlog = inputs["card"], inputs["levelled"], inputs["backlog"]
    done = inputs["validation"]["completeness"]
    tasks = backlog_tasks(backlog)
    pilot = [t.get("id") for t in card.get("tasks") or [] if t.get("in_pilot")]
    blocking = [q for q in card.get("open_questions") or [] if set(q.get("blocks") or []) & set(pilot)]
    missing = done["required"] - done["satisfied"]
    complete = done["percent"] == 100 and not blocking and not levelled["blockers"]
    return {
        "percent": done["percent"], "satisfied": done["satisfied"], "required": done["required"],
        "missing": missing, "pilot_tasks": len(pilot), "blocking_questions": len(blocking),
        "blockers": len(levelled["blockers"]), "warnings": len(levelled["warnings"]),
        "tasks_done": sum(1 for t in tasks if t["status"] == "done"), "tasks_total": len(tasks),
        "complete": complete,
    }


# --- Small renderers --------------------------------------------------------------------------------------

def esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def fmt(value, null="none"):
    """A value as plain text: lists joined, booleans as yes or no, None as the given word."""
    if value is None or value == "":
        return null
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return ", ".join(fmt(v) for v in value) if value else "none"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def cite_text(cite):
    """A cite as text: the page file name and its anchor, never a link."""
    if not cite:
        return ""
    path, _, anchor = str(cite).partition("#")
    name = path.rstrip("/").split("/")[-1] or path
    return name + ("#" + anchor if anchor else "")


def source_text(source):
    """A provenance source as text: each of its sources ('; ' between them) as cite_text gives it."""
    return _validate.SOURCE_SEPARATOR.join(cite_text(one) for one in _validate.split_sources(source))


def cite(cite_value):
    return '<span class="cite">Cite: <code>%s</code></span>' % esc(cite_text(cite_value)) if cite_value else ""


UNVERIFIED_TAG = '<span class="tag unv">&#9888; Unverified</span>'
OVERRIDDEN_TAG = '<span class="tag ovr">&#9998; Overridden</span>'


def plural(n, word, many=None):
    return "%d %s" % (n, word if n == 1 else (many or word + "s"))


def first_seen(items):
    out = []
    for item in items:
        if item not in out:
            out.append(item)
    return out


def grouped(pairs):
    """[(value, [task ids])] in first-seen order, from (task id, value) pairs."""
    order = first_seen([value for _, value in pairs])
    return [(value, [tid for tid, v in pairs if v == value]) for value in order]


def counted(pairs, null="undecided"):
    rows = grouped(pairs)
    if not rows:
        return "none"
    return "; ".join("%s: %s (%s)" % (esc(fmt(value, null)), plural(len(ids), "task"), esc(", ".join(ids)))
                     for value, ids in rows)


def decision_value(name, decision):
    null = "none" if name.split(".")[-1] in NULL_IS_A_VALUE else "undecided"
    return fmt(decision.get("value"), null)


# --- Decisions --------------------------------------------------------------------------------------------

def task_decision(levelled_task, name):
    """The levelled decision for a name in TASK_DECISIONS: a decision, the data_controls dict or a list."""
    if name.startswith("autonomy."):
        return levelled_task["autonomy"][name.split(".", 1)[1]]
    return levelled_task[name]


def parts_of(name, got):
    """The decisions behind one cell: [(label, decision)]."""
    if name == "data_controls":
        return [(sub.replace("_", " "), d) for sub, d in got.items()]
    if name == "connectors":
        return []
    return [(None, got)]


def is_unverified(name, got):
    if name == "connectors":
        return any(c.get("unverified") for c in got)
    return any(d.get("unverified") for _, d in parts_of(name, got))


def override_text(decision, label=None):
    ov = decision.get("overridden")
    if not ov:
        return ""
    result = ov.get("rule_result")
    if isinstance(result, dict):
        result = "; ".join("%s %s" % (k.replace("_", " "), fmt(v)) for k, v in result.items())
    return ('<p class="ovr">%s%s. The rule\'s result: %s. Reason: %s Approved by: %s.</p>'
            % (OVERRIDDEN_TAG, " (%s)" % esc(label) if label else "", esc(fmt(result, "undecided")),
               esc(ov.get("reason")), esc(fmt(ov.get("approved_by"), "not recorded"))))


def why(decision, label=None):
    """One decision's reason, rule, basis and cite, as a list item."""
    bits = []
    if label:
        bits.append("<strong>%s:</strong>" % esc(label.capitalize()))
    bits.append(esc(decision.get("reason")))
    meta = []
    if decision.get("rule"):
        meta.append("rule <code>%s</code>" % esc(decision["rule"]))
    if decision.get("basis"):
        meta.append("basis: %s" % esc(decision["basis"]))
    if meta:
        bits.append("(%s)" % ", ".join(meta))
    if decision.get("cite"):
        bits.append(cite(decision["cite"]))
    if decision.get("unverified"):
        bits.append(UNVERIFIED_TAG)
    return "<li>%s</li>" % " ".join(bits)


def connector_value(c, products):
    bits = ["<strong>%s</strong>" % esc(c.get("system"))]
    if products.get(c.get("system")):
        bits.append("(%s)" % esc(products[c["system"]]))
    bits.append(": %s, %s identity, %s" % (esc(c.get("access")), esc(c.get("identity")), esc(c.get("permission"))))
    if c.get("unverified"):
        bits.append(UNVERIFIED_TAG)
    return "<li>%s</li>" % " ".join(bits)


def connector_why(c):
    bits = ["<strong>%s:</strong>" % esc(c.get("system")), esc(c.get("how"))]
    if c.get("runbook"):
        bits.append("Runbook: <code>%s</code>." % esc(cite_text(c["runbook"])))
    else:
        bits.append("No runbook.")
    bits.append(cite(c.get("cite")))
    if c.get("unverified"):
        bits.append(UNVERIFIED_TAG)
    return "<li>%s</li>" % " ".join(bits)


def decision_cell(tid, name, got, products):
    unverified = is_unverified(name, got)
    attrs = ' data-decision="%s.%s"' % (esc(tid), esc(name))
    if unverified:
        attrs += ' data-unverified="true"'
    out = ["<td%s>" % attrs]
    if name == "connectors":
        out.append('<ul class="plain">%s</ul>' % "".join(connector_value(c, products) for c in got)
                   if got else "none")
        reasons = "".join(connector_why(c) for c in got)
    elif name == "data_controls":
        out.append("<span>%s</span>" % "; ".join(
            "%s %s" % (esc(label), esc(decision_value(label.replace(" ", "_"), d))) for label, d in parts_of(name, got)))
        reasons = "".join(why(d, label) for label, d in parts_of(name, got))
    else:
        out.append("<span>%s</span>" % esc(decision_value(name, got)))
        reasons = why(got)
    if unverified and name != "connectors":  # each unverified connector carries its own label
        out.append(UNVERIFIED_TAG)
    for label, d in parts_of(name, got):
        out.append(override_text(d, label))
    if reasons:
        out.append('<details><summary>Why</summary><ul class="why">%s</ul></details>' % reasons)
    out.append("</td>")
    return "".join(out)


# --- Sections ---------------------------------------------------------------------------------------------

def section_open(index):
    name, sid = SECTIONS[index]
    return '<section data-section="%s" id="%s">' % (esc(name), esc(sid))


def render_header(ctx, date):
    card, profile, levelled, s = ctx["card"], ctx["profile"], ctx["levelled"], ctx["summary"]
    role = card.get("role") or {}
    plan = profile.get("plan") or {}
    owners = profile.get("owners") or {}
    outcome = card.get("outcome") or {}
    plan_d = levelled["persona_plan"]
    out = [section_open(0), "<h1>%s</h1>" % esc(ctx["title"])]
    sub = [esc(profile.get("display_name") or profile.get("customer"))]
    if profile.get("fictional") is True:
        sub.append('<span class="tag">Fictional sample</span>')
    out.append('<p class="sub">%s</p>' % " ".join(sub))
    out.append('<p class="lead" data-field="sponsor-line">Tasks in the pilot: %d. Blockers: %d. Backlog tasks '
               'done: %d of %d.</p>' % (s["pilot_tasks"], s["blockers"], s["tasks_done"], s["tasks_total"]))
    reasons = []
    if s["missing"]:
        reasons.append("%s not yet answered or default" % plural(s["missing"], "required field"))
    if s["blocking_questions"]:
        reasons.append("%s %s an in-pilot task" % (plural(s["blocking_questions"], "open question"),
                                                   "blocks" if s["blocking_questions"] == 1 else "block"))
    if s["blockers"]:
        reasons.append(plural(s["blockers"], "blocker"))
    status = '<strong data-field="complete">%s</strong>' % ("Complete" if s["complete"] else "Not complete")
    if s["complete"]:
        status = "&#10003; " + status
    else:
        status = "&#10007; " + status + ': <span data-field="complete-reasons">%s</span>' % esc("; ".join(reasons))
    pack = levelled["source"].get("pack") or profile.get("industry")
    try:
        pack_name = _packs.load_pack(pack).get("name")
    except Exception:  # an unknown pack is a validation error; show the id alone
        pack_name = None
    rows = [
        ("Role", "%s; team: %s" % (esc(role.get("name")), esc(role.get("team"))) if role.get("team")
         else esc(role.get("name"))),
        ("Customer", esc(profile.get("display_name"))),
        ("Plan tier", "%s, %s seats" % (esc(plan.get("tier")), esc(fmt(plan.get("seats"), "unknown")))),
        ("Industry pack", "%s%s" % (esc(pack), " (%s)" % esc(pack_name) if pack_name else "")),
        ("Pilot users", "%s of %s in the role" % (esc(fmt(role.get("pilot_users"), "unknown")),
                                                  esc(fmt(role.get("headcount"), "unknown")))),
        ("Completeness", '<span data-field="completeness">%d%%</span> (%d of %d required fields answered or '
                         'default)' % (s["percent"], s["satisfied"], s["required"])),
        ("Status", status),
    ]
    for name, label in (("plugin_name", "Role plugin"), ("distribution", "Distribution"),
                        ("settings_baseline", "Settings baseline")):
        d = plan_d[name]
        attrs = ' data-decision="persona.%s"' % name
        value = '<span%s>%s</span>' % (attrs, esc(decision_value(name, d)))
        if d.get("unverified"):
            value += " " + UNVERIFIED_TAG
        rows.append((label, value + override_text(d)))
    rows += [
        ("Sponsor goal", esc(fmt(outcome.get("sponsor_goal"), "not given"))),
        ("Owners", "; ".join("%s: %s" % (label, esc(fmt(owners.get(key), "not named")))
                             for key, label in (("sponsor", "sponsor"), ("technical_owner", "technical owner"),
                                                ("business_owner", "business owner")))),
    ]
    out.append('<dl class="facts">%s</dl>' % "".join("<dt>%s</dt><dd>%s</dd>" % (k, v) for k, v in rows))
    out.append('<p class="generated">Generated %s by the dashboard command from card.json, customer-profile.json, '
               'levelled.json and backlog.json. Never edit it by hand.</p>' % esc(date))
    out.append("</section>")
    return "\n".join(out)


def render_contents():
    links = "".join('<li><a href="#%s">%s</a></li>' % (esc(sid), esc(name)) for name, sid in SECTIONS)
    return '<nav aria-label="Contents"><p class="toc-title">Contents</p><ol class="toc">%s</ol></nav>' % links


def _task_pairs(ctx, getter):
    return [(t["id"], getter(t["id"], t)) for t in ctx["tasks"] if t.get("id") in ctx["levelled"]["tasks"]]


def _lt(ctx, tid):
    return ctx["levelled"]["tasks"][tid]


def _item_plugin_name(ctx):
    d = ctx["levelled"]["persona_plan"]["plugin_name"]
    return "Role plugin", esc(decision_value("plugin_name", d))


def _item_role_team(ctx):
    role = ctx["card"].get("role") or {}
    return "Team", "%s; %s of %s people in the pilot" % (esc(role.get("team")), esc(fmt(role.get("pilot_users"))),
                                                         esc(fmt(role.get("headcount"))))


def _voice(key, label):
    def item(ctx):
        return label, esc(fmt((ctx["card"].get("voice") or {}).get(key), "not given"))
    return item


def _item_client_skills(ctx):
    pairs = _task_pairs(ctx, lambda tid, t: _lt(ctx, tid)["runtime"]["value"])
    ids = [tid for tid, v in pairs if v == "client-skill"]
    return "Client skills", "%s (%s)" % (plural(len(ids), "task"), esc(", ".join(ids) or "none"))


def _item_skill_owner(ctx):
    return "Skill owners", "; ".join("%s %s" % (esc(t["id"]), esc(fmt(t.get("skill_owner"), "not named")))
                                     for t in ctx["tasks"]) or "none"


def _item_starting_points(ctx):
    points = ctx["levelled"]["persona_plan"].get("starting_points") or []
    if not points:
        return "Starting points", "none in the industry pack"
    items = []
    for p in points:
        text = "%s <strong>%s</strong> (%s), %s" % (esc(p.get("kind")), esc(p.get("name")), esc(p.get("where")),
                                                    esc(p.get("use")))
        if p.get("unverified"):
            text += " " + UNVERIFIED_TAG
        items.append("<li>%s</li>" % text)
    return "Starting points", '<ul class="plain">%s</ul>' % "".join(items)


def _item_tools(ctx):
    tools = ctx["levelled"].get("tools") or []
    if not tools:
        return "Tools", "none"
    items = []
    for tool in tools:
        perm = tool["permission"]
        system = tool.get("system")
        product = ctx["products"].get(system)
        text = "<strong>%s</strong>%s: %s, %s (%s)" % (
            esc(system), " (%s)" % esc(product) if product else "",
            "read" if tool.get("use") == "read" else "write (%s)" % esc(tool.get("use")),
            esc(decision_value("permission", perm)), esc(", ".join(tool.get("tasks") or [])))
        if perm.get("unverified"):
            text += " " + UNVERIFIED_TAG
        items.append("<li>%s</li>" % text)
    return "Tools (system, read or write, permission)", '<ul class="plain">%s</ul>' % "".join(items)


def _item_systems(ctx):
    items = []
    for system in ctx["profile"].get("systems") or []:
        text = "<strong>%s</strong> (%s): %s, %s; access model: %s%s" % (
            esc(system.get("id")), esc(system.get("product")), esc(system.get("kind")),
            esc(fmt(system.get("edition"), "edition not given")), esc(fmt(system.get("access_model"), "not given")),
            "; on a private network" if system.get("private_network") else "")
        items.append("<li>%s</li>" % text)
    return "Systems", '<ul class="plain">%s</ul>' % "".join(items) if items else "none"


def _item_runtime(ctx):
    return "Tasks per runtime", counted(_task_pairs(ctx, lambda tid, t: _lt(ctx, tid)["runtime"]["value"]))


def _item_works_in(ctx):
    return "Works in", esc(fmt((ctx["card"].get("role") or {}).get("works_in")))


def _item_self_hosting(ctx):
    value = (ctx["profile"].get("runtime_preferences") or {}).get("self_hosting_required")
    return "Self-hosting required", esc(fmt(value, "not given"))


def _item_identity(ctx):
    return "Tasks per identity", counted(_task_pairs(ctx, lambda tid, t: _lt(ctx, tid)["identity"]["value"]))


def _item_connector_identity(ctx):
    pairs = []
    for t in ctx["tasks"]:
        for c in _lt(ctx, t["id"])["connectors"]:
            pairs.append(("%s %s" % (t["id"], c.get("system")), c.get("identity")))
    rows = grouped(pairs)
    return "Connector identities", "; ".join("%s: %s" % (esc(fmt(v)), plural(len(ids), "connector"))
                                             for v, ids in rows) or "none"


def _item_sign_in(ctx):
    identity = ctx["profile"].get("identity") or {}
    return "Sign-in", "%s; SSO %s; SCIM %s" % (esc(fmt(identity.get("idp"), "not given")),
                                               esc(fmt(identity.get("sso"), "unknown")),
                                               esc(fmt(identity.get("scim"), "unknown")))


def _item_memory_wanted(ctx):
    return "Role wants personal memory", esc(fmt((ctx["card"].get("memory") or {}).get("personal_memory_wanted"),
                                                 "not given"))


def _item_task_memory(ctx):
    return "Memory per task", "; ".join(
        "%s %s" % (esc(t["id"]), esc(decision_value("memory", _lt(ctx, t["id"])["memory"]))) for t in ctx["tasks"])


def _item_memory_notes(ctx):
    return "Notes", esc(fmt((ctx["card"].get("memory") or {}).get("notes"), "none"))


def _item_baseline(ctx):
    d = ctx["levelled"]["persona_plan"]["settings_baseline"]
    return "Settings baseline", esc(decision_value("settings_baseline", d))


def _item_web_tools(ctx):
    return "Web tools", counted(_task_pairs(
        ctx, lambda tid, t: _lt(ctx, tid)["data_controls"]["web_tools"]["value"]))


def _item_autonomy(ctx):
    starts = [_lt(ctx, t["id"])["autonomy"]["start"]["value"] for t in ctx["tasks"]]
    ceilings = [_lt(ctx, t["id"])["autonomy"]["ceiling"]["value"] for t in ctx["tasks"]]

    def span(values):
        known = [v for v in values if isinstance(v, (int, float))]
        if not known:
            return "undecided"
        low, high = min(known), max(known)
        return fmt(low) if low == high else "%s to %s" % (fmt(low), fmt(high))

    undecided = [t["id"] for t, v in zip(ctx["tasks"], ceilings) if v is None]
    text = "start %s; ceiling %s" % (span(starts), span(ceilings))
    if undecided:
        text += "; ceiling undecided for %s" % ", ".join(undecided)
    return "Autonomy range", esc(text)


def _item_data_class(ctx):
    return "Data classes", counted([(t["id"], t.get("data_class")) for t in ctx["tasks"]])


def _item_devices(ctx):
    devices = ctx["profile"].get("devices") or {}
    role = ctx["card"].get("role") or {}
    return "Devices", "role device %s; MDM %s; managed: %s; unmanaged: %s" % (
        esc(fmt(role.get("device"), "not given")), esc(fmt(devices.get("mdm"), "not given")),
        esc(fmt(devices.get("managed_share"), "not given")), esc(fmt(devices.get("unmanaged_users"), "not given")))


def _item_compliance(ctx):
    c = ctx["profile"].get("compliance") or {}
    return "Compliance", "retention %s; walls %s; PHI %s; BAA %s; MNPI %s" % (
        esc(fmt(c.get("retention"), "not given")), esc(fmt(c.get("walls"), "not given")),
        esc(fmt(c.get("phi"), "unknown")), esc(fmt(c.get("baa"), "unknown")), esc(fmt(c.get("mnpi"), "unknown")))


def _item_examples(ctx):
    bits = []
    for t in ctx["tasks"]:
        ex = t.get("examples") or {}
        bits.append("%s %s good, %s bad" % (esc(t["id"]), esc(fmt(ex.get("good"), "not yet")),
                                            esc(fmt(ex.get("bad"), "not yet"))))
    return "Examples per task", "; ".join(bits) or "none"


def _item_scorecard(ctx):
    targets = (ctx["card"].get("outcome") or {}).get("scorecard_targets") or []
    return "Scorecard targets", "; ".join("%s %s" % (esc(t.get("metric")), esc(fmt(t.get("value"))))
                                          for t in targets) or "none yet"


def _item_distribution(ctx):
    d = ctx["levelled"]["persona_plan"]["distribution"]
    return "Distribution", esc(decision_value("distribution", d))


def _item_governance_log(ctx):
    value = None
    for feature in ctx["backlog"]["epic"]["features"]:
        for story in feature["stories"]:
            if value is None and "governance_log" in (story.get("fields") or {}):
                value = story["fields"]["governance_log"]
    return "Governance log", esc(fmt(value, "not given"))


def _item_governance_profile(ctx):
    g = ctx["profile"].get("governance") or {}
    return "Governance", "log destination: %s; action log required: %s; source audit: %s; spend owner: %s" % (
        esc(fmt(g.get("log_destination"), "not given")), esc(fmt(g.get("action_log_required"), "not given")),
        esc(fmt(g.get("existing_source_audit"), "not given")), esc(fmt(g.get("spend_owner"), "not given")))


def _item_plan_fit(ctx):
    pairs = _task_pairs(ctx, lambda tid, t: _lt(ctx, tid)["plan_fit"]["value"])
    text = counted(pairs)
    limits = [(tid, _lt(ctx, tid)["plan_fit"]) for tid, v in pairs if v != "ok"]
    if limits:
        text += '<ul class="plain">%s</ul>' % "".join(
            "<li>%s %s: %s</li>" % (esc(tid), esc(decision_value("plan_fit", d)), esc(d.get("reason")))
            for tid, d in limits)
    return "Plan fit", text


PANEL_ITEMS = {
    "persona.plugin_name": _item_plugin_name,
    "role.team": _item_role_team,
    "voice.serves": _voice("serves", "Serves"),
    "voice.tone": _voice("tone", "Tone"),
    "voice.never": _voice("never", "Never"),
    "voice.escalate_to": _voice("escalate_to", "Escalates to"),
    "tasks.client_skills": _item_client_skills,
    "tasks.skill_owner": _item_skill_owner,
    "persona.starting_points": _item_starting_points,
    "tools": _item_tools,
    "systems": _item_systems,
    "tasks.runtime": _item_runtime,
    "role.works_in": _item_works_in,
    "runtime_preferences.self_hosting_required": _item_self_hosting,
    "tasks.identity": _item_identity,
    "connectors.identity": _item_connector_identity,
    "identity.sign_in": _item_sign_in,
    "memory.personal_memory_wanted": _item_memory_wanted,
    "tasks.memory": _item_task_memory,
    "memory.notes": _item_memory_notes,
    "persona.settings_baseline": _item_baseline,
    "tasks.web_tools": _item_web_tools,
    "tasks.autonomy": _item_autonomy,
    "tasks.data_class": _item_data_class,
    "devices": _item_devices,
    "compliance": _item_compliance,
    "tasks.examples": _item_examples,
    "outcome.scorecard_targets": _item_scorecard,
    "persona.distribution": _item_distribution,
    "governance.log": _item_governance_log,
    "governance.profile": _item_governance_profile,
    "tasks.plan_fit": _item_plan_fit,
}


def render_anatomy(ctx):
    counts = ctx["field_counts"]
    tasks = backlog_tasks(ctx["backlog"])
    out = [section_open(1), "<h2>Anatomy grid</h2>",
           '<p class="note">Each panel shows the decisions for one part of the twin, its required fields that are '
           'answered or default (card and customer profile), and its backlog tasks that are done.</p>',
           '<div class="grid">']
    for part, name, items in PANELS:
        satisfied, required = counts.get(part, [0, 0])
        part_tasks = [t for t in tasks if t.get("part") == part]
        done = sum(1 for t in part_tasks if t["status"] == "done")
        rows = "".join("<dt>%s</dt><dd>%s</dd>" % PANEL_ITEMS[key](ctx) for key in items)
        out.append('<div class="panel" data-part="%s"><h3>%s %s</h3><dl>%s</dl>'
                   '<p class="counts">Required fields answered: %d of %d. Backlog tasks done: %d of %d.</p></div>'
                   % (part, part, esc(name), rows, satisfied, required, done, len(part_tasks)))
    out.append("</div>")
    satisfied, required = counts.get("context", [0, 0])
    out.append('<p class="note" data-field="context-fields">Fields outside the nine parts (context): %d of %d '
               'required fields answered or default.</p>' % (satisfied, required))
    out.append("</section>")
    return "\n".join(out)


def render_features(ctx):
    card, levelled = ctx["card"], ctx["levelled"]
    out = [section_open(2), "<h2>Feature list</h2>"]
    features = list(card.get("features") or [])
    known = set(f.get("id") for f in features)
    orphans = [t for t in ctx["tasks"] if t.get("feature") not in known]
    if orphans:
        features.append({"id": None, "name": "Tasks with no feature", "why": ""})
    for feature in features:
        tasks = [t for t in ctx["tasks"] if (t.get("feature") == feature.get("id")) or
                 (feature.get("id") is None and t in orphans)]
        out.append('<div class="feature"><h3>%s</h3>' % esc(feature.get("name") or feature.get("id")))
        if feature.get("why"):
            out.append('<p class="note">%s</p>' % esc(feature["why"]))
        if not tasks:
            out.append("<p>No tasks.</p>")
        for task in tasks:
            tid = task.get("id")
            lt = levelled["tasks"].get(tid)
            cost = task.get("cost_of_mistake") or {}
            head = ('<p class="task-title"><strong>%s</strong> %s</p>' % (esc(tid), esc(task.get("name"))))
            facts = ('<p class="task-facts">%s. Priority %s. Trigger %s. Data class %s. %s per week x %s minutes '
                     'each x %s users. Cost of a mistake: %s%s.</p>' % (
                         "In pilot" if task.get("in_pilot") else "Later",
                         esc(fmt(task.get("priority"))), esc(fmt(task.get("trigger"))),
                         esc(fmt(task.get("data_class"))), esc(fmt(task.get("frequency_per_week"), "unknown")),
                         esc(fmt(task.get("minutes_each"), "unknown")), esc(fmt(task.get("users"), "unknown")),
                         esc(fmt(cost.get("level"), "unknown")),
                         " (%s)" % esc(cost["what_happens"]) if cost.get("what_happens") else ""))
            out.append('<div class="task">%s%s' % (head, facts))
            if lt is None:
                out.append("<p>Not levelled.</p></div>")
                continue
            rows = []
            for name in TASK_DECISIONS:
                if name == "autonomy.ceiling":
                    continue
                if name == "autonomy.start":
                    start = decision_cell(tid, "autonomy.start", lt["autonomy"]["start"], ctx["products"])
                    ceiling = decision_cell(tid, "autonomy.ceiling", lt["autonomy"]["ceiling"], ctx["products"])
                    rows.append('<tr><th scope="row">Autonomy start</th>%s</tr>' % start)
                    rows.append('<tr><th scope="row">Autonomy ceiling</th>%s</tr>' % ceiling)
                    rows.append('<tr><th scope="row">Autonomy</th><td>%s to %s</td></tr>' % (
                        esc(decision_value("autonomy.start", lt["autonomy"]["start"])),
                        esc(decision_value("autonomy.ceiling", lt["autonomy"]["ceiling"]))))
                    continue
                rows.append('<tr><th scope="row">%s</th>%s</tr>' % (
                    DECISION_LABELS[name], decision_cell(tid, name, task_decision(lt, name), ctx["products"])))
            out.append('<div class="scroll"><table class="decisions">%s</table></div></div>' % "".join(rows))
        out.append("</div>")
    out.append("</section>")
    return "\n".join(out)


def _about_order(ctx, items):
    order = ["persona"] + [t.get("id") for t in ctx["tasks"]]
    order += first_seen([i["about"] for i in items if i["about"] not in order])
    return order


def _about_label(ctx, about):
    if about == "persona":
        return "About the persona"
    names = dict((t.get("id"), t.get("name")) for t in ctx["tasks"])
    return "About %s: %s" % (about, names[about]) if about in names else "About %s" % about


def _code_list(ctx, items, kind):
    out = []
    for about in _about_order(ctx, items):
        group = [i for i in items if i["about"] == about]
        if not group:
            continue
        out.append('<p class="group">%s</p><ul class="codes">' % esc(_about_label(ctx, about)))
        for item in group:
            attrs = ' data-code="%s" data-about="%s"' % (esc(item["code"]), esc(item["about"]))
            if item.get("unverified"):
                attrs += ' data-unverified="true"'
            tag = ('<span class="tag bad">&#10007; Blocker</span>' if kind == "blocker"
                   else '<span class="tag warn">&#9888; Warning</span>')
            out.append('<li%s>%s <code>%s</code>%s %s Fix: %s %s</li>' % (
                attrs, tag, esc(item["code"]), " " + UNVERIFIED_TAG if item.get("unverified") else "",
                esc(item.get("message")), esc(item.get("fix")), cite(item.get("cite"))))
        out.append("</ul>")
    return "".join(out)


def unverified_items(ctx):
    """Every decision and code that rests on an unverified fact, as text lines."""
    levelled = ctx["levelled"]
    lines = []
    for name in PERSONA_DECISIONS:
        d = levelled["persona_plan"][name]
        if d.get("unverified"):
            lines.append("persona.%s: %s. %s" % (name, decision_value(name, d), d.get("reason")))
    for p in levelled["persona_plan"].get("starting_points") or []:
        if p.get("unverified"):
            lines.append("Starting point %s (%s)" % (p.get("name"), cite_text(p.get("cite"))))
    for t in ctx["tasks"]:
        lt = levelled["tasks"].get(t.get("id"))
        if lt is None:
            continue
        for name in TASK_DECISIONS:
            got = task_decision(lt, name)
            if not is_unverified(name, got):
                continue
            if name == "connectors":
                systems = [c.get("system") for c in got if c.get("unverified")]
                lines.append("%s.connectors: %s" % (t["id"], ", ".join(systems)))
            else:
                reasons = [d.get("reason") for _, d in parts_of(name, got) if d.get("unverified")]
                lines.append("%s.%s: %s" % (t["id"], name, " ".join(reasons)))
    for tool in levelled.get("tools") or []:
        if tool["permission"].get("unverified"):
            lines.append("Tool %s %s permission" % (tool.get("system"), tool.get("use")))
    for kind in ("blockers", "warnings"):
        for item in levelled[kind]:
            if item.get("unverified"):
                lines.append("%s about %s: %s" % (item["code"], item["about"], item.get("message")))
    return lines


def render_blockers(ctx):
    levelled = ctx["levelled"]
    owner = ((ctx["profile"].get("owners") or {}).get("compliance"))
    out = [section_open(3), "<h2>Blockers and warnings</h2>"]
    if owner:
        out.append('<p class="note">Compliance owner: %s.</p>' % esc(owner))
    out.append("<h3>Blockers</h3>")
    out.append(_code_list(ctx, levelled["blockers"], "blocker") if levelled["blockers"]
               else "<p>No blockers. Every task can be built as asked on this plan and data class.</p>")
    out.append("<h3>Warnings</h3>")
    out.append(_code_list(ctx, levelled["warnings"], "warning") if levelled["warnings"] else "<p>No warnings.</p>")
    out.append("<h3>Rests on an unverified fact</h3>")
    lines = unverified_items(ctx)
    out.append('<ul class="unverified">%s</ul>' % "".join("<li>%s %s</li>" % (UNVERIFIED_TAG, esc(line))
                                                           for line in lines)
               if lines else "<p>Nothing rests on an unverified fact.</p>")
    out.append("</section>")
    return "\n".join(out)


def _done_of(tasks):
    return "%d of %d tasks done" % (sum(1 for t in tasks if t["status"] == "done"), len(tasks))


def _status(status):
    return '<span class="status">%s</span>' % esc(STATUS_WORDS.get(status, status))


def _backlog_task(task):
    steps = []
    for step in task.get("how") or []:
        text = esc(step.get("text"))
        if step.get("link"):
            text += " <code>%s</code>" % esc(cite_text(step["link"]))
        steps.append("<li>%s</li>" % text)
    return ('<li><details><summary>%s <code>%s</code> %s <span class="owner">owner: %s</span></summary>'
            '<ol>%s</ol><p>Done when: %s</p></details></li>' % (
                _status(task["status"]), esc(task["id"]), esc(task.get("title")), esc(task.get("owner_role")),
                "".join(steps), esc(task.get("done_when"))))


def _story(story):
    gates = story.get("gated_by") or []
    gate_text = ('<ul class="plain">%s</ul>' % "".join(
        "<li>%s <code>%s</code>: %s</li>" % (esc(g.get("kind")), esc(g.get("id")), esc(g.get("text"))) for g in gates)
        if gates else "nothing")
    return ('<details><summary>%s <code>%s</code> %s <span class="owner">(%s)</span></summary>'
            '<p>%s</p><p>Part %s. %s. Priority %s.</p><div class="gates">Gated by: %s</div>'
            '<ul class="tasks">%s</ul></details>' % (
                _status(story["status"]), esc(story["id"]), esc(story.get("title")), esc(_done_of(story["tasks"])),
                esc(story.get("statement")), esc(story.get("part")), "In pilot" if story.get("in_pilot") else "Later",
                esc(fmt(story.get("priority"))), gate_text, "".join(_backlog_task(t) for t in story["tasks"])))


def render_backlog(ctx):
    backlog = ctx["backlog"]
    epic = backlog["epic"]
    out = [section_open(4), "<h2>Backlog</h2>",
           '<p class="note">Status words: [ ] todo, [~] in progress, [x] done. To change a status, edit backlog.json '
           'and run the backlog and dashboard commands again.</p>']
    out.append('<details class="epic" open><summary>%s <code>%s</code> %s <span class="owner">(%s)</span></summary>'
               % (_status(epic["status"]), esc(epic["id"]), esc(epic.get("title")), esc(_done_of(backlog_tasks(backlog)))))
    for feature in epic["features"]:
        tasks = [t for s in feature["stories"] for t in s["tasks"]]
        out.append('<details class="feature-bl"><summary>%s <code>%s</code> %s <span class="owner">(%s; %s)</span>'
                   '</summary>' % (_status(feature["status"]), esc(feature["id"]), esc(feature.get("title")),
                                   esc(plural(len(feature["stories"]), "story", "stories")), esc(_done_of(tasks))))
        out.append("".join(_story(s) for s in feature["stories"]))
        out.append("</details>")
    out.append("</details>")
    retired = backlog.get("retired") or []
    if retired:
        out.append("<h3>Retired</h3>")
        out.append('<ul class="plain">%s</ul>' % "".join(
            "<li>%s <code>%s</code> %s</li>" % (_status(r.get("status")), esc(r.get("id")), esc(r.get("title")))
            for r in retired))
    out.append("</section>")
    return "\n".join(out)


def render_questions(ctx):
    pilot = set(t.get("id") for t in ctx["tasks"] if t.get("in_pilot"))
    questions = list(ctx["card"].get("open_questions") or [])
    first = [q for q in questions if set(q.get("blocks") or []) & pilot]
    rest = [q for q in questions if q not in first]
    out = [section_open(5), "<h2>Open questions</h2>"]
    if not questions:
        out.append("<p>No open questions.</p>")
    else:
        out.append('<p class="note">%s; %d block an in-pilot task and come first.</p>' % (
            plural(len(questions), "open question"), len(first)))
        items = []
        for q in first + rest:
            blocks = q.get("blocks") or []
            in_pilot = [b for b in blocks if b in pilot]
            items.append('<li><strong>%s</strong> %s<br>Blocks: %s%s. Owner: %s. Due: %s.</li>' % (
                esc(q.get("id")), esc(q.get("question")), esc(", ".join(blocks) or "nothing"),
                ' <span class="tag bad">blocks the pilot (%s)</span>' % esc(", ".join(in_pilot)) if in_pilot else "",
                esc(fmt(q.get("owner"), "not named")), esc(fmt(q.get("due"), "not set"))))
        out.append('<ul class="questions">%s</ul>' % "".join(items))
    out.append("</section>")
    return "\n".join(out)


def render_provenance(ctx):
    records = (("card", ctx["card"]), ("profile", ctx["profile"]))
    out = [section_open(6), "<h2>Where each answer came from</h2>",
           '<p class="note">Fields with a provenance entry, by status. Answered: a person said it. Default: taken '
           'from a named default. Assumed: the consultant\'s guess, to be confirmed. Open: no answer yet.</p>']
    rows = []
    for status in PROVENANCE_STATUSES:
        cells = []
        for _, data in records:
            prov = data.get("provenance") or {}
            cells.append(sum(1 for p in prov.values() if isinstance(p, dict) and p.get("status") == status))
        rows.append("<tr><th scope=\"row\">%s</th><td>%d</td><td>%d</td></tr>" % (status.capitalize(), cells[0], cells[1]))
    totals = [len(data.get("provenance") or {}) for _, data in records]
    rows.append("<tr><th scope=\"row\">Total</th><td>%d</td><td>%d</td></tr>" % (totals[0], totals[1]))
    out.append('<div class="scroll"><table class="counts-table"><thead><tr><th scope="col">Status</th>'
               '<th scope="col">Card</th><th scope="col">Profile</th></tr></thead><tbody>%s</tbody></table></div>'
               % "".join(rows))
    out.append("<h3>Assumed or open</h3>")
    pending = []
    for record, data in records:
        for path, p in (data.get("provenance") or {}).items():
            if isinstance(p, dict) and p.get("status") in ("assumed", "open"):
                pending.append("<li><code>%s:%s</code> %s. Owner: %s. Due: %s.%s</li>" % (
                    record, esc(path), esc(p["status"]), esc(fmt(p.get("owner"), "not named")),
                    esc(fmt(p.get("due"), "not set")),
                    " Source: <code>%s</code>." % esc(source_text(p["source"])) if p.get("source") else ""))
    out.append('<ul class="plain">%s</ul>' % "".join(pending) if pending else "<p>Nothing is assumed or open.</p>")
    out.append("<h3>Interview files the card cites</h3>")
    files = sorted(set(one.split("#", 1)[0] for p in (ctx["card"].get("provenance") or {}).values()
                       if isinstance(p, dict) for one in _validate.split_sources(p.get("source"))
                       if one.startswith("interviews/")))
    out.append('<ul class="plain">%s</ul>' % "".join("<li><code>%s</code></li>" % esc(f) for f in files)
               if files else "<p>The card cites no interview file.</p>")
    out.append("</section>")
    return "\n".join(out)


# --- The page ---------------------------------------------------------------------------------------------

STYLE = """
:root{--bg:#ffffff;--fg:#1c1c1e;--muted:#55565c;--line:#d5d6db;--panel:#f5f5f7;--code:#ececf0;--link:#1d4fa3;--bad:#a3191d;--warn:#7a5000;--ok:#1c6b39;--ovr:#5a3c99}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#151517;--fg:#ececef;--muted:#a6a7ad;--line:#3a3b40;--panel:#1f1f23;--code:#2a2b30;--link:#8db4ff;--bad:#ff8a85;--warn:#f0c060;--ok:#7fd49b;--ovr:#c3a8ff}}
:root[data-theme="dark"]{--bg:#151517;--fg:#ececef;--muted:#a6a7ad;--line:#3a3b40;--panel:#1f1f23;--code:#2a2b30;--link:#8db4ff;--bad:#ff8a85;--warn:#f0c060;--ok:#7fd49b;--ovr:#c3a8ff}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
main{max-width:1120px;margin:0 auto;padding:12px 16px 32px}
h1{font-size:22px;margin:8px 0 2px}
h2{font-size:18px;margin:24px 0 8px;padding-top:8px;border-top:2px solid var(--line)}
h3{font-size:15px;margin:14px 0 6px}
p,li,dd,td,th,summary{overflow-wrap:anywhere}
p{margin:4px 0}
a{color:var(--link)}
code{font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--code);padding:0 3px;border-radius:3px}
.sub,.note,.generated,.cite,.owner,.group{color:var(--muted)}
.lead{font-weight:600}
.tag{display:inline-block;border:1px solid currentColor;border-radius:3px;padding:0 4px;font-size:12px;margin:0 2px}
.unv,.warn{color:var(--warn)}
.bad{color:var(--bad)}
.ovr{color:var(--ovr)}
.status{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;white-space:nowrap}
dl{margin:4px 0;display:grid;grid-template-columns:minmax(90px,max-content) minmax(0,1fr);gap:2px 10px}
dt{color:var(--muted)}
dd{margin:0;min-width:0}
.toc{display:flex;flex-wrap:wrap;gap:4px 14px;padding-left:20px;margin:4px 0}
.toc-title{font-weight:600;margin-top:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:8px}
.panel,.task{background:var(--panel);border:1px solid var(--line);border-radius:4px;padding:8px;min-width:0}
.panel h3{margin-top:0}
.panel dl{grid-template-columns:minmax(0,1fr);gap:0}
.panel dd{margin-bottom:4px}
.counts{font-weight:600}
.task{margin:6px 0}
.task-title{font-weight:600}
.scroll{overflow-x:auto;max-width:100%}
table{border-collapse:collapse;width:100%}
th,td{border-top:1px solid var(--line);padding:4px 6px;text-align:left;vertical-align:top}
.decisions th{width:9em;font-weight:600}
ul,ol{margin:4px 0;padding-left:20px}
ul.plain,ul.codes,ul.why,ul.questions,ul.unverified,ul.tasks{padding-left:16px}
details{margin:2px 0}
details details{margin-left:12px}
summary{cursor:pointer}
@media (max-width:480px){dl{grid-template-columns:minmax(0,1fr)}.decisions th{width:auto}.decisions tr,.decisions th,.decisions td{display:block}.decisions th{border-top:1px solid var(--line);padding-bottom:0}.decisions td{border-top:0}}
@media print{nav{display:none}details>*{display:block}details:not([open])>*{display:block}details::details-content{display:block;content-visibility:visible}summary{list-style:none}body{background:#ffffff;color:#000000}}
""".strip()


def build_page(inputs, date):
    card = inputs["card"]
    profile = inputs["profile"]
    role = (card.get("role") or {}).get("name") or card.get("id") or "Persona"
    ctx = dict(inputs)
    ctx.update({
        "title": "%s twin" % role,
        "tasks": [t for t in card.get("tasks") or [] if isinstance(t, dict)],
        "products": dict((s.get("id"), s.get("product")) for s in profile.get("systems") or []
                         if isinstance(s, dict)),
        "summary": summary(inputs),
        "field_counts": field_counts(card, profile, inputs["catalogue"]),
    })
    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % esc(ctx["title"]),
        "<style>\n%s\n</style>" % STYLE,
        "</head>",
        "<body>",
        "<main>",
        render_header(ctx, date),
        render_contents(),
        render_anatomy(ctx),
        render_features(ctx),
        render_blockers(ctx),
        render_backlog(ctx),
        render_questions(ctx),
        render_provenance(ctx),
        "</main>",
        "</body>",
        "</html>",
    ]
    return "\n".join(parts) + "\n", ctx["summary"]


def render(persona_dir, date=None):
    """The page for the persona in persona_dir as a string. Never writes.

    Raises UsageError for a date that is not a real YYYY-MM-DD date, and DashboardError when the card does
    not validate or levelled.json or backlog.json is missing or out of date (the message says which and what
    to run next).
    """
    date = parse_date(date)
    page, _ = build_page(load_inputs(persona_dir), date)
    return page


def write_dashboard(persona_dir, date=None):
    """Render and write <persona_dir>/dashboard.html; nothing is written when rendering is refused.

    A date that is not a real calendar date raises UsageError before anything is read.
    """
    date = parse_date(date)
    try:
        inputs = load_inputs(persona_dir)
    except DashboardError as exc:
        return {"ok": False, "validation": exc.validation, "error": str(exc), "path": None, "summary": None}
    page, figures = build_page(inputs, date)
    path = Path(persona_dir) / DASHBOARD_FILE
    path.write_bytes(page.encode("utf-8"))
    return {"ok": True, "validation": inputs["validation"], "error": None, "path": str(path), "summary": figures}
