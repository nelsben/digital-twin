"""Level a persona card: turn card.json and its customer profile into levelled.json.

level(persona_dir) validates the card first and levels nothing when there are
errors. Otherwise it builds flat facts from the card, the profile, the
industry pack and data/plan-fit.json, applies the rules in data/rules.json and
returns the result; it never writes. write_levelled(persona_dir) does the same
and writes <persona_dir>/levelled.json.

    {"ok": bool,                    # False when validation failed (nothing levelled)
     "validation": {...},           # the validate() result
     "levelled": {...} or None}     # the levelled.json content

Rules are data: {"id", "decides", "when", "then", "cite", "unverified",
"basis", "reason"} plus "fix" on blockers and warnings. No decision value is
written in this file; every value comes from a rule, a fact or a card
override. Design of record: partner-kit/docs/design.md, section 7.
"""

import hashlib
import json
import posixpath
import re
from pathlib import Path

from . import fields as _fields
from . import packs as _packs
from . import validate as _validate

PLUGIN_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PLUGIN_DIR / "data"
RULES_PATH = DATA_DIR / "rules.json"
PLAN_FIT_PATH = DATA_DIR / "plan-fit.json"
DESIGN_PATH = PLUGIN_DIR.parent.parent / "docs" / "design.md"
LEVELLED_FILE = "levelled.json"

LEVELLED_VERSION = 1
RULES_VERSION = 1
PLAN_FIT_VERSION = 1

UNDECIDED = "undecided"
COMBINES = ("first", "strictest")
BASES = ("compendium", "our-recommendation")
CODE_DECISIONS = ("blocker", "warning")
PLAN_TIERS = ("team", "enterprise", "individual")
CAPABILITY_VALUES = ("yes", "no", "limited")
RULE_KEYS = ("id", "decides", "when", "then", "cite", "unverified", "basis", "reason")
OPTIONAL_RULE_KEYS = ("fix",)
CAPABILITY_KEYS = ("id", "name", "team", "enterprise", "individual", "lost_on_team", "cite", "unverified")

ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CITE_PATTERN = re.compile(r"^docs/compendium/[0-9]{2}-[a-z0-9-]+\.md#[a-z0-9_-]+$")
PLUGIN_NAME_PATTERN = re.compile(r"^twin-[a-z0-9-]+$")

# Decisions the engine computes, in the order it computes them for each task. A rule may read
# only the decisions computed before its own.
TASK_DECISIONS = ("runtime", "identity", "autonomy.start", "autonomy.ceiling",
                  "data_controls.settings_baseline", "data_controls.web_tools", "data_controls.surfaces",
                  "data_controls.retention", "memory")
DATA_CONTROLS = ("settings_baseline", "web_tools", "surfaces", "retention")
DECISION_ORDER = TASK_DECISIONS + ("connectors.identity", "connectors.permission", "plan_fit")
DECISION_FACTS = TASK_DECISIONS + ("plan_fit",)
DECISION_SCOPE = dict([(name, "task") for name in TASK_DECISIONS] + [
    ("connectors.identity", "task"), ("connectors.permission", "tool"), ("plan_fit", "task"),
    ("persona.distribution", "persona"), ("persona.settings_baseline", "persona")])

# Card overrides: the decisions an override may replace, and those it may not.
OVERRIDABLE = ("runtime", "identity", "autonomy.start", "autonomy.ceiling", "data_controls", "memory")
NOT_OVERRIDABLE = ("connectors", "plan_fit")

# Facts. Card and profile facts read the field at that path; the rest are derived.
CARD_FACTS = ("role.works_in", "role.device", "role.plugin_name", "memory.personal_memory_wanted")
PROFILE_FACTS = ("plan.tier", "identity.sso", "identity.scim", "devices.mdm", "compliance.retention",
                 "compliance.phi", "compliance.baa", "compliance.mnpi", "governance.action_log_required",
                 "runtime_preferences.self_hosting_required", "network.can_allowlist_anthropic_ips")
DERIVED_PERSONA_FACTS = ("systems.kinds", "systems.products", "pack.id", "pack.settings_baseline",
                         "persona.data_classes", "persona.products")
TASK_FIELD_FACTS = ("trigger", "data_class", "output.audience", "reversible", "touches_money",
                    "cost_of_mistake.level", "reads_untrusted_input", "in_pilot")
DERIVED_TASK_FACTS = ("task.write_actions", "task.write_products", "task.input_products", "task.products",
                      "task.reads_private_network", "task.shared_tool_ceiling")
TOOL_FACTS = ("tool.use", "tool.level", "tool.wanted_differs")
TASK_FACTS = tuple("task." + name for name in TASK_FIELD_FACTS) + DERIVED_TASK_FACTS
CAPABILITY_PREFIX = "capability."

# Codes the engine raises itself (the rest come from rules). Each is listed in design section 7.2.
ENGINE_CODES = ("decision-undecided", "override-applied", "field-open",
                "override-not-allowed", "override-unknown-target", "plugin-name-invalid")
