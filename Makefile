test:
	nox --session=tests

install:
	poetry install

interactive:
	poetry run python

build:
	poetry build

publish:
	poetry publish

update-hooks:
	nox --session=pre-commit -- autoupdate

aliases:
	poetry run obsidian-llm --task aliases

aliases-test:
	poetry run obsidian-llm --task aliases --test-vault

bump-note-status:
	poetry run obsidian-llm --task bump-note-status

bump-patch:
	poetry version patch

merge-syncthing-conflicts:
	poetry run obsidian-llm --task merge-syncthing-conflicts

linkify:
	poetry run obsidian-llm --task linkify