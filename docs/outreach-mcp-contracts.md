# External outreach — mcp-contracts interoperability

Target: `mcp-contracts/mcp-contracts`

Status: **not submitted from this repository**. The connected GitHub App does not have
write access to the external repository, so no upstream issue/PR should be claimed.

## Ready-to-submit upstream issue

### Title

Interop idea: concrete old-valid/new-invalid witnesses from .mcpc.json snapshots

### Body

Hi — I maintain ArgWitness, a deterministic tool for producing a concrete input
that validates against an old tool schema and fails against a new one.

ArgWitness v0.2.0 now accepts the current mcp-contracts v1-style `.mcpc.json`
snapshot shape directly (object-map `tools` keyed by tool name), so a pair of
snapshots can be consumed without a conversion script:

```bash
python -m pip install argwitness==0.2.0
argwitness compare before.mcpc.json after.mcpc.json --show-values
```

The intent is complementary rather than overlapping with `mcpdiff`:
mcp-contracts remains responsible for snapshot capture, classification,
hashes/signatures, resources/prompts, and live conformance. ArgWitness only reads
tool input schemas/metadata and, where bounded search can establish one, returns an
independently revalidated old-valid/new-invalid argument object. If it cannot
establish one, it returns review rather than claiming compatibility.

The adapter is continuously checked against your public fixtures at pinned commit
`5228e7ad71b080c3d56001b3019289703f5dc231`. The CI comparison uses
`server-v1.mcpc.json` and `server-v2-breaking.mcpc.json` and verifies the removed
`delete_contact` tool is reported as an `AW001` break. Separate ArgWitness tests
cover a tightened numeric bound that yields a concrete witness.

Would this be useful enough to mention under integrations/ecosystem docs, or is
there a preferred extension point/format you would want an external witness tool
to target instead?

No change to mcp-contracts is required for the current integration, and I am happy
to adapt the boundary if the snapshot shape has a more appropriate stable surface.

## Evidence rules

- Do not count submitting this issue as adoption.
- Do not count a maintainer reply as a dependent repository/package.
- Count an external integration only after a public external repository actually
  uses ArgWitness or an external maintainer publishes a reproducible case.
- Preserve the public URL and date for any external evidence.
