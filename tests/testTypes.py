from autowrap.Types import CppType

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

    _testErr("int **")
    _testErr("int &*")
    _testErr("int &&")
    _testErr("long int")
    _testErr("unsigned unsigned int")

def _testType(t):
    assert t == str(CppType.from_string(t)) ==  t, str(CppType.from_string(t))

def _testErr(s):
    try:
        CppType.from_string(s)
    except:
        pass
    else:
        assert False, "'%s' did not throw exception" % s

