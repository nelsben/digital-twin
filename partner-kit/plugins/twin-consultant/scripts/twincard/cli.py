"""Command line for the persona-card workflow.

    python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py validate <persona-dir>
    python3 .../cli.py validate --json <persona-dir>
    python3 .../cli.py level <persona-dir>          # writes <persona-dir>/levelled.json
    python3 .../cli.py level --json <persona-dir>
    python3 .../cli.py backlog <persona-dir>        # writes backlog.json and backlog.md
    python3 .../cli.py backlog --json <persona-dir> [--plan-out FILE]
    python3 .../cli.py dashboard <persona-dir> [--date YYYY-MM-DD]   # writes dashboard.html
    python3 .../cli.py all <persona-dir> [--date YYYY-MM-DD]   # validate, level, backlog, dashboard
    python3 .../cli.py build <persona-dir> [--all-tasks]   # scaffolds <persona-dir>/build/ (design 8a)

Runs from any working directory. Exit codes: 0 on success; 1 when validation
fails (level, backlog and dashboard then write nothing), when levelled.json is
missing or no longer what level gives for the current card, profile and kit data
(backlog and dashboard write nothing), when backlog.json is missing or no longer
what backlog gives (dashboard writes nothing), or when levelling reports a
blocker (level still writes levelled.json, backlog still writes both files,
dashboard still writes dashboard.html); 2 on a usage error, a missing persona
folder (for level, backlog and dashboard, a folder with no card.json), an output
that cannot be written, a kit data file or backlog.json that cannot be read or is
not in its shape, an unknown status in backlog.json or a --date that is not a
real YYYY-MM-DD date. A usage error or refusal is one line on stderr ending
"Next: <what to do>". With --json, level and backlog print exactly one JSON
document on stdout.
The all command runs the four in order and stops only when validation fails (nothing is
written, exit 1); a levelling blocker still writes every file and exits 1.
The build command is not part of all. It writes nothing and exits 1 when validation fails,
levelled.json is missing or stale, or levelling reports a blocker; it exits 2, writing nothing,
when data/build-kinds.json or build/build.json cannot be read or is not in its shape, or
build.json gives an unknown status. A file a person has changed is kept and listed on stderr.
"""

import argparse
import json
import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    # Run as a script: make the twincard package importable from its parent folder.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from twincard import backlog as backlog_mod  # noqa: E402
from twincard import build as build_mod  # noqa: E402
from twincard import dashboard as dashboard_mod  # noqa: E402
from twincard import fields as fields_mod  # noqa: E402
from twincard import packs as packs_mod  # noqa: E402
from twincard.level import LEVELLED_FILE, LevelError, write_levelled  # noqa: E402
from twincard.validate import qualified, validate  # noqa: E402

EXIT_OK = 0
EXIT_INVALID = 1
EXIT_USAGE = 2

DATA_NEXT = ("restore the twin-consultant plugin's data files (undo the edit, or reinstall the plugin), "
             "then run the command again")
VALIDATION_ERROR = "card.json or customer-profile.json has validation errors. Next: fix them, then run level again."


class Refusal(Exception):
    """A usage error or a refusal: one stderr line, exit 2."""


class Parser(argparse.ArgumentParser):
    """argparse with a one-line usage error that says what to do next."""

    def error(self, message):
        self.exit(EXIT_USAGE, "%s: %s. Next: run %s --help to see the commands and their arguments.\n"
                  % (self.prog, message, self.prog))


