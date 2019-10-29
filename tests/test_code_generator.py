from __future__ import print_function
from __future__ import absolute_import

import pytest

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

import autowrap.DeclResolver
import autowrap.CodeGenerator
import autowrap.PXDParser
import autowrap.Utils
import autowrap.Code
import autowrap

import os
import math
import copy
import sys

from .utils import expect_exception

test_files = os.path.join(os.path.dirname(__file__), "test_files")


def test_number_conv():

    target = os.path.join(test_files, "number_conv.pyx")

    include_dirs = autowrap.parse_and_generate_code(["number_conv.pxd"],
                                                    root=test_files, target=target,  debug=True)

    mod = autowrap.Utils.compile_and_import("number_conv", [target, ], include_dirs)

    mf = mod.add_max_float(0)
    mf2 = mod.add_max_float(mf)
    assert not math.isinf(mf2), "somehow overflow happened"

    repr_ = "%.13e" % mod.pass_full_precision(0.05)
    assert repr_.startswith("5.0000000000000"), "loss of precision during conversion: %s" % repr_

    inl = [0.05]
    outl = mod.pass_full_precision_vec(inl)

    repr_ = "%.13e" % inl[0]
    assert repr_.startswith("5.0000000000000"), "loss of precision during conversion: %s" % repr_

    repr_ = "%.13e" % outl[0]
    assert repr_.startswith("5.0000000000000"), "loss of precision during conversion: %s" % repr_


def test_shared_ptr():

    target = os.path.join(test_files, "shared_ptr_test.pyx")
    include_dirs = autowrap.CodeGenerator.fixed_include_dirs(True) + [test_files]
    m = autowrap.Utils.compile_and_import("m", [target, ], include_dirs)
    assert m.__name__ == "m"

    h1 = m.Holder(b"uwe")
    assert h1.count() == 1
    assert h1.size() == 3
    h2 = h1.getRef()
    h3 = h1.getCopy()
    assert h1.count() == 2
    assert h1.size() == 3

    assert h2.count() == 2
    assert h2.size() == 3

    assert h3.count() == 1
    assert h3.size() == 3

    h2.addX()
    assert h1.count() == 2
    assert h1.size() == 4

    assert h2.count() == 2
    assert h2.size() == 4

    assert h3.count() == 1
    assert h3.size() == 3

    del h2

    assert h1.count() == 1
    assert h1.size() == 4

def sub_libcpp_copy_constructors(libcpp):
    """ Test copy constructors
    """
    import copy

    # Create new Int, make Python copy (shallow copy)
    int_wrp = libcpp.Int(1)
    assert int_wrp.i_ == 1
    int_wrpcpy = int_wrp
    assert int_wrpcpy.i_ == 1

    # changing one should change the other
    int_wrpcpy.i_ = 2
    assert int_wrp.i_ == 2
    assert int_wrpcpy.i_ == 2

    # Make real copy using copy()
    int_wrp2 = copy.copy(int_wrp)
    int_wrp2.i_ = 3
    assert int_wrp2.i_ == 3
    assert int_wrp.i_ == 2
    assert int_wrpcpy.i_ == 2

    # Make real copy using deepcopy()
    int_wrp3 = copy.deepcopy(int_wrp)
    int_wrp3.i_ = 4
    assert int_wrp3.i_ == 4
    assert int_wrp.i_ == 2
    assert int_wrpcpy.i_ == 2

    # Make real copy using copy constructor
    int_wrp4 = libcpp.Int(int_wrp)
    int_wrp4.i_ = 5
    assert int_wrp4.i_ == 5
    assert int_wrp.i_ == 2
    assert int_wrpcpy.i_ == 2

    # changing one should change the other
    int_wrpcpy.i_ = 1
    assert int_wrp.i_ == 1
    assert int_wrpcpy.i_ == 1

