from obsidian_llm.io import count_links_in_file
from obsidian_llm.io import list_files_with_tag


def bump_note_status(vault_path: str) -> None:
    """scans all notes currently tagged as stubs (`📝/🟥️`) and decide whether to bump its status.

    In particular, we count the number of links in the body of the note and suggest a status based on that. Note status are as follows:
    - `📝/🟥️`: *Stub*. 0 links.
    - `📝/🟧️`: *Processing*. 1-4 links.
    - `📝/🟩️`: *Evergreen*. 5+ links.
    """
    # Define the status tags
    status_tags = {"📝/🟥️": "Stub", "📝/🟧️": "Processing", "📝/🟩️": "Evergreen"}
    stubs = list_files_with_tag(vault_path, "📝")
    stubs.extend(list_files_with_tag(vault_path, "📝/🟥️"))

    for file_path in stubs:
        num_links = count_links_in_file(file_path)
        bump_note_status_for_file(file_path, num_links, status_tags)
from obsidian_llm.io import parse_frontmatter, read_md
import yaml

def bump_note_status_for_file(file_path: str, num_links: int, status_tags: dict) -> None:
    """
    Updates the status of a note based on the number of links it contains.

    :param file_path: Path to the markdown file.
    :param num_links: Number of links in the note.
    :param status_tags: Dictionary mapping status tags to their descriptions.
    """
    # Determine the new status based on the number of links
    if num_links == 0:
        new_status = "📝/🟥️"  # Stub
    elif 1 <= num_links <= 4:
        new_status = "📝/🟧️"  # Processing
    else:
        new_status = "📝/🟩️"  # Evergreen

    # Read the current frontmatter
    frontmatter_dict, frontmatter_str = parse_frontmatter(file_path)
    if frontmatter_dict is None:
        frontmatter_dict = {}

    # Update the tags in the frontmatter
    if 'tags' in frontmatter_dict:
        if isinstance(frontmatter_dict['tags'], list):
            # Remove old status tags and add the new status
            frontmatter_dict['tags'] = [tag for tag in frontmatter_dict['tags'] if tag not in status_tags]
            frontmatter_dict['tags'].append(new_status)
        elif isinstance(frontmatter_dict['tags'], str):
            # Replace the old status tag with the new status
            if frontmatter_dict['tags'] in status_tags:
                frontmatter_dict['tags'] = new_status
            else:
                frontmatter_dict['tags'] = [frontmatter_dict['tags'], new_status]
    else:
        # No tags present, add the new status
        frontmatter_dict['tags'] = [new_status]

    # Serialize the updated frontmatter back to a YAML string
    updated_frontmatter_content = yaml.dump(frontmatter_dict, default_flow_style=False, sort_keys=False, indent=2)
    updated_frontmatter_content = "---\n" + updated_frontmatter_content + "---\n"

    # Replace the original frontmatter in the file content with the updated frontmatter content
    content = read_md(file_path)
    new_content = content.replace(frontmatter_str, updated_frontmatter_content, 1)

    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.write(new_content)
