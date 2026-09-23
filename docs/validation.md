# Release validation record

Date: 2026-09-23.

This record distinguishes deterministic implementation/release evidence from external adoption. Publication and CI success are verified; live-provider behavior and independent downstream use are not inferred from them.

## Current release evidence — v0.3.0

| Check | Verified result |
| --- | --- |
| GitHub `main` tests | Passed on Python 3.10, 3.12, and 3.13 |
| GitHub Action smoke test | Passed; unchanged succeeds and a breaking contract fails closed |
| Source unit/subprocess tests | 61 tests in the v0.3.0 release validation path |
| Soundness fixture matrix | 144 schema pairs; emitted witnesses are independently revalidated |
| Package build | Wheel and source distribution built successfully |
| `twine check` | Passed for wheel and source distribution |
| Clean installed-wheel smoke test | Passed outside the source checkout |
| mcp-contracts interoperability | Passed against pinned public upstream fixtures |
| tool-schema interoperability | Passed against pinned public upstream source-generated OpenAI/Anthropic/MCP envelopes |
| Cisco mcpdesc interoperability | Passed against pinned public multi-protocol and historical Microsoft Learn fixtures |
| PyPI trusted publication | `argwitness==0.3.0` accepted through GitHub OIDC |
| PyPI digital attestations | Generated for both wheel and source distribution |
| GitHub Release | `v0.3.0` published successfully |
| GitHub Release assets | wheel, sdist, both publish attestations, and `SHA256SUMS` |

The release publisher returned the public version URL `https://pypi.org/project/argwitness/0.3.0/`.

## v0.3.0 attested subject digests

- wheel SHA-256: `272466d559ce31bf7ed3a65c5793297d3cd211cb85a4aa1a85cacacaf8c949bb`
- source distribution SHA-256: `4ce514c100120f40965ec045951dd27b277af31588975567fac12ede5b90984e`

GitHub Release also ships a generated `SHA256SUMS` covering the published release files.

## mcp-contracts interoperability

CI checks public snapshot fixtures from `mcp-contracts/mcp-contracts` at commit
`5228e7ad71b080c3d56001b3019289703f5dc231`. The workflow compares
`server-v1.mcpc.json` with `server-v2-breaking.mcpc.json` and verifies that
the removed `delete_contact` tool is reported as `AW001` breaking.

## tool-schema interoperability

CI checks public `slegarraga/tool-schema` source at commit
`56ca752ca2a4d25af17b542259fc75b69aceaba8`. It builds that project and uses
its real `toTool` implementation to generate before/after OpenAI, Anthropic,
and MCP envelopes for the same schema migration. ArgWitness must emit an
independently revalidated old-valid/new-invalid witness for all three outputs.

## Cisco mcpcontract / mcpdesc interoperability

CI checks `cisco-open/mcptoolkit-contract` at commit
`fd346ddb245b437e274a9400b73920bf0c017c98`.

The public `multi-protocol.mcpdesc.json` fixture proves that ArgWitness fails
closed when duplicate protocol-specific tool variants are ambiguous and that
`--protocol-version` selects the intended effective view.

CI also compares two historical public Microsoft Learn mcpdesc snapshots from
that repository. The migration removes an optional `question` property from an
open object schema. Because the newer JSON Schema still accepts unknown
properties, ArgWitness returns `review` rather than fabricating a concrete
validator-level witness. This preserves the distinction between semantic/rules-
based compatibility analysis and a demonstrated old-valid/new-invalid input.

These pinned checks demonstrate interoperability with those specific upstream
revisions. They are not evidence that the upstream projects endorse, depend on,
or adopt ArgWitness.

## Scope limits

A concrete witness proves one input-schema incompatibility; failure to generate one does not certify compatibility. The evidence does not establish production adoption, provider API conformance, live server behavior, model tool-selection quality, Windows/macOS coverage, or resistance to adversarial resource exhaustion.

## Reproduce from source

```bash
python -m pip install .
python -m unittest discover -s tests -v
python examples/demo.py
python -m build
python -m twine check dist/*
```

## Reproduce from registry

```bash
python -m pip install argwitness==0.3.0
argwitness --version
```
