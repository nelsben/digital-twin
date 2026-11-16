#!/usr/bin/env python3
"""Scratch-org dry run of the wall test (Salesforce record-access cases).

Replays the API-level cases of engagements/sample-pe/wall-test-protocol.md
(WT-01 to WT-16) as a test user on each side of a two-role scratch org,
deploys the kit's twin-marker metadata, and runs the UserRecordAccess
HasEditAccess query from the CRM-update skill's level-2-writes.md as each test
user. Then it prints a pass or fail table and deletes the scratch org.

    python3 wall_test.py <dev-hub-alias> [--keep-org] [--stages a,b,c]

The Dev Hub alias is an argument and is never stored. Python 3 standard library
plus the Salesforce CLI (`sf`). See README.md.

Safety: every sf call except the scratch-org create and `sf org list` must name
--target-org as the scratch org or one of the two test-user aliases below.
Anything else raises before the CLI runs.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT_DIR = HERE.parent  # starter-kit/connectors/salesforce, holds the marker force-app
ORG = "twin-wall-test"
USER_ALIAS = {"D": "twin-wall-d", "I": "twin-wall-i"}
ALLOWED_TARGETS = {ORG, USER_ALIAS["D"], USER_ALIAS["I"]}
ROLE_NAME = {"D": "Deal Team", "I": "Investor Relations"}
USER_LAST = {"D": "WALLTEST-D-USER", "I": "WALLTEST-I-USER"}
OTHER = {"D": "I", "I": "D"}
TOKEN_RE = {"D": re.compile(r"ZD[A-Z0-9]{6}"), "I": re.compile(r"ZI[A-Z0-9]{6}")}
STAGES = ["setup", "cases", "marker", "delete"]


# ---------------------------------------------------------------- sf wrapper

def _flag(args, names):
    for i, a in enumerate(args):
        if a in names and i + 1 < len(args):
            return args[i + 1]
    return None


def guard(args):
    """Refuse any sf call that could reach an org other than the scratch org."""
    if args[:3] == ["org", "create", "scratch"]:
        return
    if args[:2] == ["org", "list"]:
        return
    target = _flag(args, ("--target-org", "-o"))
    if target not in ALLOWED_TARGETS:
        raise SystemExit("refused: sf %s has target %r, not the scratch org or a test user"
                         % (" ".join(args[:3]), target))


def sf(args, cwd=None, timeout=1200):
    """Run `sf <args> --json` and return the parsed JSON (status 0 is success)."""
    guard(args)
    try:
        p = subprocess.run(["sf"] + args + ["--json"], capture_output=True, text=True,
                           cwd=cwd, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"status": 1, "name": "Timeout", "message": "sf %s timed out" % " ".join(args[:3])}
    try:
        return json.loads(p.stdout)
    except ValueError:
        return {"status": 1, "name": "NoJson", "message": (p.stdout + p.stderr)[-1500:]}


def err_text(res):
    return "%s: %s" % (res.get("name", "error"), str(res.get("message", ""))[:600])


def org_in_list(alias):
    res = sf(["org", "list"])
    if res.get("status") != 0:
        return False
    rows = res.get("result", {}).get("scratchOrgs", []) + res.get("result", {}).get("nonScratchOrgs", [])
    return any(r.get("alias") == alias and not r.get("isExpired") for r in rows)


def query(alias, soql):
    """SOQL as the user behind alias. Returns ok, records, total, err."""
    res = sf(["data", "query", "--query", soql, "--target-org", alias])
    if res.get("status") == 0:
        r = res["result"]
        recs = [{k: v for k, v in rec.items() if k != "attributes"} for rec in r.get("records", [])]
        return {"ok": True, "records": recs, "total": r.get("totalSize", len(recs)), "err": ""}
    return {"ok": False, "records": [], "total": 0, "err": err_text(res)}


def search(alias, sosl):
    res = sf(["data", "search", "--query", sosl, "--target-org", alias])
    if res.get("status") == 0:
        recs = [{k: v for k, v in rec.items() if k != "attributes"}
                for rec in res["result"].get("searchRecords", [])]
        return {"ok": True, "records": recs, "total": len(recs), "err": ""}
    return {"ok": False, "records": [], "total": 0, "err": err_text(res)}


# ----------------------------------------------------------------- reporting

ROWS = []  # (case id, actor, what it checks, PASS|FAIL|NOT RUN, detail)
EXTRA = []  # (label, value) lines for the marker and access sections


def add(case_id, actor, what, status, detail=""):
    ROWS.append((case_id, actor, what, status, detail))


def log(msg):
    print(msg, flush=True)


# --------------------------------------------------------------------- setup

def write_json(directory, name, data):
    path = Path(directory) / name
    path.write_text(json.dumps(data, indent=2))
    return str(path)


def stage_setup(dev_hub, tmp):
    if org_in_list(ORG):
        log("setup: scratch org %s already exists, reusing it" % ORG)
    else:
        log("setup: creating scratch org %s (Enterprise, 3 days)" % ORG)
        res = sf(["org", "create", "scratch", "--definition-file", str(HERE / "config" / "project-scratch-def.json"),
                  "--alias", ORG, "--target-dev-hub", dev_hub, "--duration-days", "3",
                  "--no-track-source", "--wait", "20"], cwd=str(HERE))
        if res.get("status") != 0:
            raise SystemExit("scratch org create failed, stopping. Error: " + err_text(res))
    res = sf(["project", "deploy", "start", "--source-dir", "force-app", "--target-org", ORG, "--wait", "20"],
             cwd=str(HERE))
    if res.get("status") != 0:
        raise SystemExit("setup metadata deploy failed. Error: " + err_text(res)
                         + " " + json.dumps(res.get("result", {}).get("details", {}).get("componentFailures", []))[:800])
    log("setup: roles and private sharing deployed")

    roles = query(ORG, "SELECT Id, Name, ParentRoleId FROM UserRole WHERE Name IN ('Deal Team','Investor Relations')")
    if not roles["ok"] or len(roles["records"]) != 2:
        raise SystemExit("setup: roles not found. " + roles["err"])
    for r in roles["records"]:
        if r["ParentRoleId"] is not None:
            raise SystemExit("setup: role %s has a parent role, so the hierarchy is not flat" % r["Name"])
    role_id = {side: next(r["Id"] for r in roles["records"] if r["Name"] == ROLE_NAME[side]) for side in "DI"}
    log("setup: Deal Team and Investor Relations both sit at the top of the hierarchy")

    for side in "DI":
        have = query(ORG, "SELECT Id FROM User WHERE LastName = '%s'" % USER_LAST[side])
        auth = sf(["org", "display", "--target-org", USER_ALIAS[side]])
        if have["ok"] and have["records"] and auth.get("status") == 0:
            continue
        if have["ok"] and have["records"]:
            raise SystemExit("setup: user %s exists but its CLI alias is gone; delete the scratch org and rerun"
                             % USER_LAST[side])
        definition = write_json(tmp, "user-%s.json" % side, {
            "Username": "walltest.%s.user@twinwalltest.example" % side.lower(),
            "LastName": USER_LAST[side],
            "FirstName": "Test",
            "Email": "walltest-%s@example.com" % side.lower(),
            "Alias": "wt%s" % side.lower(),
            "ProfileName": "Standard User",
            "UserRoleId": role_id[side],
            "generatePassword": False,
        })
        res = sf(["org", "create", "user", "--definition-file", definition, "--set-alias", USER_ALIAS[side],
                  "--set-unique-username", "--target-org", ORG])
        if res.get("status") != 0:
            raise SystemExit("setup: creating user %s failed. Error: %s" % (USER_LAST[side], err_text(res)))
    log("setup: one test user per role, profile Standard User, no admin rights")

    users = query(ORG, "SELECT Id, LastName FROM User WHERE LastName IN ('WALLTEST-D-USER','WALLTEST-I-USER')")
    owner = {side: next(u["Id"] for u in users["records"] if u["LastName"] == USER_LAST[side]) for side in "DI"}
    seed(owner, tmp)


def token():
    import secrets
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(6))


def seed(owner, tmp):
    """Wipe any WALLTEST records, then insert invented records on each side, owned by that side's user."""
    lines = [
        "delete [SELECT Id FROM Task WHERE Subject LIKE 'WALLTEST-%'];",
        "delete [SELECT Id FROM Opportunity WHERE Name LIKE 'WALLTEST-%'];",
        "delete [SELECT Id FROM Contact WHERE LastName LIKE 'WALLTEST-%'];",
        "delete [SELECT Id FROM Account WHERE Name LIKE 'WALLTEST-%'];",
    ]
    for side in "DI":
        t = {k: "Z%s%s" % (side, token()) for k in ("account", "contact", "opp1", "opp2", "task")}
        s, o = side, owner[side]
        lines += [
            "{",
            "Account a = new Account(Name='WALLTEST-%s-ACCOUNT', OwnerId='%s', Description='Invented record, Project Larch. Content token %s');" % (s, o, t["account"]),
            "insert a;",
            "Contact c = new Contact(LastName='WALLTEST-%s-CONTACT', FirstName='Test', AccountId=a.Id, Email='%s@example.com');" % (s, t["contact"]),
            "insert c;",
            "Opportunity o1 = new Opportunity(Name='WALLTEST-%s-OPP-1', OwnerId='%s', AccountId=a.Id, StageName='Prospecting', CloseDate=Date.today().addDays(30), Description='Invented record, Project Larch. Content token %s');" % (s, o, t["opp1"]),
            "Opportunity o2 = new Opportunity(Name='WALLTEST-%s-%s', OwnerId='%s', AccountId=a.Id, StageName='Prospecting', CloseDate=Date.today().addDays(30), Description='Invented second opportunity. Content token %s');" % (s, t["opp2"], o, t["opp2"]),
            "insert new List<Opportunity>{o1, o2};",
            "insert new Task(Subject='WALLTEST-%s-ACTIVITY', WhatId=o1.Id, OwnerId='%s', Status='Not Started', Description='Invented activity. Content token %s');" % (s, o, t["task"]),
            "}",
        ]
    path = Path(tmp) / "seed.apex"
    path.write_text("\n".join(lines))
    res = sf(["apex", "run", "--file", str(path), "--target-org", ORG])
    ok = res.get("status") == 0 and res.get("result", {}).get("success")
    if not ok:
        raise SystemExit("setup: seeding failed. Error: " + err_text(res) + " " + json.dumps(res.get("result", {}))[:800])
    log("setup: seeded 5 invented records on each side (2 opportunities, account, contact, task)")


