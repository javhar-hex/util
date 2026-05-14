from __future__ import annotations
from typing import Generic, Iterable, Iterator, TypeVar

T = TypeVar("T")


class ZSet(Generic[T]):
    """
    Lightweight deeply immutable set.
    """
    __slots__ = ("_data", "_hash")

    def __init__(self, iterable: Iterable[T]) -> None:
        try:
            data = frozenset(iterable)
        except TypeError as e:
            raise TypeError(f"ZSet requires all elements to be hashable: {e}") from e
        object.__setattr__(self, "_data", data)
        object.__setattr__(self, "_hash", hash(data))

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("ZSet is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("ZSet is immutable")

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ZSet):
            return self._hash == other._hash and self._data == other._data
        return NotImplemented

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __contains__(self, item: object) -> bool:
        return item in self._data

    def __and__(self, other: ZSet[T]) -> ZSet[T]:
        return ZSet(self._data & other._data)

    def __or__(self, other: ZSet[T]) -> ZSet[T]:
        return ZSet(self._data | other._data)

    def __sub__(self, other: ZSet[T]) -> ZSet[T]:
        return ZSet(self._data - other._data)

    def __xor__(self, other: ZSet[T]) -> ZSet[T]:
        return ZSet(self._data ^ other._data)

    def issubset(self, other: ZSet[T]) -> bool:
        return self._data.issubset(other._data)

    def issuperset(self, other: ZSet[T]) -> bool:
        return self._data.issuperset(other._data)

    def isdisjoint(self, other: ZSet[T]) -> bool:
        return self._data.isdisjoint(other._data)

    def __repr__(self) -> str:
        return f"ZSet({set(self._data)})"
