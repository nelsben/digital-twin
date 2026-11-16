"""Command line for the persona-card workflow.

    python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py validate <persona-dir>
    python3 .../cli.py validate --json <persona-dir>
    python3 .../cli.py level <persona-dir>          # writes <persona-dir>/levelled.json
    python3 .../cli.py level --json <persona-dir>
    python3 .../cli.py backlog <persona-dir>        # writes backlog.json and backlog.md
    python3 .../cli.py backlog --json <persona-dir> [--plan-out FILE]
    python3 .../cli.py dashboard <persona-dir> [--date YYYY-MM-DD]   # writes dashboard.html

Runs from any working directory. Exit codes: 0 on success; 1 when validation
fails (level, backlog and dashboard then write nothing), when levelled.json is
missing or out of date (backlog and dashboard write nothing), when backlog.json is
missing or out of date (dashboard writes nothing), or when levelling reports a
blocker (level still writes levelled.json, backlog still writes both files,
dashboard still writes dashboard.html); 2 on a usage error, a missing persona
folder (for level, backlog and dashboard, a folder with no card.json), an unknown
status in backlog.json or a --date that is not a real YYYY-MM-DD date.
The all command is planned (partner-kit/docs/design.md, section 3).
"""

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    # Run as a script: make the twincard package importable from its parent folder.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from twincard import backlog as backlog_mod  # noqa: E402
from twincard import dashboard as dashboard_mod  # noqa: E402
from twincard.level import LEVELLED_FILE, write_levelled  # noqa: E402
from twincard.validate import qualified, validate  # noqa: E402

EXIT_OK = 0
EXIT_INVALID = 1
EXIT_USAGE = 2


def build_parser():
    parser = argparse.ArgumentParser(
        prog="cli.py", description="Persona-card workflow tools for the twin-consultant plugin.")
    commands = parser.add_subparsers(dest="command", metavar="command")
    commands.required = True
    check = commands.add_parser(
        "validate", help="check card.json and ../../customer-profile.json and report completeness")
    check.add_argument("persona_dir", help="the persona folder that holds card.json")
    check.add_argument("--json", action="store_true", help="print the full result as JSON")
    levelling = commands.add_parser(
        "level", help="validate, then level the card by rule and write levelled.json next to card.json")
    levelling.add_argument("persona_dir", help="the persona folder that holds card.json")
    levelling.add_argument("--json", action="store_true", help="print levelled.json (or the validation errors) as JSON")
    backlog = commands.add_parser(
        "backlog", help="build backlog.json and backlog.md from card.json, levelled.json and the task library")
    backlog.add_argument("persona_dir", help="the persona folder that holds card.json and levelled.json")
    backlog.add_argument("--json", action="store_true", help="print backlog.json (or the validation errors) as JSON")
    backlog.add_argument("--plan-out", metavar="FILE", help="also write the backlog as a tree_import plan to FILE")
    board = commands.add_parser(
        "dashboard", help="render dashboard.html from card.json, the profile, levelled.json and backlog.json")
    board.add_argument("persona_dir", help="the persona folder that holds card.json, levelled.json and backlog.json")
    board.add_argument("--date", metavar="YYYY-MM-DD", help="the generated date shown on the page (default: today)")
    return parser


def format_line(item):
    return "%s: %s. Next: %s" % (qualified(item["record"], item["path"]), item["message"], item["fix"])


def format_text(result):
    lines = [format_line(error) for error in result["errors"]]
    lines += ["warning: " + format_line(warning) for warning in result["warnings"]]
    done = result["completeness"]
    line = "Completeness: %d%% (%d of %d required fields answered or default)" % (
        done["percent"], done["satisfied"], done["required"])
    if done["missing"]:
        line += "; not yet answered: " + ", ".join(done["missing"])
    lines.append(line)
    if result["errors"]:
        lines.append("Not valid: %d error(s)." % len(result["errors"]))
    else:
        lines.append("Valid.")
    return "\n".join(lines)


def format_level(result, persona_dir):
    if not result["ok"]:
        return format_text(result["validation"]) + "\nNot levelled: fix the errors above, then run level again."
    levelled = result["levelled"]
    lines = []
    for kind, items in (("blocker", levelled["blockers"]), ("warning", levelled["warnings"])):
        for item in items:
            lines.append("%s: %s %s: %s Next: %s" % (kind, item["about"], item["code"], item["message"], item["fix"]))
    lines.append("Wrote %s: %d task(s), %d blocker(s), %d warning(s); complete: %s." % (
        Path(persona_dir) / LEVELLED_FILE, len(levelled["tasks"]), len(levelled["blockers"]),
        len(levelled["warnings"]), "yes" if levelled["complete"] else "no"))
    return "\n".join(lines)