# ------------------------------------------------------------ discover seeds

def discover():
    """As the scratch org admin (the conductor), read each side's ids and content tokens."""
    seeds = {side: {"ids": {}, "tokens": {}} for side in "DI"}
    q = {
        "opp": query(ORG, "SELECT Id, Name, Description FROM Opportunity WHERE Name LIKE 'WALLTEST-%'"),
        "acct": query(ORG, "SELECT Id, Name, Description FROM Account WHERE Name LIKE 'WALLTEST-%'"),
        "con": query(ORG, "SELECT Id, LastName, Email FROM Contact WHERE LastName LIKE 'WALLTEST-%'"),
        "task": query(ORG, "SELECT Id, Subject, Description FROM Task WHERE Subject LIKE 'WALLTEST-%'"),
    }
    for k, r in q.items():
        if not r["ok"]:
            raise SystemExit("discover: %s query failed. %s" % (k, r["err"]))
    for side in "DI":
        pre = "WALLTEST-%s-" % side
        tok = TOKEN_RE[side]
        for r in q["opp"]["records"]:
            if r["Name"] == pre + "OPP-1":
                seeds[side]["ids"]["opp1"] = r["Id"]
                seeds[side]["tokens"]["opp1"] = tok.search(r["Description"]).group(0)
            elif r["Name"].startswith(pre):
                seeds[side]["ids"]["opp2"] = r["Id"]
                seeds[side]["tokens"]["opp2"] = tok.search(r["Name"]).group(0)
        for r in q["acct"]["records"]:
            if r["Name"] == pre + "ACCOUNT":
                seeds[side]["ids"]["account"] = r["Id"]
                seeds[side]["tokens"]["account"] = tok.search(r["Description"]).group(0)
        for r in q["con"]["records"]:
            if r["LastName"] == pre + "CONTACT":
                seeds[side]["ids"]["contact"] = r["Id"]
                seeds[side]["tokens"]["contact"] = tok.search(r["Email"]).group(0)
        for r in q["task"]["records"]:
            if r["Subject"] == pre + "ACTIVITY":
                seeds[side]["ids"]["task"] = r["Id"]
                seeds[side]["tokens"]["task"] = tok.search(r["Description"]).group(0)
        if len(seeds[side]["ids"]) != 5 or len(seeds[side]["tokens"]) != 5:
            raise SystemExit("discover: side %s does not hold all 5 seeded records and tokens" % side)
    return seeds


