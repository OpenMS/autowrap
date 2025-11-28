from __future__ import print_function
from __future__ import unicode_literals

__license__ = """

Copyright (c) 2012-2014, Uwe Schmitt, ETH Zurich, all rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

Neither the name of the mineway GmbH nor the names of its contributors may be
used to endorse or promote products derived from this software without specific
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


import pdb
import autowrap.PXDParser
import os

from autowrap.Types import CppType as CppType
from autowrap.Code import Code as Code
from .utils import expect_exception


def _parse(pxdFileName):
    test_file = os.path.join(os.path.dirname(__file__), "test_files", pxdFileName)
    return autowrap.PXDParser.parse_pxd_file(test_file)


def test_long():
    cld, gund, fund = autowrap.PXDParser.parse_str(
        """
cdef extern from "*":

    cdef cppclass T[U,V]:
        pass

    long gun()
    T[long int,int] fun()
    """
    )
    assert str(gund.result_type) == "long int"
    assert str(fund.result_type) == "T[long int,int]"


def test_multiline_annotations():
    (cdcl,) = autowrap.PXDParser.parse_str(
        """
cdef extern from "*":

    cdef cppclass T:
        fun(int x,    # a:3
            float y,  # b:4
           )

    """
    )
    (mdcl,) = cdcl.methods.get("fun")
    assert mdcl.annotations == dict(a="3", b="4")


def test_multiline_annotations_plus_afterdecl():
    (cdcl,) = autowrap.PXDParser.parse_str(
        """
cdef extern from "*":

    cdef cppclass T:
    # wrap-doc:
    #  Foobar wrap-wdsadas dsada
    #  continue
    # Not enough spaces
    #  Enough spaces again but after a line without colon
      # wrap-newwrapshiftedcomment:
      #       str w/ many spaces under an annot that is not wrap-doc
    # wrap-secondnewwraprightafterthelast:
    #  bla
    # wrap-notext

        fun(int x,    # a:3 wrap-doc:Will be overwritten
            float y,  # b:4
           )
        # wrap-doc:
        #  multiline
        #  for function
        

    """
    )
    (mdcl,) = cdcl.methods.get("fun")

    expected = dict(a="3", b="4")
    c = Code()
    c.addRawList(["multiline", "for function"])
    expected["wrap-doc"] = c.render()
    mdcl.annotations["wrap-doc"] = mdcl.annotations["wrap-doc"].render()
    assert mdcl.annotations == expected

    expected = dict()
    c = Code()
    c.addRawList(["Foobar wrap-wdsadas dsada", "continue"])
    expected["wrap-doc"] = c.render()
    expected["wrap-newwrapshiftedcomment"] = [
        "str w/ many spaces under an annot that is not wrap-doc"
    ]
    expected["wrap-secondnewwraprightafterthelast"] = ["bla"]
    expected["Not enough spaces"] = True
    expected["Enough spaces again but after a line without colon"] = True
    expected["wrap-notext"] = True
    cdcl.annotations["wrap-doc"] = cdcl.annotations["wrap-doc"].render()
    assert cdcl.annotations == expected


def test_minimal():
    (cld,) = autowrap.PXDParser.parse_str(
        """
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
    """
    )

    assert cld.name == "Minimal"
    assert cld.template_parameters is None

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
    assert arguments == [[("inp", CppType("int"))], [("inp", CppType("float"))]]

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


def test_ref():
    (gun,) = autowrap.PXDParser.parse_str(
        """
cdef extern from "":
    unsigned int & gun (vector[double &] &)
            """
    )
    assert gun.result_type == CppType.from_string("unsigned int &")
    ((n, t),) = gun.arguments
    assert t == CppType.from_string("vector[double &] &")


def test_ptr():
    (gun,) = autowrap.PXDParser.parse_str(
        """
cdef extern from "":
    unsigned int * gun (vector[double *] *)
            """
    )
    assert gun.result_type == CppType.from_string("unsigned int *")
    ((n, t),) = gun.arguments
    assert t == CppType.from_string("vector[double *] *")


def test_enum():
    (E,) = autowrap.PXDParser.parse_str(
        """
cdef extern from "":
    cdef enum E:
                A, B, C
            """
    )

    assert E.name == "E"
    A, B, C = E.items
    assert A == ("A", 0)
    assert B == ("B", 1)
    assert C == ("C", 2)


def test_class_and_enum():
    A, E = autowrap.PXDParser.parse_str(
        """