DESIGN_CITE = "partner-kit/docs/design.md#7-levelling-datarulesjson-levelpy"
DESIGN_VALUES_CITE = "partner-kit/docs/design.md#72-decision-values"
DESIGN_PROVENANCE_CITE = "partner-kit/docs/design.md#43-provenance-and-completeness"
UNREACHED_CONNECTOR_CITE = "docs/compendium/11-connectors.md#adding-a-connector-that-isnt-in-the-directory"


class LevelError(ValueError):
    """A fault in rules.json or plan-fit.json, or a condition that names an unknown fact."""


class Open(object):
    """The value of a fact whose field is open: asked, not yet answered."""

    __slots__ = ("record", "path", "owner", "due")

    def __init__(self, record, path, owner=None, due=None):
        self.record, self.path, self.owner, self.due = record, path, owner, due

    def __repr__(self):
        return "Open(%s:%s)" % (self.record, self.path)


class FactOpen(Exception):
    """matches() needed a fact whose field is still open."""

    def __init__(self, fact, value):
        Exception.__init__(self, "%s is open (%s:%s)" % (fact, value.record, value.path))
        self.fact, self.value = fact, value


# --- Conditions ----------------------------------------------------------------------------------

def fact_names(when):
    """Return the fact names a condition reads, in order, including those inside any/all/not."""
    out = []
    if not isinstance(when, dict):
        raise LevelError("a condition must be an object of fact names, 'any', 'all' or 'not'; got %r" % (when,))
    for key, want in when.items():
        if key in ("any", "all"):
            if not isinstance(want, list) or not want:
                raise LevelError("'%s' takes a non-empty list of conditions" % key)
            for item in want:
                out.extend(fact_names(item))
        elif key == "not":
            out.extend(fact_names(want))
        else:
            out.append(key)
    return out


def _same(value, want):
    if isinstance(value, bool) or isinstance(want, bool):
        return isinstance(value, bool) and isinstance(want, bool) and value == want
    return value == want


def _test(value, want):
    wants = want if isinstance(want, list) else [want]
    values = value if isinstance(value, list) else [value]
    return any(_same(v, w) for v in values for w in wants)


def _match(when, facts):
    for key, want in when.items():
        if key == "any":
            pending = None
            hit = False
            for item in want:
                try:
                    if _match(item, facts):
                        hit = True
                        break
                except FactOpen as exc:
                    pending = pending or exc
            if not hit:
                if pending is not None:
                    raise pending
                return False
        elif key == "all":
            if not all(_match(item, facts) for item in want):
                return False
        elif key == "not":
            if _match(want, facts):
                return False
        else:
            value = facts[key]
            if isinstance(value, Open):
                raise FactOpen(key, value)
            if not _test(value, want):
                return False
    return True


def matches(when, facts, known=None):
    """True when the condition holds for these facts.

    A condition is an object: each fact name maps to a value, or to a list of allowed values; a
    list-valued fact matches when any of its items does. 'any' and 'all' take lists of conditions
    and 'not' takes one. Keys are checked in order and the first that fails ends the check. Every
    fact name is checked before anything is evaluated, so an unknown name always raises LevelError.
    A fact whose field is open raises FactOpen when it is reached.
    """
    names = set(known) if known is not None else set(facts)
    for name in fact_names(when):
        if name not in names:
            raise LevelError("unknown fact %r" % name)
    return _match(when, facts)


# --- Loading rules.json and plan-fit.json ---------------------------------------------------------

def _read_json(path, what):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LevelError("%s (%s) cannot be read as JSON: %s" % (what, path, exc))


def design_codes(path=None):
    """Return the blocker and warning codes listed in design section 7.2, or None without the file."""
    target = Path(path) if path is not None else DESIGN_PATH
    if not target.is_file():
        return None
    text = target.read_text(encoding="utf-8")
    m = re.search(r"^### 7\.2 Decision values\n(.*?)^## 8\.", text, re.MULTILINE | re.DOTALL)
    if not m:
        return set()
    return set(re.findall(r"^- `([a-z0-9-]+)`: \S", m.group(1), re.MULTILINE))


def load_plan_fit(path=None):
    """Return plan-fit.json, checked; raise LevelError naming the capability at fault."""
    data = _read_json(path or PLAN_FIT_PATH, "plan-fit.json")
    if not isinstance(data, dict) or data.get("plan_fit_version") != PLAN_FIT_VERSION:
        raise LevelError("plan-fit.json must be an object with plan_fit_version %d" % PLAN_FIT_VERSION)
    if sorted(data) != ["capabilities", "plan_fit_version"] or not isinstance(data["capabilities"], list):
        raise LevelError("plan-fit.json holds plan_fit_version and a list of capabilities, nothing else")
    seen = set()
    for cap in data["capabilities"]:
        cid = cap.get("id") if isinstance(cap, dict) else None
        where = "plan-fit.json capability %r" % (cid,)
        if not isinstance(cap, dict) or sorted(cap) != sorted(CAPABILITY_KEYS):
            raise LevelError("%s must have exactly the keys %s" % (where, ", ".join(CAPABILITY_KEYS)))
        if not isinstance(cid, str) or not ID_PATTERN.match(cid) or cid in seen:
            raise LevelError("%s: the id must be kebab-case and unique" % where)
        seen.add(cid)
        for tier in PLAN_TIERS:
            if cap[tier] not in CAPABILITY_VALUES:
                raise LevelError("%s: %s must be one of %s" % (where, tier, ", ".join(CAPABILITY_VALUES)))
        if not isinstance(cap["cite"], str) or not CITE_PATTERN.match(cap["cite"]):
            raise LevelError("%s: cite must be a compendium page with an anchor" % where)
        if not isinstance(cap["unverified"], bool):
            raise LevelError("%s: unverified must be true or false" % where)
    return data