def blob(results):
    return json.dumps([r["records"] for r in results])


def leaks(text, side, seeds):
    """Leak (L): any of side's names, content tokens or record ids in the text. Returns what was found."""
    found = []
    if "WALLTEST-%s-" % side in text:
        found.append("name WALLTEST-%s-" % side)
    for k, t in seeds[side]["tokens"].items():
        if t in text:
            found.append("token of %s" % k)
    for k, i in seeds[side]["ids"].items():
        if i[:15] in text:
            found.append("id of %s" % k)
    return found


def identity_check(side):
    who = sf(["org", "display", "user", "--target-org", USER_ALIAS[side]])
    if who.get("status") != 0:
        return False, err_text(who)
    uid = who["result"].get("id")
    r = query(USER_ALIAS[side], "SELECT LastName, UserRole.Name, Profile.Name, Profile.PermissionsModifyAllData, "
              "Profile.PermissionsViewAllData FROM User WHERE Id = '%s'" % uid)
    if not (r["ok"] and r["records"]):
        return False, r["err"] or "no user row"
    u = r["records"][0]
    ok = (u["LastName"] == USER_LAST[side] and u["UserRole"]["Name"] == ROLE_NAME[side]
          and u["Profile"]["Name"] == "Standard User"
          and not u["Profile"]["PermissionsModifyAllData"] and not u["Profile"]["PermissionsViewAllData"])
    return ok, "%s, role %s, profile %s, no Modify All Data, no View All Data" % (
        u["LastName"], u["UserRole"]["Name"], u["Profile"]["Name"])


