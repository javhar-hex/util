from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from typing import Generic, SupportsIndex, TypeVar, overload

T = TypeVar("T")


class ZVec(Sequence[T], Generic[T]):
    """
    Lightweight immutable vector.

    By default, the vector is deeply immutable, which requires each of the elements to be
    deeply immutable itself. The vector is hashable and stores its precomputed hash.
    Alternatively the vector can be instantiated with `require_hash=False`, which allows
    mutable elements. If mutable elements are present, `is_mutable` will return `False` 
    and `hash()` will raise a TypeError.
    """
    __slots__ = ("_data", "_hash")

    def __init__(self, items: Iterable[T], require_hash: bool = True) -> None:
        data = _parse_items(items)
        h = _parse_hash(data, require_hash)
        object.__setattr__(self, "_data", data)
        object.__setattr__(self, "_hash", h)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("ZList is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("ZList is immutable")

    def __hash__(self) -> int:
        if self._hash is None:
            raise TypeError("Not all elements are hashable.")
        return self._hash

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ZVec):
            return self._hash == other._hash and self._data == other._data
        return NotImplemented

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __contains__(self, item: object) -> bool:
        return item in self._data

    def __reversed__(self) -> Iterator[T]:
        return reversed(self._data)

    def __add__(self, other: ZVec[T]) -> ZVec[T]:
        return ZVec(self._data + other._data)

    @overload
    def __getitem__(self, index: SupportsIndex) -> T: ...
    @overload
    def __getitem__(self, index: slice) -> ZVec[T]: ...
    def __getitem__(self, index: SupportsIndex | slice) -> T | ZVec[T]:
        if isinstance(index, slice):
            return ZVec(self._data[index])
        return self._data[index]

    def __repr__(self) -> str:
        return f"ZList({list(self._data)})"
    
    def is_hashable(self) -> bool:
        return self._hash is not None


def _parse_items(items: Iterable[T]) -> tuple[T, ...]:
    try:
        return tuple(items)
    except TypeError as e:
        raise TypeError(f"ZVec requires an iterable: {e}") from e
    
def _parse_hash(items: tuple[T, ...], require_hash: bool) -> int | None:
    try:
        return hash(items)
    except TypeError as e:
        if not require_hash:
            return None
        raise TypeError(f"Zlist requires all elements to be hashable: {e}") from e