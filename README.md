# ArgWitness

**Don't just flag a breaking tool change. Show the call it breaks.**

[English](README.md) · [العربية](README.ar.md) · [Schema support](docs/schema-support.md) · [Design](docs/design.md) · [Contributing](CONTRIBUTING.md)

ArgWitness finds concrete JSON arguments that an old AI tool schema accepts and a new one rejects. It imports saved **MCP**, **OpenAI function tools**, and **Anthropic tools**, searches for counterexamples, shrinks them, and checks captured calls offline.

No API keys. No model calls. No server execution. No telemetry.

> **Alpha v0.1.0.** A confirmed counterexample proves one schema incompatibility. Failing to find one does **not** prove compatibility. Unresolved changes fail CI with `review`, not a green checkmark.

## The problem in one example

You change a search tool's maximum `limit` from `100` to `20`. The tool still exists and simple smoke tests pass. Previously valid agent calls now fail.

ArgWitness produces evidence:

```console
$ argwitness compare examples/before.mcp.json examples/after.mcp.json --show-values
ArgWitness 0.1.0 — BREAKING
  AW002 "search_docs": breaking — Concrete call accepted before and rejected after
    OLD accepts -> NEW rejects (generated)
    {"query": "a", "limit": 100}
```

The arguments are validated against **both** schemas before reporting. `--show-values` is explicit because even schema enums and examples can contain sensitive information.

## Try it in a minute

Requires Python 3.10+. Install from this source checkout (the package has not been published to PyPI):

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install .
python examples/demo.py
```

The demo generates a witness, checks two synthetic calls against the new contract, and independently verifies a saved witness. It requires no live services. Installation downloads dependencies; subsequent analysis is offline.

## Four commands

```bash
# Search for calls that break after a schema change. A detected break exits 1.
argwitness compare before.json after.json

# Add sanitized production-shaped examples; values are omitted from reports by default.
argwitness compare before.json after.json --calls calls.jsonl --format json

# Check captured arguments against a catalog without invoking any tool.
argwitness replay after.json calls.jsonl --format markdown

# Independently recheck {"tool": "name", "arguments": {...}} evidence.
argwitness verify before.json after.json witness.json

# Normalize provider-specific envelopes to a shared tool catalog.
argwitness normalize tools.json
```

Reports support `text`, `json`, and `markdown`. Redirect stdout to save a report. `normalize` always emits JSON and preserves catalog values; it is not a redaction command.

## What it catches

| Change | Evidence |
| --- | --- |
| New required field | A formerly valid call without that field |
| Narrowed enum | A value that was removed |
| Tightened number or length bound | A call on an old/new boundary |
| Number changed to integer | A fractional argument |
| Closed additional properties | A formerly accepted extra property |
| Nested field or array changes | An object containing a rejected nested value |
| Removed tool | A structural removal finding |
| Description, annotations, strict mode, or output schema changed | Human review; input validation cannot establish semantic behavior |

Generated search is deterministic and bounded. It is strongest on common object arguments and scalar/array boundaries. Complex patterns, interacting conditions, large structures, and recursive schemas may need captured calls or human review. See [exact limits](docs/schema-support.md).

## Provider inputs

| Source | Catalog shape | Captured call shape |
| --- | --- | --- |
| MCP | `{"tools":[{"name":"...","inputSchema":{...}}]}` or JSON-RPC `result` | `tools/call` request, or `{tool, arguments}` |
| OpenAI Chat Completions | `[{"type":"function","function":{"name":"...","parameters":{...}}}]` | `{function:{name,arguments}}` |
| OpenAI Responses | `[{"type":"function","name":"...","parameters":{...}}]` | `{type:"function_call",name,arguments}` |
| Anthropic | `[{"name":"...","input_schema":{...}}]` | `{type:"tool_use",name,input}` |

Save tool arrays rather than entire API request bodies. Calls can be JSONL or a JSON array; OpenAI argument strings are decoded as JSON. Combine all MCP catalog pages first. Duplicate tool names and incomplete paginated catalogs are rejected. Tools from different servers need explicit namespacing.

These are **schema-envelope adapters**, not live SDK integrations or provider-conformance certification. See [integration examples](docs/integrations.md).

## Honest CI states

| Exit | Meaning | Suggested action |
| --- | --- | --- |
| `0` | Existing schemas and metadata unchanged, or tools only added | Proceed under your policy; runtime behavior is untested |
| `1` | A breaking witness or removed tool; replay failure; unconfirmed verification | Block and inspect |
| `2` | Change needs review or baseline traffic was invalid | Review; do not silently ignore |
| `3` | Bad input, unsupported schema, missing file, or analysis error | Fix the input/configuration |

If any breaking finding exists, comparison exits `1` even when there are also review findings. A widening input schema returns `review` in this release: there is no schema-inclusion prover.

## Python API

```python
from argwitness import compare, replay, verify_witness

before = {"tools": [{"name": "search", "inputSchema": {"type": "object"}}]}
after = {"tools": [{"name": "search", "inputSchema": {
    "type": "object", "required": ["query"]
}}]}

report = compare(before, after, show_values=True)
assert report["status"] == "breaking"
value = next(f["witness"]["arguments"] for f in report["findings"] if "witness" in f)
assert verify_witness(before, after, {"tool": "search", "arguments": value})["status"] == "confirmed"
```

## Trust boundaries

- The validator is `python-jsonschema`, using Draft 2020-12. `format` is annotation-only. Unknown keywords, unsupported dialects, and external references are rejected.
- Reports omit argument values by default but include tool names, schema paths, and catalog hashes. Those may still be sensitive. Sanitize before sharing.
- JSON Schema regexes can consume CPU. File/search limits are not a security sandbox; process untrusted schemas in a resource-limited environment.
- A witness says nothing about business logic, model routing, authorization, output compatibility, or whether a live server follows its advertised schema.
- Report digests identify normalized input catalogs. They are not signatures, identity attestations, or proof that a server ever exposed a catalog.

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/demo.py
python -m pip install build
python -m build
```

The tests include end-to-end CLI exit behavior, provider envelopes, privacy defaults, and an independent validation check over 144 schema pairs. These are synthetic tests, not evidence of production adoption or a benchmark against other tools.

## Why another tool?

MCP contract diffing already has useful projects, including [mcp-contracts](https://github.com/mcp-contracts/mcp-contracts) and [Cisco mcptoolkit-contract](https://github.com/cisco-open/mcptoolkit-contract). ArgWitness focuses on a small reusable job: **find and independently recheck a concrete breaking input across provider envelopes**, then incorporate sanitized observed calls. It can complement a schema diff pipeline.

We make no first-of-its-kind, performance, or superiority claim. See [positioning and sources](docs/positioning.md). The most useful next contribution is a small real schema change where the generated search misses a counterexample.

## License

MIT. Maintained by GenRamzi. No affiliation with or endorsement from Anthropic, OpenAI, or the MCP project.