# --------------------------------------------------------------------- cases

def blocked_status(leak, reached, control_ok):
    if not reached or not control_ok:
        return "NOT RUN"
    return "FAIL" if leak else "PASS"


def read_queries(side, seeds):
    ids = seeds[side]["ids"]
    pre = "WALLTEST-%s-" % side
    by_name = [
        ("opp1", "SELECT Id, Name, Description FROM Opportunity WHERE Name = '%sOPP-1'" % pre),
        ("account", "SELECT Id, Name, Description FROM Account WHERE Name = '%sACCOUNT'" % pre),
        ("contact", "SELECT Id, LastName, Email FROM Contact WHERE LastName = '%sCONTACT'" % pre),
        ("task", "SELECT Id, Subject, Description FROM Task WHERE Subject = '%sACTIVITY'" % pre),
    ]
    by_id = [
        ("opp1", "SELECT Id, Name, Description FROM Opportunity WHERE Id = '%s' FOR VIEW" % ids["opp1"]),
        ("account", "SELECT Id, Name, Description FROM Account WHERE Id = '%s' FOR VIEW" % ids["account"]),
        ("contact", "SELECT Id, LastName, Email FROM Contact WHERE Id = '%s' FOR VIEW" % ids["contact"]),
        ("task", "SELECT Id, Subject, Description FROM Task WHERE Id = '%s'" % ids["task"]),
    ]
    return by_name + by_id


