import autowrap.PXDParser
import os

from  autowrap.Types import CppType as CppType

from utils import expect_exception

def _parse(pxdFileName):
    test_file = os.path.join(os.path.dirname(__file__),
                             'test_files',
                             pxdFileName)
    return autowrap.PXDParser.parse_pxd_file(test_file)


def test_minimal():
    cld, = autowrap.PXDParser.parse_str("""
cdef extern from "Minimal.hpp":

    cdef cppclass Minimal:
        Minimal(int a)
        int getA()
        unsigned int method0(unsigned int input)
        float method1(float input)
        double method2(double input)
        char method3(char input)

        void overloaded(int inp)
        void overloaded(float inp)

        void run(Minimal)
        void run2(Minimal *)
    """)

    assert cld.name == "Minimal"
    assert cld.template_parameters  == None

    assert len(cld.methods["Minimal"]) == 1
    assert len(cld.methods["getA"]) == 1
    assert len(cld.methods["method0"]) == 1

    assert cld.methods["Minimal"][0].name == "Minimal"
    assert len(cld.methods["Minimal"][0].arguments) == 1
    argname, arg_type = cld.methods["Minimal"][0].arguments[0]
    assert argname == "a"
    assert arg_type == CppType("int")

    assert len(cld.methods["getA"][0].arguments) == 0

    def subtest(name, inp_type):
        meth = cld.methods[name][0]
        assert meth.result_type == inp_type, str(meth.result_type)
        assert meth.arguments[0][1] == inp_type

    subtest("method0", CppType("int", is_unsigned=True))
    subtest("method1", CppType("float"))
    subtest("method2", CppType("double"))
    subtest("method3", CppType("char"))

    assert len(cld.methods["overloaded"]) == 2

    arguments = []
    for meth in cld.methods["overloaded"]:
        assert meth.name == "overloaded"
        assert meth.result_type == CppType("void")
        arguments.append(meth.arguments)
    assert arguments == [[ (u"inp", CppType("int"))], [(u"inp", CppType("float"))]]

    run_meth = cld.methods["run2"][0]
    name, arg_type = run_meth.arguments[0]
    assert str(arg_type) == "Minimal *"
    run_meth = cld.methods["run"][0]
    name, arg_type = run_meth.arguments[0]
    assert str(arg_type) == "Minimal"


def test_int_container_pxd_parsing():
    cld1, cld2 = _parse("int_container_class.pxd")
    assert cld1.name == "X"
    assert cld2.name == "XContainer"


def test_enum():
    E, = autowrap.PXDParser.parse_str("""
cdef extern from "":
    cdef enum E:
                A, B, C
            """)

    assert E.name == "E"
    A, B, C = E.items
    assert A == ("A", 0)
    assert B == ("B", 1)
    assert C == ("C", 2)

def test_class_and_enum():
    A, E = autowrap.PXDParser.parse_str("""
cdef extern from "":

    cdef cppclass A:
        A()

    cdef enum E:
                A, B, C
    """)

    assert A.name == "A"
    method, = A.methods.values()[0]
    assert method.name == "A"
    assert len(method.arguments) == 0

    assert E.name == "E"
    A, B, C = E.items
    assert A == ("A", 0)
    assert B == ("B", 1)
    assert C == ("C", 2)

def test_multi_enum():
    E, F = autowrap.PXDParser.parse_str("""
cdef extern from "":
    cdef enum E:
                A, B, C

    cdef enum F:
                X, Y=4, Z

            """)

    assert E.name == "E"
    A, B, C = E.items
    assert A == ("A", 0)
    assert B == ("B", 1)
    assert C == ("C", 2)

    assert F.name == "F"
    X, Y, Z = F.items
    assert X == ("X", 0)
    assert Y == ("Y", 4)
    assert Z == ("Z", 5)


def test_multi_mixed():
    E, F, X = autowrap.PXDParser.parse_str("""
cdef extern from "":
    cdef enum E:
                A, B, C

    cdef enum F:
                G, H=4, I

    cdef cppclass X:
         void fun(int)

            """)

    assert E.name == "E"
    A, B, C = E.items
    assert A == ("A", 0)
    assert B == ("B", 1)
    assert C == ("C", 2)

    assert F.name == "F"
    G, H, I = F.items
    assert G == ("G", 0)
    assert H == ("H", 4)
    assert I == ("I", 5)

    assert X.name == "X", X
    (fun,),  = X.methods.values()
    assert fun.result_type == CppType("void"), fun.result_type
    assert fun.name == "fun"
    (arg_name, type_), = fun.arguments
    assert arg_name == ""
    assert type_ == CppType("int")


def test_multi_classes_in_one_file():
    inst1, inst2 = autowrap.PXDParser.parse_str("""
cdef extern from "A.h":
    cdef cppclass A[B,C] :
        # wrap-instances:
        #   A[int,int]
        void run()

    cdef cppclass C[E] :
        # wrap-instances:
        #   C[float]
        pass

    """)
    assert inst1.name == u"A"
    assert inst1.template_parameters == [ u"B", u"C" ]
    assert inst1.methods.keys() == ["run"]
    assert inst2.name == u"C"
    assert inst2.template_parameters == [ u"E", ]
    assert len(inst2.methods) == 0

def test_typedef():
    decl1, decl2 = autowrap.PXDParser.parse_str("""
cdef extern from "A.h":
    ctypedef unsigned int myInt
    ctypedef long * allInt
    """)
    assert decl1.name == 'myInt', decl1.name
    assert decl2.name == 'allInt', decl2.name
    assert str(decl1.type_) == "unsigned int"
    assert str(decl2.type_) == "int *", str(decl2.type_)

@expect_exception
def test_doubleptr():

    autowrap.PXDParser.parse_str("""
cdef extern from "A.h":
    void fun(int **)
        """)

def test_aliased_ptr():
    d1, d2 = autowrap.PXDParser.parse_str("""
cdef extern from "A.h":
    ctypedef int integer
    ctypedef integer * iptr
        """)
    assert d1.name == "integer"
    assert d2.name == "iptr"
    assert str(d1.type_) == "int"
    assert str(d2.type_) == "integer *", str(d2.type_)

def test_multi_alias():
    d1, d2, d3, d4 = autowrap.PXDParser.parse_str("""
cdef extern from "A.h":
    ctypedef int X
    ctypedef X * iptr
    ctypedef X Y
    ctypedef Y * iptr2
        """)
    assert d1.name == "X"
    assert str(d1.type_) == "int"
    assert d2.name == "iptr"
    assert str(d2.type_) == "X *"
    assert d3.name == "Y"
    assert str(d3.type_) == "X"
    assert d4.name == "iptr2"
    assert str(d4.type_) == "Y *"

def test_function():
    decl1, decl2 = autowrap.PXDParser.parse_str("""
cdef extern from "A.h":
    int floor(float x)
    int ceil(float x)
    """)

    assert decl1.name == "floor"
    assert decl2.name == "ceil"

    (name, t), = decl1.arguments
    assert name == "x"
    assert str(t) == "float"
    (name, t), = decl2.arguments
    assert name == "x"
    assert str(t) == "float"


def test_inner_unsigned():
    decl1, decl2 = autowrap.PXDParser.parse_str("""

cdef extern from "A.h":

    cdef cppclass A[X]:
        # wrap-ignore
        pass

    cdef cppclass T:
        fun(A[unsigned int])

    """)

    fun,  = decl2.methods.get("fun")
    (__, arg_t), = fun.arguments
    assert str(arg_t) == "A[unsigned int]"


