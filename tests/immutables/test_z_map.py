import pytest

from javhar_util.immutables import ZMap


def test_init() -> None:
    zmap = ZMap({"a": 1, "b": "xyz", "c": False})
    assert len(zmap) == 3
    assert zmap["a"] == 1
    assert zmap["b"] == "xyz"
    assert zmap["c"] == False

    zmap = ZMap([("a", 1), ("b", 2)])
    assert zmap["a"] == 1
    assert zmap["b"] == 2


def test_disallow_mutable_keys() -> None:
    with pytest.raises(TypeError):
        _ = ZMap([([1, 2], 1), ("b", 2)])


def test_disallow_mutable_values() -> None:
    with pytest.raises(TypeError):
        _ = ZMap({"a": 1, "b": [1, 2]})


def test_allow_mutable_values() -> None:
    zmap = ZMap({"a": 1, "b": [1, 2]}, require_hash=False)
    assert zmap["b"] == [1, 2]


def test_immutable() -> None:
    d = {"a": 1, "b": 2}
    zmap = ZMap(d)
    d["a"] = 3
    d["c"] = 5
    assert len(zmap) == 2
    assert zmap["a"] == 1

    for field, value in (("_data", {"x": 9}), ("_hash", 0)):
        with pytest.raises(AttributeError):
            setattr(zmap, field, value)

    with pytest.raises(AttributeError):
        del zmap._data

    with pytest.raises(AttributeError):
        del zmap._hash


def test_hash_immutable_values() -> None:
    zmap = ZMap({"a": 1, "b": 2})
    assert hash(zmap) == hash(zmap)

    zmap2 = ZMap({"b": 2, "a": 1})
    assert hash(zmap2) == hash(zmap)

    d = {zmap: "value"}
    assert d[zmap] == "value"

    s = {zmap, zmap2}
    assert len(s) == 1

    outer = ZMap({zmap: zmap2})
    assert hash(outer) is not None


def test_hash_mutable_values() -> None:
    zmap = ZMap({"a": 1, "b": [2, 3]}, require_hash=False)
    with pytest.raises(TypeError):
        _ = hash(zmap)


def test_eq() -> None:
    assert ZMap({"a": 1, "b": 2}) == ZMap({"b": 2, "a": 1})
    assert ZMap({"a": 1, "b": 2}) != ZMap({"a": 2, "b": 1})
    assert ZMap({"a": 1, "b": 2}) != ZMap({"a": 1})
    assert ZMap({"a": 1, "b": 2}) != {"a": 1, "b": 2}


def test_eq_mutable_values() -> None:
    assert ZMap({"a": 1, "b": [2, 3]}, require_hash=False) == ZMap(
        {"b": [2, 3], "a": 1}, require_hash=False
    )


def test_len() -> None:
    assert len(ZMap({"a": 1, "b": 2})) == 2
    assert len(ZMap({})) == 0
    assert len(ZMap({"a": 1, "b": [2, 3]}, require_hash=False)) == 2


def test_iter() -> None:
    zmap = ZMap({"a": 1, "b": 2, "c": 3})
    keys = set(zmap)
    assert keys == {"a", "b", "c"}


def test_contains() -> None:
    zmap = ZMap({"a": 1, "b": 2})
    assert "a" in zmap
    assert "b" in zmap
    assert "c" not in zmap


def test_getitem() -> None:
    zmap = ZMap({"a": 1, "b": 2})
    assert zmap["a"] == 1
    assert zmap["b"] == 2
    with pytest.raises(KeyError):
        _ = zmap["c"]

    nested = ZMap[str, object]({"a": 1, "b": [2, 3]}, require_hash=False)
    assert nested["b"] == [2, 3]


def test_get() -> None:
    zmap = ZMap({"a": 1, "b": 2})
    assert zmap.get("a") == 1
    assert zmap.get("a", 99) == 1
    assert zmap.get("c") is None
    assert zmap.get("c", 99) == 99


def test_keys() -> None:
    zmap = ZMap({"a": 1, "b": 2})
    assert set(zmap.keys()) == {"a", "b"}


def test_values() -> None:
    zmap = ZMap({"a": 1, "b": 2})
    assert set(zmap.values()) == {1, 2}

    nested = ZMap[str, object]({"a": 1, "b": [2, 3]}, require_hash=False)
    assert len(nested.values()) == 2
    assert [2, 3] in nested.values()


def test_items() -> None:
    zmap = ZMap({"a": 1, "b": 2})
    assert set(zmap.items()) == {("a", 1), ("b", 2)}


def test_repr() -> None:
    zmap = ZMap({"a": 1, "b": 2})
    assert isinstance(repr(zmap), str)


def test_is_hashable() -> None:
    zmap = ZMap({"a": 1, "b": 2})
    assert zmap.is_hashable

    nested = ZMap[str, object]({"a": 1, "b": [2, 3]}, require_hash=False)
    assert not nested.is_hashable
