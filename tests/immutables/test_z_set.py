import pytest

from util.dtypes.immutables.z_set import ZSet


def test_init():
    zset = ZSet({"a", 1, False, (3, 4), "a"})
    assert len(zset) == 4
    assert set(zset) == {False, (3, 4), 1, "a"}


def test_immutable():
    s = {"a", "b"}
    zset = ZSet(s)
    s.add("c")
    s.remove("a")
    assert set(zset) == {"a", "b"}

    with pytest.raises(AttributeError):
        zset._data = {"x", "y"}

    with pytest.raises(AttributeError):
        del zset._data

    with pytest.raises(AttributeError):
        zset._hash = 0

    with pytest.raises(AttributeError):
        del zset._hash


def test_hash():
    zset = ZSet({"a", "b"})
    assert hash(zset) == hash(zset)

    zset2 = ZSet({"b", "a"})
    assert hash(zset2) == hash(zset)

    d = {zset: "value"}
    assert d[zset] == "value"

    s = {zset, zset2}
    assert len(s) == 1

    outer = ZSet({zset, zset2})
    assert hash(outer) is not None


def test_eq():
    assert ZSet({"a", "b"}) == ZSet({"b", "a"})
    assert ZSet({"a", "b"}) != ZSet({"a", "c"})
    assert ZSet({"a", "b"}) != ZSet({"a"})


def test_len():
    assert len(ZSet({"a", "b"})) == 2
    assert len(ZSet(set())) == 0


def test_iter():
    zset = ZSet({"a", "b", "c"})
    items = set(item for item in zset)
    assert items == {"b", "c", "a"}


def test_contains():
    zset = ZSet({"a", "b"})
    assert "a" in zset
    assert "b" in zset
    assert "c" not in zset


def test_operations():
    lhs = ZSet({"L", "LR"})
    rhs = ZSet({"R", "LR"})
    assert set(lhs | rhs) == {"L", "R", "LR"}
    assert set(lhs & rhs) == {"LR"}
    assert set(lhs - rhs) == {"L"}
    assert set(lhs ^ rhs) == {"L", "R"}


def test_issubset():
    assert ZSet({"a", "b"}).issubset(ZSet({"b", "c", "a"}))
    assert not ZSet({"a", "b"}).issubset(ZSet({"b", "c", "d"}))


def test_issuperset():
    assert ZSet({"a", "b", "c"}).issuperset(ZSet({"c", "a"}))
    assert not ZSet({"a", "b", "c"}).issuperset(ZSet({"a", "d"}))


def test_isdisjoint():
    assert ZSet({"a", "b"}).isdisjoint(ZSet({"c", "d"}))
    assert not ZSet({"a", "b"}).isdisjoint(ZSet({"a", "c"}))


def test_repr():
    zset = ZSet({"a", "b"})
    assert isinstance(repr(zset), str)