def _allowed_facts(scope, decides, capabilities):
    allowed = set(CARD_FACTS + PROFILE_FACTS + DERIVED_PERSONA_FACTS)
    allowed |= set(CAPABILITY_PREFIX + cap["id"] for cap in capabilities)
    if scope in ("task", "tool"):
        allowed |= set(TASK_FACTS)
        if decides in DECISION_ORDER:
            allowed |= set(DECISION_ORDER[:DECISION_ORDER.index(decides)]) & set(DECISION_FACTS)
        else:
            allowed |= set(DECISION_FACTS)
    if scope == "tool":
        allowed |= set(TOOL_FACTS)
    return allowed


def rule_scope(rule):
    """'persona', 'task' or 'tool': where a rule is evaluated."""
    if rule["decides"] in DECISION_SCOPE:
        return DECISION_SCOPE[rule["decides"]]
    names = set(fact_names(rule["when"]))
    if names & set(TOOL_FACTS):
        return "tool"
    if names & (set(TASK_FACTS) | set(DECISION_FACTS)):
        return "task"
    return "persona"


def load_rules(path=None, plan_fit=None, codes=None):
    """Return rules.json, checked; raise LevelError naming the rule at fault.

    codes is the set of blocker and warning codes the rules may raise; by default it is read from
    design section 7.2 when the design file is present (it is not, in an installed plugin).
    """
    plan_fit = plan_fit if plan_fit is not None else load_plan_fit()
    codes = codes if codes is not None else design_codes()
    data = _read_json(path or RULES_PATH, "rules.json")
    if not isinstance(data, dict) or data.get("rules_version") != RULES_VERSION:
        raise LevelError("rules.json must be an object with rules_version %d" % RULES_VERSION)
    if sorted(data) != ["decisions", "rules", "rules_version"]:
        raise LevelError("rules.json holds rules_version, decisions and rules, nothing else")
    decisions = data["decisions"]
    if not isinstance(decisions, dict):
        raise LevelError("rules.json decisions must be an object")
    for name, spec in decisions.items():
        if name not in DECISION_SCOPE:
            raise LevelError("rules.json decisions: unknown decision %r" % name)
        if not isinstance(spec, dict) or spec.get("combine") not in COMBINES or \
                not set(spec) <= {"combine", "order"}:
            raise LevelError("rules.json decisions.%s: combine must be one of %s" % (name, ", ".join(COMBINES)))
        if "order" in spec and (spec["combine"] != "strictest" or not isinstance(spec["order"], list)):
            raise LevelError("rules.json decisions.%s: order is a list, for a strictest decision only" % name)
    if codes is not None:
        missing = [code for code in ENGINE_CODES if code not in codes]
        if missing:
            raise LevelError("the engine's codes %s are not listed in design section 7.2" % ", ".join(missing))
    seen = set()
    capabilities = plan_fit["capabilities"]
    for rule in data["rules"]:
        rid = rule.get("id") if isinstance(rule, dict) else None
        where = "rule %r" % (rid,)
        if not isinstance(rule, dict):
            raise LevelError("rules.json: every rule is an object")
        keys = set(rule)
        if not set(RULE_KEYS) <= keys or not keys <= set(RULE_KEYS + OPTIONAL_RULE_KEYS):
            raise LevelError("%s must have the keys %s (and fix on a blocker or warning)" % (where, ", ".join(RULE_KEYS)))
        if not isinstance(rid, str) or not ID_PATTERN.match(rid):
            raise LevelError("%s: the id must be kebab-case" % where)
        if rid in seen:
            raise LevelError("%s: the id is used twice" % where)
        seen.add(rid)
        decides = rule["decides"]
        if decides not in CODE_DECISIONS and decides not in decisions:
            raise LevelError("%s decides an unknown decision %r" % (where, decides))
        try:
            names = fact_names(rule["when"])
        except LevelError as exc:
            raise LevelError("%s: %s" % (where, exc))
        allowed = _allowed_facts(rule_scope(rule), decides, capabilities)
        for name in names:
            if name not in allowed:
                raise LevelError("%s reads an unknown fact %r (or one not known where it is evaluated)" % (where, name))
        then = rule["then"]
        if decides in CODE_DECISIONS:
            if not isinstance(then, str) or not ID_PATTERN.match(then):
                raise LevelError("%s: a %s rule's then is its code, in kebab-case" % (where, decides))
            if codes is not None and then not in codes:
                raise LevelError("%s raises the code %r, which design section 7.2 does not list" % (where, then))
            if not isinstance(rule.get("fix"), str) or not rule["fix"].strip():
                raise LevelError("%s: a %s rule needs a fix" % (where, decides))
        else:
            if "fix" in rule:
                raise LevelError("%s: only a blocker or warning rule has a fix" % where)
            if isinstance(then, dict):
                if sorted(then) != ["fact"] or then["fact"] not in allowed:
                    raise LevelError("%s: then {\"fact\": name} must name a known fact" % where)
            spec = decisions[decides]
            if spec["combine"] == "strictest" and "order" in spec and not isinstance(then, dict) \
                    and then != UNDECIDED and then not in spec["order"]:
                raise LevelError("%s: %r is not in the order of %s" % (where, then, decides))
        if not isinstance(rule["cite"], str) or not CITE_PATTERN.match(rule["cite"]):
            raise LevelError("%s: cite must be a compendium page with an anchor" % where)
        if not isinstance(rule["unverified"], bool):
            raise LevelError("%s: unverified must be true or false" % where)
        if rule["basis"] not in BASES:
            raise LevelError("%s: basis must be one of %s" % (where, ", ".join(BASES)))
        if not isinstance(rule["reason"], str) or not rule["reason"].strip():
            raise LevelError("%s: reason must be a sentence" % where)
    return data


