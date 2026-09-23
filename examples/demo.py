"""Run after installation: python examples/demo.py. No API keys or network."""
from pathlib import Path
from argwitness import compare, replay, verify_witness
from argwitness.cli import load_calls, render
from argwitness.contracts import read_json

root = Path(__file__).parent
before = read_json(root / "before.mcp.json")
after = read_json(root / "after.mcp.json")
observed = load_calls(root / "calls.jsonl")
print("1. Find a breaking call without any recorded traffic")
report = compare(before, after, show_values=True)
print(render(report))
assert report["status"] == "breaking"
print("2. Replay sanitized captured arguments, without executing tools")
result = replay(after, observed)
print(render(result))
assert [c["status"] for c in result["calls"]] == ["invalid", "valid"]
print("3. Independently verify a concrete witness")
result = verify_witness(before, after, read_json(root / "witness.json"))
print(render(result))
assert result["status"] == "confirmed"
