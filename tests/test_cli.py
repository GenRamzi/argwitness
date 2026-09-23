import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from argwitness.cli import render
from argwitness.contracts import InputError, catalog, parse_json

ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "argwitness", *map(str, args)],
                              cwd=ROOT, capture_output=True, text=True)

    def test_breaking_json_and_exit(self):
        r = self.run_cli("compare", "examples/before.mcp.json", "examples/after.mcp.json", "--format", "json", "--show-values")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(json.loads(r.stdout)["status"], "breaking")

    def test_unchanged_exit(self):
        r = self.run_cli("compare", "examples/before.mcp.json", "examples/before.mcp.json")
        self.assertEqual(r.returncode, 0)

    def test_review_exit(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / "a.json", Path(d) / "b.json"
            a.write_text('{"tools":[{"name":"a","inputSchema":{"type":"object"}}]}')
            b.write_text('{"tools":[{"name":"a","description":"changed","inputSchema":{"type":"object"}}]}')
            self.assertEqual(self.run_cli("compare", a, b).returncode, 2)

    def test_error_exit_no_traceback(self):
        r = self.run_cli("compare", "missing.json", "missing.json")
        self.assertEqual(r.returncode, 3)
        self.assertNotIn("Traceback", r.stderr)

    def test_replay_exit(self):
        r = self.run_cli("replay", "examples/after.mcp.json", "examples/calls.jsonl", "--format", "json")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(len(json.loads(r.stdout)["calls"]), 2)

    def test_verify_exit(self):
        r = self.run_cli("verify", "examples/before.mcp.json", "examples/after.mcp.json", "examples/witness.json")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_normalize(self):
        r = self.run_cli("normalize", "examples/openai.json")
        self.assertEqual(r.returncode, 0)
        self.assertIn("inputSchema", json.loads(r.stdout)["tools"][0])

    def test_markdown_escaping(self):
        r = render({"status":"review", "findings":[{"tool":"<script>|`x`\n", "status":"review"}]}, "markdown")
        self.assertNotIn("<script>", r)
        self.assertIn("&#124;", r)

    def test_terminal_escape(self):
        r = render({"status":"review", "findings":[{"tool":"\x1b[2J", "status":"review"}]})
        self.assertNotIn("\x1b", r)

    def test_pagination_rejected(self):
        with self.assertRaises(InputError):
            catalog({"tools":[], "nextCursor":"more"})

    def test_float_overflow_rejected(self):
        with self.assertRaises(InputError):
            parse_json('{"x":1e999}')

    def test_invalid_limit(self):
        r = self.run_cli("compare", "examples/before.mcp.json", "examples/after.mcp.json", "--limit", "0")
        self.assertEqual(r.returncode, 3)


if __name__ == "__main__":
    unittest.main()
