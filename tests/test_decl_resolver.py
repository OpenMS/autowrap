from __future__ import print_function

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

import autowrap.DeclResolver as DeclResolver
import autowrap.PXDParser
import os
from autowrap.Types import CppType
from autowrap.Utils import print_map

from .utils import expect_exception


def test_inst_decl_parser():
    name, type_ = DeclResolver.parse_inst_decl("A := B[]")
    assert name == "A" and str(type_) == "B[]", (str(name), str(type_))
    name, type_ = DeclResolver.parse_inst_decl("A := B[X]")
    assert name == "A" and str(type_) == "B[X]", (str(name), str(type_))
    name, type_ = DeclResolver.parse_inst_decl("A := B[X*]")
    assert name == "A" and str(type_) == "B[X *]", (str(name), str(type_))
    name, type_ = DeclResolver.parse_inst_decl("A := B[X,Y]")
    assert name == "A" and str(type_) == "B[X,Y]", (str(name), str(type_))
    name, type_ = DeclResolver.parse_inst_decl("A := B[X,Y*]")
    assert name == "A" and str(type_) == "B[X,Y *]", (str(name), str(type_))

    name, type_ = DeclResolver.parse_inst_decl("A := B[1,Y*]")
    assert name == "A" and str(type_) == "B[1,Y *]", (str(name), str(type_))


def test_function_resolution():
    decls, instance_mapping = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "A.h":
    ctypedef int X
    ctypedef float Y
    Y fun(X i)
    C[Y] gun(C[X] i)
    """
    )

    X, Y, fun, gun = sorted(decls, key=lambda d: d.name)

    assert str(fun.result_type) == "float"
    ((n, t),) = fun.arguments
    assert str(t) == "int"
    assert n == "i"

    assert str(gun.result_type) == "C[float]"
    ((n, t),) = gun.arguments
    assert str(t) == "C[int]"
    assert n == "i"


def test_method_resolution():
    decls, instance_mapping = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "A.h":
    ctypedef int X
    ctypedef float Y
    cdef cppclass T:
        Y fun(X i)
        C[Y] gun(C[X] i)
    """
    )
    T, X, Y = sorted(decls, key=lambda d: d.name)

    assert T.name == "T"
    (fun,) = T.methods.get("fun")
    assert str(fun.result_type) == "float"
    ((n, t),) = fun.arguments
    assert str(t) == "int"
    assert n == "i"

    (gun,) = T.methods.get("gun")
    assert str(gun.result_type) == "C[float]"
    ((n, t),) = gun.arguments
    assert str(t) == "C[int]"
    assert n == "i"


