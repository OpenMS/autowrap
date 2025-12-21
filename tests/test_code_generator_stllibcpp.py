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


def test_stl_libcpp():
    target = os.path.join(test_files, "generated", "libcpp_stl_test.pyx")

    include_dirs = autowrap.parse_and_generate_code(
        ["libcpp_stl_test.pxd"], root=test_files, target=target, debug=True
    )

    libcpp_stl = autowrap.Utils.compile_and_import(
        "libcpp_stl",
        [
            target,
        ],
        include_dirs,
    )
    assert libcpp_stl.__name__ == "libcpp_stl"
    print(dir(libcpp_stl))

    t = libcpp_stl.LibCppSTLTest()

    i1 = libcpp_stl.IntWrapper(1)
    i2 = libcpp_stl.IntWrapper(2)

    m1 = libcpp_stl.MapWrapper()
    m1.map_ = {3: 8.0}
    m2 = libcpp_stl.MapWrapper(m1)
    m2.map_ = {3: 8.0, 7: 9.0}

    assert len(m1.map_) == 1
    assert len(m2.map_) == 2

    # Test wrapping of operator[]
    vec_wrapper = libcpp_stl.IntVecWrapper()
    vec_wrapper.push_back(5)
    assert vec_wrapper[0] == 5
    vec_wrapper[0] = 7
    assert vec_wrapper[0] == 7

    vec_wrapper = libcpp_stl.LibCppSTLVector()
    itest = libcpp_stl.IntWrapper(5)
    vec_wrapper.push_back(itest)
    assert vec_wrapper[0].i_ == 5
    itest = libcpp_stl.IntWrapper(7)
    vec_wrapper[0] = itest
    assert vec_wrapper[0].i_ == 7

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
    vec_inp = [i1, i2, i2]
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
    map_inp = {i2: 5}
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
    map_inp = {5: i2}
    assert t.process_9_map(map_inp) == 5
    assert len(map_inp) == 1
    assert list(map_inp.values())[0].i_ == 2 + 10

    res = t.process_10_map(5)
    assert len(res) == 1
    assert list(res.values())[0].i_ == 5
    assert list(res.keys())[0] == 5 + 10

    # Test shared_ptr < const Widget >
    const_res = t.process_11_const()
    assert const_res.i_ == 42

    # Part 6
    # Test std::map< string, IntWrapper >
    i1 = libcpp_stl.IntWrapper(1)
    i2 = libcpp_stl.IntWrapper(2)
    map_inp = {b"test": i2}
    assert t.process_12_map(map_inp) == 2 + 10
    assert len(map_inp) == 1
    assert list(map_inp.values())[0].i_ == 2 + 10

    # Part 7
    # Test std::map< Widget, vector<int> >
    i1 = libcpp_stl.IntWrapper(1)
    i2 = libcpp_stl.IntWrapper(2)
    map_inp = {i2: [6, 2]}
    assert t.process_13_map(map_inp) == 2
    assert len(map_inp) == 1
    assert list(map_inp.values())[0][0] == 6 + 10
    assert list(map_inp.values())[0][1] == 2

    # Part 8
    # Test std::map< Widget, Widget2 >
    vec_wrapper = libcpp_stl.IntVecWrapper()
    vec_wrapper.push_back(6)
    vec_wrapper.push_back(2)
    i1 = libcpp_stl.IntWrapper(1)
    i2 = libcpp_stl.IntWrapper(2)
    map_inp = {i2: vec_wrapper}
    assert t.process_14_map(map_inp) == 2
    assert len(map_inp) == 1
    assert list(map_inp.values())[0][0] == 6 + 10
    assert list(map_inp.values())[0][1] == 2

    # Part 9
    # Test string-keyed operator[] (arbitrary type getitem/setitem)
    string_map = libcpp_stl.StringKeyMap()
    assert string_map.size() == 0

    # Test setitem with string key
    string_map[b"hello"] = 42
    assert string_map.size() == 1
    assert string_map.contains(b"hello")

    # Test getitem with string key
    assert string_map[b"hello"] == 42

    # Test setting and getting another key
    string_map[b"world"] = 100
    assert string_map.size() == 2
    assert string_map[b"world"] == 100

    # Test overwriting existing key
    string_map[b"hello"] = 99
    assert string_map[b"hello"] == 99
