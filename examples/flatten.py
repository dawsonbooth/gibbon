from pathlib import Path

from gibbon import Tree

root_src = Path(__file__).parent.parent / "tests/root"
root_dest = Path(__file__).parent.parent / "tests/dest"


def parse(path: Path) -> str:
    print(f"Parsed: {path.name}")
    return path.name


if __name__ == "__main__":
    with Tree(root_src, root_dest=root_dest, glob="**/*.txt", parse=parse) as tree:
        tree.flatten()