cdef extern from "":

    cdef cppclass A:
        A()

    cdef enum E:
                A, B, C
    """
    )

    assert A.name == "A"
    (method,) = A.methods.get("A")
    assert method.name == "A"
    assert len(method.arguments) == 0

    assert E.name == "E"
    A, B, C = E.items
    assert A == ("A", 0)
    assert B == ("B", 1)
    assert C == ("C", 2)


def test_multi_enum():
    E, F = autowrap.PXDParser.parse_str(
        """
cdef extern from "":
    cdef enum E:
                A, B, C

    cdef enum F:
                X, Y=4, Z

            """
    )

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
    E, F, X = autowrap.PXDParser.parse_str(
        """
cdef extern from "":
    cdef enum E:
                A, B, C

    cdef enum F:
                G, H=4, I

    cdef cppclass X:
         void fun(int)

            """
    )

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
    ((fun,),) = X.methods.values()
    assert fun.result_type == CppType("void"), fun.result_type
    assert fun.name == "fun"
    ((arg_name, type_),) = fun.arguments
    assert arg_name == ""
    assert type_ == CppType("int")


def test_multi_classes_in_one_file():
    inst1, inst2 = autowrap.PXDParser.parse_str(
        """
cdef extern from "A.h":
    cdef cppclass A[B,C] :
        # wrap-instances:
        #   A[int,int]
        void run()

    cdef cppclass C[E] :
        # wrap-instances:
        #   C[float]
        pass

    """
    )
    assert inst1.name == "A"
    assert inst1.template_parameters == ["B", "C"]
    assert list(inst1.methods.keys()) == ["run"]
    assert inst2.name == "C"
    assert inst2.template_parameters == [
        "E",
    ]
    assert len(inst2.methods) == 0


def test_typedef():
    decl1, decl2 = autowrap.PXDParser.parse_str(
        """
cdef extern from "A.h":
    ctypedef unsigned int myInt
    ctypedef long * allInt
    """
    )
    assert decl1.name == "myInt", decl1.name
    assert decl2.name == "allInt", decl2.name
    assert str(decl1.type_) == "unsigned int"
    assert str(decl2.type_) == "long int *", str(decl2.type_)


def test_typedef2():
    (decl1,) = autowrap.PXDParser.parse_str(
        """
cdef extern from "A.h":
    ctypedef size_t x
    """
    )
    assert decl1.name == "x", decl1.name
    assert str(decl1.type_) == "size_t", str(decl1.type_)


@expect_exception
def test_doubleptr():
    autowrap.PXDParser.parse_str(
        """
cdef extern from "A.h":
    void fun(int **)
        """
    )


def test_aliased_ptr():
    d1, d2 = autowrap.PXDParser.parse_str(
        """
cdef extern from "A.h":
    ctypedef int integer
    ctypedef integer * iptr
        """
    )
    assert d1.name == "integer"
    assert d2.name == "iptr"
    assert str(d1.type_) == "int"
    assert str(d2.type_) == "integer *", str(d2.type_)


def test_multi_alias():
    d1, d2, d3, d4 = autowrap.PXDParser.parse_str(
        """
cdef extern from "A.h":
    ctypedef int X
    ctypedef X * iptr
    ctypedef X Y
    ctypedef Y * iptr2
        """
    )
    assert d1.name == "X"
    assert str(d1.type_) == "int"
    assert d2.name == "iptr"
    assert str(d2.type_) == "X *"
    assert d3.name == "Y"
    assert str(d3.type_) == "X"
    assert d4.name == "iptr2"
    assert str(d4.type_) == "Y *"


def test_function():
    decl1, decl2 = autowrap.PXDParser.parse_str(
        """
cdef extern from "A.h":
    int floor(float x)
    int ceil(float x)
    """
    )

    assert decl1.name == "floor"
    assert decl2.name == "ceil"

    ((name, t),) = decl1.arguments
    assert name == "x"
    assert str(t) == "float"
    ((name, t),) = decl2.arguments
    assert name == "x"
    assert str(t) == "float"


def test_inner_unsigned():
    decl1, decl2 = autowrap.PXDParser.parse_str(
        """

cdef extern from "A.h":

    cdef cppclass A[X]:
        # wrap-ignore
        pass

    cdef cppclass T:
        fun(A[unsigned int])

    """
    )

    (fun,) = decl2.methods.get("fun")
    ((__, arg_t),) = fun.arguments
    assert str(arg_t) == "A[unsigned int]"


def test_static():
    (decl,) = autowrap.PXDParser.parse_str(
        """

cdef extern from "A.h":

    cdef cppclass A:
        int fun(int x) # wrap-static

    """
    )

    (fun,) = decl.methods.get("fun")
    ((__, arg_t),) = fun.arguments
    assert str(arg_t) == "int"


def test_free_function():
    (decl,) = autowrap.PXDParser.parse_str(
        """