def test_libcpp():

    target = os.path.join(test_files, "libcpp_test.pyx")

    include_dirs = autowrap.parse_and_generate_code(["libcpp_test.pxd"],
                                                    root=test_files, target=target,  debug=True)

    libcpp = autowrap.Utils.compile_and_import("libcpp", [target, ], include_dirs)
    assert libcpp.__name__ == "libcpp"
    print(dir(libcpp))
    assert len(libcpp.LibCppTest.__doc__) == 214
    assert len(libcpp.LibCppTest.twist.__doc__) == 124
    assert len(libcpp.LibCppTest.gett.__doc__) == 66
    assert len(libcpp.ABS_Impl1.__doc__) == 89

    sub_libcpp_copy_constructors(libcpp)

    t = libcpp.LibCppTest()

    assert t.twist([b"hi", 2]) == [2, b"hi"]
    li = [1]
    li2 = t.process(li)
    assert li == li2 == [1, 42]

    assert t.twist.__doc__.find("Dont forget this stuff") != -1

    in1 = [1, 2]
    out = t.process2(in1)
    assert out == in1 == [42, 11]

    in1 = [t, 1]
    out = t.process3(in1)

    assert in1[0].gett() == 0
    assert in1[1] == 42
    assert out[0].gett() == 0
    assert out[1] == 42

    in1 = [1, t]
    out = t.process4(in1)

    assert in1[0] == 42
    assert in1[1].gett() == 0
    assert out[0] == 42
    assert out[1].gett() == 0

    t2 = libcpp.LibCppTest(12)
    in1 = [t, t2]
    out = t.process5(in1)
    assert in1[0].gett() == 43
    assert in1[1].gett() == 12
    assert out[0].gett() == 12
    assert out[1].gett() == 43

    in1 = [[1, 2.0], [2, 3.0]]
    out = t.process6(in1)
    assert in1 == [(1, 2.0), (2, 3.0), (7, 11.0)]
    assert out[::-1] == [(1, 2.0), (2, 3.0), (7, 11.0)]

    out = t.process7([0, 1])
    assert out == [1, 0]

    in_ = [0, 1, 0]
    out = t.process8(in_)
    assert in_ == out[::-1]

    in_ = set((1, 2))
    out = t.process9(in_)
    assert sorted(out) == [1, 2, 42]
    assert sorted(in_) == [1, 2, 42]

    in_ = set((libcpp.EEE.A, libcpp.EEE.B))
    out = t.process10(in_)
    assert sorted(out) == sorted(in_)
    assert sorted(in_) == sorted(in_)

    in_ = set((t2,))
    out = t.process11(in_)
    assert sorted(x.gett() for x in in_) == [12, 42]
    assert sorted(x.gett() for x in out) == [12, 42]

    out = t.process12(1, 2.0)
    assert list(out.items()) == [(1, 2.0)]

    out = t.process13(libcpp.EEE.A, 2)
    print (list(out.items()))
    print ([(libcpp.EEE.A, 2)])
    print (list(out.items()) == [(libcpp.EEE.A, 2)])
    assert list(out.items()) == [(libcpp.EEE.A, 2)]

    out = t.process14(libcpp.EEE.A, 3)
    assert list(out.items()) == [(3, libcpp.EEE.A)]

    out = t.process15(12)
    (k, v),  = out.items()
    assert k == 12
    assert v.gett() == 12

    assert t.process16({42: 2.0, 12: 1.0}) == 2.0

    assert t.process17({libcpp.EEE.A: 2.0, libcpp.EEE.B: 1.0}) == 2.0

    assert t.process18({23: t, 12: t2}) == t.gett()

    dd = dict()
    t.process19(dd)
    assert len(dd) == 1
    assert list(dd.keys()) == [23]
    assert list(dd.values())[0].gett() == 12

    dd = dict()
    t.process20(dd)
    assert list(dd.items()) == [(23, 42.0)]

    d1 = dict()
    t.process21(d1, {42: 11})
    assert d1.get(1) == 11

    d1 = dict()
    t.process211(d1, {b"42": [11, 6]})
    assert d1.get(1) == 11

    d2 = dict()
    t.process212(d2, {b"42": [ [11, 6], [2] , [8] ]})
    assert d2.get(1) == 11

    d3 = dict()
    t.process214(d3, {b"42": [ [11, 6], [2, 8] ]})
    assert d3.get(1) == 11

    d1 = set((42,))
    d2 = set()
    t.process22(d1, d2)
    assert d1 == set()
    assert d2 == set((42,))

    l1 = [1, 2]
    l2 = []

    t.process23(l1, l2)
    assert l1 == [1]
    assert l2 == [2.0]

    l1 = [1, 2.0]
    l2 = [2, 3]

    t.process24(l1, l2)
    assert l1 == [3, 2.0]

    i1 = libcpp.Int(1)
    i2 = libcpp.Int(2)
    i3 = libcpp.Int(3)

    assert t.process25([i1, i2, i3]) == 6
    assert t.process25([]) == 0

    assert t.process26([[i1, i2, i3]]) == 6
    assert t.process26([[i1, i2, i3], [i1]]) == 7
    assert t.process26([[i1, i2, i3], [i1], [i1, i2]]) == 10

    empty_list = [[]]
    empty_list = [[], [], []]
    t.process29(empty_list)
    assert len(empty_list) == 3
    assert len(empty_list[0]) == 1
    assert len(empty_list[1]) == 1
    assert len(empty_list[2]) == 1
    assert empty_list[0][0].i_ == 42

    empty_list = [[[[]]],   [[[]]]]
    t.process30(empty_list)

    assert len(empty_list) == 2
    assert len(empty_list[0]) == 2
    assert len(empty_list[1]) == 2
    assert empty_list[0][1][0][0].i_ == 42
    assert empty_list[1][1][0][0].i_ == 42

    assert t.process31([1, 2, 3]) == 6
    assert t.process31([]) == 0

    assert t.process32([[1, 2, 3]]) == 6
    assert t.process32([[1, 2, 3], [1]]) == 7
    assert t.process32([[1, 2, 3], [1], [1, 2]]) == 10

    i1 = libcpp.Int(1)
    assert t.process33(i1) == 2
    i2 = libcpp.Int(10)
    assert t.process33(i2) == 11

    # process34 modifies the shared ptr and returns it as well, there exists
    # only 1 C++ object of libcpp.Int but multiple Python objects point to it
    # using their shared_ptr.
    i1 = libcpp.Int(10)
    i2 = t.process34(i1)
    assert isinstance(i2, libcpp.Int)
    assert i1.i_ == 11
    assert i2.i_ == 11
    i3 = t.process34(i2)
    assert i1.i_ == 12
    assert i2.i_ == 12
    assert i3.i_ == 12

    try:
        assert t.integer_ptr is None
        assert False
    except Exception:
        # Should throw an exception
        assert True

    i1 = libcpp.Int(1)
    i2 = libcpp.Int(2)
    i3 = libcpp.Int(3)
    t.integer_ptr = i1
    assert t.integer_ptr.i_ == 1
    t.integer_ptr = i2
    assert t.integer_ptr.i_ == 2

    try:
        t.integer_vector_ptr
        assert False
    except Exception:
        # Should throw an exception
        assert True

    t.integer_vector_ptr = [i1, i2, i3]
    assert len(t.integer_vector_ptr) == 3


    # process35 uses a const shared_ptr of which it makes a copy
    # This means that i1, i2 and i3 are three distinct objects that will not
    # affect each other when manipulated
    i1 = libcpp.Int(20)
    i2 = t.process35(i1)
    assert isinstance(i2, libcpp.Int)
    assert i1.i_ == 21
    assert i2.i_ == 21
    i3 = t.process35(i2)
    assert i1.i_ == 21
    assert i2.i_ == 22
    assert i3.i_ == 22

    # 
    # Testing raw ptr
    #
    i1 = libcpp.Int(1)
    assert t.process36(i1) == 2
    assert t.process36(i1) == 3
    i2 = libcpp.Int(10)
    assert t.process36(i2) == 11
    #
    i1 = libcpp.Int(1)
    assert t.process37(i1).i_ == 2
    assert t.process37(i1).i_ == 3
    i2 = libcpp.Int(10)
    assert t.process37(i2).i_ == 11

    # return of NULL
    i1 = libcpp.Int(18)
    assert t.process37(i1) == None

    # return of const ptr
    i1 = libcpp.Int(1)
    assert t.process39(i1).i_ == 2
    assert t.process39(i1).i_ == 3
    i2 = libcpp.Int(10)
    assert t.process39(i2).i_ == 11

    rval = t.process39(i2)
    assert rval.i_ == 12

    # 
    # Unsigned Int 
    #
    res = t.process38(5)
    assert len(res) == 2
    assert len(res[0]) == 1
    assert res[0][0] == 5
    assert res[1][0] == 5


    # Testing abstract base class
    i1 = libcpp.ABS_Impl1(1)
    i2 = libcpp.ABS_Impl1(4)
    res = t.process40(i1)
    assert res == 1
    res = t.process40(i2)
    assert res == 4

    assert i1.get() == 1
    assert i2.get() == 4

    # Testing unsafe call
    i1 = libcpp.ABS_Impl1(__createUnsafeObject__=True)
    i2 = libcpp.ABS_Impl2(__createUnsafeObject__=True)

    try:
        i1 = libcpp.ABS_Impl1()
        raise Exception("Expected Exception not thrown")
    except Exception:
        pass

    try:
        i1 = libcpp.ABS_Impl2()
        raise Exception("Expected Exception not thrown")
    except Exception:
        pass

    # Use in dict/set
    # For this to work, the class needs to have __hash__ and __richcmp__ which
    # are wrapped by "wrap-hash" and operator== and operator!=
    tset = set([libcpp.LibCppTest(), libcpp.LibCppTest()])
    assert len(tset) == 1, len(tset)
    t1 = libcpp.LibCppTest(1)
    t2 = libcpp.LibCppTest(2)
    tset = set([t1, t1])
    assert len(tset) == 1
    tset = set([t1, t2])
    assert len(tset) == 2

    tdict = {t1 : "a", t2 : "b"}
    assert len(tdict) == 2