def test_method_resolution_in_template_class():
    decls, instance_mapping = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "A.h":
    ctypedef int X
    cdef cppclass T[Y]:
        # wrap-instances:
        #   T := T[float]
        Y fun(X i)
        C[Y] gun(C[X] i)
        T[Y] hun(T[Y] j)

    """
    )
    T, X = sorted(decls, key=lambda d: d.name)

    assert T.name == "T"
    (fun,) = T.methods.get("fun")
    assert str(fun.result_type) == "float"
    ((n, t),) = fun.arguments
    assert str(t) == "int"
    assert n == "i"

    (gun,) = T.methods.get("gun")
    assert str(gun.result_type) == "C[float]"
    ((n, t),) = gun.arguments
    assert str(t) == "C[int]"
    assert n == "i"

    (gun,) = T.methods.get("hun")
    assert str(gun.result_type) == "T"
    ((n, t),) = gun.arguments
    assert str(t) == "T"
    assert n == "j"


def _resolve(*names, **kwargs):
    root = os.path.join(os.path.dirname(__file__), "test_files")
    num_processes = kwargs.get("num_processes", 1)
    return autowrap.DeclResolver.resolve_decls_from_files(
        names, root=root, num_processes=num_processes
    )


def test_simple():
    (cdcl, enumdcl, f1, f2, f3, f4), map_ = _resolve("minimal.pxd", num_processes=1)

    assert cdcl.name == "Minimal"
    assert enumdcl.name == "ABCorD"
    assert sorted(map_.keys()) == ["ABCorD", "Minimal"]
    assert sorted(map(str, map_.values())) == ["ABCorD", "Minimal"]
    assert f1.name == "top_function"
    assert f2.name == "sumup"
    assert f3.name == "run_static"
    assert f3.name == f3.cpp_decl.name
    assert f4.name == "run_static_extra_arg"
    assert f4.cpp_decl.name == "run_static"  # need to remember the raw cpp fxn name


def test_simple_mp():
    (cdcl, enumdcl, f1, f2, f3, f4), map_ = _resolve("minimal.pxd", num_processes=2)

    assert cdcl.name == "Minimal"
    assert enumdcl.name == "ABCorD"
    assert sorted(map_.keys()) == ["ABCorD", "Minimal"]


def test_singular():
    resolved, map_ = _resolve("templates.pxd")

    assert len(resolved) == 2, len(resolved)
    res0, res1 = resolved
    if res0.name > res1.name:
        res0, res1 = res1, res0
    assert res0.name == "TemplatesInt", res0.name
    assert res1.name == "TemplatesMixed", res1.name

    res0_names = map(lambda m: m.name, res0.get_flattened_methods())
    res1_names = map(lambda m: m.name, res1.get_flattened_methods())
    assert list(res0_names) == [
        "TemplatesInt",
        "getA",
        "getB",
        "toA",
        "toB",
        "convert",
        "r0",
        "r1",
        "r2",
        "r3",
    ], res0_names

    res0_restypes = map(str, (m.result_type for m in res0.get_flattened_methods()))

    assert list(res0_restypes) == [
        "void",
        "int",
        "int",
        "int",
        "int",
        "void",
        "TemplatesInt",
        "TemplatesMixed",
        "Templates[double,float]",
        "TemplatesInt",
    ], res0_restypes

    res0_names = map(lambda m: m.name, res0.get_flattened_methods())
    res1_names = map(lambda m: m.name, res1.get_flattened_methods())
    print(res0_names)
    print(res1_names)
    assert list(res0_names) == [
        "TemplatesInt",
        "getA",
        "getB",
        "toA",
        "toB",
        "convert",
        "r0",
        "r1",
        "r2",
        "r3",
    ], res0_names

    first_arg_names = map(
        lambda m: None if len(m.arguments) == 0 else str(m.arguments[0][0]),
        res0.get_flattened_methods(),
    )
    assert list(first_arg_names) == [
        "a",
        None,
        None,
        None,
        None,
        "arg0",
        "",
        "",
        None,
        "",
    ], first_arg_names

    second_arg_names = map(
        lambda m: None if len(m.arguments) < 2 else str(m.arguments[1][0]),
        res0.get_flattened_methods(),
    )
    assert list(second_arg_names) == [
        "b",
        None,
        None,
        None,
        None,
        "arg1",
        None,
        None,
        None,
        "",
    ], second_arg_names

    first_arg_types = map(
        lambda m: None if len(m.arguments) == 0 else str(m.arguments[0][1]),
        res0.get_flattened_methods(),
    )

    assert list(first_arg_types) == [
        "int",
        None,
        None,
        None,
        None,
        "list[int]",
        "TemplatesMixed",
        "TemplatesInt",
        None,
        "int",
    ], first_arg_types

    second_arg_types = map(
        lambda m: None if len(m.arguments) < 2 else str(m.arguments[1][1]),
        res0.get_flattened_methods(),
    )
    assert list(second_arg_types) == [
        "int",
        None,
        None,
        None,
        None,
        "list[int] &",
        None,
        None,
        None,
        "int",
    ], second_arg_types

    res1_restypes = map(lambda m: str(m.result_type), res1.get_flattened_methods())
    assert list(res1_restypes) == [
        "void",
        "int",
        "float",
        "int",
        "float",
        "void",
        "TemplatesInt",
        "TemplatesMixed",
        "Templates[double,float]",
        "TemplatesMixed",
    ], res1_restypes

    res1_names = map(lambda m: m.name, res1.get_flattened_methods())
    assert list(res1_names) == [
        "TemplatesMixed",
        "getA",
        "getB",
        "toA",
        "toB",
        "convert",
        "r0",
        "r1",
        "r2",
        "r3",
    ], res1_names

    first_arg_names = map(
        lambda m: None if len(m.arguments) == 0 else str(m.arguments[0][0]),
        res1.get_flattened_methods(),
    )
    assert list(first_arg_names) == [
        "a",
        None,
        None,
        None,
        None,
        "arg0",
        "",
        "",
        None,
        "",
    ], first_arg_names

    second_arg_names = map(
        lambda m: None if len(m.arguments) < 2 else str(m.arguments[1][0]),
        res1.get_flattened_methods(),
    )
    assert list(second_arg_names) == [
        "b",
        None,
        None,
        None,
        None,
        "arg1",
        None,
        None,
        None,
        "",
    ], second_arg_names

    first_arg_types = map(
        lambda m: None if len(m.arguments) == 0 else str(m.arguments[0][1]),
        res1.get_flattened_methods(),
    )

    assert list(first_arg_types) == [
        "int",
        None,
        None,
        None,
        None,
        "list[int]",
        "TemplatesMixed",
        "TemplatesInt",
        None,
        "int",
    ], first_arg_types

    second_arg_types = map(
        lambda m: None if len(m.arguments) < 2 else str(m.arguments[1][1]),
        res1.get_flattened_methods(),
    )
    assert list(second_arg_types) == [
        "float",
        None,
        None,
        None,
        None,
        "list[float] &",
        None,
        None,
        None,
        "float",
    ], second_arg_types


def test_multi_inherit():
    resolved, map_ = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "A.h":
    cdef cppclass A[U]:
        # wrap-ignore
        void Afun(U, int)

cdef extern from "B.h":
    cdef cppclass B[X]:
        # wrap-ignore
        # wrap-inherits:
        #     A[X]
        X BIdentity(X)

cdef extern from "C.h":
    cdef cppclass C[Y]:
        # wrap-ignore
        # wrap-inherits:
        #     A[Y]
        void Cint(int, Y)

cdef extern from "D.h":
    cdef cppclass D[F, G]:
        # wrap-inherits:
        #  B[G]
        #  C[F]
        #
        # wrap-instances:
        #  D1 := D[float,int]
        #  D2 := D[int,float]
        pass
    """
    )

    data = dict()
    for class_instance in resolved:
        mdata = []
        for m in class_instance.get_flattened_methods():
            li = [str(m.result_type), m.name]
            li += [str(t) for n, t in m.arguments]
            mdata.append(li)
        data[class_instance.name] = sorted(mdata)

    assert data == {
        "D1": sorted(
            [
                ["void", "Afun", "int", "int"],
                ["void", "Afun", "float", "int"],
                ["int", "BIdentity", "int"],
                ["void", "Cint", "int", "float"],
            ]
        ),
        "D2": sorted(
            [
                ["void", "Afun", "float", "int"],
                ["void", "Afun", "int", "int"],
                ["float", "BIdentity", "float"],
                ["void", "Cint", "int", "int"],
            ]
        ),
    }


