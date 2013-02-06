from autowrap.Types import CppType
from utils import expect_exception

def testTypeParse():
    _testType("unsigned int")

    T = CppType("T")
    assert str(T) == "T"

    Tlist = str(CppType("list",[T]))
    _testType(Tlist)

    _testType("list[T]")

    _testType("list[T,T]")

    _testType("list[list[T],T]")

    _testType("int")
    _testType("int *")
    _testType("unsigned int *")
    _testType("int &")
    _testType("unsigned int &")

    _testType("X[int]")
    _testType("X[unsigned int]")
    _testType("X[int *]")
    _testType("X[unsigned int *]")
    _testType("X[int &]")
    _testType("X[unsigned int &]")

    _testType("X[int,float]")
    _testType("X[unsigned int,float]")
    _testType("X[int *,float]")
    _testType("X[unsigned int *,float]")
    _testType("X[int &,float]")
    _testType("X[unsigned int &,float]")

    _testType("X[int,Y[str]]")
    _testType("X[unsigned int,Y[str]]")
    _testType("X[int *,Y[str]]")
    _testType("X[unsigned int *,Y[str]]")
    _testType("X[int &,Y[str]]")
    _testType("X[unsigned int &,Y[str]]")

    _testErr("long int")
    _testErr("unsigned unsigned int")

def _testType(t):
    assert t == str(CppType.from_string(t)) ==  t, str(CppType.from_string(t))

@expect_exception
def _testErr(s):
    CppType.from_string(s)

def test_check_for_recursion():
    _test_check_for_recursion_1()
    _test_check_for_recursion_2()

def _test_check_for_recursion_1():
    CppType.from_string("A").check_for_recursion()
    CppType.from_string("A[B]").check_for_recursion()
    CppType.from_string("A[B,B]").check_for_recursion()
    CppType.from_string("A[B,C]").check_for_recursion()
    CppType.from_string("A[B[C],C]").check_for_recursion()
    CppType.from_string("A[B[C],D]").check_for_recursion()
    CppType.from_string("A[B[C],D[E]]").check_for_recursion()
    CppType.from_string("A[B[C],D[E],D]").check_for_recursion()
    CppType.from_string("A[B[C],D[E],B]").check_for_recursion()

def _test_check_for_recursion_2():
    _assert_exeception_when_testing("A[A]")
    _assert_exeception_when_testing("A[B[A]]")
    _assert_exeception_when_testing("A[B[A],C]")
    _assert_exeception_when_testing("A[C,B[A]]")
    _assert_exeception_when_testing("A[B[C[A]]]")
    _assert_exeception_when_testing("A[B[D,C[A]]]")
    _assert_exeception_when_testing("A[B[D,C[A],D]]")

def _assert_exeception_when_testing(str_):
    try:
        CppType.from_string(str_).check_for_recursion()
    except Exception, e:
        estr = str(e)
        if not estr.startswith("recursion check for "):
            if not estr.endswith(" failed"):
                raise e
    else:
        assert False, "invalid type '%s' passed test" % str_

def _check(type_, trans, expected_str_repres):
    out = str(type_.transformed(trans))
    if out != expected_str_repres:
        lines = ["transform %s with:" % type_]
        for k, v in trans.items():
            lines.append("  %s -> %s" % (k, v))
        lines.append("got: %s, expected: %s" % (out, expected_str_repres))
        assert False, "\n".join(lines)


def test_base_type_collecting():

    def check(t, tobe):
        collected = "".join(sorted(t.all_occuring_base_types()))
        if collected != tobe:
            msg = "input '%s', collected '%s'" % (t, collected)
            assert False, msg

    check(CppType.from_string("A"), "A")
    check(CppType.from_string("A[B]"), "AB")
    check(CppType.from_string("A[B,C]"), "ABC")
    check(CppType.from_string("A[B[C]]"), "ABC")
    check(CppType.from_string("A[B[C],D]"), "ABCD")
    check(CppType.from_string("A[B[C[D]]]"), "ABCD")


def test_transform():

    A = CppType("A")
    B = CppType("B")
    X = CppType("X")

    trans = dict(A=X)
    trans2 = dict(A=CppType("C", [X]))
    _check(A, trans2, "C[X]")
    _check(A, trans, "X")

    B_A = CppType("B", [A])
    _check(B_A, trans, "B[X]")
    _check(B_A, trans2, "B[C[X]]")

    B_A_A = CppType("B", [A, A])
    _check(B_A_A, trans, "B[X,X]")
    _check(B_A_A, trans2, "B[C[X],C[X]]")

    B_A_C = CppType("B", [A, CppType("D")])
    assert str(B_A_C) == "B[A,D]"
    _check(B_A_C, trans, "B[X,D]")
    _check(B_A_C, trans2, "B[C[X],D]")


def test_inv_transform():
    A = CppType.from_string("A")
    AX = CppType.from_string("A[X]")
    AXX = CppType.from_string("A[X,X]")
    ABX = CppType.from_string("A[B[X]]")
    ABXX = CppType.from_string("A[B[X],X]")

    T=CppType.from_string("T")

    def check(t, map_, expected):
        is_ = str(t.inv_transformed(map_))
        assert is_ == expected, is_

    map1 = dict(Z=A)
    check(A, map1, "Z")
    check(AX, map1, "A[X]")

    map2 = dict(Z=CppType.from_string("B[X]"))
    check(ABX, map2, "A[Z]")
    check(ABXX, map2, "A[Z,X]")

    ABXp = ABX.copy()
    ABXp.is_ptr = True
    check(ABXp, map2, "A[Z] *")

    ABXXp = ABXX.copy()
    ABXXp.template_args[0].is_ptr = True

    check(ABXXp, map2, "A[Z *,X]")