# --- Facts ----------------------------------------------------------------------------------------

def _get(data, dotted):
    node = data
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _unset(value):
    return value is None or value == "" or value == []


def _fact(record, path, value, provenance, catalogue_path, catalogue):
    """The fact's value: Open when the field is open and empty, the catalogue default when unset."""
    prov = provenance.get(path) if isinstance(provenance, dict) else None
    if _unset(value) and isinstance(prov, dict) and prov.get("status") == "open":
        return Open(record, path, prov.get("owner"), prov.get("due"))
    if value is None:
        entry = _fields.entry_for(record, catalogue_path, catalogue)
        default = entry.get("default") if entry else None
        if isinstance(default, dict):
            return default.get("value")
    return value


def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def match_default(system, defaults):
    """The pack's connector default for a profile system: the same product, else a same-kind product
    whose words contain, or are contained in, the system's product words."""
    product = (system.get("product") or "").lower()
    for entry in defaults:
        if (entry.get("product") or "").lower() == product and product:
            return entry
    words = _tokens(product)
    for entry in defaults:
        if entry.get("system_kind") != system.get("kind"):
            continue
        theirs = _tokens(entry.get("product"))
        if words and theirs and (words <= theirs or theirs <= words):
            return entry
    return None


def _systems(profile, pack):
    out = {}
    for system in profile.get("systems") or []:
        default = match_default(system, pack.get("connector_defaults") or [])
        product = default["product"] if default else system.get("product")
        out[system.get("id")] = {"system": system, "default": default, "product": product}
    return out


def _unique(items):
    out = []
    for item in items:
        if item is not None and not isinstance(item, Open) and item not in out:
            out.append(item)
    return out


def _uses(task):
    """The connector tools a task uses, in order: (system, 'read' or the write action)."""
    out = []
    for item in task.get("inputs") or []:
        use = "read" if item.get("access") != "write" else "write"
        if (item.get("system"), use) not in out:
            out.append((item.get("system"), use))
    for item in task.get("writes") or []:
        if (item.get("system"), item.get("action")) not in out:
            out.append((item.get("system"), item.get("action")))
    return out


def persona_facts(card, profile, pack, plan_fit, catalogue):
    card_prov, profile_prov = card.get("provenance") or {}, profile.get("provenance") or {}
    facts = {}
    for path in CARD_FACTS:
        facts[path] = _fact("card", path, _get(card, path), card_prov, path, catalogue)
    for path in PROFILE_FACTS:
        facts[path] = _fact("profile", path, _get(profile, path), profile_prov, path, catalogue)
    systems = _systems(profile, pack)
    tasks = card.get("tasks") or []
    used = _unique([s for task in tasks for s, _ in _uses(task)])
    facts["systems.kinds"] = _unique([entry["system"].get("kind") for entry in systems.values()])
    facts["systems.products"] = _unique([entry["product"] for entry in systems.values()])
    facts["pack.id"] = pack.get("id")
    facts["pack.settings_baseline"] = pack.get("settings_baseline")
    facts["persona.data_classes"] = _unique([task.get("data_class") for task in tasks])
    facts["persona.products"] = _unique([systems[s]["product"] for s in used if s in systems])
    tier = facts["plan.tier"]
    for cap in plan_fit["capabilities"]:
        name = CAPABILITY_PREFIX + cap["id"]
        facts[name] = tier if isinstance(tier, Open) else (cap.get(tier) if tier in PLAN_TIERS else None)
    return facts


