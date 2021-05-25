from pathlib import Path
from typing import Callable, Sequence, TypeVar

T = TypeVar("T")

Getter = Callable[[T], str]

Hierarchy = Sequence[Getter]

Operation = Callable[[Path, T], Path]
