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


def sub_libcpp_copy_constructors(libcpp):
    """Test copy constructors"""
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
    target = os.path.join(test_files, "generated", "libcpp_test.pyx")

    include_dirs = autowrap.parse_and_generate_code(
        ["libcpp_test.pxd"], root=test_files, target=target, debug=True
    )

    libcpp = autowrap.Utils.compile_and_import(
        "libcpp",
        [
            target,
        ],
        include_dirs,
    )
    assert libcpp.__name__ == "libcpp"
    print(dir(libcpp))
    assert len(libcpp.LibCppTest.__doc__) == 214
    assert len(libcpp.LibCppTest.twist.__doc__) == 111
    assert len(libcpp.LibCppTest.gett.__doc__) == 72
    # Length changed due to Sphinx RST syntax (:py:class:`AbstractBaseClass` instead of AbstractBaseClass)
    assert len(libcpp.ABS_Impl1.__doc__) == 98

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

    in_ = {1, 2}
    out = t.process9(in_)
    assert sorted(out) == [1, 2, 42]
    assert sorted(in_) == [1, 2, 42]

    in_ = {libcpp.EEE.A, libcpp.EEE.B}
    out = t.process10(in_)
    assert sorted(out) == sorted(in_)
    assert sorted(in_) == sorted(in_)

    in_ = {t2}
    out = t.process11(in_)
    assert sorted(x.gett() for x in in_) == [12, 42]
    assert sorted(x.gett() for x in out) == [12, 42]

    out = t.process12(1, 2.0)
    assert list(out.items()) == [(1, 2.0)]

    out = t.process13(libcpp.EEE.A, 2)
    assert list(out.items()) == [(libcpp.EEE.A, 2)]

    out = t.process14(libcpp.EEE.A, 3)
    assert list(out.items()) == [(3, libcpp.EEE.A)]

    out = t.process15(12)
    ((k, v),) = out.items()
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
    t.process212(d2, {b"42": [[11, 6], [2], [8]]})
    assert d2.get(1) == 11

    d3 = dict()
    t.process214(d3, {b"42": [[11, 6], [2, 8]]})
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

    empty_list = [[[[]]], [[[]]]]
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

    # process35 uses a shared_ptr for a const type, of which it makes a copy
    # This means that i1, i2 and i3 are three distinct objects that will not
    # affect each other when manipulated
    # TODO other option would be to have a second IntConst Wrapper type with only const methods
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
    tset = {libcpp.LibCppTest(), libcpp.LibCppTest()}
    assert len(tset) == 1, len(tset)
    t1 = libcpp.LibCppTest(1)
    t2 = libcpp.LibCppTest(2)
    tset = {t1, t1}
    assert len(tset) == 1
    tset = {t1, t2}
    assert len(tset) == 2

    tdict = {t1: "a", t2: "b"}
    assert len(tdict) == 2