def test_stl_libcpp():

    target = os.path.join(test_files, "libcpp_stl_test.pyx")

    include_dirs = autowrap.parse_and_generate_code(["libcpp_stl_test.pxd"],
                                                    root=test_files, target=target,  debug=True)

    libcpp_stl = autowrap.Utils.compile_and_import("libcpp_stl", [target, ], include_dirs)
    assert libcpp_stl.__name__ == "libcpp_stl"
    print(dir(libcpp_stl))

    t = libcpp_stl.LibCppSTLTest()

    i1 = libcpp_stl.IntWrapper(1)
    i2 = libcpp_stl.IntWrapper(2)

    m1 = libcpp_stl.MapWrapper()
    m1.map_ = {3 : 8.0}
    m2 = libcpp_stl.MapWrapper(m1)
    m2.map_ = {3 : 8.0, 7 : 9.0}

    assert len(m1.map_) == 1
    assert len(m2.map_) == 2


    # Part 1
    # Test std::set< Widget* >
    set_inp = set([i1])
    assert t.process_1_set(set_inp) == 1 + 10
    assert list(set_inp)[0].i_ == 1 + 10
    set_inp = set([i2])
    assert t.process_1_set(set_inp) == 2 + 10
    assert list(set_inp)[0].i_ == 2 + 10

    expected = set([i1])
    res = t.process_2_set(i1) 
    assert len(res) == len(expected)
    # they should be the same object
    assert list(res)[0].i_ == list(expected)[0].i_

    # Part 2
    # Test std::vector< shared_ptr < Widget > >
    i1 = libcpp_stl.IntWrapper(1)
    i2 = libcpp_stl.IntWrapper(2)
    vec_inp = [ i1, i2, i2]
    assert len(vec_inp) == 3
    assert vec_inp[0].i_ == 1 
    assert t.process_3_vector(vec_inp) == 1 + 10
    assert len(vec_inp) == 4
    assert vec_inp[0].i_ == 1 + 10

    i1 = libcpp_stl.IntWrapper(1)
    out_vec = t.process_4_vector(i1)
    assert i1.i_ == 1 + 10
    assert len(out_vec) == 1
    assert out_vec[0].i_ == 1 + 10
    # they should be the same object
    assert i1.i_ == out_vec[0].i_
    i1.i_ += 10
    assert i1.i_ == 1 + 20
    assert out_vec[0].i_ == 1 + 20

    # Part 3
    # Test std::vector< Widget* >
    i1 = libcpp_stl.IntWrapper(1)
    i2 = libcpp_stl.IntWrapper(2)
    vec_inp = [i1]
    assert t.process_5_vector(vec_inp) == 1 + 10
    assert vec_inp[0].i_ == 1 + 10
    vec_inp = [i2]
    assert t.process_5_vector(vec_inp) == 2 + 10
    assert vec_inp[0].i_ == 2 + 10

    expected = [i1]
    res = t.process_6_vector(i1) 
    assert len(res) == len(expected)
    # they should be the same object
    assert res[0].i_ == expected[0].i_

    # Part 4
    # Test std::map< Widget, int >
    i1 = libcpp_stl.IntWrapper(1)
    i2 = libcpp_stl.IntWrapper(2)
    map_inp = {i2 : 5}
    assert t.process_7_map(map_inp) == 2
    assert len(map_inp) == 1
    assert list(map_inp.values())[0] == 5 + 10

    res = t.process_8_map(5)
    assert len(res) == 1
    assert list(res.keys())[0].i_ == 5
    assert list(res.values())[0] == 5 + 10

    # Part 5
    # Test std::map< int, Widget >
    i1 = libcpp_stl.IntWrapper(1)
    i2 = libcpp_stl.IntWrapper(2)
    map_inp = { 5: i2 }
    assert t.process_9_map(map_inp) == 5
    assert len(map_inp) == 1
    assert list(map_inp.values())[0].i_ == 2 + 10

    res = t.process_10_map(5)
    assert len(res) == 1
    assert list(res.values())[0].i_ == 5
    assert list(res.keys())[0] == 5 + 10

    # Test shared_ptr < const Widget >
    const_res = t.process_11_const()
    const_res.i_ == 42

