import pytest

from util.dtypes.immutables.z_map import ZMap


def test_init():
    zmap = ZMap({"a": 1, "b": "xyz", "c": False})
    assert len(zmap) == 3
    assert zmap["a"] == 1
    assert zmap["b"] == "xyz"
    assert zmap["c"] == False


def test_disallow_mutable_items():
    with pytest.raises(TypeError):
        _ = ZMap({"a": 1, "b": [1, 2]})


def test_immutable():
    d = {"a": 1, "b": 2}
    zmap = ZMap(d)
    d["a"] = 3
    d["c"] = 5
    assert len(zmap) == 2
    assert zmap["a"] == 1

    with pytest.raises(AttributeError):
        zmap._data = {"x": 9}

    with pytest.raises(AttributeError):
        del zmap._data

    with pytest.raises(AttributeError):
        zmap._hash = 0

    with pytest.raises(AttributeError):
        del zmap._hash


def test_hash():
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


def test_eq():
    assert ZMap({"a": 1, "b": 2}) == ZMap({"b": 2, "a": 1})
    assert ZMap({"a": 1, "b": 2}) != ZMap({"a": 2, "b": 1})
    assert ZMap({"a": 1, "b": 2}) != ZMap({"a": 1})
    assert ZMap({"a": 1, "b": 2}) != {"a": 1, "b": 2}


def test_len():
    assert len(ZMap({"a": 1, "b": 2})) == 2
    assert len(ZMap({})) == 0


def test_iter():
    zmap = ZMap({"a": 1, "b": 2, "c": 3})
    keys = set(key for key in zmap)
    assert keys == {"a", "b", "c"}


def test_contains():
    zmap = ZMap({"a": 1, "b": 2})
    assert "a" in zmap
    assert "b" in zmap
    assert "c" not in zmap


def test_getitem():
    zmap = ZMap({"a": 1, "b": 2})
    assert zmap["a"] == 1
    assert zmap["b"] == 2
    with pytest.raises(KeyError):
        _ = zmap["c"]


def test_get():
    zmap = ZMap({"a": 1, "b": 2})
    assert zmap.get("a") == 1
    assert zmap.get("a", 99) == 1
    assert zmap.get("c") is None
    assert zmap.get("c", 99) == 99


def test_keys():
    zmap = ZMap({"a": 1, "b": 2})
    assert set(zmap.keys()) == {"a", "b"}


def test_values():
    zmap = ZMap({"a": 1, "b": 2})
    assert set(zmap.values()) == {1, 2}


def test_items():
    zmap = ZMap({"a": 1, "b": 2})
    assert set(zmap.items()) == {("a", 1), ("b", 2)}


def test_repr():
    zmap = ZMap({"a": 1, "b": 2})
    assert isinstance(repr(zmap), str)
