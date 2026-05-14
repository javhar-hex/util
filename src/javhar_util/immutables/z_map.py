from types import MappingProxyType
from typing import Generic, ItemsView, Iterator, KeysView, Mapping, TypeVar, ValuesView

K = TypeVar("K")
V = TypeVar("V")


class ZMap(Generic[K, V]):
    __slots__ = ("_data", "_hash")

    def __init__(self, mapping: Mapping[K, V]) -> None:
        data = dict(mapping)
        try:
            computed_hash = hash(frozenset(data.items()))
        except TypeError as e:
            raise TypeError(
                f"ZMap requires all keys and values to be hashable: {e}"
            ) from e
        object.__setattr__(self, "_data", MappingProxyType(data))
        object.__setattr__(self, "_hash", computed_hash)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("ZMap is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("ZMap is immutable")

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ZMap):
            return self._hash == other._hash and self._data == other._data
        return NotImplemented

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __contains__(self, item: object) -> bool:
        return item in self._data

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def get(self, key: K, default: V | None = None) -> V | None:
        return self._data.get(key, default)

    def keys(self) -> KeysView[K]:
        return self._data.keys()

    def values(self) -> ValuesView[V]:
        return self._data.values()

    def items(self) -> ItemsView[K, V]:
        return self._data.items()

    def __repr__(self) -> str:
        return f"ZMap({self._data})"
