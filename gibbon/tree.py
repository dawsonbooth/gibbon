from __future__ import annotations

import os
import shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Callable, Generic, List, Tuple, Union

from tqdm import tqdm

from .types import T


class Tree(Generic[T]):
    root: Path
    glob: str
    # parse: Callable[[Path], T]  # FIXME: https://github.com/python/mypy/issues/708
    show_progress: bool

    sources: Tuple[Path, ...]
    destinations: List[Path]
    transformations: List[Callable[[T], Path]]  # FIXME: https://github.com/python/mypy/issues/3737
    should_resolve: bool

    def __init__(
        self,
        root_folder: Union[str, os.PathLike[str]],
        glob: str = "**/*.*",
        parse: Callable[[Path], T] = Path,  # type: ignore  # FIXME: https://github.com/python/mypy/issues/3737
        show_progress: bool = False,
    ):
        self.root = Path(root_folder)
        self.glob = glob
        self.parse = parse
        self.show_progress = show_progress
        self.reset()

    def reset(self) -> Tree:
        self.sources = tuple(self.root.glob(self.glob))
        self.destinations = list(self.sources)
        self.transformations = list()

        return self

    def transform(self, *transformations: Callable[[T], Path]) -> None:
        for transform in transformations:
            self.transformations.append(transform)

    def resolve(self) -> Tree:
        with ProcessPoolExecutor() as executor:
            parsed_sources = executor.map(self.parse, self.sources)
        destinations = self.destinations
        if self.show_progress:
            parsed_sources = tqdm(parsed_sources, desc="Process paths", total=len(self.sources))
            destinations = tqdm(destinations, desc="Move paths")

        for i, parsed_source in enumerate(parsed_sources):
            # Perform transformations
            try:
                for transform in self.transformations:
                    self.destinations[i] = transform(parsed_source)
            except Exception as e:
                self.destinations[i] = self.root / e.__class__.__name__ / self.destinations[i].name

        for i, destination in enumerate(destinations):
            # Rename if duplicate
            num_duplicates = 0
            new_name = destination.name
            while True:
                renamed = False
                for j, other in enumerate(self.destinations):
                    if new_name == other.name and i != j:
                        num_duplicates += 1
                        renamed = True
                        new_name = f"{destination.stem} ({num_duplicates}){destination.suffix}"

                if not renamed:
                    self.destinations[i] = destination.parent / new_name
                    break

            # Move file
            os.makedirs(destination.parent, exist_ok=True)
            shutil.move(str(self.sources[i]), str(self.destinations[i]))

        # Remove empty folders
        for path in self.root.rglob("*"):
            if path.is_dir() and len([p for p in path.rglob("*") if not p.is_dir()]) == 0:
                if path.exists():
                    shutil.rmtree(path)

        self.reset()

        return self

    def __enter__(self) -> Tree[T]:
        return self

    def __exit__(self, *args) -> None:
        if None in args:
            self.resolve()