@expect_exception
def test_cycle_detection_in_class_hierarchy0():
    _resolve("Cycle0.pxd", "Cycle1.pxd", "Cycle2.pxd")


@expect_exception
def test_cycle_detection_in_class_hierarchy1():
    _resolve("Cycle1.pxd", "Cycle2.pxd", "Cycle0.pxd")


@expect_exception
def test_cycle_detection_in_class_hierarchy2():
    _resolve("Cycle2.pxd", "Cycle0.pxd", "Cycle1.pxd")


def test_nested_templates():
    (
        i1,
        i2,
    ), map_ = DeclResolver.resolve_decls_from_string(
        """
from libcpp.string cimport string as libcpp_string
from libcpp.vector cimport vector as libcpp_vector

cdef extern from "templated.hpp":

    cdef cppclass T:
        T(int)
        T(T) # wrap-ignore
        int get()

    cdef cppclass Templated[X]:
        # wrap-instances:
        #   Templated := Templated[T]
        Templated(X)
        libcpp_vector[Templated[X]] reverse(libcpp_vector[Templated[X]] v)
        int getTwice(Templated[X])
            """
    )

    (rev,) = i2.methods.get("reverse")
    ((n, t),) = rev.arguments
    assert str(t) == "libcpp_vector[Templated]"

    (rev,) = i2.methods.get("getTwice")
    ((n, t),) = rev.arguments
    assert str(t) == "Templated", str(t)


