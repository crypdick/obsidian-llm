# Obsidian Llm

[![PyPI](https://img.shields.io/pypi/v/obsidian-llm.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/obsidian-llm.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/obsidian-llm)][python version]
[![License](https://img.shields.io/pypi/l/obsidian-llm)][license]

[![Read the documentation at https://obsidian-llm.readthedocs.io/](https://img.shields.io/readthedocs/obsidian-llm/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/crypdick/obsidian-llm/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/crypdick/obsidian-llm/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/obsidian-llm/
[status]: https://pypi.org/project/obsidian-llm/
[python version]: https://pypi.org/project/obsidian-llm
[read the docs]: https://obsidian-llm.readthedocs.io/
[tests]: https://github.com/crypdick/obsidian-llm/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/crypdick/obsidian-llm
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

# Obsidian.md Vault Improvement Assistant

This project aims to optimize the organization of markdown files within an Obsidian.md vault by suggesting enhancements for the YAML frontmatter, specifically by proposing additional aliases. Utilizing a CLI interface and leveraging the AutoGPT library, it dynamically generates alias suggestions, thereby improving the user's workflow and the functionality of their Obsidian vault.

## Overview

The application employs a backend-centric architecture within a CLI environment, focusing on direct file-based interactions with the Obsidian vault. It uses Python as the core programming language, supported by libraries like Click for CLI interactions, AutoGPT for intelligent alias suggestion generation, and Meld for diff presentation. The project structure includes key components such as CLI interpreter (`cli.py`), Markdown enumerator (`markdown_enumerator.py`), Frontmatter verifier (`frontmatter_verifier.py`), Alias suggester (`alias_suggester.py`), among others.

## Features

1. **CLI Interface**: Simplifies the process of executing the utility and passing the Obsidian vault path as a parameter.
2. **Markdown File Identification**: Automatically identifies `.md` files within the specified Obsidian vault.
3. **YAML Frontmatter Inspection**: Checks each markdown file for a YAML frontmatter section and evaluates it.
4. **Alias Proposition**: Utilizes AutoGPT to generate and suggest new aliases based on the document's title.
5. **Interactive Diff Editing**: Presents suggested aliases to the user via the `meld` diff editor, allowing for interactive approval or modification of suggestions.

## Getting Started

### Requirements

- Python 3.6 or newer
- Installation of required packages from `requirements.txt`

### Quickstart

1. Clone the repository to your local machine.
2. Install dependencies using `pip install -r requirements.txt`.
3. Run `python cli.py --vault_path [your_vault_path]` to start the application.

## Usage

Please see the [Command-line Reference] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_Obsidian Llm_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## TODO

* help fill in missing references
* help link to relevant pages using RAG
* identify pages which are skeletal and try to flesh them out
* auto-update tags on pages based on content
* fix issue where emoticons have double quotes around them
* add @beartype to all functions and add type hints


## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/crypdick/obsidian-llm/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/crypdick/obsidian-llm/blob/main/LICENSE
[contributor guide]: https://github.com/crypdick/obsidian-llm/blob/main/CONTRIBUTING.md
[command-line reference]: https://obsidian-llm.readthedocs.io/en/latest/usage.html