def task_facts(task, card, profile, pack):
    prov = card.get("provenance") or {}
    tid = task.get("id")
    facts = {}
    for name in TASK_FIELD_FACTS:
        path = "tasks.%s.%s" % (tid, name)
        value = _get(task, name)
        entry = prov.get(path)
        if _unset(value) and isinstance(entry, dict) and entry.get("status") == "open":
            value = Open("card", path, entry.get("owner"), entry.get("due"))
        facts["task." + name] = value
    systems = _systems(profile, pack)

    def products(items):
        return _unique([systems[i.get("system")]["product"] for i in items if i.get("system") in systems])

    writes, inputs = task.get("writes") or [], task.get("inputs") or []
    facts["task.write_actions"] = _unique([w.get("action") for w in writes])
    facts["task.write_products"] = products(writes)
    facts["task.input_products"] = products(inputs)
    facts["task.products"] = _unique(facts["task.input_products"] + facts["task.write_products"])
    facts["task.reads_private_network"] = any(
        systems[i.get("system")]["system"].get("private_network") is True
        for i in inputs if i.get("system") in systems)
    facts["task.shared_tool_ceiling"] = None
    for name in DECISION_FACTS:
        facts[name] = None
    return facts


# --- The engine -----------------------------------------------------------------------------------

def _item(code, about, cite, unverified, message, fix):
    return {"code": code, "about": about, "cite": cite, "unverified": unverified, "message": message, "fix": fix}


def _decision(value, rule, cite, reason, unverified, basis):
    return {"value": value, "rule": rule, "cite": cite, "reason": reason, "unverified": unverified,
            "basis": basis, "overridden": None}


def _source_cite(persona_dir, source):
    """A card provenance source (relative to the persona folder) as a repo-relative path."""
    persona = Path(persona_dir).resolve()
    base = "engagements/%s/personas/%s" % (persona.parent.parent.name, persona.name)
    path, _, anchor = source.partition("#")
    joined = posixpath.normpath(posixpath.join(base, path))
    return joined + ("#" + anchor if anchor else "")


class _Run(object):
    """One levelling run: the loaded data, the rules by decision and what has been raised."""

    def __init__(self, rules, plan_fit, fired):
        self.rules, self.plan_fit, self.fired = rules, plan_fit, fired
        self.by_decision = {}
        for rule in rules["rules"]:
            self.by_decision.setdefault(rule["decides"], []).append(rule)
        self.known = None
        self.open = {}

    def note_open(self, about, exc, what):
        key = (about, exc.value.record, exc.value.path)
        if key in self.open:
            return
        owner = exc.value.owner or "its owner"
        due = (", due %s" % exc.value.due) if exc.value.due else ""
        self.open[key] = _item(
            "field-open", about, DESIGN_PROVENANCE_CITE, False,
            "%s:%s is open (%s%s), so %s is left undecided until it is answered."
            % (exc.value.record, exc.value.path, owner, due, what),
            "Get the answer from %s, record it with its source, and level again." % owner)

    def _then(self, rule, facts):
        then = rule["then"]
        if isinstance(then, dict):
            value = facts[then["fact"]]
            return None if isinstance(value, Open) else value
        return then

    def decide(self, name, facts, about):
        """Return (decision, undecided) for one decision, combining the matching rules."""
        spec = self.rules["decisions"][name]
        hits = []
        for rule in self.by_decision.get(name, []):
            try:
                hit = matches(rule["when"], facts, self.known)
            except FactOpen as exc:
                self.note_open(about, exc, name)
                return _decision(None, rule["id"], rule["cite"],
                                 "Open: %s:%s is not answered yet, so this is left undecided until it is."
                                 % (exc.value.record, exc.value.path), False, rule["basis"]), False
            if not hit:
                continue
            self.fired.add(rule["id"])
            value = self._then(rule, facts)
            if spec["combine"] == "first":
                hits = [(rule, value)]
                break
            if value is not None:
                hits.append((rule, value))
        if not hits:
            return _decision(None, None, DESIGN_VALUES_CITE,
                             "Undecided: no rule in rules.json covers this case, so a person must decide it.",
                             False, "our-recommendation"), True
        if spec["combine"] == "strictest":
            undecided = [hit for hit in hits if hit[1] == UNDECIDED]
            if undecided:
                hits = undecided[:1]
            else:
                order = spec.get("order")
                hits = [min(hits, key=lambda hit: order.index(hit[1]) if order else hit[1])]
        rule, value = hits[0]
        if value == UNDECIDED:
            return _decision(None, rule["id"], rule["cite"], rule["reason"], rule["unverified"], rule["basis"]), True
        return _decision(value, rule["id"], rule["cite"], rule["reason"], rule["unverified"], rule["basis"]), False

    def codes(self, scope, facts, about, rule_filter=None):
        """Every blocker and warning rule of this scope that holds: [(rule, item)]."""
        out = []
        for kind in CODE_DECISIONS:
            for rule in self.by_decision.get(kind, []):
                if rule_scope(rule) != scope or (rule_filter and not rule_filter(rule)):
                    continue
                try:
                    hit = matches(rule["when"], facts, self.known)
                except FactOpen as exc:
                    self.note_open(about, exc, "whether %s applies" % rule["then"])
                    continue
                if hit:
                    self.fired.add(rule["id"])
                    out.append((rule, _item(rule["then"], about, rule["cite"], rule["unverified"],
                                            rule["reason"], rule["fix"])))
        return out