def run_level(args, persona_dir):
    result = write_levelled(str(persona_dir))
    if args.json:
        body = result["levelled"] if result["ok"] else result["validation"]
        print(json.dumps(body, indent=2, ensure_ascii=False))
    else:
        print(format_level(result, persona_dir))
    if not result["ok"] or result["levelled"]["blockers"]:
        return EXIT_INVALID
    return EXIT_OK


def format_backlog(result, persona_dir):
    backlog = result["backlog"]
    lines = [backlog["epic"]["title"]]
    for feature in backlog["epic"]["features"]:
        lines.append("%s: %d stories, %d tasks" % (feature["id"], len(feature["stories"]),
                                                   sum(len(s["tasks"]) for s in feature["stories"])))
    lines.append("Total: %d features, %d stories, %d tasks" % backlog_mod.counts(backlog))
    for item in result["retired_now"]:
        lines.append("retired: %s (%s): %s" % (item["id"], item["status"], item["title"]))
    lines.append("Wrote %s and %s." % (Path(persona_dir) / backlog_mod.BACKLOG_JSON,
                                       Path(persona_dir) / backlog_mod.BACKLOG_MD))
    return "\n".join(lines)


def run_backlog(args, persona_dir):
    try:
        result = backlog_mod.write_backlog(str(persona_dir))
    except backlog_mod.UsageError as exc:
        sys.stderr.write("cli.py backlog: %s\n" % exc)
        return EXIT_USAGE
    if not result["ok"]:
        if args.json:
            print(json.dumps(result["validation"], indent=2, ensure_ascii=False))
        elif result["validation"]["errors"]:
            print(format_text(result["validation"]))
        print(result["error"])
        return EXIT_INVALID
    if args.plan_out:
        Path(args.plan_out).write_text(
            json.dumps(backlog_mod.plan_tree(result["backlog"]), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
    if args.json:
        sys.stdout.write(backlog_mod.render_json(result["backlog"]))
    else:
        print(format_backlog(result, persona_dir))
    if backlog_mod.has_blocker(str(persona_dir)):
        if not args.json:
            print("Blocked: levelled.json reports a blocker; the gated stories say which.")
        return EXIT_INVALID
    return EXIT_OK


def run_dashboard(args, persona_dir):
    try:
        result = dashboard_mod.write_dashboard(str(persona_dir), args.date)
    except dashboard_mod.UsageError as exc:
        sys.stderr.write("cli.py dashboard: %s\n" % exc)
        return EXIT_USAGE
    if not result["ok"]:
        if result["validation"] and result["validation"]["errors"]:
            print(format_text(result["validation"]))
        print(result["error"])
        return EXIT_INVALID
    s = result["summary"]
    print("Wrote %s." % result["path"])
    print("Completeness: %d%% (%d of %d required fields). Blockers: %d. Warnings: %d. Backlog: %d of %d tasks done."
          % (s["percent"], s["satisfied"], s["required"], s["blockers"], s["warnings"], s["tasks_done"],
             s["tasks_total"]))
    return EXIT_INVALID if s["blockers"] else EXIT_OK


def main(argv=None):
    args = build_parser().parse_args(argv)
    persona_dir = Path(args.persona_dir)
    if not persona_dir.is_dir():
        sys.stderr.write("cli.py %s: no such persona folder: %s\n" % (args.command, persona_dir))
        return EXIT_USAGE
    if args.command in ("level", "backlog", "dashboard"):
        if not (persona_dir / "card.json").is_file():
            sys.stderr.write("cli.py %s: %s holds no card.json, so it is not a persona folder\n"
                             % (args.command, persona_dir))
            return EXIT_USAGE
        if args.command == "backlog":
            return run_backlog(args, persona_dir)
        if args.command == "dashboard":
            return run_dashboard(args, persona_dir)
        return run_level(args, persona_dir)
    result = validate(str(persona_dir))
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text(result))
    return EXIT_OK if result["ok"] else EXIT_INVALID


if __name__ == "__main__":
    sys.exit(main())