def run_read(actor, target, seeds):
    """WT-01 to WT-04 shape: the four records of `target` by name, then by id, as `actor`."""
    results = []
    for key, soql in read_queries(target, seeds):
        r = query(USER_ALIAS[actor], soql)
        r["key"] = key
        results.append(r)
    reached = all(r["ok"] for r in results)
    return results, reached


def read_control_ok(results, side, seeds):
    for r in results:
        if not r["ok"] or not r["records"]:
            return False
        if seeds[side]["tokens"][r["key"]] not in blob([r]):
            return False
    return True


def sosl_for(term):
    return ("FIND {%s} IN ALL FIELDS RETURNING Opportunity(Id, Name), Account(Id, Name), "
            "Contact(Id, LastName), Task(Id, Subject)" % term)


def run_search(actor, seeds, wait):
    """WT-05 to WT-08 shape: search WALLTEST as `actor`, retrying while the index catches up."""
    own = {i[:15] for i in seeds[actor]["ids"].values()}
    deadline = time.time() + wait
    while True:
        r = search(USER_ALIAS[actor], sosl_for("WALLTEST*"))
        found = {rec.get("Id", "")[:15] for rec in r["records"]}
        if not r["ok"] or own <= found or time.time() >= deadline:
            return r
        log("cases: search as %s found %d of 5 own-side records, waiting for the index" % (actor, len(own & found)))
        time.sleep(20)


def run_lists(actor):
    """WT-09 to WT-12 shape: all opportunities, accounts and contacts, recently viewed, the All Opportunities list view."""
    results = [
        query(USER_ALIAS[actor], "SELECT Id, Name FROM Opportunity"),
        query(USER_ALIAS[actor], "SELECT Id, Name FROM Account"),
        query(USER_ALIAS[actor], "SELECT Id, LastName FROM Contact"),
        query(USER_ALIAS[actor], "SELECT Id, Name, Type FROM RecentlyViewed"),
    ]
    lv = query(USER_ALIAS[actor], "SELECT Id FROM ListView WHERE SobjectType = 'Opportunity' AND DeveloperName = 'AllOpportunities'")
    results.append(lv)
    list_view_text = ""
    if lv["ok"] and lv["records"]:
        res = sf(["api", "request", "rest", "/services/data/v62.0/sobjects/Opportunity/listviews/%s/results"
                  % lv["records"][0]["Id"], "--target-org", USER_ALIAS[actor]])
        if isinstance(res, dict) and res.get("records") is not None or res.get("status") == 0:
            list_view_text = json.dumps(res)
        else:
            list_view_text = ""
            results.append({"ok": False, "records": [], "total": 0, "err": err_text(res)})
    return results, list_view_text


def run_aggregate(actor, seeds):
    """WT-13 to WT-16 shape."""
    own, other = actor, OTHER[actor]
    c_own = query(USER_ALIAS[actor], "SELECT COUNT() FROM Opportunity WHERE Name LIKE 'WALLTEST-%s%%'" % own)
    grouped = query(USER_ALIAS[actor], "SELECT Owner.Name owner, COUNT(Id) n FROM Opportunity "
                    "WHERE Name LIKE 'WALLTEST%' GROUP BY Owner.Name")
    c_other = query(USER_ALIAS[actor], "SELECT COUNT() FROM Opportunity WHERE Name LIKE 'WALLTEST-%s%%'" % other)
    return c_own, grouped, c_other


