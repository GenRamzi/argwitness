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

Install a reviewed, immutable revision of ArgWitness (replace `REVIEWED_SHA` before
use; no published release is assumed):

```bash
python -m pip install 'git+https://github.com/GenRamzi/argwitness.git@REVIEWED_SHA'
argwitness compare contracts/baseline.json contracts/candidate.json --format markdown
```

Both exits `1` and `2` should block unattended approval. Never append `|| true` to
make contract checks green. Protect the baseline through normal repository review;
letting an untrusted patch rewrite both versions defeats the comparison.

The project's own workflow runs tests without secrets on `pull_request`, not
`pull_request_target`. The workflow matrix is configuration, not evidence of runs
that have not occurred. See the validation record for checks actually executed.

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
