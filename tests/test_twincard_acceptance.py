"""Acceptance checks for the two fictional persona-card fixtures and their expected levelling results.

The expected results live in tests/fixtures/twincard/expectations.json and were fixed before the
levelling engine exists. The vocabulary and the codes are in partner-kit/docs/design.md section 7.2.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / "partner-kit" / "plugins" / "twin-consultant"
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
CLI = SCRIPTS_DIR / "twincard" / "cli.py"
PACKS_DIR = PLUGIN_DIR / "data" / "industry-packs"
EXPECTATIONS = ROOT / "tests" / "fixtures" / "twincard" / "expectations.json"
DESIGN = ROOT / "partner-kit" / "docs" / "design.md"
SETTINGS_DIR = ROOT / "starter-kit" / "settings"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from twincard import fields as tc_fields  # noqa: E402
from twincard.validate import validate  # noqa: E402

DECISIONS = ("runtime", "identity", "autonomy.start", "autonomy.ceiling", "data_controls", "memory", "plan_fit")
RUNTIMES = {"client-skill", "claude-code-scheduled-task", "claude-tag-routine", "managed-agents",
            "managed-agents-self-hosted", "agent-sdk", "none"}
IDENTITIES = {"user", "service-account", "api-key-vault"}
PLAN_FITS = {"ok", "ok-with-limits", "needs-enterprise", "not-supported"}
DISTRIBUTIONS = {"group-targeted", "everyone"}
DASHBOARD_SECTIONS = ["Header", "Anatomy grid", "Feature list", "Blockers and warnings", "Backlog",
                      "Open questions", "Where each answer came from"]
FOUNDATION_STORIES = {"S-persona-voice", "S-connectors-and-identity", "S-guardrails-and-settings", "S-distribution",
                      "S-governance-log", "S-memory-policy", "S-pilot-rollout-and-scorecard"}
UNVERIFIED_MARKER = re.compile(r"unverified|not confirmed", re.IGNORECASE)
UNDECIDED = re.compile(r"undecided", re.IGNORECASE)


def slug(heading):
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = text.replace("`", "").replace("*", "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors_of(page_text):
    anchors, seen, in_fence = set(), {}, False
    for line in page_text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if not m:
            continue
        base = slug(m.group(1))
        n = seen.get(base, 0)
        anchors.add(base if n == 0 else "%s-%d" % (base, n))
        seen[base] = n + 1
    return anchors


def load_expectations():
    return json.loads(EXPECTATIONS.read_text(encoding="utf-8"))


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def card_of(fixture):
    return load_json(ROOT / fixture["persona_dir"] / "card.json")


def profile_of(fixture):
    return load_json((ROOT / fixture["persona_dir"] / ".." / ".." / "customer-profile.json").resolve())


def design_codes():
    text = DESIGN.read_text(encoding="utf-8")
    m = re.search(r"^### 7\.2 Decision values\n(.*?)^## 8\.", text, re.MULTILINE | re.DOTALL)
    if not m:
        return set()
    return set(re.findall(r"^- `([a-z0-9-]+)`: \S", m.group(1), re.MULTILINE))


def complete_flag(result, card):
    """Complete: valid, every required field answered or default, no open question blocks a pilot task."""
    pilot = {t.get("id") for t in card.get("tasks", []) if t.get("in_pilot")}
    blocked = any(set(q.get("blocks") or []) & pilot for q in card.get("open_questions", []))
    return bool(result["ok"]) and result["completeness"]["percent"] == 100 and not blocked


def all_decisions(exp):
    """Yield (where, decision) for every decision-shaped entry in the file."""
    for fid, fixture in exp["fixtures"].items():
        for name, d in fixture["persona"].items():
            yield "%s.persona.%s" % (fid, name), d
        for tid, decisions in fixture["tasks"].items():
            for name, d in decisions.items():
                yield "%s.%s.%s" % (fid, tid, name), d
    for variant in exp["variants"]:
        for name, d in variant["expect"]["decisions"].items():
            yield "variant %s: %s" % (variant["id"], name), d


def all_codes(exp):
    """Yield (where, blocker-or-warning) for every code entry in the file."""
    for fid, fixture in exp["fixtures"].items():
        for kind in ("blockers", "warnings"):
            for w in fixture[kind]:
                yield "%s.%s" % (fid, kind), w
    for variant in exp["variants"]:
        for kind in ("blockers_added", "blockers_removed", "warnings_added", "warnings_removed"):
            for w in variant["expect"][kind]:
                yield "variant %s: %s" % (variant["id"], kind), w


def all_cites(exp):
    for where, d in all_decisions(exp):
        yield where, d["cite"], d["unverified"]
    for where, w in all_codes(exp):
        yield where, w["cite"], w["unverified"]
    for variant in exp["variants"]:
        yield "variant %s" % variant["id"], variant["cite"], False
    for fid, fixture in exp["fixtures"].items():
        for item in fixture["backlog"]["must_have_tasks"]:
            yield "%s.backlog %s" % (fid, item["story"]), item["cite"], False


# --- Applying a variant's change --------------------------------------------------------------------

def _resolve(record, data, path, catalogue, create):
    """Walk an instance path such as tasks.C4.writes[1].action; return (parent, key, catalogue path)."""
    keys = catalogue["keys"][record]
    tokens = path.split(".")
    node, cat, i = data, [], 0
    while i < len(tokens):
        token = tokens[i]
        m = re.fullmatch(r"([A-Za-z_]+)\[(\d+)\]", token)
        name = m.group(1) if m else token
        list_path = ".".join(cat + [name])
        last = i == len(tokens) - 1
        if m:
            if list_path not in keys or keys[list_path] is not None:
                raise KeyError("%s is not a positional list" % list_path)
            items = node.setdefault(name, []) if create else node.get(name, [])
            index = int(m.group(2))
            if index == len(items) and create:
                items.append({})
            if index >= len(items):
                raise KeyError("%s has no item %d" % (list_path, index))
            node = items[index]
            cat.append(name + "[]")
            i += 1
        elif list_path in keys and keys[list_path] is not None and not last:
            key_field, wanted = keys[list_path], tokens[i + 1]
            matches = [item for item in node.get(name, []) if item.get(key_field) == wanted]
            if not matches:
                raise KeyError("%s has no item %s" % (list_path, wanted))
            node = matches[0]
            cat.append(name + "[]")
            i += 2
        elif last:
            return node, name, ".".join(cat + [name])
        else:
            node = node.setdefault(name, {}) if create else node[name]
            cat.append(name)
            i += 1
    raise KeyError("path %s ends on a list item" % path)


def apply_change(records, change, catalogue):
    """Apply one {record, path, value}; return the catalogue path it touches."""
    record, path, value = change["record"], change["path"], change["value"]
    data = records[record]
    if path.startswith("provenance."):
        rest = path[len("provenance."):]
        _, _, cat_path = _resolve(record, copy.deepcopy(data), rest, catalogue, create=False)
        data.setdefault("provenance", {})[rest] = value
        return cat_path
    parent, key, cat_path = _resolve(record, data, path, catalogue, create=True)
    parent[key] = value
    return cat_path


class ExpectationsFileTests(unittest.TestCase):
    def setUp(self):
        self.exp = load_expectations()

    def test_file_parses_with_both_fixtures(self):
        self.assertEqual(self.exp["expectations_version"], 1)
        self.assertEqual(set(self.exp["fixtures"]), {"pe", "team"})
        self.assertGreaterEqual(len(self.exp["variants"]), 5)

    def test_every_persona_dir_exists(self):
        for fid, fixture in self.exp["fixtures"].items():
            persona_dir = ROOT / fixture["persona_dir"]
            self.assertTrue((persona_dir / "card.json").is_file(), fid)
            self.assertTrue((persona_dir / ".." / ".." / "customer-profile.json").resolve().is_file(), fid)

    def test_both_profiles_are_fictional(self):
        for fid, fixture in self.exp["fixtures"].items():
            self.assertIs(profile_of(fixture).get("fictional"), True, fid)


class ValidateTests(unittest.TestCase):
    def test_validate_command_matches_expectations(self):
        for fid, fixture in load_expectations()["fixtures"].items():
            with self.subTest(fixture=fid):
                proc = subprocess.run(
                    [sys.executable, str(CLI), "validate", "--json", fixture["persona_dir"]],
                    capture_output=True, text=True, cwd=str(ROOT), timeout=60,
                )
                want = fixture["validate"]
                self.assertEqual(proc.returncode, want["exit"], proc.stdout + proc.stderr)
                result = json.loads(proc.stdout)
                self.assertEqual(result["completeness"]["percent"], want["completeness_pct"])
                self.assertEqual(complete_flag(result, card_of(fixture)), want["complete"])


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.exp = load_expectations()

    def test_every_card_task_has_all_decisions_and_no_extra_task(self):
        for fid, fixture in self.exp["fixtures"].items():
            card_tasks = {t["id"] for t in card_of(fixture)["tasks"]}
            self.assertEqual(set(fixture["tasks"]), card_tasks, fid)
            for tid, decisions in fixture["tasks"].items():
                self.assertEqual(set(decisions), set(DECISIONS) | {"connectors"}, "%s %s" % (fid, tid))

    def test_every_decision_has_the_four_fields(self):
        for where, d in all_decisions(self.exp):
            self.assertTrue({"expected", "cite", "reason", "unverified"} <= set(d), where)
            self.assertIsInstance(d["unverified"], bool, where)
            self.assertTrue(isinstance(d["reason"], str) and d["reason"].strip(), where)

    def check_value(self, where, name, value, systems, retentions):
        if name == "runtime":
            self.assertIn(value, RUNTIMES, where)
        elif name == "identity":
            self.assertIn(value, IDENTITIES, where)
        elif name in ("autonomy.start", "autonomy.ceiling"):
            self.assertIsInstance(value, int, where)
            self.assertTrue(0 <= value <= 4, where)
        elif name == "data_controls":
            self.assertEqual(set(value), {"settings_baseline", "web_tools", "surfaces", "retention"}, where)
            baseline = value["settings_baseline"]
            self.assertTrue(baseline is None or (SETTINGS_DIR / ("%s.managed-settings.json" % baseline)).is_file(), where)
            self.assertIn(value["web_tools"], {"on", "off"}, where)
            works_in = set(tc_fields.entry_for("card", "role.works_in")["values"])
            self.assertTrue(set(value["surfaces"]) <= works_in, where)
            self.assertIn(value["retention"], retentions, where)
        elif name == "connectors":
            for c in value:
                self.assertEqual(set(c), {"system", "access", "identity"}, where)
                self.assertIn(c["system"], systems, where)
                self.assertIn(c["access"], {"read", "write"}, where)
                self.assertIn(c["identity"], IDENTITIES, where)
        elif name == "memory":
            self.assertIn(value, {"on", "off"}, where)
        elif name == "plan_fit":
            self.assertIn(value, PLAN_FITS, where)
        elif name == "plugin_name":
            self.assertRegex(value, r"^twin-[a-z0-9-]+$", where)
        elif name == "distribution":
            self.assertIn(value, DISTRIBUTIONS, where)
        elif name == "settings_baseline":
            self.assertTrue(value is None or (SETTINGS_DIR / ("%s.managed-settings.json" % value)).is_file(), where)
        else:
            self.fail("%s: unknown decision %s" % (where, name))

    def test_every_value_is_in_the_vocabulary_or_undecided(self):
        retentions = set(tc_fields.entry_for("profile", "compliance.retention")["values"])
        for fid, fixture in self.exp["fixtures"].items():
            systems = {s["id"] for s in profile_of(fixture)["systems"]}
            entries = [("persona", n, d) for n, d in fixture["persona"].items()]
            entries += [(tid, n, d) for tid, ds in fixture["tasks"].items() for n, d in ds.items()]
            for variant in self.exp["variants"]:
                if variant["base"] == fid:
                    for key, d in variant["expect"]["decisions"].items():
                        tid, name = key.split(".", 1)
                        entries.append((tid, name, d))
            for tid, name, d in entries:
                where = "%s %s %s" % (fid, tid, name)
                if d["expected"] is None and name != "settings_baseline":
                    self.assertRegex(d["reason"], UNDECIDED, where)
                    continue
                if d["expected"] is None:
                    continue
                self.check_value(where, name, d["expected"], systems, retentions)

    def test_connectors_agree_with_the_pack_defaults(self):
        for fid, fixture in self.exp["fixtures"].items():
            pack = load_json(PACKS_DIR / ("%s.json" % fixture["pack"]))
            self.assertEqual(profile_of(fixture)["industry"], fixture["pack"], fid)
            defaults = {c["product"]: c for c in pack["connector_defaults"]}
            for tid, decisions in fixture["tasks"].items():
                d = decisions["connectors"]
                unverified = False
                for c in d["expected"]:
                    product = fixture["pack_products"].get(c["system"])
                    self.assertIn(product, defaults, "%s %s %s" % (fid, tid, c["system"]))
                    unverified = unverified or defaults[product]["unverified"]
                    if decisions["runtime"]["expected"] == "client-skill":
                        self.assertTrue(defaults[product]["identity"].startswith("Per user")
                                        or c["system"] == "usage-db", "%s %s" % (fid, tid))
                        self.assertEqual(c["identity"], "user", "%s %s" % (fid, tid))
                self.assertEqual(d["unverified"], unverified, "%s %s connectors" % (fid, tid))

    def test_plugin_name_follows_the_card(self):
        for fid, fixture in self.exp["fixtures"].items():
            card = card_of(fixture)
            given = card["role"].get("plugin_name")
            want = given if given else "twin-%s" % card["id"]
            self.assertEqual(fixture["persona"]["plugin_name"]["expected"], want, fid)

    def test_persona_baseline_agrees_with_the_pack(self):
        for fid, fixture in self.exp["fixtures"].items():
            pack = load_json(PACKS_DIR / ("%s.json" % fixture["pack"]))
            self.assertEqual(fixture["persona"]["settings_baseline"]["expected"], pack["settings_baseline"], fid)


class CiteTests(unittest.TestCase):
    def test_every_cite_resolves_and_unverified_only_where_marked(self):
        pages = {}
        for where, cite, unverified in all_cites(load_expectations()):
            self.assertIn("#", cite, where)
            path, anchor = cite.split("#", 1)
            page = ROOT / path
            self.assertTrue(page.is_file(), "%s: %s does not exist" % (where, path))
            if path not in pages:
                pages[path] = page.read_text(encoding="utf-8")
            self.assertIn(anchor, anchors_of(pages[path]), "%s: no heading for #%s in %s" % (where, anchor, path))
            if unverified:
                self.assertTrue(path.startswith("docs/compendium/"), where)
                self.assertRegex(pages[path], UNVERIFIED_MARKER, "%s: %s has no Unverified marker" % (where, path))

    def test_decision_and_code_cites_are_compendium_pages(self):
        exp = load_expectations()
        for where, d in all_decisions(exp):
            if where.endswith("plugin_name"):
                continue
            self.assertTrue(d["cite"].startswith("docs/compendium/"), where)
        for where, w in all_codes(exp):
            self.assertTrue(w["cite"].startswith("docs/compendium/"), where)


class CodeTests(unittest.TestCase):
    def test_every_code_is_listed_in_design(self):
        listed = design_codes()
        self.assertTrue(listed, "design.md section 7.2 lists no codes")
        exp = load_expectations()
        for where, w in all_codes(exp):
            self.assertEqual(set(w), {"code", "about", "cite", "unverified"}, where)
            self.assertIn(w["code"], listed, where)
            self.assertRegex(w["code"], r"^[a-z0-9]+(-[a-z0-9]+)*$", where)

    def test_every_code_is_about_a_task_or_the_persona(self):
        exp = load_expectations()
        tasks = {fid: {t["id"] for t in card_of(f)["tasks"]} for fid, f in exp["fixtures"].items()}
        for fid, fixture in exp["fixtures"].items():
            for kind in ("blockers", "warnings"):
                for w in fixture[kind]:
                    self.assertIn(w["about"], tasks[fid] | {"persona"}, fid)
        for variant in exp["variants"]:
            for kind in ("blockers_added", "blockers_removed", "warnings_added", "warnings_removed"):
                for w in variant["expect"][kind]:
                    self.assertIn(w["about"], tasks[variant["base"]] | {"persona"}, variant["id"])

    def test_removed_codes_exist_in_the_base(self):
        exp = load_expectations()
        for variant in exp["variants"]:
            base = exp["fixtures"][variant["base"]]
            for kind, base_kind in (("blockers_removed", "blockers"), ("warnings_removed", "warnings")):
                for w in variant["expect"][kind]:
                    self.assertIn(w, base[base_kind], variant["id"])


class VariantTests(unittest.TestCase):
    def test_variants_apply_and_validate_as_expected(self):
        exp = load_expectations()
        catalogue = tc_fields.load_catalogue()
        ids = [v["id"] for v in exp["variants"]]
        self.assertEqual(len(ids), len(set(ids)))
        for variant in exp["variants"]:
            with self.subTest(variant=variant["id"]):
                self.assertIn(variant["base"], exp["fixtures"])
                self.assertTrue(variant["reason"].strip())
                fixture = exp["fixtures"][variant["base"]]
                persona_dir = ROOT / fixture["persona_dir"]
                engagement = persona_dir.parent.parent
                expect = variant["expect"]
                self.assertTrue({"decisions", "blockers_added", "blockers_removed", "warnings_added",
                                 "warnings_removed", "still_valid"} <= set(expect))
                self.assertTrue(expect["decisions"] or expect["blockers_added"] or expect["warnings_added"]
                                or expect["blockers_removed"] or expect["warnings_removed"])
                for key in expect["decisions"]:
                    tid, name = key.split(".", 1)
                    self.assertIn(name, DECISIONS + ("connectors",))
                    self.assertIn(tid, fixture["tasks"])
                with tempfile.TemporaryDirectory() as tmp:
                    copy_root = Path(tmp) / engagement.name
                    shutil.copytree(engagement, copy_root)
                    copy_persona = copy_root / persona_dir.relative_to(engagement)
                    records = {"profile": load_json(copy_root / "customer-profile.json"),
                               "card": load_json(copy_persona / "card.json")}
                    for change in variant["change"]:
                        cat_path = apply_change(records, change, catalogue)
                        self.assertIsNotNone(tc_fields.entry_for(change["record"], cat_path, catalogue),
                                             "%s is not in the catalogue" % cat_path)
                    (copy_root / "customer-profile.json").write_text(json.dumps(records["profile"]), encoding="utf-8")
                    (copy_persona / "card.json").write_text(json.dumps(records["card"]), encoding="utf-8")
                    result = validate(copy_persona, catalogue)
                self.assertEqual(result["ok"], expect["still_valid"], result["errors"])

    def test_override_variant_shows_the_rule_result_and_reason(self):
        found = False
        for variant in load_expectations()["variants"]:
            for key, d in variant["expect"]["decisions"].items():
                if d.get("overridden"):
                    found = True
                    self.assertIn("rule_result", d, variant["id"])
                    self.assertTrue(d.get("override_reason"), variant["id"])
                    self.assertNotEqual(d["rule_result"], d["expected"], variant["id"])
        self.assertTrue(found, "no variant overrides a rule result")


class BacklogAndDashboardTests(unittest.TestCase):
    def test_backlog_ids_follow_the_card(self):
        for fid, fixture in load_expectations()["fixtures"].items():
            card = card_of(fixture)
            backlog = fixture["backlog"]
            self.assertTrue(backlog["epic"].startswith(card["role"]["name"] + " twin for "), fid)
            features = {"F-" + f["id"] for f in card["features"]} | {"F-twin-foundation"}
            self.assertEqual(set(backlog["feature_ids"]), features, fid)
            stories = {"S-" + t["id"] for t in card["tasks"]} | FOUNDATION_STORIES
            self.assertEqual(set(backlog["story_ids"]), stories, fid)
            must = backlog["must_have_tasks"]
            self.assertGreaterEqual(len({m["story"] for m in must}), 3, fid)
            for m in must:
                self.assertIn(m["story"], stories, fid)
                self.assertTrue(m["task"].strip(), fid)

    def test_dashboard_shows_every_code_and_unverified_item(self):
        for fid, fixture in load_expectations()["fixtures"].items():
            dash = fixture["dashboard"]
            self.assertEqual(dash["sections"], DASHBOARD_SECTIONS, fid)
            codes = {w["code"] for w in fixture["blockers"] + fixture["warnings"]}
            self.assertEqual(set(dash["must_show"]["codes"]), codes, fid)
            unverified = {"%s.%s" % (tid, n) for tid, ds in fixture["tasks"].items() for n, d in ds.items()
                          if d["unverified"]}
            unverified |= {"%s:%s" % (w["code"], w["about"]) for w in fixture["blockers"] + fixture["warnings"]
                           if w["unverified"]}
            self.assertEqual(set(dash["must_show"]["unverified"]), unverified, fid)


class FixtureRecordTests(unittest.TestCase):
    def test_interview_provenance_names_a_file_with_that_question(self):
        # validate opens every answered source (design 4.3); tests/test_twincard_sources.py has the cases.
        for fid, fixture in load_expectations()["fixtures"].items():
            self.assertEqual(validate(str(ROOT / fixture["persona_dir"]))["errors"], [], fid)

    def test_no_sample_pe_stakeholder_appears_under_sample_team_cs(self):
        text = (ROOT / "engagements" / "sample-pe" / "stakeholders.md").read_text(encoding="utf-8")
        names, name_col = set(), None
        for line in text.splitlines():
            if not line.startswith("|"):
                name_col = None
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if "Name (invented)" in cells:
                name_col = cells.index("Name (invented)")
                continue
            if name_col is not None and name_col < len(cells):
                if re.fullmatch(r"[A-Z][a-z]+(?:[ -][A-Z][a-z]+)+", cells[name_col]):
                    names.add(cells[name_col])
        self.assertGreaterEqual(len(names), 10)
        for path in (ROOT / "engagements" / "sample-team-cs").rglob("*"):
            if path.is_file():
                body = path.read_text(encoding="utf-8")
                for name in names:
                    self.assertNotIn(name, body, "%s names %s" % (path, name))


# --- Levelling: levelled.json against the expectations ---------------------------------------------

def _levelled_decision(levelled, tid, name):
    node = levelled["tasks"][tid]
    for part in name.split("."):
        node = node[part]
    return node


def _items(levelled, kind):
    return {(w["code"], w["about"]): {"code": w["code"], "about": w["about"], "cite": w["cite"],
                                      "unverified": w["unverified"]} for w in levelled[kind]}


class LevelTests(unittest.TestCase):
    """The levelling engine (scripts/twincard/level.py) reproduces tests/fixtures/twincard/expectations.json."""

    @classmethod
    def setUpClass(cls):
        from twincard import level as tc_level
        cls.engine = tc_level
        cls.exp = load_expectations()
        cls.out = {}
        for fid, fixture in cls.exp["fixtures"].items():
            cls.out[fid] = tc_level.level(str(ROOT / fixture["persona_dir"]))["levelled"]

    def check_decision(self, where, got, want):
        """got is a levelled decision, the data_controls dict or a connectors list; want is from the file."""
        if isinstance(got, list):
            self.assertEqual([{k: c[k] for k in ("system", "access", "identity")} for c in got], want["expected"], where)
            self.assertEqual(any(c["unverified"] for c in got), want["unverified"], where)
            return
        if "value" not in got:
            self.assertEqual({k: d["value"] for k, d in got.items()}, want["expected"], where)
            self.assertIn(want["cite"], [d["cite"] for d in got.values()], where)
            self.assertEqual(any(d["unverified"] for d in got.values()), want["unverified"], where)
            return
        self.assertEqual(got["value"], want["expected"], where)
        self.assertEqual(got["cite"], want["cite"], where)
        self.assertEqual(got["unverified"], want["unverified"], where)
        if want.get("overridden"):
            self.assertIsNotNone(got["overridden"], where)
            self.assertEqual(got["overridden"]["rule_result"], want["rule_result"], where)
            self.assertEqual(got["overridden"]["reason"], want["override_reason"], where)

    def test_task_decisions_match(self):
        for fid, fixture in self.exp["fixtures"].items():
            levelled = self.out[fid]
            self.assertIsNotNone(levelled, fid)
            self.assertEqual(list(levelled["tasks"]), [t["id"] for t in card_of(fixture)["tasks"]], fid)
            for tid, decisions in fixture["tasks"].items():
                for name, want in decisions.items():
                    self.check_decision("%s %s %s" % (fid, tid, name), _levelled_decision(levelled, tid, name), want)

    def test_persona_plan_matches(self):
        for fid, fixture in self.exp["fixtures"].items():
            for name, want in fixture["persona"].items():
                self.check_decision("%s persona %s" % (fid, name), self.out[fid]["persona_plan"][name], want)

    def test_blockers_and_warnings_match(self):
        for fid, fixture in self.exp["fixtures"].items():
            for kind in ("blockers", "warnings"):
                want = {(w["code"], w["about"]): w for w in fixture[kind]}
                self.assertEqual(_items(self.out[fid], kind), want, "%s %s" % (fid, kind))

    def test_complete_flag_matches(self):
        for fid, fixture in self.exp["fixtures"].items():
            self.assertEqual(self.out[fid]["complete"], fixture["validate"]["complete"], fid)

    def test_committed_levelled_json_is_current(self):
        for fid, fixture in self.exp["fixtures"].items():
            path = ROOT / fixture["persona_dir"] / self.engine.LEVELLED_FILE
            self.assertTrue(path.is_file(), "%s: run cli.py level %s" % (fid, fixture["persona_dir"]))
            self.assertEqual(path.read_text(encoding="utf-8"), self.engine.render(self.out[fid]),
                             "%s: levelled.json is stale; run cli.py level %s" % (fid, fixture["persona_dir"]))

    def test_level_command_exit_codes(self):
        for fid, fixture in self.exp["fixtures"].items():
            with self.subTest(fixture=fid), tempfile.TemporaryDirectory() as tmp:
                persona_dir = ROOT / fixture["persona_dir"]
                engagement = persona_dir.parent.parent
                copy_root = Path(tmp) / engagement.name
                shutil.copytree(engagement, copy_root)
                copy_persona = copy_root / persona_dir.relative_to(engagement)
                proc = subprocess.run([sys.executable, str(CLI), "level", "--json", str(copy_persona)],
                                      capture_output=True, text=True, cwd=str(ROOT), timeout=60)
                want = 1 if fixture["blockers"] else 0
                self.assertEqual(proc.returncode, want, proc.stdout + proc.stderr)
                self.assertEqual(json.loads(proc.stdout)["complete"], fixture["validate"]["complete"], fid)

    def test_variants_change_what_they_expect(self):
        catalogue = tc_fields.load_catalogue()
        for variant in self.exp["variants"]:
            with self.subTest(variant=variant["id"]):
                fixture = self.exp["fixtures"][variant["base"]]
                base = self.out[variant["base"]]
                persona_dir = ROOT / fixture["persona_dir"]
                engagement = persona_dir.parent.parent
                with tempfile.TemporaryDirectory() as tmp:
                    copy_root = Path(tmp) / engagement.name
                    shutil.copytree(engagement, copy_root)
                    copy_persona = copy_root / persona_dir.relative_to(engagement)
                    records = {"profile": load_json(copy_root / "customer-profile.json"),
                               "card": load_json(copy_persona / "card.json")}
                    for change in variant["change"]:
                        apply_change(records, change, catalogue)
                    (copy_root / "customer-profile.json").write_text(json.dumps(records["profile"]), encoding="utf-8")
                    (copy_persona / "card.json").write_text(json.dumps(records["card"]), encoding="utf-8")
                    result = self.engine.level(str(copy_persona))
                self.assertEqual(result["ok"], variant["expect"]["still_valid"], result["validation"]["errors"])
                levelled = result["levelled"]
                expect = variant["expect"]
                for key, want in expect["decisions"].items():
                    tid, name = key.split(".", 1)
                    self.check_decision("%s %s" % (variant["id"], key), _levelled_decision(levelled, tid, name), want)
                for kind in ("blockers", "warnings"):
                    before, after = _items(base, kind), _items(levelled, kind)
                    added = {k: v for k, v in after.items() if k not in before}
                    removed = {k: v for k, v in before.items() if k not in after}
                    self.assertEqual(added, {(w["code"], w["about"]): w for w in expect[kind + "_added"]},
                                     "%s %s added" % (variant["id"], kind))
                    self.assertEqual(removed, {(w["code"], w["about"]): w for w in expect[kind + "_removed"]},
                                     "%s %s removed" % (variant["id"], kind))


# --- Backlog: backlog.json against the expectations -------------------------------------------------

class BacklogBuildTests(unittest.TestCase):
    """The backlog builder (scripts/twincard/backlog.py) reproduces the backlog part of expectations.json."""

    @classmethod
    def setUpClass(cls):
        from twincard import backlog as tc_backlog
        cls.engine = tc_backlog
        cls.exp = load_expectations()
        cls.out = {}
        for fid, fixture in cls.exp["fixtures"].items():
            cls.out[fid] = tc_backlog.build(str(ROOT / fixture["persona_dir"]))

    def stories(self, fid):
        return [s for f in self.out[fid]["backlog"]["epic"]["features"] for s in f["stories"]]

    def test_build_succeeds(self):
        for fid in self.exp["fixtures"]:
            self.assertTrue(self.out[fid]["ok"], "%s: %s" % (fid, self.out[fid]["error"]))

    def test_epic_title_matches(self):
        for fid, fixture in self.exp["fixtures"].items():
            self.assertEqual(self.out[fid]["backlog"]["epic"]["title"], fixture["backlog"]["epic"], fid)

    def test_feature_ids_match_in_order(self):
        for fid, fixture in self.exp["fixtures"].items():
            got = [f["id"] for f in self.out[fid]["backlog"]["epic"]["features"]]
            self.assertEqual(got, fixture["backlog"]["feature_ids"], fid)

    def test_story_ids_match(self):
        # Compared as a set: stories sort in-pilot first, then by priority, inside their feature,
        # while the expectations list them in card order.
        for fid, fixture in self.exp["fixtures"].items():
            got = [s["id"] for s in self.stories(fid)]
            self.assertEqual(len(got), len(set(got)), fid)
            self.assertEqual(set(got), set(fixture["backlog"]["story_ids"]), fid)

    def test_must_have_tasks_are_present(self):
        for fid, fixture in self.exp["fixtures"].items():
            by_id = {s["id"]: s for s in self.stories(fid)}
            for m in fixture["backlog"]["must_have_tasks"]:
                titles = [t["title"].lower() for t in by_id[m["story"]]["tasks"]]
                self.assertTrue(any(m["task"].lower() in title for title in titles),
                                "%s %s: no task titled like %r in %s" % (fid, m["story"], m["task"], titles))

    def test_committed_backlog_files_are_current(self):
        for fid, fixture in self.exp["fixtures"].items():
            persona_dir = ROOT / fixture["persona_dir"]
            backlog = self.out[fid]["backlog"]
            for name, body in ((self.engine.BACKLOG_JSON, self.engine.render_json(backlog)),
                               (self.engine.BACKLOG_MD, self.engine.render_md(backlog, str(persona_dir)))):
                path = persona_dir / name
                self.assertTrue(path.is_file(), "%s: run cli.py backlog %s" % (fid, fixture["persona_dir"]))
                self.assertEqual(path.read_bytes(), body.encode("utf-8"),
                                 "%s: %s is stale; run cli.py backlog %s" % (fid, name, fixture["persona_dir"]))

    def test_no_in_pilot_story_is_gated_by_a_blocker(self):
        for fid in self.exp["fixtures"]:
            for story in self.stories(fid):
                if story["in_pilot"]:
                    kinds = [g["kind"] for g in story["gated_by"]]
                    self.assertNotIn("blocker", kinds, "%s %s" % (fid, story["id"]))


class _DashboardMarks(HTMLParser):
    """The data- marks on a dashboard page, and the text of each data-field element."""

    VOID = {"meta", "br", "hr", "img", "input", "link", "wbr", "col", "area", "base", "source", "track", "embed"}

    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.sections, self.codes, self.decisions, self.unverified, self.fields = [], [], {}, [], {}
        self._open = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "data-section" in a:
            self.sections.append(a["data-section"])
        if "data-code" in a:
            self.codes.append((a["data-code"], a.get("data-about"), a.get("data-unverified") == "true"))
        if "data-decision" in a:
            self.decisions[a["data-decision"]] = a.get("data-unverified") == "true"
        if "data-unverified" in a:
            self.unverified.append(a.get("data-decision") or "%s:%s" % (a.get("data-code"), a.get("data-about")))
        if tag in self.VOID:
            return
        self._open.append((tag, a.get("data-field")))
        if a.get("data-field"):
            self.fields.setdefault(a["data-field"], "")

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        while self._open:
            name, _ = self._open.pop()
            if name == tag:
                break

    def handle_data(self, data):
        for _, field in self._open:
            if field:
                self.fields[field] += data


class DashboardAcceptanceTests(unittest.TestCase):
    """The committed dashboard.html of each fixture against expectations.json (dashboard, validate)."""

    DATE = "2026-11-15"

    @classmethod
    def setUpClass(cls):
        from twincard import dashboard
        cls.engine = dashboard
        cls.exp = load_expectations()
        cls.pages = {}
        for fid, fixture in cls.exp["fixtures"].items():
            path = ROOT / fixture["persona_dir"] / dashboard.DASHBOARD_FILE
            cls.pages[fid] = path.read_text(encoding="utf-8") if path.is_file() else ""

    def marks(self, fid):
        parser = _DashboardMarks()
        parser.feed(self.pages[fid])
        parser.close()
        return parser

    def test_sections_are_the_expected_ones_in_order(self):
        for fid, fixture in self.exp["fixtures"].items():
            self.assertEqual(self.marks(fid).sections, fixture["dashboard"]["sections"], fid)

    def test_every_must_show_code_is_an_entry(self):
        for fid, fixture in self.exp["fixtures"].items():
            shown = {code for code, _, _ in self.marks(fid).codes}
            for code in fixture["dashboard"]["must_show"]["codes"]:
                self.assertIn(code, shown, "%s: %s is not shown as a data-code" % (fid, code))

    def test_unverified_marks_are_exactly_the_expected_ones(self):
        for fid, fixture in self.exp["fixtures"].items():
            page = self.marks(fid)
            expected = fixture["dashboard"]["must_show"]["unverified"]
            for item in expected:
                if ":" in item:
                    code, about = item.split(":", 1)
                    self.assertIn((code, about, True), page.codes, "%s: %s is not marked unverified" % (fid, item))
                else:
                    self.assertIn(item, page.decisions, "%s: no data-decision cell for %s" % (fid, item))
                    self.assertTrue(page.decisions[item], "%s: %s is not marked unverified" % (fid, item))
            self.assertEqual(sorted(page.unverified), sorted(expected),
                             "%s: the page marks something else unverified" % fid)

    def test_header_shows_completeness_and_the_complete_flag(self):
        for fid, fixture in self.exp["fixtures"].items():
            fields = self.marks(fid).fields
            self.assertEqual(fields.get("completeness", "").strip(), "%d%%" % fixture["validate"]["completeness_pct"],
                             fid)
            word = "Complete" if fixture["validate"]["complete"] else "Not complete"
            self.assertEqual(fields.get("complete", "").strip(), word, fid)

    def test_committed_dashboard_is_current(self):
        for fid, fixture in self.exp["fixtures"].items():
            persona_dir = ROOT / fixture["persona_dir"]
            page = self.engine.render(str(persona_dir), self.DATE)
            self.assertTrue(self.pages[fid], "%s: run cli.py dashboard %s --date %s"
                            % (fid, fixture["persona_dir"], self.DATE))
            self.assertEqual(self.pages[fid], page, "%s: dashboard.html is stale; run cli.py dashboard %s --date %s"
                             % (fid, fixture["persona_dir"], self.DATE))


if __name__ == "__main__":
    unittest.main()

# Later cards add their checks for levelled.json, backlog.json and dashboard.html in this file,
# next to the checks above. They compare the engine's output with tests/fixtures/twincard/expectations.json
# and may not edit tests/fixtures/twincard/expectations.json: if a page changes a result, a new card
# changes the fixture on purpose, with the page that moved it.