def stage_cases(seeds, search_wait):
    log("cases: identity of each test user")
    for side in "DI":
        ok, detail = identity_check(side)
        add("ID-" + side, side + "T" if side == "D" else "IR", "alias resolves to the intended user", "PASS" if ok else "FAIL", detail)
        if not ok:
            raise SystemExit("cases: identity check failed for %s: %s" % (side, detail))
    actor_name = {"D": "DT", "I": "IR"}
    nums = {"D": 0, "I": 2}  # DT cases come first in each group, IR second

    # WT-01 to WT-04: read by name and id
    ctrl = {}
    for actor in "DI":
        c_id, b_id = "WT-%02d" % (1 + nums[actor]), "WT-%02d" % (2 + nums[actor])
        results, reached = run_read(actor, actor, seeds)
        ok = read_control_ok(results, actor, seeds)
        ctrl[c_id] = ok
        add(c_id, actor_name[actor], "own 4 records by name and by id, 4 tokens", "PASS" if ok else "FAIL",
            "" if ok else "; ".join(r["err"] or "no row or token for %s" % r["key"] for r in results if not r["ok"] or not r["records"])[:300])
        results, reached = run_read(actor, OTHER[actor], seeds)
        found = leaks(blob(results), OTHER[actor], seeds)
        rows = sum(len(r["records"]) for r in results)
        add(b_id, actor_name[actor], "other side's 4 records by name and by id", blocked_status(found, reached, ctrl[c_id]),
            "%d rows returned; leak: %s" % (rows, ", ".join(found) or "none"))

    # WT-05 to WT-08: search
    for actor in "DI":
        c_id, b_id = "WT-%02d" % (5 + nums[actor]), "WT-%02d" % (6 + nums[actor])
        r = run_search(actor, seeds, search_wait)
        found_ids = {rec.get("Id", "")[:15] for rec in r["records"]}
        own_ids = {i[:15] for i in seeds[actor]["ids"].values()}
        ok = r["ok"] and own_ids <= found_ids
        ctrl[c_id] = ok
        add(c_id, actor_name[actor], "search WALLTEST, all 5 own-side ids appear", "PASS" if ok else "FAIL",
            "found %d of 5 own-side ids (%d items)" % (len(own_ids & found_ids), r["total"]) if r["ok"] else r["err"])
        found = leaks(blob([r]), OTHER[actor], seeds)
        count_over = r["total"] > 5
        probe = search(USER_ALIAS[actor], "FIND {%s} IN ALL FIELDS RETURNING Opportunity(Id, Name), Account(Id, Name), "
                       "Contact(Id, LastName), Task(Id, Subject)" % seeds[OTHER[actor]]["tokens"]["opp1"])
        if probe["ok"] and probe["records"]:
            found.append("token search returned %d records" % len(probe["records"]))
        status = blocked_status(found or count_over, r["ok"] and probe["ok"], ok)
        add(b_id, actor_name[actor], "same search, nothing from the other side, no more than 5 items", status,
            "%d items; leak: %s; other side's token search: %d records" % (r["total"], ", ".join(found) or "none", len(probe["records"])))

    # WT-09 to WT-12: lists
    for actor in "DI":
        c_id, b_id = "WT-%02d" % (9 + nums[actor]), "WT-%02d" % (10 + nums[actor])
        results, lv_text = run_lists(actor)
        reached = all(r["ok"] for r in results)
        text = blob(results)
        need = [seeds[actor]["ids"][k][:15] for k in ("opp1", "opp2", "account", "contact")]
        ok = reached and all(n in text for n in need)
        ctrl[c_id] = ok
        add(c_id, actor_name[actor], "lists show own opportunities, account, contact ids", "PASS" if ok else "FAIL",
            "" if ok else "; ".join(r["err"] for r in results if not r["ok"])[:300] or "an own-side id is missing")
        found = leaks(text + lv_text, OTHER[actor], seeds)
        rv = [r for r in results[3:4]]
        add(b_id, actor_name[actor], "same lists, no other-side name or id", blocked_status(found, reached, ok),
            "leak: %s; recently viewed rows: %d; All Opportunities list view %s" % (
                ", ".join(found) or "none", len(rv[0]["records"]) if rv and rv[0]["ok"] else -1,
                "read" if lv_text else "not read"))

    # WT-13 to WT-16: aggregates
    for actor in "DI":
        c_id, b_id = "WT-%02d" % (13 + nums[actor]), "WT-%02d" % (14 + nums[actor])
        c_own, grouped, c_other = run_aggregate(actor, seeds)
        ok = c_own["ok"] and c_own["total"] == 2
        ctrl[c_id] = ok
        add(c_id, actor_name[actor], "count of own-side opportunities is 2", "PASS" if ok else "FAIL",
            "count %s" % c_own["total"] if c_own["ok"] else c_own["err"])
        reached = grouped["ok"] and c_other["ok"]
        groups = grouped["records"]
        total = sum(g.get("n", 0) for g in groups)
        names = {g.get("owner") for g in groups}
        bad = []
        if total != 2:
            bad.append("grouped total %s, not 2" % total)
        if USER_LAST[OTHER[actor]] in names:
            bad.append("group row names %s" % USER_LAST[OTHER[actor]])
        if c_other["total"] != 0:
            bad.append("other-side count %s, not 0" % c_other["total"])
        add(b_id, actor_name[actor], "grouped count is 2 with own owner only; other side's count is 0",
            blocked_status(bad, reached, ok), "grouped total %s, owners %s, other-side count %s%s" % (
                total, sorted(n for n in names if n), c_other["total"], "; " + "; ".join(bad) if bad else ""))


