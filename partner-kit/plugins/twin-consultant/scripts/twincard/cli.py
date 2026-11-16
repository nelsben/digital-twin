"""Command line for the persona-card workflow.

    python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py validate <persona-dir>
    python3 .../cli.py validate --json <persona-dir>
    python3 .../cli.py level <persona-dir>          # writes <persona-dir>/levelled.json
    python3 .../cli.py level --json <persona-dir>

Runs from any working directory. Exit codes: 0 on success; 1 when validation
fails (level then writes nothing) or when levelling reports a blocker (level
still writes levelled.json); 2 on a usage error or a missing persona folder
(for level, a folder with no card.json).
The backlog, dashboard and all commands are planned (partner-kit/docs/design.md,
section 3).
"""

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    # Run as a script: make the twincard package importable from its parent folder.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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


def main(argv=None):
    args = build_parser().parse_args(argv)
    persona_dir = Path(args.persona_dir)
    if not persona_dir.is_dir():
        sys.stderr.write("cli.py %s: no such persona folder: %s\n" % (args.command, persona_dir))
        return EXIT_USAGE
    if args.command == "level":
        if not (persona_dir / "card.json").is_file():
            sys.stderr.write("cli.py level: %s holds no card.json, so it is not a persona folder\n" % persona_dir)
            return EXIT_USAGE
        return run_level(args, persona_dir)
    result = validate(str(persona_dir))
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text(result))
    return EXIT_OK if result["ok"] else EXIT_INVALID


if __name__ == "__main__":
    sys.exit(main())