def test_non_template_class_with_annotation():
    (instance,), map_I = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "A.h":
    cdef cppclass A:
        # wrap-instances:
        #  B := A
        pass
    """
    )
    assert instance.name == "B"


def test_template_class_with_ptrtype():
    (instance,), map_ = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "A.h":
    cdef cppclass A[X]:
        # wrap-instances:
        #  Ax := A[int*]
        pass
    """
    )
    assert instance.name == "Ax"
    (real_type,) = map_.values()
    assert str(real_type) == "A[int *]", str(real_type)


def test_multi_decls_in_one_file():
    (inst1, inst2, enum), map_ = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "A.h":
    cdef cppclass A[B,C] :
        # wrap-instances:
        #   A := A[int,int]
        pass

    cdef cppclass C[E] :
        # wrap-instances:
        #   C := C[float]
        pass

    cdef enum F:
            G, H=4, I
    """
    )
    assert inst1.name == "A"
    T1, T2 = inst1.cpp_decl.template_parameters
    assert T1 == "B", T1
    assert T2 == "C", T2
    assert len(inst1.methods) == 0

    assert inst2.name == "C"
    (T1,) = inst2.cpp_decl.template_parameters
    assert T1 == "E", T1
    assert len(inst2.methods) == 0

    assert enum.name == "F"
    G, H, I = enum.items
    assert G == ("G", 0)
    assert H == ("H", 4)
    assert I == ("I", 5)

    assert str(map_["A"]) == "A[int,int]"
    assert str(map_["C"]) == "C[float]"
    assert str(map_["F"]) == "F"


def test_int_container():
    # tests nested types, and constructor name mapping
    (r0, r1), map_ = _resolve("int_container_class.pxd")
    assert r0.name == "Xint"
    assert [m.name for m in r0.get_flattened_methods()] == [
        "Xint",
        "operator+",
        "getValue",
    ]
    assert r1.name == "XContainerInt"
    assert [m.name for m in r1.get_flattened_methods()] == [
        "XContainerInt",
        "push_back",
        "size",
    ]


def test_typedef_with_fun():
    decls, map_ = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "X.h":
    ctypedef int X
    X fun(X x)
            """
    )

    X, fun = sorted(decls, key=lambda d: d.name)

    assert fun.name == "fun"
    assert str(fun.result_type) == "int"
    ((n, t),) = fun.arguments
    assert n == "x"
    assert str(t) == "int"


def test_typedef_chaining():
    decls, map_ = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "X.h":
    ctypedef int X
    ctypedef X* iptr
    ctypedef X Y
    ctypedef Y* iptr2
    iptr2 fun(iptr, Y *)
            """
    )

    X, Y, fun, iptr, iptr2 = sorted(decls, key=lambda d: d.name)

    assert str(fun.result_type) == "int *"
    t1, t2 = map(str, (t for (n, t) in fun.arguments))
    assert t1 == "int *", t1
    assert t2 == "int *", t2


@expect_exception
def double_ptr_typedef():
    (function,), map_ = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "X.h":
    ctypedef int X
    ctypedef X * iptr
    ctypedef X * Y
    ctypedef Y * iptr2
    iptr2 fun(iptr, Y)
            """
    )


