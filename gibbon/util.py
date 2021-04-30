import os
import shutil
from pathlib import Path


def safe_move(source: Path, destination: Path) -> None:
    if source == destination:
        return

    if not destination.parent.exists():
        os.makedirs(destination.parent)
        shutil.move(str(source), str(destination))
        return

    if not destination.exists():
        shutil.move(str(source), str(destination))
        return

    stem, suffix = destination.stem, destination.suffix
    destination = destination.parent / f"{stem} (1){suffix}"

    i = 1
    while destination.exists():
        destination = destination.parent / f"{stem} ({i}){suffix}"
        i += 1

    shutil.move(str(source), str(destination))


def is_empty(folder: Path, ignore_dirs: bool = False):
    for f in folder.rglob("*"):
        if not ignore_dirs or (ignore_dirs and not f.is_dir()):
            return False
    return True
