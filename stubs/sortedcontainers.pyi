from typing import Any
from collections.abc import Iterable
from collections.abc import Iterator
from collections.abc import MutableSequence
from typing import TypeVar
from typing import overload

T = TypeVar("T")

class SortedList(MutableSequence[T]):
    def __init__(self, iterable: Iterable[T] | None = None, key: Any = None): ...
    def __delitem__(self, index: int | slice) -> None: ...
    def __len__(self) -> int: ...
    def __setitem__(self, index: int | slice, value: T | Iterable[T]) -> None: ...
    @overload
    def __getitem__(self, index: int) -> T: ...
    @overload
    def __getitem__(self, index: slice) -> MutableSequence[T]: ...
    def insert(self, index: int, value: T) -> None: ...
    def add(self, value: T) -> None: ...
    def irange_key(
        self,
        min_key: Any = None,
        max_key: Any = None,
        inclusive: bool = True,
        reverse: bool = False,
    ) -> Iterator[T]: ...
