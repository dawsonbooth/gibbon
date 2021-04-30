from __future__ import annotations

import os
import shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Callable, Generic, Iterable, List, Optional, Tuple, Union

from tqdm import tqdm

from .types import T
from .util import is_empty, safe_move


class Tree(Generic[T]):
    root: Path
    glob: str
    parse: Optional[Callable[[Path], T]]
    show_progress: bool

    sources: Tuple[Path, ...]
    transformations: List[Callable[[T], Path]]

    def __init__(
        self,
        root_folder: Union[str, os.PathLike[str]],
        glob: str,
        parse: Optional[Callable[[Path], T]] = None,
        show_progress: bool = False,
    ):
        self.root = Path(root_folder)
        self.glob = glob
        self.parse = parse
        self.show_progress = show_progress
        self.refresh()

    def refresh(self) -> Tree:
        self.sources = tuple(self.root.glob(self.glob))
        self.transformations = list()

        return self

    def transform(self, *transformations: Callable[[T], Path]) -> None:
        for transform in transformations:
            self.transformations.append(transform)

    def resolve(self) -> Tree:
        # Parse files
        parsed_sources: Iterable[Tuple]
        if self.parse is not None:
            with ProcessPoolExecutor() as executor:
                parsed_sources = zip(self.sources, executor.map(self.parse, self.sources))
        else:
            parsed_sources = zip(self.sources, self.sources)

        # Perform transformations
        if self.show_progress:
            parsed_sources = tqdm(parsed_sources, desc="Process files", total=len(self.sources))

        destinations = list()
        for source, parsed in parsed_sources:
            destination = source
            try:
                for transform in self.transformations:
                    # TODO: Figure out better framework for transformations
                    destination = transform(parsed)
            except Exception as e:
                destination = self.root / e.__class__.__name__ / destination.name
            destinations.append(destination)

        # Move files
        paths = zip(self.sources, destinations)

        if self.show_progress:
            paths = tqdm(paths, desc="Move files", total=len(self.sources))

        for source, destination in paths:
            safe_move(source, destination)
            if is_empty(source.parent, ignore_dirs=True):
                shutil.rmtree(source.parent)

        self.refresh()

        return self

    def __enter__(self) -> Tree[T]:
        return self

    def __exit__(self, *args) -> None:
        if None in args:
            self.resolve()