cdef extern from "A.h":

    int fun(int x)

    """
    )

    assert decl.name == "fun"
    assert str(decl.result_type) == "int"
    ((__, arg_t),) = decl.arguments
    assert str(arg_t) == "int"


def test_attributes():
    (decl,) = autowrap.PXDParser.parse_str(
        """

cdef extern from "A.h":

    cdef cppclass A:
        int i
        float f
        int fun(int x) # wrap-static

    """
    )

    (fun,) = decl.methods.get("fun")
    ((__, arg_t),) = fun.arguments
    assert str(arg_t) == "int"


def test_annotation_typical_error_detection():
    # tests typical error for key:value decls in comments
    # with " " behind ":", eg "wrap-as: xyz" instead of "wrap-as:xyz":
    try:
        (cdcl,) = autowrap.PXDParser.parse_str(
            """

cdef extern from "*":
    cdef cppclass T:
        void fun() # wrap-as: xyz
        """
        )
    except:
        pass
    else:
        assert False, "expected exception"

    # annotation below is ok now !
    (cdcl,) = autowrap.PXDParser.parse_str(
        """

cdef extern from "*":
    cdef cppclass T:
        void fun() # wrap-as:xyz
        """
    )


def test_annotations():
    (cld,) = autowrap.PXDParser.parse_str(
        """
cdef extern from "*":
        cdef cppclass T:
            # wrap-ignore
            # wrap-as:
            #   Z

            void fun() # wrap-test:test  wrap-as:gun
            void fun(int x) # wrap-as:gun wrap-test:test
            void gun(
                    )  # wrap-as:hun

            void gun(
                    int x
                    )  # wrap-as:hun
            void iun(int x)
            void hun(int x
                    )  # wrap-as:jun
            void kun(int x) # wrap-with-no-gil
"""
    )

    assert len(cld.annotations) == 2
    assert cld.annotations["wrap-as"] == ["Z"]
    assert cld.annotations["wrap-ignore"] is True

    for mdcl in cld.methods["fun"]:
        # Also test if multiple annotations are correctly represented
        assert mdcl.annotations == {"wrap-as": "gun", "wrap-test": "test"}

    for mdcl in cld.methods["gun"]:
        assert mdcl.annotations == {"wrap-as": "hun"}

    for mdcl in cld.methods["iun"]:
        assert mdcl.annotations == {}

    for mdcl in cld.methods["hun"]:
        assert mdcl.annotations == {"wrap-as": "jun"}

    for mdcl in cld.methods["kun"]:
        assert mdcl.annotations == {"wrap-with-no-gil": True}


def test_parsing_of_nested_template_args():
    td1, td2, td3 = autowrap.PXDParser.parse_str(
        """

cdef extern from "*":

    ctypedef  A[B[C]]                   pfui
    ctypedef  A[C,D[E[F]]]              uiii
    ctypedef  A[Y, B[C[Y], C[Y, D[E]]]] huii
    """
    )

    assert str(td1.type_) == "A[B[C]]"
    assert str(td2.type_) == "A[C,D[E[F]]]"
    assert str(td3.type_) == "A[Y,B[C[Y],C[Y,D[E]]]]", str(td.type_)


def test_multiline_docs():
    lines = ["# wrap-doc:", "#  first line", "#    second line indented", "#  "]
    result = autowrap.PXDParser._parse_multiline_annotations(lines)

    assert result["wrap-doc"].content[0] == "first line"
    assert result["wrap-doc"].content[1] == "  second line indented"
    assert result["wrap-doc"].content[2] == ""


def test_consecutive_multiline_annotations():
    """Test that consecutive multiline annotations separated by empty lines are parsed correctly."""
    (cdcl,) = autowrap.PXDParser.parse_str(
        """
cdef extern from "*":
    cdef cppclass LinearInterpolation[V,W]:
        # wrap-doc:
        #  Linear interpolation for gridded data
        #  Supports various interpolation methods
        
        # wrap-instances:
        #   LinearInterpolation := LinearInterpolation[double, double]
        
        pass
    """
    )
    
    # Verify both annotations were parsed
    assert "wrap-doc" in cdcl.annotations
    assert "wrap-instances" in cdcl.annotations
    
    # Verify wrap-doc content
    expected_doc_content = ["Linear interpolation for gridded data", "Supports various interpolation methods"]
    assert cdcl.annotations["wrap-doc"].content == expected_doc_content
    
    # Verify wrap-instances content
    expected_instances = ["LinearInterpolation := LinearInterpolation[double, double]"]
    assert cdcl.annotations["wrap-instances"] == expected_instances