def override_problems(overrides, task_ids):
    """Blockers for card overrides the engine will not apply: [(index, blocker)]."""
    out = []
    for index, override in enumerate(overrides or []):
        task, decision = override.get("task"), override.get("decision")
        if decision in NOT_OVERRIDABLE:
            out.append((index, _item(
                "override-not-allowed", task if task in task_ids else "persona", DESIGN_CITE, False,
                "overrides[%d] replaces %s, which follows from the other decisions and cannot be overridden."
                % (index, decision),
                "Override the decision it follows from (runtime, identity or data_controls), or change the card.")))
        elif task not in task_ids or decision not in OVERRIDABLE:
            out.append((index, _item(
                "override-unknown-target", task if task in task_ids else "persona", DESIGN_CITE, False,
                "overrides[%d] names task %r and decision %r, which levelling does not have." % (index, task, decision),
                "Name a task id on the card and one of: %s." % ", ".join(OVERRIDABLE))))
    return out


def _apply_override(decision, value, override):
    out = dict(decision)
    out["overridden"] = {"rule_result": decision["value"], "reason": override.get("reason"),
                         "approved_by": override.get("approved_by")}
    out["value"] = value
    return out


def _strictest(results, order):
    best = None
    for result in results:
        if result is None or result["value"] is None:
            continue
        if best is None or order.index(result["value"]) < order.index(best["value"]):
            best = result
    return best


def _level_tasks(run, card, profile, pack, persona, overrides, shared):
    """One pass over every task with the shared-tool ceilings given; returns the per-task state."""
    out = {}
    for task in card.get("tasks") or []:
        tid = task.get("id")
        facts = dict(persona)
        facts.update(task_facts(task, card, profile, pack))
        facts["task.shared_tool_ceiling"] = shared.get(tid)
        state = {"facts": facts, "decisions": {}, "undecided": [], "overrides": []}
        for name in TASK_DECISIONS:
            decision, undecided = run.decide(name, facts, tid)
            target, sub = (name, None) if not name.startswith("data_controls.") else ("data_controls", name.split(".", 1)[1])
            override = overrides.get((tid, target))
            if override is not None:
                value = override.get("value")
                if sub is None or (isinstance(value, dict) and sub in value):
                    decision = _apply_override(decision, value if sub is None else value[sub], override)
                    state["overrides"].append((target, decision))
                    undecided = False
            if undecided:
                state["undecided"].append(decision)
            state["decisions"][name] = decision
            facts[name] = decision["value"]
        identity, undecided = run.decide("connectors.identity", facts, tid)
        if undecided:
            state["undecided"].append(identity)
        state["connector_identity"] = identity
        state["uses"] = _uses(task)
        state["task"] = task
        out[tid] = state
    return out


def _permission(run, state, use, level):
    facts = dict(state["facts"])
    facts.update({"tool.use": use, "tool.level": level, "tool.wanted_differs": False})
    decision, _ = run.decide("connectors.permission", facts, state["task"].get("id"))
    return decision


def _tools(states):
    tools = []
    for tid, state in states.items():
        for system, use in state["uses"]:
            for tool in tools:
                if tool["system"] == system and tool["use"] == use:
                    tool["tasks"].append(tid)
                    break
            else:
                tools.append({"system": system, "use": use, "tasks": [tid]})
    return tools


def _ceiling(state):
    return state["decisions"]["autonomy.ceiling"]["value"]


def _shared_pass(run, states, shared):
    """Find tools whose tasks want different settings; return (new shared ceilings, differing tools)."""
    new, differ = dict(shared), []
    for tool in _tools(states):
        wanted = []
        for tid in tool["tasks"]:
            level = _ceiling(states[tid])
            if level is not None:
                wanted.append(_permission(run, states[tid], tool["use"], level)["value"])
        if len(set(v for v in wanted if v is not None)) <= 1:
            continue
        differ.append((tool["system"], tool["use"]))
        levels = [_ceiling(states[tid]) for tid in tool["tasks"] if _ceiling(states[tid]) is not None]
        lowest = min(levels)
        for tid in tool["tasks"]:
            level = _ceiling(states[tid])
            overridden = states[tid]["decisions"]["autonomy.ceiling"]["overridden"] is not None
            if level is not None and level > lowest and not overridden:
                new[tid] = min(new.get(tid, lowest), lowest)
    return new, differ


def _walk_decisions(when):
    return [name for name in fact_names(when) if name in DECISION_FACTS]


