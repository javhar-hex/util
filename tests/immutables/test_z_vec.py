import pytest

from javhar_util.immutables import ZVec


def test_init() -> None:
    zvec = ZVec([0, 1, 2])
    assert list(zvec) == [0, 1, 2]
    assert len(zvec) == 3

    zvec = ZVec([0, 1, 2])
    assert list(zvec) == [0, 1, 2]
    assert len(zvec) == 3

    zvec = ZVec(range(3))
    assert list(zvec) == [0, 1, 2]
    assert len(zvec) == 3

    chars = ZVec("abc")
    assert list(chars) == ["a", "b", "c"]
    assert len(chars) == 3

    zvec = ZVec({0, 1, 2})
    assert set(zvec) == {0, 1, 2}
    assert len(zvec) == 3

    zvec = ZVec([])
    assert list(zvec) == []
    assert len(zvec) == 0

    mixed = ZVec[object]([0, "a", (1, "b")])
    assert list(mixed) == [0, "a", (1, "b")]
    assert len(mixed) == 3


def test_disallow_mutable_items() -> None:
    with pytest.raises(TypeError):
        _ = ZVec([0, 1, [2, 3]])

    with pytest.raises(TypeError):
        _ = ZVec([0, 1, {"a": 2}])


def test_allow_mutable_items() -> None:
    zvec = ZVec([0, 1, [2, 3]], require_hash=False)
    assert list(zvec) == [0, 1, [2, 3]]


def test_immutable() -> None:
    t = [1, 2, 3]
    zvec = ZVec(t)

    t[0] = 0
    assert list(zvec) == [1, 2, 3]

    for field, value in (("_data", (4, 5, 6)), ("_hash", 0)):
        with pytest.raises(AttributeError):
            setattr(zvec, field, value)

    with pytest.raises(AttributeError):
        del zvec._data

    with pytest.raises(AttributeError):
        del zvec._hash


def test_hash_immutable_items() -> None:
    assert hash(ZVec([1, 2, 3])) == hash(ZVec([1, 2, 3]))
    assert hash(ZVec([1, 2, 3])) == hash(ZVec([1, 2, 3], require_hash=False))

    zvec = ZVec([1, 2, 3])
    assert hash(zvec) == hash(zvec)

    d = {zvec: "value"}
    assert d[zvec] == "value"

    z2 = ZVec([1, 2, 3])
    s = {zvec, z2}
    assert len(s) == 1

    inner = ZVec([1, 2, 3])
    outer = ZVec([inner, inner])
    assert hash(outer) is not None


def test_hash_mutable_items() -> None:
    zvec = ZVec([1, 2, [3, 4]], require_hash=False)
    with pytest.raises(TypeError):
        _ = hash(zvec)


def test_eq() -> None:
    assert ZVec([1, 2, 3]) == ZVec([1, 2, 3])
    assert ZVec([1, 2, 3]) != ZVec([1, 2, 4])
    assert ZVec([1, 2, 3]) != ZVec([1, 3, 2])
    assert ZVec([1, 2, 3]) != ZVec([1, 2])
    assert ZVec([1, 2, 3]) != [1, 2, 3]
    assert ZVec([1, 2, 3]) != (1, 2, 3)


def test_eq_mutable_items() -> None:
    nested = ZVec[object]([1, [2, 3]], require_hash=False)
    assert nested == ZVec[object]([1, [2, 3]], require_hash=False)


def test_len() -> None:
    assert len(ZVec([0, 1, 2])) == 3
    assert len(ZVec([])) == 0
    assert len(ZVec[object]([1, [2, 3]], require_hash=False)) == 2


def test_iter() -> None:
    zvec = ZVec([1, 2, 3])
    items = [item for item in zvec]
    assert items == [1, 2, 3]

    nested = ZVec[object]([1, [2, 3]], require_hash=False)
    assert [item for item in nested] == [1, [2, 3]]


def test_contains() -> None:
    zvec = ZVec([1, 2, 3])
    assert 2 in zvec
    assert 4 not in zvec

    nested = ZVec[object]([1, [2, 3]], require_hash=False)
    assert 1 in nested
    assert [2, 3] in nested


def test_reversed() -> None:
    zvec = ZVec([1, 2, 3])
    assert list(reversed(zvec)) == [3, 2, 1]

    nested = ZVec[object]([1, [2, 3]], require_hash=False)
    assert list(reversed(nested)) == [[2, 3], 1]


def test_add() -> None:
    zvec_lhs = ZVec([1, 2])
    zvec_rhs = ZVec([3, 4])
    result = zvec_lhs + zvec_rhs
    assert isinstance(result, ZVec)
    assert list(result) == [1, 2, 3, 4]
    assert list(zvec_lhs) == [1, 2]
    assert list(zvec_rhs) == [3, 4]


def test_getitem_int() -> None:
    zvec = ZVec([10, 20, 30])
    assert zvec[0] == 10
    assert zvec[-1] == 30


def test_getitem_slice() -> None:
    zvec = ZVec([1, 2, 3, 4, 5])
    sliced = zvec[1:3]
    assert isinstance(sliced, ZVec)
    assert list(sliced) == [2, 3]


def test_repr() -> None:
    zvec = ZVec([1, 2, 3])
    assert isinstance(repr(zvec), str)


def test_is_hashable() -> None:
    zvec = ZVec([1, 2, 3])
    assert zvec.is_hashable

    nested = ZVec[object]([1, [2, 3]], require_hash=False)
    assert not nested.is_hashable
