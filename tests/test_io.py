from tempfile import NamedTemporaryFile

from obsidian_llm.io import count_links_in_file


def test_count_links_in_file():
    """
    Test the count_links_in_file function with a temporary markdown file.
    """
    with NamedTemporaryFile(mode="w+", suffix=".md", delete=False) as tmp:
        # Write content with WikiLinks to the temporary file
        content = "This is a test file with [[WikiLink1]] and [[WikiLink2]]."
        tmp.write(content)
        tmp.seek(0)  # Go back to the start of the file
        # Count the links in the temporary file
        link_count = count_links_in_file(tmp.name)
        assert link_count == 2, "The link count should be 2."

        # Write content without WikiLinks to the temporary file
        tmp.truncate(0)  # Clear the file
        tmp.seek(0)  # Go back to the start of the file
        content = "This is a test file without WikiLinks."
        tmp.write(content)
        tmp.seek(0)  # Go back to the start of the file
        # Count the links in the temporary file
        link_count = count_links_in_file(tmp.name)
        assert link_count == 0, "The link count should be 0."
