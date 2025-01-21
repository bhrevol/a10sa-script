"""Generic utilities."""
from typing import Literal
from typing import Union

from typing import TypeAlias


_ByteOrder: TypeAlias = Union[Literal["little"], Literal["big"]]


def to_uint(data: bytes, byteorder: _ByteOrder = "big") -> int:
    """Convert bytes to unsigned integer."""
    return int.from_bytes(data, byteorder=byteorder, signed=False)


def to_u32(n: int, byteorder: _ByteOrder = "big") -> bytes:
    """Convert unsigned int to bytes."""
    return n.to_bytes(4, byteorder=byteorder, signed=False)
