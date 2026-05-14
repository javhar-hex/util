import pytest

from util.dtypes.immutables.z_vec import ZVec


def test_init():
    zvec = ZVec([0, 1, 2])
    assert list(zvec) == [0, 1, 2]
    assert len(zvec) == 3

    zvec = ZVec([0, 1, 2])
    assert list(zvec) == [0, 1, 2]
    assert len(zvec) == 3

    zvec = ZVec(range(3))
    assert list(zvec) == [0, 1, 2]
    assert len(zvec) == 3

    zvec = ZVec("abc")
    assert list(zvec) == ["a", "b", "c"]
    assert len(zvec) == 3

    zvec = ZVec({0, 1, 2})
    assert set(zvec) == {0, 1, 2}
    assert len(zvec) == 3

    zvec = ZVec([])
    assert list(zvec) == []
    assert len(zvec) == 0

    zvec = ZVec([0, "a", (1, "b")])
    assert list(zvec) == [0, "a", (1, "b")]
    assert len(zvec) == 3


def test_disallow_mutable_items():
    with pytest.raises(TypeError):
        _ = ZVec([0, 1, [2, 3]])

    with pytest.raises(TypeError):
        _ = ZVec([0, 1, {"a": 2}])


def test_immutable():
    t = [1, 2, 3]
    zvec = ZVec(t)

    t[0] = 0
    assert list(zvec) == [1, 2, 3]

    with pytest.raises(AttributeError):
        zvec._data = (4, 5, 6)

    with pytest.raises(AttributeError):
        del zvec._data

    with pytest.raises(AttributeError):
        zvec._hash = 0

    with pytest.raises(AttributeError):
        del zvec._hash


def test_hash():
    assert hash(ZVec([1, 2, 3])) == hash(ZVec([1, 2, 3]))

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


def test_eq():
    assert ZVec([1, 2, 3]) == ZVec([1, 2, 3])
    assert ZVec([1, 2, 3]) != ZVec([1, 2, 4])
    assert ZVec([1, 2, 3]) != ZVec([1, 3, 2])
    assert ZVec([1, 2, 3]) != ZVec([1, 2])
    assert ZVec([1, 2, 3]) != [1, 2, 3]
    assert ZVec([1, 2, 3]) != (1, 2, 3)


def test_len():
    assert len(ZVec([0, 1, 2])) == 3
    assert len(ZVec([])) == 0


def test_iter():
    zvec = ZVec([1, 2, 3])
    items = [item for item in zvec]
    assert items == [1, 2, 3]


def test_contains():
    zvec = ZVec([1, 2, 3])
    assert 2 in zvec
    assert 4 not in zvec


def test_reversed():
    zvec = ZVec([1, 2, 3])
    assert list(reversed(zvec)) == [3, 2, 1]


def test_add():
    zvec_lhs = ZVec([1, 2])
    zvec_rhs = ZVec([3, 4])
    result = zvec_lhs + zvec_rhs
    assert isinstance(result, ZVec)
    assert list(result) == [1, 2, 3, 4]
    assert list(zvec_lhs) == [1, 2]
    assert list(zvec_rhs) == [3, 4]


def test_getitem_int():
    zvec = ZVec([10, 20, 30])
    assert zvec[0] == 10
    assert zvec[-1] == 30


def test_getitem_slice():
    zvec = ZVec([1, 2, 3, 4, 5])
    sliced = zvec[1:3]
    assert isinstance(sliced, ZVec)
    assert list(sliced) == [2, 3]


def test_repr():
    zvec = ZVec([1, 2, 3])
    assert isinstance(repr(zvec), str)
