# Changelog

## 0.2.0 — 2026-09-23

- Add direct import of mcp-contracts v1-style `.mcpc.json` snapshots with object-map tools.
- Preserve tool metadata while deriving tool names from snapshot map keys.
- Reject conflicting embedded names rather than silently choosing one.
- Document the interoperability boundary: tool schemas only; no snapshot hash/signature or resource/prompt verification.

## 0.1.0 — 2026-09-23

- MCP, OpenAI function, and Anthropic catalog/call envelope adapters.
- Bounded counterexample generation and structural shrinking.
- Offline observed-call validation and independent witness rechecking.
- Distinct breaking, review, unchanged, added, and input-error states.
- Text, JSON, and Markdown reports with argument values omitted by default.
- Python API, command line interface, synthetic demo, and regression tests.
- Fail-closed GitHub Action with workspace-bounded paths and privacy-preserving defaults.
- Tag-gated GitHub/PyPI release automation using OIDC trusted publishing.

Published to PyPI as `argwitness==0.1.0` through GitHub OIDC trusted publishing, with digital attestations for the wheel and source distribution and matching GitHub Release artifacts/checksums.

Live provider verification and independent adoption are not claimed.
