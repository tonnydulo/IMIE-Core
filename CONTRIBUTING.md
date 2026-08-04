# Contributing to IMIE Core

Development work is performed on the `develop` branch.

## Workflow

1. Make and test changes on `develop`.
2. Push the changes to `origin/develop`.
3. Open a pull request from `develop` into `main`.
4. Wait for all required CI checks to pass.
5. Merge the pull request into `main`.

Direct pushes, force pushes, and deletion of the `main` branch are restricted.

## Local validation

Before pushing changes, run:

```powershell
python -m pip check
python -W error::DeprecationWarning -m pytest
```

Packaging-related changes should also be validated with:

```powershell
python -m build
python -m twine check dist/*
```

## Release workflow

Release versions must match in:

- `pyproject.toml`
- `src/imie/version.py`
- the Git tag, using the format `vMAJOR.MINOR.PATCH`

Release tags are created only after CI passes on `main`.
