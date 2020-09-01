# Shaman API

## Dependencies

This application is a REST API written in Python built using [FastAPI](https://fastapi.tiangolo.com) framework.
It also uses [pymongo](https://api.mongodb.com/python/current/) to interact with [MongoDB](https://www.mongodb.com) database.

## Quick start

It is recommended to have docker installed in order to contribute to the project.

- Deploy MongoDB instances using:

```bash
make dev-environment
```

- Install the package using [`poetry`](https://python-poetry.org):

```bash
poetry install
```

- Start the application and code 😀

```bash
shaman-api dev
```

### Development workflow

### Run the test

Simply run [pytest](https://docs.pytest.org/en/latest/) to run the tests

```bash
pytest
```

### Format the code

[black](https://black.readthedocs.io/en/stable/) is used to format the code. There is no configuration or option required, simply run:

```bash
black src/ tests/
```

### Lint the code

[Flake8](https://flake8.pycqa.org/en/latest/) is used to perform linting. Simply run the tool to perform linting:

```bash
flake8
```

Note: pytest, black and flake8 are configured to integrate with VSCode editor in the [./.vscode/](./.vscode/) directory

### Udate package version

Package version is incremented using [`bump2version`](https://github.com/c4urself/bump2version).
Each version update will create a new commit and a new tag.

#### Patch update

You can also to a patch version upgrade:

```bash
bumpversion patch
```

version `1.0.0` would be upgraded to version `1.0.1` with this command.

#### Minor update

In order to do a minor version upgrade run:

```bash
bumpversion minor
```

Version `1.0.1.` would be upgrade to version `1.1.0` with this command.

#### Major update

In order to do a major version upgrade run:

```bash
bumpversion major
```

Version `1.1.0` would be upgrade to version `2.0.0` with this command.
