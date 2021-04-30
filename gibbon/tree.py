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

    sources: Tuple[Path, ...] = tuple()
    transformations: List[Callable[[T], Path]] = list()

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

    def refresh(self) -> Tree[T]:
        self.sources = tuple(self.root.glob(self.glob))

        return self

    def should_resolve(self) -> bool:
        return len(self.transformations) > 0

    def transform(self, *transformations: Callable[[T], Path]) -> None:
        self.transformations.extend(transformations)

    def resolve(self) -> Tree[T]:
        if not self.should_resolve():
            return self

        # Parse files
        parsed_sources: Iterable[Tuple]
        if self.parse is not None:
            with ProcessPoolExecutor() as executor:
                parsed_sources = zip(self.sources, executor.map(self.parse, self.sources))
        else:
            parsed_sources = zip(self.sources, self.sources)

        # Perform transformations
        # TODO: Figure out better framework for transformations
        if self.show_progress:
            parsed_sources = tqdm(parsed_sources, desc="Process files", total=len(self.sources))

        destinations = list()
        for source, parsed in parsed_sources:
            destination = source
            try:
                for transform in self.transformations:
                    destination = transform(parsed)
            except Exception as e:
                destination = self.root / e.__class__.__name__ / destination.name
            destinations.append(destination)
        self.transformations.clear()

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
