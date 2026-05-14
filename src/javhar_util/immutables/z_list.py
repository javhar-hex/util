from typing import Generic, TypeVar, Iterator, Iterable, overload

T = TypeVar("T")


class ZList(Generic[T]):
    """
    Lightweight deeply immutable list.
    """
    __slots__ = ("_data", "_hash")

    def __init__(self, iterable: Iterable[T]) -> None:
        data = tuple(iterable)
        try:
            h = hash(data)
        except TypeError as e:
            raise TypeError(f"ZList requires all elements to be hashable: {e}") from e
        object.__setattr__(self, "_data", data)
        object.__setattr__(self, "_hash", h)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"ZList is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError(f"ZList is immutable")

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ZList):
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

    def __add__(self, other: "ZList[T]") -> "ZList[T]":
        return ZList(self._data + other._data)

    @overload
    def __getitem__(self, index: int) -> T: ...
    @overload
    def __getitem__(self, index: slice) -> "ZList[T]": ...
    def __getitem__(self, index: int | slice) -> "T | ZList[T]":
        if isinstance(index, slice):
            return ZList(self._data[index])
        return self._data[index]

    def __repr__(self) -> str:
        return f"ZList({list(self._data)})"
