from pathlib import Path

from gibbon import Tree

root_folder = Path(__file__).parent.parent / "tests/root"


def parse(path: Path) -> str:
    print(f"Parsed: {path.name}")
    return path.name


def flatten(parsed: str) -> Path:
    print(f"Flattened: {parsed}")
    return root_folder / parsed


if __name__ == "__main__":
    with Tree(root_folder, glob="**/*.txt", parse=parse) as tree:
        tree.transform(flatten)
