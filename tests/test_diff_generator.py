import logging
from tempfile import NamedTemporaryFile

from obsidian_llm.diff_generator import generate_diff_and_update
from obsidian_llm.frontmatter_verifier import parse_frontmatter
from obsidian_llm.frontmatter_verifier import verify_frontmatter


# set logging level to INFO
logging.basicConfig(level=logging.INFO)


def test_generate_diff_and_update_without_frontmatter():
    file_path = "./tests/test_vault/without_frontmatter.md"

    # do not edit the original file. instead, create a copy as a temporary file
    with NamedTemporaryFile(mode="w+", suffix=".md") as tmp_file:
        with open(file_path, "r") as original_file:
            content = original_file.read()
            tmp_file.write(content)
            tmp_file.seek(0)

        tmp_frontmatter = parse_frontmatter(content)
        assert (
            tmp_frontmatter is None
        ), f"Expected no frontmatter, but found: {tmp_frontmatter}"
        generate_diff_and_update(
            tmp_file.name,
            new_aliases=None,
            frontmatter_dict=tmp_frontmatter,
            content=content,
        )


def test_generate_diff_and_update_with_frontmatter_no_alias():
    file_path = "./tests/test_vault/with_frontmatter.md"

    print("Testing with frontmatter and no existing aliases")

    # do not edit the original file. instead, create a copy as a temporary file
    with NamedTemporaryFile(mode="w+", suffix=".md") as tmp_file:
        with open(file_path, "r") as original_file:
            content = original_file.read()
            tmp_file.write(content)
            # reset pointer
            tmp_file.seek(0)

        tmp_frontmatter, _asstr = verify_frontmatter(tmp_file.name)
        generate_diff_and_update(
            tmp_file.name,
            new_aliases=["alias1", "alias2"],
            frontmatter_dict=tmp_frontmatter,
            content=content,
        )

        # new file should have the new aliases in the frontmatter
        frontmatter, _asstr = verify_frontmatter(tmp_file.name)
    assert isinstance(
        frontmatter, dict
    ), f"Expected frontmatter, but found: {frontmatter}"
    assert (
        "aliases" in frontmatter
    ), f"Expected 'aliases' key in frontmatter, but found: {frontmatter}"
    for alias in ["alias1", "alias2"]:
        assert (
            alias in frontmatter["aliases"]
        ), f"Expected '{alias}' in aliases, but found: {frontmatter['aliases']}"


def test_generate_diff_and_update_with_existing_alias():
    file_path = "./tests/test_vault/with_frontmatter_and_alias.md"

    print("Testing with frontmatter and existing aliases (list format)")

    # do not edit the original file. instead, create a copy as a temporary file
    with NamedTemporaryFile(mode="w+", suffix=".md") as tmp_file:
        with open(file_path, "r") as original_file:
            content = original_file.read()
            tmp_file.write(content)
            tmp_file.seek(0)

        tmp_frontmatter, _asstr = verify_frontmatter(tmp_file.name)
        generate_diff_and_update(
            tmp_file.name,
            new_aliases=["alias1", "alias2"],
            frontmatter_dict=tmp_frontmatter,
            content=content,
        )

        # new file should have the new aliases in the frontmatter
        frontmatter, _asstr = verify_frontmatter(tmp_file.name)
    assert isinstance(
        frontmatter, dict
    ), f"Expected frontmatter, but found: {frontmatter}"
    assert (
        "aliases" in frontmatter
    ), f"Expected 'aliases' key in frontmatter, but found: {frontmatter}"
    for alias in ["alias1", "alias2"]:
        assert (
            alias in frontmatter["aliases"]
        ), f"Expected '{alias}' in aliases, but found: {frontmatter['aliases']}"
    for alias in ["existing_alias1", "existing_alias2"]:
        assert (
            alias in frontmatter["aliases"]
        ), f"Expected '{alias}' in aliases, but found: {frontmatter['aliases']}"


def test_generate_diff_and_update_with_existing_alias_yaml():
    file_path = "./tests/test_vault/with_frontmatter_and_alias_yaml.md"

    print("Testing with frontmatter and existing aliases (YAML format)")

    # do not edit the original file. instead, create a copy as a temporary file
    with NamedTemporaryFile(mode="w+", suffix=".md") as tmp_file:
        with open(file_path, "r") as original_file:
            content = original_file.read()
            tmp_file.write(content)
            tmp_file.seek(0)
        tmp_frontmatter, _asstr = verify_frontmatter(tmp_file.name)
        generate_diff_and_update(
            tmp_file.name,
            new_aliases=["alias1", "alias2"],
            frontmatter_dict=tmp_frontmatter,
            content=content,
        )

        # new file should have the new aliases in the frontmatter
        frontmatter, _asstr = verify_frontmatter(tmp_file.name)
    assert isinstance(
        frontmatter, dict
    ), f"Expected frontmatter, but found: {frontmatter}"
    assert (
        "aliases" in frontmatter
    ), f"Expected 'aliases' key in frontmatter, but found: {frontmatter}"
    for alias in ["alias1", "alias2"]:
        assert (
            alias in frontmatter["aliases"]
        ), f"Expected '{alias}' in aliases, but found: {frontmatter['aliases']}"
    for alias in ["existing_alias1", "existing_alias2"]:
        assert (
            alias in frontmatter["aliases"]
        ), f"Expected '{alias}' in aliases, but found: {frontmatter['aliases']}"
