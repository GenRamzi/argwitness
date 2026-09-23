# Integration recipes

## Saved tool definitions

Export definitions from your application or a trusted catalog-export workflow.
ArgWitness does not connect to MCP servers and does not initialize or spawn them.
For MCP pagination, combine the `tools` arrays from every page into one object
and omit `nextCursor` only after all pages are present.

OpenAI function tools may use nested Chat Completions envelopes or flat Responses
envelopes. Anthropic definitions use `input_schema`. Native hosted/built-in tools,
custom free-form tools, and full SDK request bodies are not supported.

The adapters preserve strict mode, annotations, descriptions, and other metadata
for review. They do not implement each provider's extra schema restrictions, nor
does accepting a catalog prove that a provider will accept that API request.

## mcp-contracts snapshot interop

ArgWitness can consume the current v1-style `.mcpc.json` snapshot shape from
[mcp-contracts](https://github.com/mcp-contracts/mcp-contracts) directly. The
snapshot's object-map tool keys become tool names, so no conversion script is
required:

```bash
argwitness compare contracts/v1.mcpc.json contracts/v2.mcpc.json --show-values
```

This interop is intentionally narrow and complementary. ArgWitness reads tool
`inputSchema` plus tool metadata in order to find old-valid/new-invalid inputs.
It does **not** verify mcp-contracts content hashes or signatures, connect to the
server, or analyze snapshot resources/prompts. Use mcp-contracts itself for those
responsibilities.

## Cisco mcpcontract / MCP Description interop

ArgWitness can consume JSON MCP Description (`mcpdesc`) documents directly when
the effective tool names are unique. For authored multi-protocol documents where
the same tool name has protocol-specific variants, select one view explicitly:

```bash
argwitness compare before.mcpdesc.json after.mcpdesc.json \
  --protocol-version 2026-07-28 \
  --format json
```

The GitHub Action exposes the same setting as `protocol-version`.

ArgWitness deliberately fails with input-error exit `3` when a multi-protocol
document contains duplicate tool variants and no protocol version is selected.
It does not guess which protocol contract the caller intended.

Pinned CI checks this behavior against
`cisco-open/mcptoolkit-contract` commit
`fd346ddb245b437e274a9400b73920bf0c017c98`, including Cisco's public
`multi-protocol.mcpdesc.json` fixture. A second CI check compares two public
historical Microsoft Learn mcpdesc snapshots from that repository. That real
migration removes an optional `question` property from an open object schema;
because the newer JSON Schema still accepts unknown properties, ArgWitness
returns `review` rather than inventing a concrete validator-level witness.

This is complementary to mcpcontract's semantic/rules-based compatibility
analysis. ArgWitness only claims a breaking input when OLD accepts it and NEW
rejects it under the advertised input schemas.

## Captured calls

Create sanitized JSONL records:

```json
{"tool":"search_docs","arguments":{"query":"public docs","limit":50}}
```

Then:

```bash
argwitness compare baseline.json candidate.json --calls sanitized-calls.jsonl --format json
```

`replay` is shorthand for validation of arguments against saved schemas. It never
replays side effects or contacts a live server. Record formats are documented in
the README; tool results and transcripts are not accepted as call records.

## CI in another repository

Prefer the bundled GitHub Action and pin the latest reviewed immutable release tag or commit:

```yaml
name: Tool contract compatibility
on:
  pull_request:
permissions:
  contents: read

jobs:
  argwitness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: GenRamzi/argwitness@v0.2.0
        with:
          before: contracts/baseline.json
          after: contracts/candidate.json
          calls: contracts/sanitized-calls.jsonl
          format: markdown
          report: artifacts/argwitness.md
```

The Action constrains input and report paths to `GITHUB_WORKSPACE`, suppresses raw
argument values by default, and fails for breaking, review, and input-error states.
Protect the baseline through normal repository review; letting an untrusted patch
rewrite both versions defeats the comparison.

The CLI remains useful when a GitHub Action is not appropriate:

```bash
python -m pip install 'argwitness==0.2.0'
argwitness compare contracts/baseline.json contracts/candidate.json --format markdown
```

Never append `|| true` to make contract checks green. The project's workflows run
without secrets on `pull_request`, not `pull_request_target`. See the validation
record for checks actually executed.

## Agent instructions

You can add the following instruction to an existing agent workflow:

> When changing tool arguments, compare the saved baseline and candidate with
> ArgWitness. Fix or explain breaking/review findings. Include a sanitized witness
> for any intentional breaking change. Never describe exit 2 as compatible.

This is a command-line integration, not a packaged Claude/Codex plugin or MCP server.

## Official envelope references

- [MCP tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
- [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [Anthropic tool definitions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools)
