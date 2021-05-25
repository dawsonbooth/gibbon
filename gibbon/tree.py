from __future__ import annotations

import os
import shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Callable, Dict, Generic, Iterable, Optional, Tuple, Union

from tqdm import tqdm

from .types import Hierarchy, Operation, T
from .util import is_empty, safe_move


def build_parent(item: T, ordering: Hierarchy) -> Path:
    parent = Path()

    for getter in ordering:
        parent /= str(getter(item))

    return parent


class Tree(Generic[T]):
    root_src: Path
    root_dest: Path
    glob: str
    parse: Optional[Callable[[Path], T]]
    show_progress: bool

    sources: Tuple[Path, ...] = tuple()
    operations: Dict[str, Operation] = dict()

    def __init__(
        self,
        root_src: Union[str, os.PathLike[str]],
        glob: str,
        root_dest: Optional[Union[str, os.PathLike[str]]] = None,
        parse: Optional[Callable[[Path], T]] = None,
        show_progress: bool = False,
    ):
        self.root_src = Path(root_src)
        self.root_dest = Path(root_dest or root_src)
        self.glob = glob
        self.parse = parse
        self.show_progress = show_progress

        self.refresh()

    def refresh(self) -> Tree[T]:
        self.sources = tuple(self.root_src.glob(self.glob))

        return self

    def organize(self, ordering: Hierarchy) -> Tree:
        self.operations["organize"] = lambda path, item: self.root_dest / build_parent(item, ordering) / path.name
        self.operations.pop("flatten", None)

        return self

    def flatten(self) -> Tree:
        self.operations["flatten"] = lambda path, _: self.root_dest / path.name
        self.operations.pop("organize", None)

        return self

    def rename(self, create_filename: Callable[[T], str]) -> Tree:
        self.operations["rename"] = lambda path, item: path.parent / create_filename(item)

        return self

    def resolve(self) -> Tree[T]:
        if len(self.operations) == 0:
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
                for operate in self.operations.values():
                    destination = operate(destination, parsed)
            except Exception as e:
                destination = self.root_dest / e.__class__.__name__ / destination.name
            destinations.append(destination)
        self.operations.clear()

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
