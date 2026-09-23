"""CLI with deterministic reports and explicit CI exit states."""

import argparse
import html
import json
import sys

from . import __version__
from .contracts import InputError, normalize, parse_json, read_json, read_text
from .engine import compare, replay, verify_witness


def load_calls(path):
    if not path:
        return []
    text = read_text(path)
    if text.lstrip().startswith("["):
        data = parse_json(text)
        return data
    return [parse_json(line) for line in text.splitlines() if line.strip()]


def render(report, mode="text"):
    if mode == "json":
        return json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False) + "\n"
    status = report.get("status", "normalized").upper()
    if mode == "markdown":
        lines = [f"## ArgWitness — {status}", "", "| Tool | Result | Evidence |", "| --- | --- | --- |"]
        esc = lambda s: html.escape(str(s)).replace("|", "&#124;").replace("\n", " ").replace("\r", " ").replace("`", "&#96;")
        for finding in report.get("findings", report.get("calls", [])):
            lines.append(f"| {esc(finding['tool'])} | {esc(finding['status'])} | {esc(finding.get('reason', ''))} |")
            if "arguments" in finding.get("witness", {}):
                lines.append(f"| | Counterexample | {esc(json.dumps(finding['witness']['arguments'], ensure_ascii=True))} |")
        lines += ["", "A bounded search can establish a counterexample; it cannot certify compatibility."]
        return "\n".join(lines) + "\n"
    lines = [f"ArgWitness {__version__} — {status}"]
    for finding in report.get("findings", report.get("calls", [])):
        # JSON escaping also prevents terminal control sequences in untrusted names.
        name = json.dumps(finding["tool"], ensure_ascii=True)
        lines.append(f"  {finding.get('code', '')} {name}: {finding['status']} — {finding.get('reason', '')}")
        if "witness" in finding:
            witness = finding["witness"]
            lines.append("    OLD accepts -> NEW rejects (" + witness["source"] + ")")
            if "arguments" in witness:
                lines.append("    " + json.dumps(witness["arguments"], ensure_ascii=True))
            else:
                lines.append("    Values omitted. Use --show-values only with sanitized data.")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Find concrete breaking calls in AI tool contract changes. No servers are invoked.")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    diff = commands.add_parser("compare", help="Find old-valid/new-invalid calls")
    diff.add_argument("before")
    diff.add_argument("after")
    diff.add_argument("--calls", help="Sanitized JSONL or JSON array of observed calls")
    diff.add_argument("--limit", type=int, default=512)
    rep = commands.add_parser("replay", help="Validate captured arguments offline; never invoke tools")
    rep.add_argument("catalog")
    rep.add_argument("calls")
    ver = commands.add_parser("verify", help="Independently revalidate {tool, arguments} witness JSON")
    ver.add_argument("before")
    ver.add_argument("after")
    ver.add_argument("witness")
    norm = commands.add_parser("normalize", help="Convert provider tools to a common catalog")
    norm.add_argument("catalog")
    for child in (diff, rep, ver):
        child.add_argument("--format", choices=("text", "json", "markdown"), default="text")
    for child in (diff, rep):
        child.add_argument("--show-values", action="store_true", help="Include potentially sensitive argument values in reports")
    args = parser.parse_args(argv)
    try:
        if args.command == "normalize":
            sys.stdout.write(json.dumps(normalize(read_json(args.catalog)), indent=2, ensure_ascii=True) + "\n")
            return 0
        if args.command == "compare":
            report = compare(read_json(args.before), read_json(args.after), load_calls(args.calls),
                             limit=args.limit, show_values=args.show_values)
            code = {"breaking": 1, "review": 2, "added": 0, "unchanged": 0}[report["status"]]
        elif args.command == "replay":
            report = replay(read_json(args.catalog), load_calls(args.calls), show_values=args.show_values)
            code = 1 if report["status"] == "invalid" else 0
        else:
            report = verify_witness(read_json(args.before), read_json(args.after), read_json(args.witness))
            code = 0 if report["status"] == "confirmed" else 1
        sys.stdout.write(render(report, args.format))
        return code
    except (InputError, OSError, ValueError, RecursionError) as exc:
        message = str(exc) if isinstance(exc, InputError) else "Cannot read or process input; check files and JSON structure"
        sys.stderr.write("argwitness: " + message + "\n")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