def level(persona_dir, fired=None, rules=None, plan_fit=None, catalogue=None):
    """Level the persona in persona_dir. Never writes. See the module docstring for the result."""
    catalogue = catalogue if catalogue is not None else _fields.load_catalogue()
    validation = _validate.validate(persona_dir, catalogue)
    if not validation["ok"]:
        return {"ok": False, "validation": validation, "levelled": None}
    plan_fit = plan_fit if plan_fit is not None else load_plan_fit()
    rules = rules if rules is not None else load_rules(plan_fit=plan_fit)
    fired = fired if fired is not None else set()
    persona_path = Path(persona_dir)
    card_path = persona_path / _validate.CARD_FILE
    profile_path = (persona_path / ".." / ".." / _validate.PROFILE_FILE).resolve()
    card_bytes, profile_bytes = card_path.read_bytes(), profile_path.read_bytes()
    card, profile = json.loads(card_bytes.decode("utf-8")), json.loads(profile_bytes.decode("utf-8"))
    pack = _packs.load_pack(profile.get("industry"))

    run = _Run(rules, plan_fit, fired)
    persona = persona_facts(card, profile, pack, plan_fit, catalogue)
    tasks = card.get("tasks") or []
    task_ids = [task.get("id") for task in tasks]
    run.known = set(persona) | set(TASK_FACTS) | set(DECISION_FACTS) | set(TOOL_FACTS)

    blockers, warnings = [], []
    problems = override_problems(card.get("overrides"), task_ids)
    skipped = set(index for index, _ in problems)
    blockers.extend(item for _, item in problems)
    overrides = {}
    for index, override in enumerate(card.get("overrides") or []):
        key = (override.get("task"), override.get("decision"))
        if index not in skipped and key not in overrides:
            overrides[key] = override

    # Tasks, then the shared-tool fixed point: a task whose tool is shared with a task allowed less
    # is levelled again with the lower ceiling, until nothing changes.
    shared, differ = {}, []
    while True:
        run.open = {}
        states = _level_tasks(run, card, profile, pack, persona, overrides, shared)
        new, found = _shared_pass(run, states, shared)
        differ.extend(tool for tool in found if tool not in differ)
        if new == shared:
            break
        shared = new

    systems = _systems(profile, pack)
    tools_out = []
    tool_states = _tools(states)
    permissions = {}
    for tool in tool_states:
        per_task = []
        for tid in tool["tasks"]:
            start = states[tid]["decisions"]["autonomy.start"]["value"]
            result = _permission(run, states[tid], tool["use"], start)
            permissions[(tid, tool["system"], tool["use"])] = result
            per_task.append(result)
        order = rules["decisions"]["connectors.permission"]["order"]
        wanted = {}
        for tid in tool["tasks"]:
            level_ = _ceiling(states[tid])
            wanted[tid] = None if level_ is None else _permission(run, states[tid], tool["use"], level_)["value"]
        best = _strictest(per_task, order) or per_task[0]
        tools_out.append({"system": tool["system"], "use": tool["use"], "tasks": list(tool["tasks"]),
                          "permission": best, "wanted": wanted})

    tasks_out = {}
    for tid in task_ids:
        state = states[tid]
        facts = state["facts"]
        connectors = []
        for system, use in state["uses"]:
            access = "read" if use == "read" else "write"
            for entry in connectors:
                if entry["system"] == system:
                    if access == "write":
                        entry["access"] = "write"
                    break
            else:
                default = systems.get(system, {}).get("default")
                connectors.append({
                    "system": system, "access": access, "identity": state["connector_identity"]["value"],
                    "how": default.get("how") if default else None,
                    "runbook": default.get("runbook") if default else None,
                    "permission": None,
                    "cite": default.get("cite") if default else UNREACHED_CONNECTOR_CITE,
                    "unverified": bool(default.get("unverified")) if default else False})
        order = rules["decisions"]["connectors.permission"]["order"]
        for entry in connectors:
            results = [permissions[(tid, s, u)] for s, u in state["uses"] if s == entry["system"]]
            best = _strictest(results, order)
            entry["permission"] = best["value"] if best else None
        plan, undecided = run.decide("plan_fit", facts, tid)
        if undecided:
            state["undecided"].append(plan)
        facts["plan_fit"] = plan["value"]
        state["plan_fit"] = plan
        state["connectors"] = connectors

    # Blockers and warnings: the persona's, each task's, then each shared tool's (about its first task).
    raised = run.codes("persona", persona, "persona")
    for tid in task_ids:
        state = states[tid]
        for decision in state["undecided"]:
            warnings.append(_item("decision-undecided", tid, decision["cite"], decision["unverified"],
                                  decision["reason"],
                                  "Decide it with the customer and record the answer as an override on the card."))
        for target, decision in state["overrides"]:
            ov = decision["overridden"]
            warnings.append(_item(
                "override-applied", tid, decision["cite"], decision["unverified"],
                "A card override sets %s to %s; the rule's result was %s. Reason: %s Approved by: %s."
                % (target, json.dumps(decision["value"]), json.dumps(ov["rule_result"]), ov["reason"],
                   ov["approved_by"]),
                "Check the override still holds whenever the card changes; remove it to return to the rule."))
        found = run.codes("task", state["facts"], tid)
        raised.extend(found)
        # An overridden decision that an Unverified rule now warns about rests on that fact too.
        for rule, _ in found:
            if not rule["unverified"]:
                continue
            for name in _walk_decisions(rule["when"]):
                decision = state["decisions"].get(name)
                if decision is not None and decision["overridden"] is not None:
                    decision["unverified"] = True
    for tool in tool_states:
        first = tool["tasks"][0]
        facts = dict(states[first]["facts"])
        facts.update({"tool.use": tool["use"],
                      "tool.level": states[first]["decisions"]["autonomy.start"]["value"],
                      "tool.wanted_differs": (tool["system"], tool["use"]) in differ})
        raised.extend(run.codes("tool", facts, first))
    for rule, item in raised:
        (blockers if rule["decides"] == "blocker" else warnings).append(item)
    warnings.extend(run.open.values())

    plugin = _plugin_name(card, persona, persona_dir, catalogue)
    if not isinstance(plugin["value"], str) or not PLUGIN_NAME_PATTERN.match(plugin["value"]):
        blockers.append(_item(
            "plugin-name-invalid", "persona", "starter-kit/templates/role-plugin/README.md#steps", False,
            "The role plugin name %r does not match twin-<role> in lower-case kebab-case." % (plugin["value"],),
            "Set role.plugin_name to a name such as twin-<role>, or leave it empty to use twin-<persona id>."))
    distribution, undecided_d = run.decide("persona.distribution", persona, "persona")
    baseline, undecided_b = run.decide("persona.settings_baseline", persona, "persona")
    for decision, undecided in ((distribution, undecided_d), (baseline, undecided_b)):
        if undecided:
            warnings.append(_item("decision-undecided", "persona", decision["cite"], decision["unverified"],
                                  decision["reason"], "Decide it with the customer and record it in the design."))
    starting = [{"kind": p.get("kind"), "name": p.get("name"), "where": p.get("where"), "use": p.get("use"),
                 "cite": p.get("cite"), "unverified": p.get("unverified")}
                for p in pack.get("anthropic_starting_points") or []]

    rank = dict((tid, i + 1) for i, tid in enumerate(task_ids))
    blockers = _dedupe(sorted(blockers, key=lambda item: rank.get(item["about"], 0)))
    warnings = _dedupe(sorted(warnings, key=lambda item: rank.get(item["about"], 0)))

    pilot = set(task.get("id") for task in tasks if task.get("in_pilot"))
    blocked = any(set(q.get("blocks") or []) & pilot for q in card.get("open_questions") or [])
    complete = validation["ok"] and validation["completeness"]["percent"] == 100 and not blocked and not blockers

    tasks_json = {}
    for tid in task_ids:
        state = states[tid]
        d = state["decisions"]
        tasks_json[tid] = {
            "runtime": d["runtime"],
            "identity": d["identity"],
            "autonomy": {"start": d["autonomy.start"], "ceiling": d["autonomy.ceiling"]},
            "data_controls": dict((sub, d["data_controls." + sub]) for sub in DATA_CONTROLS),
            "connectors": state["connectors"],
            "memory": d["memory"],
            "plan_fit": state["plan_fit"],
        }
    levelled = {
        "levelled_version": LEVELLED_VERSION,
        "customer": card.get("customer"),
        "persona": card.get("id"),
        "source": {
            "card_sha256": hashlib.sha256(card_bytes).hexdigest(),
            "profile_sha256": hashlib.sha256(profile_bytes).hexdigest(),
            "rules_version": rules["rules_version"],
            "pack": pack.get("id"),
        },
        "persona_plan": {
            "plugin_name": plugin,
            "distribution": distribution,
            "settings_baseline": baseline,
            "starting_points": starting,
        },
        "tasks": tasks_json,
        "tools": tools_out,
        "blockers": blockers,
        "warnings": warnings,
        "complete": complete,
    }
    return {"ok": True, "validation": validation, "levelled": levelled}


