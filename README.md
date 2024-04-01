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

This project aims to automate maintainence of the markdown files within an Obsidian.md vault.

## Features

- **Filling Missing Aliases**: suggests missing aliases within the YAML frontmatter
- **Bumping Note Status**: scans all notes currently tagged as stubs (`📝/🟥️`) and decide whether to bump its status. In particular, we count the number of links in the body of the note and suggest a status based on that. Note status are as follows:
  - `📝/🟥️`: _Stub_. 0 links.
  - `📝/🟧️`: _Processing_. 1-4 links.
  - `📝/🟩️`: _Evergreen_. 5+ links.
- (planned feature) **Bumping Journal Status**: scans all journal notes tagged as incomplete (`📓/🟥️`) and decides whether to bump its status. In particular, we use ChatGPT to decide whether there are any action items in the note. If there are, it will prompt the user to capture them into a task manager (manual step). When the user indicates they have finished capturing the tasks, the
  - `📓/🟨`: _Captured_. The note contained action items, and the user has finished capturing them into a task manager.
  - `📓/🟩️`: _Processed_. The note contained no action items, and does not need to be processed further.

All edits are presented to the user in a `meld` diff editor, allowing for interactive approval or modification of suggestions.

## Getting Started

### Requirements

- Python 3.11
- Installation of required packages from `poetry.lock` file

### Quickstart

1. Clone the repository to your local machine.
2. Install dependencies using `poetry install`.
3. (Optional) Create a `.env` file in the root directory using `sample.env` as a template.
4. Run `poetry run obsidian-llm --task <task type>` to start the application. Task types include:
   - `aliases`: suggest missing aliases within the YAML frontmatter
   - `bump-note-status`: suggest bumping of a note's status based on the content
   - `bump-journal-status`: suggest bumping of a journal's status based on the content

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

- help fill in missing references
- help link to relevant pages using RAG
- identify pages which are skeletal and try to flesh them out
- auto-update tags on pages based on content
- fix issue where emoticons have double quotes around them
- add @beartype to all functions and add type hints
- consolidate all prompts into prompts/ folder

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
