from pathlib import Path

from gibbon import Tree

root_folder = Path(__file__).parent / "root"

original_hierarchy = set(root_folder.rglob("*.*"))


def parse(path: Path) -> str:
    return path.name


def organize(name: str) -> Path:
    stem = name[: name.index(".")]
    if stem.isalpha():
        return root_folder / "alpha" / name
    elif stem.isnumeric():
        if bool(int(stem) % 2):
            return root_folder / "numeric" / "odd" / name
        else:
            return root_folder / "numeric" / "even" / name
    else:
        return root_folder / "ERROR"


def flatten(name: str) -> Path:
    return root_folder / name


def restore():
    with Tree(root_folder, parse=parse) as tree:
        tree.transform(flatten)


def test_flatten():
    with Tree(root_folder, parse=parse) as tree:
        tree.transform(flatten)

    hierarchy = set(root_folder.glob("*.*"))

    assert hierarchy == original_hierarchy

    restore()


def test_organize():
    with Tree(root_folder, parse=parse) as tree:
        tree.transform(organize)

    hierarchy = set(root_folder.rglob("*.*"))

    assert len(hierarchy) == len(original_hierarchy)
    assert hierarchy != original_hierarchy

    restore()
