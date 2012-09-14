from autowrap.Types import CppType

def testTypeParse():
    T = CppType("T")
    assert CppType.parseDeclaration("T") == T
    _testType(T)

    Tlist = CppType("list", [T])
    _testType(Tlist)

    assert CppType.parseDeclaration("list[T]") == Tlist
    _testType(CppType.parseDeclaration("list[T]"))

    assert CppType.parseDeclaration("list[T, T]") == CppType("list", [T, T])
    _testType(CppType.parseDeclaration("list[T, T]"))

    assert CppType.parseDeclaration("list[list[T], T]") == CppType("list",
            [ Tlist, T])
    _testType(CppType.parseDeclaration("list[list[T], T]"))

def _testType(t):
    assert CppType.parseDeclaration(str(t)) ==  t, str(t)

