import pytest

from javhar_util.immutables import ZSet


def test_init() -> None:
    zset = ZSet(["a", "a", 1, False, (3, 4)])
    assert len(zset) == 4
    assert set(zset) == {False, (3, 4), 1, "a"}


def test_immutable() -> None:
    s = {"a", "b"}
    zset = ZSet(s)
    s.add("c")
    s.remove("a")
    assert set(zset) == {"a", "b"}

    for field, value in (("_data", frozenset({"x", "y"})), ("_hash", 0)):
        with pytest.raises(AttributeError):
            setattr(zset, field, value)

    with pytest.raises(AttributeError):
        del zset._data

    with pytest.raises(AttributeError):
        del zset._hash


def test_hash() -> None:
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


def test_eq() -> None:
    assert ZSet({"a", "b"}) == ZSet({"b", "a"})
    assert ZSet({"a", "b"}) != ZSet({"a", "c"})
    assert ZSet({"a", "b"}) != ZSet({"a"})


def test_len() -> None:
    assert len(ZSet({"a", "b"})) == 2
    assert len(ZSet(set())) == 0


def test_iter() -> None:
    zset = ZSet({"a", "b", "c"})
    items = set(zset)
    assert items == {"b", "c", "a"}


def test_contains() -> None:
    zset = ZSet({"a", "b"})
    assert "a" in zset
    assert "b" in zset
    assert "c" not in zset


def test_operations() -> None:
    lhs = ZSet({"L", "LR"})
    rhs = ZSet({"R", "LR"})
    assert set(lhs | rhs) == {"L", "R", "LR"}
    assert set(lhs & rhs) == {"LR"}
    assert set(lhs - rhs) == {"L"}
    assert set(lhs ^ rhs) == {"L", "R"}


def test_issubset() -> None:
    assert ZSet({"a", "b"}).issubset(ZSet({"b", "c", "a"}))
    assert not ZSet({"a", "b"}).issubset(ZSet({"b", "c", "d"}))


def test_issuperset() -> None:
    assert ZSet({"a", "b", "c"}).issuperset(ZSet({"c", "a"}))
    assert not ZSet({"a", "b", "c"}).issuperset(ZSet({"a", "d"}))


def test_isdisjoint() -> None:
    assert ZSet({"a", "b"}).isdisjoint(ZSet({"c", "d"}))
    assert not ZSet({"a", "b"}).isdisjoint(ZSet({"a", "c"}))


def test_repr() -> None:
    zset = ZSet({"a", "b"})
    assert isinstance(repr(zset), str)