def test_minimal():

    from autowrap.ConversionProvider import (TypeConverterBase,
                                             special_converters)

    class SpecialIntConverter(TypeConverterBase):

        def get_base_types(self):
            return "int",

        def matches(self, cpp_type):
            return cpp_type.is_unsigned

        def matching_python_type(self, cpp_type):
            return "int"

        def type_check_expression(self, cpp_type, argument_var):
            return "isinstance(%s, int)" % (argument_var,)

        def input_conversion(self, cpp_type, argument_var, arg_num):
            code = ""
            # here we inject special behavoir for testing if this converter
            # was called !
            call_as = "(1 + <int>%s)" % argument_var
            cleanup = ""
            return code, call_as, cleanup

        def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
            return "%s = <int>%s" % (output_py_var, input_cpp_var)

    special_converters.append(SpecialIntConverter())

    target = os.path.join(test_files, "minimal_wrapper.pyx")
    include_dirs = autowrap.parse_and_generate_code(["minimal.pxd",
                                                     "minimal_td.pxd"],
                                                    root=test_files, target=target,  debug=True)
    cpp_source = os.path.join(test_files, "minimal.cpp")
    wrapped = autowrap.Utils.compile_and_import("wrapped", [target, cpp_source],
                                                include_dirs)
    os.remove(target)
    assert wrapped.__name__ == "wrapped"

    minimal = wrapped.Minimal()

    assert len(minimal.compute.__doc__) == 297

    # test members
    assert minimal.m_accessible == 0
    assert minimal.m_const == -1

    minimal.m_accessible = 10
    assert minimal.m_accessible == 10

    try:
        minimal.m_const = 10
        assert False
    except AttributeError:
        # That is what we expected, cant modify a const member
        pass


    assert minimal.compute(3) == 4
    # overloaded for float:
    assert minimal.compute(0.0) == 42.0

    assert minimal.compute(1, 2) == 3
    assert minimal.compute_int(4) == 5
    assert minimal.compute(b"uwe") == b'ewu'
    assert minimal.compute_str(b"emzed") == b"dezme"
    assert minimal.pass_charptr(b"emzed") == b"emzed"
    assert minimal.pass_const_charptr(b"emzed") == b"emzed"

    assert minimal.compute_int() == 42

    # the c++ code of test_special_converter returns the same value, but
    # our special converter above modifies the function, so:
    assert minimal.test_special_converter(0) == 1

    expect_exception(lambda: minimal.compute(None))()

    assert minimal.compute_charp(b"uwe") == 3

    assert minimal.run(minimal) == 4
    assert minimal.run2(minimal) == 5

    # Note that both C++ calls run3 and run4 do modify the object -- the fact
    # that Cython thinks run4 is const does not impact this!
    tm = wrapped.Minimal(5)
    assert tm.get() == 5
    assert tm.run3(tm) == 14
    assert tm.get() == 10
    assert tm.run3(tm) == 24
    assert tm.get() == 20
    tm = wrapped.Minimal(5)
    assert tm.run4(tm) == 14
    assert tm.get() == 10
    assert tm.run4(tm) == 24
    assert tm.get() == 20

    assert minimal.create().compute(3) == 4

    assert minimal.sumup([1, 2, 3]) == 6

    m2 = wrapped.Minimal(-1)
    assert m2.compute(3) == 3

    assert wrapped.Minimal.ABCorD.A == 0
    assert wrapped.Minimal.ABCorD.B == 2
    assert wrapped.Minimal.ABCorD.C == 3
    assert wrapped.Minimal.ABCorD.D == 4

    in_ = [m2, minimal]

    m3 = copy.copy(m2)
    assert m3 == m2

    m3 = wrapped.Minimal([1, 2, 3])
    assert m3.compute(0) == 4

    ### Different ways of wrapping a function: 
    # all three call() methods (call, call2, call3) do exactly the same thing
    # and all modify the input argument. However, they are wrapped differently
    # in the pxd file:
    #
    #   int call(libcpp_vector[Minimal] what) # ref-arg-out:0
    #   int call2(libcpp_vector[Minimal]& what) # ref-arg-out:0
    #   int call3(const libcpp_vector[Minimal]& what) # ref-arg-out:0
    #
    # and therefore only call2 will actually modify its input arguments (since
    # call assumes call by value, call3 assumes call by const-ref and only
    # call2 implements a full call by ref).
    #
    assert len(in_) == 2
    assert m3.call(in_) == 1
    assert len(in_) == 2
    assert in_ == [m2, minimal]

    assert len(in_) == 2
    assert m3.call3(in_) == 1
    assert len(in_) == 2
    assert in_ == [m2, minimal]

    assert len(in_) == 2
    assert m3.call2(in_) == 1
    assert len(in_) == 3
    assert in_ == [m2, minimal, m2]

    in_ = [b"a", b"bc"]
    assert m3.call_str(in_) == 3
    assert in_ == [b"a", b"bc", b"hi"]

    msg, = m3.message()
    assert msg == b"hello"

    m1, m2 = m3.create_two()
    assert m1.compute(42) == 42
    assert m2.compute(42) == 43

    assert m2.enumTest(wrapped.Minimal.ABCorD.A) == wrapped.Minimal.ABCorD.A

    expect_exception(lambda: m2.enumTest(1))()

    m2.setVector([m2, m1, m3])
    a, b, c = m2.getVector()
    assert a == m2
    assert b == m1
    assert c == m3

    a, b, c = list(m2)  # call __iter__
    assert a == m2
    assert b == m1
    assert c == m3

    assert m2.test2Lists([m1], [1, 2]) == 3
    assert m1 == m1

    # tests operator[] + size:
    assert list(m1) == []
    assert list(m2) == [m2, m1, m3]

    assert wrapped.top_function(42) == 84
    assert wrapped.sumup([1, 2, 3]) == 6
    assert wrapped.Minimal.run_static(1) == 4
    assert wrapped.Minimal.run_static_extra_arg(1, True) == 4

    # != not declared, so:
    expect_exception(lambda m1, m2: m1 != m2)(m1, m2)

    assert m1.toInt() == 4711

    assert m2[0] == 1
    assert m2[1] == 2
    assert m2[2] == 3

    with pytest.raises(OverflowError):
        m2[-1]

    with pytest.raises(IndexError):
        m2[3]

    # operator add
    assert wrapped.Minimal(1) + wrapped.Minimal(2) == wrapped.Minimal(3)

    m1 = wrapped.Minimal(1)
    m1 += m1
    assert m1 == wrapped.Minimal(2)

    m1 = wrapped.Minimal(1)
    m1 = m1 + m1
    assert m1 == wrapped.Minimal(2)

    # operator mult
    assert wrapped.Minimal(5) * wrapped.Minimal(2) == wrapped.Minimal(10)

    m1 = wrapped.Minimal(3)
    m1 = m1 * m1
    m2 = m1 * m1
    assert m1 == wrapped.Minimal(9)
    assert m2 == wrapped.Minimal(81)


