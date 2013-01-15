
import autowrap.Utils

def test_hierarchy_detector0():

    dd = dict()
    dd[1] = [2]
    dd[2] = [1]
    assert autowrap.Utils.find_cycle(dd) == [2,1]

    dd = dict()
    dd[1] = [2]
    assert autowrap.Utils.find_cycle(dd) is None


def test_hierarchy_detector1():

    dd = dict()
    dd[1] = [2, 3]
    dd[2] = [3]
    assert autowrap.Utils.find_cycle(dd) is None

def test_hierarchy_detector2():

    dd = dict()
    dd[1] = [2, 3]
    dd[2] = [3]
    dd[3] = [4]
    dd[4] = [2]
    assert autowrap.Utils.find_cycle(dd) == [4, 2, 3]


def test_hierarchy_detector3():

    dd = dict()
    dd[1] = [2]
    dd[2] = [3,4]
    dd[3] = [5]
    assert autowrap.Utils.find_cycle(dd) is None


def test_nested_mapping_flattening():
    from autowrap.Types import CppType
    B = CppType.from_string("B")
    Y = CppType.from_string("Y")
    Z = CppType.from_string("Z")
    CXD = CppType.from_string("C[X,D]")

    mapping = dict(A=B, B=CXD, C=Z, D=Y)
    autowrap.Utils.flatten(mapping)
    assert str(mapping["A"]) == "Z[X,Y]"
    assert str(mapping["B"]) == "Z[X,Y]"
    assert str(mapping["C"]) == "Z"
    assert str(mapping["D"]) == "Y"

