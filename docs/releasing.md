# Releasing ArgWitness

ArgWitness is release-ready in the repository, but registry publication requires one external account setup step.

## PyPI trusted publisher

Before creating the first release tag, configure a **pending trusted publisher** in PyPI for a new project:

- PyPI project name: `argwitness`
- GitHub owner: `GenRamzi`
- Repository: `argwitness`
- Workflow filename: `release.yml`
- Environment: leave unset unless the workflow is changed to use one

PyPI supports pending trusted publishers for projects that do not exist yet. The first successful OIDC publish creates the project; creating the pending publisher alone does not reserve the name.

## Release procedure

1. Confirm main CI and the Action smoke test are green.
2. Confirm `pyproject.toml` and `CHANGELOG.md` describe the same version.
3. Configure the pending PyPI trusted publisher.
4. Create an immutable tag matching the package version, for example `v0.1.0`.
5. The release workflow reruns tests and the demo, builds wheel/sdist, validates metadata, publishes through PyPI OIDC, and creates a GitHub Release with the built artifacts.
6. Confirm both the PyPI project and GitHub Release before changing README wording from source-install to registry-install.

Do not create the tag before the pending publisher exists. A failed publish is not a release.
