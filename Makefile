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

bump-patch:
	poetry version patch
