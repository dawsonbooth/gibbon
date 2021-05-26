from typing import TypeVar

T = TypeVar("T")


class Stringable:
    ...

    def __str__(self) -> str:
        ...
