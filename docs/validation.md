# Release validation record

Date: 2026-09-23.

This record distinguishes deterministic implementation/release evidence from external adoption. Publication and CI success are verified; live-provider behavior and independent downstream use are not inferred from them.

## Release evidence

| Check | Verified result |
| --- | --- |
| GitHub `main` tests | Passed on Python 3.10, 3.12, and 3.13 |
| GitHub Action smoke test | Passed; unchanged succeeds and a breaking contract fails closed |
| Source unit/subprocess tests | 54 tests in the release validation path |
| Soundness fixture matrix | 144 schema pairs; emitted witnesses are independently revalidated |
| Package build | Wheel and source distribution built successfully |
| `twine check` | Passed for wheel and source distribution |
| Clean installed-wheel smoke test | Passed outside the source checkout |
| PyPI trusted publication | `argwitness==0.1.0` accepted through GitHub OIDC |
| PyPI digital attestations | Generated for both wheel and source distribution |
| GitHub Release | `v0.1.0` published successfully |
| GitHub Release assets | wheel, sdist, both publish attestations, and `SHA256SUMS` |

The release workflow's PyPI publisher returned the public version URL `https://pypi.org/project/argwitness/0.1.0/`.

## Package digests observed during trusted publication

- wheel subject SHA-256: `4d366c6e9f209a19c5a8ba86c52afc539ad7c521549c590f9d44631ad66e8a32`
- source distribution subject SHA-256: `14adc4d0856eeea64273fb76dc2e177bb659120fe1d9edaad408f786b64692dc`

GitHub Release also ships a generated `SHA256SUMS` covering the release files present after trusted publication.

## Scope limits

The fixtures are synthetic. This evidence does not establish production adoption, provider API conformance, server behavior, model tool-selection quality, Windows/macOS coverage, or resistance to adversarial resource exhaustion. A concrete witness proves one incompatibility; failure to generate one does not certify compatibility.

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
python -m pip install argwitness==0.1.0
argwitness --version
```

## v0.2.0 interoperability validation

The release adds direct parsing for mcp-contracts v1-style snapshots where `tools` is an object map. CI verifies name derivation, metadata preservation, embedded-name conflict rejection, and a concrete old-valid/new-invalid witness for a tightened numeric bound. The release passed Python 3.10/3.12/3.13, Action smoke testing, package build, `twine check`, and clean-wheel installation before trusted publication.

## Pinned upstream interoperability fixture

CI checks the parser against public snapshot fixtures from `mcp-contracts/mcp-contracts`
at commit `5228e7ad71b080c3d56001b3019289703f5dc231`. The workflow compares the
upstream `server-v1.mcpc.json` and `server-v2-breaking.mcpc.json` fixtures and
asserts that the removed `delete_contact` tool is reported as `AW001` breaking.

This demonstrates compatibility with that pinned public snapshot shape. It is not
evidence that mcp-contracts endorses, depends on, or adopts ArgWitness, and it does
not imply compatibility with future snapshot-format changes.