# -------------------------------------------------------------------- marker

def stage_marker(seeds):
    marker_src = "force-app"
    log("marker: validating the kit's marker metadata (dry run)")
    dry = sf(["project", "deploy", "start", "--source-dir", marker_src, "--target-org", ORG, "--dry-run", "--wait", "20"],
             cwd=str(KIT_DIR))
    attempts = []
    if dry.get("status") == 0:
        attempts.append(("validate (dry run)", "pass", ""))
        real = sf(["project", "deploy", "start", "--source-dir", marker_src, "--target-org", ORG, "--wait", "20"],
                  cwd=str(KIT_DIR))
        if real.get("status") == 0:
            attempts.append(("deploy", "pass", ""))
        else:
            attempts.append(("deploy", "fail", err_text(real) + " " + failures(real)))
    else:
        attempts.append(("validate (dry run)", "fail", err_text(dry) + " " + failures(dry)))
    deployed = attempts[-1][0] == "deploy" and attempts[-1][1] == "pass"
    if not deployed:
        log("marker: first attempt failed; enabling Opportunity history (README step 1) and trying once more")
        hist = sf(["project", "deploy", "start", "--source-dir", "optional/enable-opportunity-history",
                   "--target-org", ORG, "--wait", "20"], cwd=str(HERE))
        attempts.append(("enable Opportunity history, then redeploy", "pass" if hist.get("status") == 0 else "fail",
                         "" if hist.get("status") == 0 else err_text(hist) + " " + failures(hist)))
        if hist.get("status") == 0:
            real = sf(["project", "deploy", "start", "--source-dir", marker_src, "--target-org", ORG, "--wait", "20"],
                      cwd=str(KIT_DIR))
            attempts.append(("deploy after history", "pass" if real.get("status") == 0 else "fail",
                             "" if real.get("status") == 0 else err_text(real) + " " + failures(real)))
            deployed = real.get("status") == 0
    for name, st, detail in attempts:
        EXTRA.append(("marker " + name, st.upper() + (": " + detail if detail else "")))
    add("MARKER", "admin", "kit's force-app (field and 2 permission sets) deploys", "PASS" if deployed else "FAIL",
        "; ".join("%s %s" % (n, s) for n, s, _ in attempts))

    # HasEditAccess, as each test user, against a record on each side (level-2-writes.md step 2)
    log("marker: UserRecordAccess HasEditAccess as each test user")
    for actor in "DI":
        who = sf(["org", "display", "user", "--target-org", USER_ALIAS[actor]])
        uid = who["result"]["id"] if who.get("status") == 0 else None
        for target in "DI":
            rec = seeds[target]["ids"]["opp1"]
            r = query(USER_ALIAS[actor], "SELECT RecordId, HasReadAccess, HasEditAccess FROM UserRecordAccess "
                      "WHERE UserId = '%s' AND RecordId = '%s'" % (uid, rec))
            own = actor == target
            expect = "HasEditAccess true" if own else "HasEditAccess false"
            if r["ok"] and r["records"]:
                row = r["records"][0]
                got = "HasReadAccess %s, HasEditAccess %s" % (str(row["HasReadAccess"]).lower(), str(row["HasEditAccess"]).lower())
                good = bool(row["HasEditAccess"]) == own
            elif r["ok"]:
                got, good = "no row returned", not own
            else:
                got, good = r["err"], False
            case = "ACCESS-%s%s" % (actor, target)
            add(case, "DT" if actor == "D" else "IR", "HasEditAccess on %s-side opportunity (expected: %s)" % (
                "own" if own else "other", expect), "PASS" if good else "FAIL", got)


