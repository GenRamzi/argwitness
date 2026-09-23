# Releasing ArgWitness

ArgWitness v0.1.0 was published successfully on 2026-09-23 through PyPI trusted publishing from GitHub Actions.

## Trusted publisher

The PyPI publisher is bound to:

- PyPI project: `argwitness`
- GitHub owner: `GenRamzi`
- Repository: `argwitness`
- Workflow filename: `release.yml`
- Environment name: unset

The release workflow uses `id-token: write`; no long-lived PyPI API token is required.

## Permanent release paths

Releases are intentionally limited to:

1. an immutable `v*` tag whose version exactly matches `pyproject.toml`, or
2. an explicit manual workflow dispatch whose requested version exactly matches `pyproject.toml`.

The one-time issue trigger used to bootstrap v0.1.0 was removed immediately after the successful first publication.

## Release gates

Before any future release:

1. `main` Tests must be green on Python 3.10, 3.12, and 3.13.
2. The Action smoke test must prove that unchanged contracts pass and breaking contracts fail closed.
3. The package job must build wheel/sdist, pass `twine check`, and install the wheel in a clean virtual environment.
4. `pyproject.toml` and `CHANGELOG.md` must agree on the intended version.
5. Launch the workflow only for that exact version.

The release workflow repeats source tests, the demo, dependency checks, build validation, and an installed-wheel smoke test. It publishes through PyPI OIDC, generates SHA-256 checksums, and creates a matching GitHub Release containing the distributions, PyPI attestations, and checksum file.

## v0.1.0 evidence

The first release workflow completed successfully. PyPI accepted both `argwitness-0.1.0-py3-none-any.whl` and `argwitness-0.1.0.tar.gz` and returned the public project/version URL. GitHub Release `v0.1.0` targets commit `885fc13714efc120b97952e43467b24624f7e5aa` and includes the wheel, source distribution, their publish attestations, and `SHA256SUMS`.
