
def test_hierarchy_detector0():
    import autowrap.Utils

    dd = dict()
    dd[1] = [2]
    dd[2] = [1]
    assert autowrap.Utils.find_cycle(dd) == [2,1]

    dd = dict()
    dd[1] = [2]
    assert autowrap.Utils.find_cycle(dd) is None


def test_hierarchy_detector1():
    import autowrap.Utils

    dd = dict()
    dd[1] = [2, 3]
    dd[2] = [3]
    assert autowrap.Utils.find_cycle(dd) is None

def test_hierarchy_detector2():
    import autowrap.Utils

    dd = dict()
    dd[1] = [2, 3]
    dd[2] = [3]
    dd[3] = [4]
    dd[4] = [2]
    assert autowrap.Utils.find_cycle(dd) == [4, 2, 3]


def test_hierarchy_detector3():
    import autowrap.Utils

    dd = dict()
    dd[1] = [2]
    dd[2] = [3,4]
    dd[3] = [5]
    assert autowrap.Utils.find_cycle(dd) is None