def _dedupe(items):
    out, seen = [], set()
    for item in items:
        key = (item["code"], item["about"], item["message"] if item["code"] == "field-open" else None)
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def _plugin_name(card, persona, persona_dir, catalogue):
    value = persona["role.plugin_name"]
    entry = _fields.entry_for("card", "role.plugin_name", catalogue) or {}
    default_cite = (entry.get("default") or {}).get("source")
    if isinstance(value, str) and value:
        prov = (card.get("provenance") or {}).get("role.plugin_name") or {}
        source = prov.get("source")
        cite = _source_cite(persona_dir, source) if source else default_cite
        return _decision(value, None, cite, "The card names the role plugin %s in role.plugin_name." % value,
                         False, "our-recommendation")
    return _decision("twin-%s" % card.get("id"), None, default_cite,
                     "The card leaves role.plugin_name empty, so the engine uses the persona id as the role "
                     "in twin-<role> (design 4.2).", False, "our-recommendation")


def render(levelled):
    """levelled.json's text: keys in a fixed order, two-space indent, UTF-8, a trailing newline."""
    return json.dumps(levelled, indent=2, ensure_ascii=False) + "\n"


def write_levelled(persona_dir, **kwargs):
    """Level and write <persona_dir>/levelled.json; nothing is written when validation fails."""
    result = level(persona_dir, **kwargs)
    if result["ok"]:
        (Path(persona_dir) / LEVELLED_FILE).write_bytes(render(result["levelled"]).encode("utf-8"))
    return result
