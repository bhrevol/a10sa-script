from typing import Any
from typing import Iterable
from typing import Iterator
from typing import MutableSequence
from typing import Optional
from typing import TypeVar
from typing import Union
from typing import overload


T = TypeVar("T")

class SortedList(MutableSequence[T]):
    def __init__(self, iterable: Optional[Iterable[T]] = None, key: Any = None): ...
    def __delitem__(self, index: Union[int, slice]) -> None: ...
    def __len__(self) -> int: ...
    def __setitem__(
        self, index: Union[int, slice], value: Union[T, Iterable[T]]
    ) -> None: ...
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
