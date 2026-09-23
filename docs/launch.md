# Initial adoption work

The next product milestone is useful independent feedback, not a star target.

## One-sentence description

ArgWitness finds concrete calls that break when AI tool schemas change, across
saved MCP, OpenAI, and Anthropic definitions, without executing the tools.

## Current public release

ArgWitness v0.3.0 is published on PyPI and GitHub. It supports direct mcp-contracts
snapshot import plus JSON MCP Description (`mcpdesc`) with explicit protocol
selection, and CI verifies interoperability against pinned public revisions of
mcp-contracts, tool-schema, and Cisco mcpcontract. This is interoperability
evidence, not upstream adoption or endorsement.

## Demo to share

1. Run `python examples/demo.py` in a source checkout.
2. Show the OLD maximum of 100 and NEW maximum of 20.
3. Show the generated call that OLD accepts and NEW rejects.
4. Show the replay result and independent witness verification.
5. Explain that unresolved changes return review, and that this is an alpha.

## Ask early adopters for specific evidence

Invite maintainers you already have permission to contact to try one sanitized
schema migration. Ask what was useful, which witness was missed, and what they
would need to use it in CI. Do not send unsolicited bulk messages or manufacture
issues, dependents, or external contributions.

Potential contribution tasks:

- A real nested-union migration fixture with expected old/new results.
- A safe, bounded method to generate strings for common regex fragments.
- A precise diagnostics improvement for recursive schemas.
- Independently verified Windows installation and CLI instructions.

## Evidence log template

Record public integration URL, independent maintainer, date, issue resolved, and
permission to describe the result. Keep self-owned demonstrations separate.
Measure false breaking findings, missed known counterexamples, and review burden.
Publish methodology before making comparative accuracy or performance claims.

## Application timing

The OSS-program readiness document records today's gaps. A source release can
start an adoption process; it cannot create the historical usage required for
some support tracks. Recheck program terms and actual metrics before submission.

## Current outreach targets

1. `mcp-contracts/mcp-contracts` — direct snapshot interop is implemented and
   continuously tested; the ready-to-submit upstream issue is in
   `docs/outreach-mcp-contracts.md`.
2. `slegarraga/tool-schema` — pinned source interoperability is implemented;
   public GitHub Discussion: https://github.com/slegarraga/tool-schema/discussions/45
3. `cisco-open/mcptoolkit-contract` — pinned mcpdesc interoperability is now
   implemented against real multi-protocol and historical Microsoft Learn fixtures;
   outreach should reference this reproducible result rather than generic promotion.

A failed attempt to write to an external repository because of connector
permissions is not external activity and must not be reported as one.

## Pinned tool-schema interoperability

ArgWitness CI also checks public `slegarraga/tool-schema` source at pinned commit
`56ca752ca2a4d25af17b542259fc75b69aceaba8`. The workflow builds that project,
uses its real `toTool` implementation to generate before/after OpenAI, Anthropic,
and MCP envelopes from the same schema migration, and requires ArgWitness to emit
an independently revalidated breaking witness for all three.

This is technical interoperability evidence only. It is not adoption, endorsement,
or a dependency relationship with tool-schema.

## Pinned Cisco mcpdesc interoperability

ArgWitness CI checks `cisco-open/mcptoolkit-contract` at commit
`fd346ddb245b437e274a9400b73920bf0c017c98`. It verifies explicit
`--protocol-version` selection against Cisco's multi-protocol fixture and checks
the evidence boundary against two historical Microsoft Learn mcpdesc snapshots.

The historical migration demonstrates why ArgWitness is complementary to
rules-based compatibility tooling: removing an optional property from an open
object can be semantically important while still lacking an old-valid/new-invalid
JSON Schema witness. ArgWitness reports `review` instead of overstating evidence.