def test_templated():

    target = os.path.join(test_files, "templated_wrapper.pyx")

    decls, instance_map = autowrap.parse(["templated.pxd"], root=test_files)

    co = autowrap.Code.Code()
    co.add("""def special(self):
             |    return "hi" """)

    methods = dict(T=co)

    include_dirs = autowrap.generate_code(decls, instance_map, target=target,
                                          debug=True, manual_code=methods)

    cpp_source = os.path.join(test_files, "templated.cpp")
    cpp_sources = []

    twrapped = autowrap.Utils.compile_and_import("twrapped",
                                                 [target] + cpp_sources,
                                                 include_dirs)
    os.remove(target)
    assert twrapped.__name__ == "twrapped"

    t = twrapped.T(42)
    assert t.special() == "hi"
    templated = twrapped.Templated(t)
    assert templated.get().get() == 42

    assert templated.passs(templated) == templated

    in_ = [templated, templated]
    assert templated.summup(in_) == 42 + 42
    __, __, tn = in_
    assert tn.get().get() == 11

    tn, __, __ = templated.reverse(in_)
    assert tn.get().get() == 11

    y = twrapped.Y()
    _, __, tn = y.passs(in_)
    assert tn.get().get() == 11

    # renamed attribute
    templated.f_att = 2
    assert templated.f_att == 2.0
    templated.f_att = 4
    assert templated.f_att == 4.0

    t13 = twrapped.T(13)
    templated._x = t13
    assert templated._x.get() == 13
    t17 = twrapped.T(17)
    templated._x = t17
    assert templated._x.get() == 17

    templated.xi = [t13, t17]
    assert templated.xi[0].get() == 13
    assert templated.xi[1].get() == 17

    templated.xi = [t17, t13]
    assert templated.xi[0].get() == 17
    assert templated.xi[1].get() == 13

    # Test second template (it adds 1 to everything)
    t_o = twrapped.T2(42)
    templated_o = twrapped.Templated_other(t_o)
    assert templated_o.get().get() == 43
    assert templated_o.passs(templated_o) == templated_o

    # Try out the adding 1 thing
    t11 = twrapped.T2(10)
    t12 = twrapped.T2(11)

    templated_o.xi = [t11, t12]
    assert templated_o.xi[0].get() == 11
    assert templated_o.xi[1].get() == 12

    # Test free functions
    assert templated.computeSeven() == 7
    assert templated_o.computeSeven() == 7