def failures(res):
    f = res.get("result", {}).get("details", {}).get("componentFailures", []) if isinstance(res.get("result"), dict) else []
    return json.dumps([{"file": x.get("fullName"), "problem": x.get("problem")} for x in f])[:800] if f else ""


# -------------------------------------------------------------------- delete

def stage_delete():
    for side in "DI":
        sf(["org", "logout", "--target-org", USER_ALIAS[side], "--no-prompt"])
    res = sf(["org", "delete", "scratch", "--target-org", ORG, "--no-prompt"])
    if res.get("status") != 0:
        log("delete: FAILED, the scratch org still exists with alias %s. Error: %s" % (ORG, err_text(res)))
        return False
    gone = not org_in_list(ORG)
    log("delete: scratch org deleted; alias %s %s in `sf org list`" % (ORG, "is gone" if gone else "STILL LISTED"))
    return gone


# ---------------------------------------------------------------------- main

def print_table():
    width = [max(len(str(r[i])) for r in ROWS + [("Case", "Actor", "Checks", "Result", "Detail")]) for i in range(4)]
    head = ("Case", "Actor", "Checks", "Result", "Detail")
    for row in [head] + ROWS:
        log("| " + " | ".join(str(row[i]).ljust(width[i]) for i in range(4)) + " | " + str(row[4]))
    for label, value in EXTRA:
        log("%s: %s" % (label, value))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("dev_hub", help="alias of the Dev Hub to create the scratch org from")
    ap.add_argument("--keep-org", action="store_true", help="skip the delete stage")
    ap.add_argument("--stages", default=",".join(STAGES), help="comma list from: " + ", ".join(STAGES))
    ap.add_argument("--search-wait", type=int, default=240, help="seconds to wait for the search index (default 240)")
    args = ap.parse_args()
    stages = [s for s in args.stages.split(",") if s]
    if any(s not in STAGES for s in stages):
        ap.error("unknown stage")
    if args.keep_org and "delete" in stages:
        stages.remove("delete")

    log("wall test dry run, %s" % date.today().isoformat())
    with tempfile.TemporaryDirectory() as tmp:
        if "setup" in stages:
            stage_setup(args.dev_hub, tmp)
        seeds = None
        if "cases" in stages or "marker" in stages:
            seeds = discover()
            info = sf(["org", "display", "--target-org", ORG])
            if info.get("status") == 0:
                log("API version: %s" % info["result"].get("apiVersion"))
        if "cases" in stages:
            stage_cases(seeds, args.search_wait)
        if "marker" in stages:
            stage_marker(seeds)
        print_table()
        if "delete" in stages:
            if not stage_delete():
                sys.exit(2)
    failed = [r for r in ROWS if r[3] != "PASS"]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