def build_parser():
    parser = Parser(
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
    backlog.add_argument("--json", action="store_true",
                         help="print backlog.json (or, when refused, the error and the validation errors) as JSON")
    backlog.add_argument("--plan-out", metavar="FILE", help="also write the backlog as a tree_import plan to FILE")
    board = commands.add_parser(
        "dashboard", help="render dashboard.html from card.json, the profile, levelled.json and backlog.json")
    board.add_argument("persona_dir", help="the persona folder that holds card.json, levelled.json and backlog.json")
    board.add_argument("--date", metavar="YYYY-MM-DD", help="the generated date shown on the page (default: today)")
    everything = commands.add_parser(
        "all", help="validate, level, backlog and dashboard in order; stops only when validation fails")
    everything.add_argument("persona_dir", help="the persona folder that holds card.json")
    everything.add_argument("--date", metavar="YYYY-MM-DD",
                            help="the generated date shown on the dashboard (default: today)")
    scaffold = commands.add_parser(
        "build", help="scaffold each task's skill and runtime wrapper under build/ from card.json and levelled.json")
    scaffold.add_argument("persona_dir", help="the persona folder that holds card.json and levelled.json")
    scaffold.add_argument("--all-tasks", action="store_true",
                          help="build every task, not only the pilot tasks (in_pilot true)")
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


def _show(value, none="undecided"):
    return none if value is None else str(value)


def format_task_lines(levelled):
    """One line per task: its id and seven decisions, in task order."""
    lines = []
    for task_id, decisions in levelled["tasks"].items():
        autonomy = decisions["autonomy"]
        connectors = ", ".join("%s %s" % (c["system"], c["access"]) for c in decisions.get("connectors") or []) or "none"
        lines.append("%s: runtime %s; identity %s; autonomy %s to %s; settings baseline %s; memory %s; plan fit %s; connectors %s" % (
            task_id, _show(decisions["runtime"]["value"]), _show(decisions["identity"]["value"]),
            _show(autonomy["start"]["value"]), _show(autonomy["ceiling"]["value"]),
            _show(decisions["data_controls"]["settings_baseline"]["value"], "none"),
            _show(decisions["memory"]["value"]), _show(decisions["plan_fit"]["value"]), connectors))
    return lines


def format_findings(levelled):
    return ["%s: %s %s: %s Next: %s" % (kind, item["about"], item["code"], item["message"], item["fix"])
            for kind, items in (("blocker", levelled["blockers"]), ("warning", levelled["warnings"]))
            for item in items]


def format_level(result, persona_dir):
    if not result["ok"]:
        return format_text(result["validation"]) + "\nNot levelled: fix the errors above, then run level again."
    levelled = result["levelled"]
    lines = format_task_lines(levelled) + format_findings(levelled)
    lines.append("Wrote %s: %d task(s), %d blocker(s), %d warning(s); complete: %s." % (
        Path(persona_dir) / LEVELLED_FILE, len(levelled["tasks"]), len(levelled["blockers"]),
        len(levelled["warnings"]), "yes" if levelled["complete"] else "no"))
    return "\n".join(lines)


def refused_json(validation, error):
    """The JSON a refused level or backlog prints: the validate() result with ok false and the error."""
    body = dict(validation) if validation else {"errors": [], "warnings": []}
    body["ok"] = False
    body["error"] = error
    return json.dumps(body, indent=2, ensure_ascii=False)


def print_json(text):
    sys.stdout.write(text if text.endswith("\n") else text + "\n")


def run_level(args, persona_dir):
    result = write_levelled(str(persona_dir))
    if args.json:
        if result["ok"]:
            print_json(json.dumps(result["levelled"], indent=2, ensure_ascii=False))
        else:
            print_json(refused_json(result["validation"], VALIDATION_ERROR))
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
    result = backlog_mod.write_backlog(str(persona_dir))
    if not result["ok"]:
        if args.json:
            print_json(refused_json(result["validation"], result["error"]))
            sys.stderr.write(result["error"] + "\n")
            return EXIT_INVALID
        if result["validation"]["errors"]:
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
        line = "Blocked: levelled.json reports a blocker; the gated stories say which."
        if args.json:
            sys.stderr.write(line + "\n")
        else:
            print(line)
        return EXIT_INVALID
    return EXIT_OK


def run_dashboard(args, persona_dir):
    result = dashboard_mod.write_dashboard(str(persona_dir), args.date)
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


def run_all(args, persona_dir):
    """validate, level, backlog, dashboard in order, by the same functions the single commands call."""
    date = dashboard_mod.parse_date(args.date)
    checked = validate(str(persona_dir))
    if not checked["ok"]:
        print("validate: failed")
        print("\n".join(format_line(error) for error in checked["errors"]))
        print("Not valid: %d error(s). Skipped: level, backlog, dashboard. Nothing written." % len(checked["errors"]))
        return EXIT_INVALID
    done = checked["completeness"]
    print("validate: ok. Completeness: %d%% (%d of %d required fields)" % (
        done["percent"], done["satisfied"], done["required"]))
    result = write_levelled(str(persona_dir))
    levelled = result["levelled"]
    blocked = bool(levelled["blockers"])
    print("level: %s %s" % ("blocked" if blocked else "ok", Path(persona_dir) / LEVELLED_FILE))
    for line in format_task_lines(levelled) + format_findings(levelled):
        print(line)
    built = backlog_mod.write_backlog(str(persona_dir))
    if not built["ok"]:
        print("backlog: failed")
        print(built["error"])
        print("Skipped: dashboard.")
        return EXIT_INVALID
    print("backlog: %s %s and %s" % ("blocked" if blocked else "ok", Path(persona_dir) / backlog_mod.BACKLOG_JSON,
                                     Path(persona_dir) / backlog_mod.BACKLOG_MD))
    for item in built["retired_now"]:
        print("retired: %s (%s): %s" % (item["id"], item["status"], item["title"]))
    board = dashboard_mod.write_dashboard(str(persona_dir), date)
    if not board["ok"]:
        print("dashboard: failed")
        print(board["error"])
        return EXIT_INVALID
    print("dashboard: %s %s" % ("blocked" if blocked else "ok", board["path"]))
    return EXIT_INVALID if blocked else EXIT_OK


def run_build(args, persona_dir):
    result = build_mod.write_build(str(persona_dir), args.all_tasks)
    if not result["ok"]:
        if result["validation"] and result["validation"]["errors"]:
            print(format_text(result["validation"]))
        print(result["error"])
        return EXIT_INVALID
    for path in result["kept"]:
        sys.stderr.write("kept: %s (a person changed it, so build left it as it is)\n" % path)
    for item in result["manifest"]["artifacts"]:
        print("%s: %s, runtime %s, skill %s%s: %s" % (
            item["id"], item["kind"], item["runtime"]["value"], item["skill_name"],
            " (derived)" if item["skill_name_derived"] else "", item["status"]))
    print("Wrote %s: %d artifact(s); %d file(s) written, %d kept." % (
        Path(persona_dir) / build_mod.BUILD_DIR / build_mod.MANIFEST, len(result["manifest"]["artifacts"]),
        len(result["written"]), len(result["kept"])))
    return EXIT_OK


OUTPUTS = {
    "level": (LEVELLED_FILE,),
    "backlog": (backlog_mod.BACKLOG_JSON, backlog_mod.BACKLOG_MD),
    "dashboard": (dashboard_mod.DASHBOARD_FILE,),
    "all": (LEVELLED_FILE, backlog_mod.BACKLOG_JSON, backlog_mod.BACKLOG_MD, dashboard_mod.DASHBOARD_FILE),
    "build": (),
}


def check_writable(path):
    """Refusal unless path can be written: an existing writable file, or a new file in a writable folder."""
    path = Path(path)
    if path.is_dir():
        raise Refusal("cannot write %s: it is a folder. Next: give a file path" % path)
    if path.exists():
        if not os.access(str(path), os.W_OK):
            raise Refusal("cannot write %s: the file is read-only. Next: make it writable (chmod u+w), then run "
                          "the command again" % path)
        return
    folder = path.parent
    if not folder.is_dir():
        raise Refusal("cannot write %s: the folder %s does not exist. Next: create the folder or give another "
                      "path, then run the command again" % (path, folder))
    if not os.access(str(folder), os.W_OK):
        raise Refusal("cannot write %s: the folder %s is read-only. Next: make it writable, then run the "
                      "command again" % (path, folder))


def _sentence(text):
    text = str(text).strip()
    return text[:-1] if text.endswith(".") else text


def data_error_line(exc):
    """One line for a kit data file that cannot be read or is not in its shape."""
    text = _sentence(exc)
    if "Next:" in text:
        return text
    return "%s. Next: %s" % (text, DATA_NEXT)


def run(args):
    persona_dir = Path(args.persona_dir)
    if not persona_dir.is_dir():
        raise Refusal("no such persona folder: %s. Next: give the path of a persona folder, "
                      "engagements/<customer>/personas/<persona-id>" % persona_dir)
    if args.command == "validate":
        result = validate(str(persona_dir))
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_text(result))
        return EXIT_OK if result["ok"] else EXIT_INVALID
    if not (persona_dir / "card.json").is_file():
        raise Refusal("%s holds no card.json, so it is not a persona folder. Next: give the folder that holds "
                      "card.json, or start one from templates/card.json" % persona_dir)
    if getattr(args, "date", None) is not None or args.command in ("dashboard", "all"):
        dashboard_mod.parse_date(args.date)
    for name in OUTPUTS[args.command]:
        check_writable(persona_dir / name)
    if getattr(args, "plan_out", None):
        check_writable(args.plan_out)
    if args.command == "build":
        folder = persona_dir / build_mod.BUILD_DIR
        check_writable(folder / build_mod.MANIFEST if folder.is_dir() else folder)
        return run_build(args, persona_dir)
    if args.command == "backlog":
        return run_backlog(args, persona_dir)
    if args.command == "dashboard":
        return run_dashboard(args, persona_dir)
    if args.command == "all":
        return run_all(args, persona_dir)
    return run_level(args, persona_dir)


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except (Refusal, backlog_mod.UsageError, dashboard_mod.UsageError, build_mod.UsageError) as exc:
        line = _sentence(exc) if "Next:" in str(exc) else "%s. Next: run the command again with a usable value" % _sentence(exc)
    except (LevelError, backlog_mod.BacklogError, packs_mod.PackError, fields_mod.CatalogueError,
            build_mod.BuildError) as exc:
        line = data_error_line(exc)
    except OSError as exc:
        where = exc.filename or "a file"
        line = "cannot read or write %s: %s. Next: check the file and its folder can be read and written, then " \
               "run the command again" % (where, exc.strerror or exc)
    line = " ".join(line.split())
    line = line if line.endswith(".") else line + "."
    if getattr(args, "json", False):
        print_json(refused_json(None, line))
    sys.stderr.write("cli.py %s: %s\n" % (args.command, line))
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