def test_gil_unlock():

    target = os.path.join(test_files, "gil_testing_wrapper.pyx")
    include_dirs = autowrap.parse_and_generate_code(["gil_testing.pxd"],
                                                    root=test_files, target=target,  debug=True)

    wrapped = autowrap.Utils.compile_and_import("gtwrapped", [target, ],
                                                include_dirs)
    g = wrapped.GilTesting(b"Jack")
    g.do_something(b"How are you?")
    assert g.get_greetings() == b"Hello Jack, How are you?"


def test_automatic_string_conversion():
    target = os.path.join(test_files, "libcpp_utf8_string_test.pyx")
    include_dirs = autowrap.parse_and_generate_code(["libcpp_utf8_string_test.pxd"],
                                                    root=test_files, target=target,  debug=True)

    wrapped = autowrap.Utils.compile_and_import("libcpp_utf8_string_wrapped", [target, ],
                                                include_dirs)
    h = wrapped.Hello()

    input_bytes = b"J\xc3\xbcrgen"
    input_unicode = b"J\xc3\xbcrgen".decode('utf-8')

    expected = b"Hello J\xc3\xbcrgen"

    msg = h.get(input_bytes)
    assert isinstance(msg, bytes)
    assert msg == expected

    msg = h.get(input_unicode)
    assert isinstance(msg, bytes)
    assert msg == expected

    input_greet_bytes = b"Hall\xc3\xb6chen"
    input_greet_unicode = input_greet_bytes.decode('utf-8')

    expected = b"Hall\xc3\xb6chen J\xc3\xbcrgen"

    msg = h.get_more({"greet": input_greet_unicode, "name": input_bytes})
    assert isinstance(msg, bytes)
    assert msg == expected


def test_automatic_output_string_conversion():
    target = os.path.join(test_files, "libcpp_utf8_output_string_test.pyx")
    include_dirs = autowrap.parse_and_generate_code(["libcpp_utf8_output_string_test.pxd"],
                                                    root=test_files, target=target, debug=True)

    wrapped = autowrap.Utils.compile_and_import("libcpp_utf8_output_string_wrapped", [target, ],
                                                include_dirs)
    h = wrapped.LibCppUtf8OutputStringTest()

    input_bytes = b"J\xc3\xbcrgen"
    input_unicode = b"J\xc3\xbcrgen".decode('utf-8')

    expected = b"Hello J\xc3\xbcrgen".decode('utf-8')
    expected_type = str
    if sys.version_info[0] < 3:
        expected_type = unicode

    msg = h.get(input_bytes)
    assert isinstance(msg, expected_type)
    assert msg == expected

    msg = h.get(input_unicode)
    assert isinstance(msg, expected_type)
    assert msg == expected


# todo: wrapped tempaltes as input of free functions and mehtods of other
# classes
#
#
if __name__ == "__main__":
    test_libcpp()
