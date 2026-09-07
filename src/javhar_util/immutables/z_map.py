from __future__ import annotations

import dataclasses as dc
from collections.abc import ItemsView, Iterable, Iterator, KeysView, Mapping, ValuesView
from types import MappingProxyType
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dc.dataclass(frozen=True, slots=True)
class ZMap(Generic[K, V]):
    """
    Lightweight immutable map.

    By default, the map is deeply immutable, which requires each of the values to be
    deeply immutable itself. The map is hashable and stores its precomputed hash.
    Alternatively the map can be instantiated with `require_hash=False`, which allows
    mutable values. If mutable values are present, `is_hashable` will return `False`
    and `hash()` will raise a TypeError.

    As with any mapping, the keys must always be hashable and therefore immutable.
    """

    _data: MappingProxyType[K, V]
    _hash: int | None

    def __init__(
        self, data: Mapping[K, V] | Iterable[tuple[K, V]], require_hash: bool = True
    ) -> None:
        data_dict = _parse_data(data)
        h = _parse_hash(data_dict, require_hash)
        object.__setattr__(self, "_data", MappingProxyType(data_dict))
        object.__setattr__(self, "_hash", h)

    def __hash__(self) -> int:
        if self._hash is None:
            raise TypeError("Not all values are hashable.")
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
        return f"ZMap({dict(self._data)})"

    @property
    def is_hashable(self) -> bool:
        return self._hash is not None


def _parse_data(data: Mapping[K, V] | Iterable[tuple[K, V]]) -> dict[K, V]:
    try:
        return dict(data)
    except TypeError as e:
        raise TypeError(f"ZMap requires all keys to be hashable: {e}") from e


def _parse_hash(data: dict[K, V], require_hash: bool) -> int | None:
    try:
        return hash(frozenset(data.items()))
    except TypeError as e:
        if not require_hash:
            return None
        raise TypeError(f"ZMap requires all keys and values to be hashable: {e}") from e
