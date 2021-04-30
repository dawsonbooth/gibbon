from pathlib import Path
from typing import Protocol, TypeVar

T = TypeVar("T")


P_T = TypeVar("P_T", covariant=True)


class Parser(Protocol[P_T]):
    def __call__(self, Path) -> P_T:
        ...


T_T = TypeVar("T_T", contravariant=True)


class Transformer(Protocol[T_T]):
    def __call__(self, arg: T_T) -> Path:
        ...
