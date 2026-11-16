"""Command line for the persona-card workflow.

    python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py validate <persona-dir>
    python3 .../cli.py validate --json <persona-dir>

Runs from any working directory. Exit codes: 0 when there are no errors, 1 when
validation fails, 2 on a usage error or a missing persona folder. Only the
validate command exists so far; level, backlog, dashboard and all are planned
(partner-kit/docs/design.md, section 3).
"""

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    # Run as a script: make the twincard package importable from its parent folder.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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


def main(argv=None):
    args = build_parser().parse_args(argv)
    persona_dir = Path(args.persona_dir)
    if not persona_dir.is_dir():
        sys.stderr.write("cli.py validate: no such persona folder: %s\n" % persona_dir)
        return EXIT_USAGE
    result = validate(str(persona_dir))
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text(result))
    return EXIT_OK if result["ok"] else EXIT_INVALID


if __name__ == "__main__":
    sys.exit(main())
