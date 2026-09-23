# Releasing ArgWitness

ArgWitness is release-ready in the repository. The first registry publication requires a **Pending Trusted Publisher** in PyPI because the project does not yet exist there.

## PyPI pending trusted publisher

In PyPI, open your account's **Publishing** page and add a GitHub Actions pending publisher with exactly:

- PyPI project name: `argwitness`
- GitHub owner: `GenRamzi`
- Repository: `argwitness`
- Workflow filename: `release.yml`
- Environment name: leave blank

The project metadata also uses the exact normalized name `argwitness`. A pending publisher does not reserve the name; the first successful OIDC publication creates the PyPI project and converts the pending publisher into a normal trusted publisher.

## Release gates

Before publishing `v0.1.0`:

1. `main` Tests must be green on Python 3.10, 3.12, and 3.13.
2. The Action smoke test must prove that unchanged contracts pass and breaking contracts fail closed.
3. The package job must build wheel/sdist, pass `twine check`, and install the wheel in a clean virtual environment.
4. `pyproject.toml` and `CHANGELOG.md` must both describe `0.1.0`.
5. The Pending Trusted Publisher must be configured in PyPI with the values above.
6. Launch the release only for exact version `0.1.0`.

The release workflow repeats source tests, the demo, dependency checks, build validation, and an installed-wheel smoke test. It then creates SHA-256 checksums, publishes through PyPI OIDC, and creates a matching GitHub Release with the distributions and checksums.

Do not describe `0.1.0` as published until both PyPI and the GitHub Release confirm it.
