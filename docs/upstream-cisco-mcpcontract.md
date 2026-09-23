# Cisco mcpcontract upstream contribution

Target: `cisco-open/mcptoolkit-contract`

The upstream `spec/implementations.md` explicitly invites tools that support
MCP Description documents to submit a PR adding themselves to the Known
Implementations list.

## Upstream change

In `spec/implementations.md`, under **Tools**, add this row after the existing
Cisco companion tools:

```markdown
| **ArgWitness** | Offline regression-witness checker for MCP Description tool input schemas; compares saved versions and emits a concrete old-valid/new-invalid argument when one can be established | [GenRamzi/argwitness](https://github.com/GenRamzi/argwitness) |
```

## PR title

```text
docs: add ArgWitness to MCP Description implementations
```

## PR body

```markdown
## Summary

Adds ArgWitness to the Known Implementations list for MCP Description tools.

ArgWitness v0.3.0 can consume JSON `mcpdesc` documents directly. For authored
multi-protocol documents with protocol-specific variants of the same tool name,
it requires an explicit `--protocol-version` rather than guessing the intended
effective contract.

## Interoperability evidence

The integration is continuously tested against public fixtures from this
repository at commit:

`fd346ddb245b437e274a9400b73920bf0c017c98`

The pinned CI verifies:

- Cisco's public `multi-protocol.mcpdesc.json` fixture fails closed when no
  protocol view is selected.
- `--protocol-version 2025-11-25` and `--protocol-version 2026-07-28`
  select the corresponding `run_job` variants.
- Two historical Microsoft Learn mcpdesc snapshots are compared without
  overstating evidence: removing an optional property from an open JSON Schema
  returns `review` when no old-valid/new-invalid validator witness exists.

Implementation and validation landed in:

https://github.com/GenRamzi/argwitness/pull/16

Current release:

https://pypi.org/project/argwitness/0.3.0/

This change only updates the implementation registry; it does not add a runtime
dependency or change mcpcontract behavior.

Signed-off-by: Ramzi Sultan <gen.ramzi@outlook.com>
```

## Contribution requirements

Cisco's contributing guide requires DCO sign-off on commits. The upstream commit
must therefore be created with the sign-off line:

```text
Signed-off-by: Ramzi Sultan <gen.ramzi@outlook.com>
```

Do not describe this PR as adoption unless Cisco merges it. An opened PR is an
external contribution attempt; a merged registry entry is stronger public
ecosystem evidence but still does not imply that Cisco depends on ArgWitness.
