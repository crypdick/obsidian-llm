import pytest


def list_conflict_files(vault_path: str) -> list:
    """
    Lists all files within the given vault directory that contain git conflict markers.

    :param vault_path: Path to the vault directory.
    :return: List of paths to files that contain conflict markers.
    """
    conflict_files = []
    for root, _, files in os.walk(vault_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                content = f.read()
                if '<<<<<<<' in content or '=======' in content or '>>>>>>>' in content:
                    conflict_files.append(file_path)
    return conflict_files

@pytest.fixture
def vault_path():
    return "./test_vault"