@expect_exception
def ctypedef_with_cycle():
    (function,), map_ = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "X.h":
    ctypedef int X
    ctypedef X Y
    ctypedef Y Z
    ctypedef Z X
    iptr2 fun(iptr, Y)
            """
    )


def test_typedef_with_class():
    decls, map_ = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "X.h":
    ctypedef int X
    ctypedef int * Y
    cdef cppclass A[B]:
        # wrap-instances:
        #   A := A[X]
        X foo(B)
        B bar(X *)
    Y fun(X *)
            """
    )

    A, X_, Y, fun = sorted(decls, key=lambda d: d.name)
    assert A.name == "A"
    assert str(map_.get("A")) == "A[int]"

    (foo,) = A.methods.get("foo")
    assert str(foo.result_type) == "int", foo.result_type
    ((__, arg_t),) = foo.arguments
    assert str(arg_t) == "int", str(arg_t)

    (bar,) = A.methods.get("bar")
    assert str(bar.result_type) == "int"
    ((__, arg_t),) = bar.arguments
    assert str(arg_t) == "int *"

    assert fun.name == "fun"
    assert str(fun.result_type) == "int *"
    ((__, arg_t),) = fun.arguments
    assert str(arg_t) == "int *", str(arg_t)


def test_typedef_with_class2():
    decls, map_ = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "X.h":
    ctypedef int X
    cdef cppclass A[B]:
        # wrap-instances:
        #   A := A[X *]
        X foo(B)
        B bar(X)
            """
    )

    A, X = sorted(decls, key=lambda d: d.name)
    assert A.name == "A"

    assert str(map_.get("A")) == "A[int *]"

    (foo,) = A.methods.get("foo")
    assert str(foo.result_type) == "int", foo.result_type
    ((__, arg_t),) = foo.arguments
    assert str(arg_t) == "int *", str(arg_t)

    (bar,) = A.methods.get("bar")
    assert str(bar.result_type) == "int *"
    ((__, arg_t),) = bar.arguments
    assert str(arg_t) == "int", str(arg_t)


def test_typedef_with_class3():
    decls, map_ = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "X.h":
    ctypedef int X
    cdef cppclass A[B,C]:
        # wrap-instances:
        #   A := A[X *,int]
        X foo(C*)
        C* bar(B)
            """
    )
    A, X = sorted(decls, key=lambda d: d.name)

    assert A.name == "A"

    assert str(map_.get("A")) == "A[int *,int]"

    (foo,) = A.methods.get("foo")
    assert str(foo.result_type) == "int", foo.result_type
    ((__, arg_t),) = foo.arguments
    assert str(arg_t) == "int *", str(arg_t)

    (bar,) = A.methods.get("bar")
    assert str(bar.result_type) == "int *"
    ((__, arg_t),) = bar.arguments
    assert str(arg_t) == "int *", str(arg_t)


def test_without_header():
    # broken
    return
    (resolved,) = DeclResolver.resolve_decls_from_string(
        """
cdef extern:
    ctypedef int X
    X fun(X x)
            """
    )


def test_method_return_values():
    (resolved,), map_ = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "minimal.hpp":
    cdef cppclass Minimal:
        Minimal create()
"""
    )
    (meth,) = resolved.methods.get("create")
    assert str(meth.result_type) == "Minimal"


def test_class_and_enum():
    (A, E), map_ = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "":

    cdef cppclass A:
        A()

    cdef enum E:
                A, B, C
    """
    )

    assert A.name == "A"
    (method,) = list(A.methods.values())[0]
    assert method.name == "A"
    assert len(method.arguments) == 0

    assert E.name == "E"
    A, B, C = E.items
    assert A == ("A", 0)
    assert B == ("B", 1)
    assert C == ("C", 2)


def test_copy_cons_decl_for_templated_class():
    (A,), map_ = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "":

    cdef cppclass A[T]:
        # wrap-instances:
        #   A := A[int]
        A(A[T] &)

    """
    )

    assert A.name == "A"
    (m,) = A.methods["A"]
    print(m)


def test_with_no_gil_annotation():
    (instance,), map_I = DeclResolver.resolve_decls_from_string(
        """
cdef extern from "A.h":
    cdef cppclass A:
        A()
        void Expensive() nogil # wrap-with-no-gil
        void Cheap()

    """
    )
    assert instance.name == "A"
    (method,) = instance.methods.get("Expensive")
    assert method.with_nogil
    (method,) = instance.methods.get("Cheap")
    assert not method.with_nogil
