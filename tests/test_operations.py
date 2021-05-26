from pathlib import Path

from gibbon import Tree

root_folder = Path(__file__).parent / "root"

original_hierarchy = set(root_folder.rglob("*.*"))


def parse(path: Path) -> str:
    return path.stem


def alpha_or_numeric(stem: str) -> str:
    if stem.isalpha():
        return "alpha"
    elif stem.isnumeric():
        return "numeric"
    return "other"


def restore():
    with Tree(root_folder, glob="**/*.txt", parse=parse) as tree:
        tree.flatten()


def test_flatten():
    with Tree(root_folder, glob="**/*.txt", parse=parse) as tree:
        tree.flatten()

    hierarchy = set(root_folder.glob("*.*"))

    assert hierarchy == original_hierarchy

    restore()


def test_organize():
    with Tree(root_folder, glob="**/*.txt", parse=parse) as tree:
        tree.organize((alpha_or_numeric,))

    hierarchy = set(root_folder.rglob("*.*"))

    assert len(hierarchy) == len(original_hierarchy)
    assert hierarchy != original_hierarchy

    restore()
