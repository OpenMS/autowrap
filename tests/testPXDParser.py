import autowrap.PXDParser
import os

from  autowrap.Types import CppType as CppType

def _parse(pxdFileName):
    test_file = os.path.join(os.path.dirname(__file__),
                             'test_files',
                             pxdFileName)
    return autowrap.PXDParser.parse(test_file)


def testMinimal():
    cld = _parse("minimal.pxd")
    assert cld.name == "Minimal"
    assert cld.template_parameters  == None

    assert len(cld.methods["Minimal"]) == 1
    assert len(cld.methods["getA"]) == 1
    assert len(cld.methods["method0"]) == 1

    assert cld.methods["Minimal"][0].name == "Minimal"
    assert len(cld.methods["Minimal"][0].args) == 1
    argname, arg_type = cld.methods["Minimal"][0].args[0]
    assert argname == "a"
    assert arg_type == CppType("int")

    assert cld.methods["getA"][0].wrap
    assert len(cld.methods["getA"][0].args) == 0

    def subtest(name, inp_type):
        meth = cld.methods[name][0]
        assert meth.result_type == inp_type
        assert meth.args[0][1] == inp_type

    subtest("method0", CppType("int", is_unsigned=True))
    subtest("method1", CppType("float"))
    subtest("method2", CppType("double"))
    subtest("method3", CppType("char"))

    assert len(cld.methods["overloaded"]) == 2

    args = []
    for meth in cld.methods["overloaded"]:
        assert meth.name == "overloaded"
        assert meth.result_type == CppType("void")
        args.append(meth.args)
    assert args == [[ (u"inp", CppType("int"))], [(u"inp", CppType("float"))]]

