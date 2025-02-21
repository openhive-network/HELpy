# HELpy and Beekeepy

<a href="https://gitlab.syncad.com/hive/helpy/-/commits/develop" target="_blank" rel="noopener noreferrer" data-qa-selector="badge_image_link" data-qa-link-url="https://gitlab.syncad.com/hive/helpy/-/commits/develop" style=""><img src="https://gitlab.syncad.com/hive/helpy/badges/develop/pipeline.svg" aria-hidden="true" class="project-badge"></a>

# Python Projects: HELpy & Beekeepy

This repository contains two Python projects: **HELpy** and **Beekeepy**. The projects are managed using `poetry`, linters can be run using the following command:

```bash
pre-commit run --all
```

## Projects

1. **HELpy**: Hive Execution Layer. More information in [`helpy/README.md`](../wax/wax/python/wax/helpy/README.md)
2. **Beekeepy**: A project that depends on **HELpy**.  More information in [`beekeepy/README.md`](beekeepy/README.md)

## Installation

Each project can be installed separately by navigating into the project directory:


For **HELpy**:

```bash
cd helpy
poetry install
```

For **Beekeepy**:

```bash
cd beekeepy
poetry install
```

## Development Setup

For development purposes, it is recommended to install all dependencies by insta the `local-tools` subproject located in the `tests/local-tools` directory. This package contains all the necessary linters and installs both **Helpy** and **Beekeepy** in editable mode.

To install `local-tools`, run the following commands:

```bash
cd tests/local-tools
poetry install
```

This setup ensures a proper development environment with all tools and dependencies in place.
