import pytest

from util.dtypes.immutables.z_list import ZList


def test_init():
    zlist = ZList([0, 1, 2])
    assert list(zlist) == [0, 1, 2]
    assert len(zlist) == 3

    zlist = ZList([0, 1, 2])
    assert list(zlist) == [0, 1, 2]
    assert len(zlist) == 3

    zlist = ZList(range(3))
    assert list(zlist) == [0, 1, 2]
    assert len(zlist) == 3

    zlist = ZList("abc")
    assert list(zlist) == ["a", "b", "c"]
    assert len(zlist) == 3

    zlist = ZList({0, 1, 2})
    assert set(zlist) == {0, 1, 2}
    assert len(zlist) == 3

    zlist = ZList([])
    assert list(zlist) == []
    assert len(zlist) == 0

    zlist = ZList([0, "a", (1, "b")])
    assert list(zlist) == [0, "a", (1, "b")]
    assert len(zlist) == 3


def test_disallow_mutable_items():
    with pytest.raises(TypeError):
        _ = ZList([0, 1, [2, 3]])

    with pytest.raises(TypeError):
        _ = ZList([0, 1, {"a": 2}])


def test_immutable_setattr():
    zl = ZList([1, 2, 3])
    with pytest.raises(AttributeError):
        zl._data = (4, 5, 6)


def test_immutable_delattr():
    zl = ZList([1, 2, 3])
    with pytest.raises(AttributeError):
        del zl._data


def test_getitem_int():
    zl = ZList([10, 20, 30])
    assert zl[0] == 10
    assert zl[-1] == 30


def test_getitem_slice():
    zl = ZList([1, 2, 3, 4, 5])
    sliced = zl[1:3]
    assert isinstance(sliced, ZList)
    assert list(sliced) == [2, 3]


def test_contains():
    zl = ZList([1, 2, 3])
    assert 2 in zl
    assert 4 not in zl


def test_iter():
    zl = ZList([1, 2, 3])
    assert list(zl) == [1, 2, 3]


def test_reversed():
    zl = ZList([1, 2, 3])
    assert list(reversed(zl)) == [3, 2, 1]


def test_add():
    zl1 = ZList([1, 2])
    zl2 = ZList([3, 4])
    result = zl1 + zl2
    assert isinstance(result, ZList)
    assert list(result) == [1, 2, 3, 4]
    assert list(zl1) == [1, 2]
    assert list(zl2) == [3, 4]


def test_eq():
    assert ZList([1, 2, 3]) == ZList([1, 2, 3])
    assert ZList([1, 2, 3]) != ZList([1, 2, 4])
    assert ZList([1, 2, 3]) != ZList([1, 3, 2])
    assert ZList([1, 2, 3]) != ZList([1, 2])
    assert ZList([1, 2, 3]) != [1, 2, 3]
    assert ZList([1, 2, 3]) != (1, 2, 3)


def test_hash():
    assert hash(ZList([1, 2, 3])) == hash(ZList([1, 2, 3]))

    zl = ZList([1, 2, 3])
    assert hash(zl) == hash(zl)

    d = {zl: "value"}
    assert d[zl] == "value"

    z2 = ZList([1, 2, 3])
    s = {zl, z2}
    assert len(s) == 1

    inner = ZList([1, 2, 3])
    outer = ZList([inner, inner])
    assert hash(outer) is not None


def test_repr():
    zl = ZList([1, 2, 3])
    assert isinstance(repr(zl), str)
