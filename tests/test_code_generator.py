from __future__ import print_function
from __future__ import absolute_import

import types

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
from Cython.Compiler.Version import version as cython_version
import os
import math
import sys

test_files = os.path.join(os.path.dirname(__file__), "test_files")


def test_enums():
    if int(cython_version[0]) < 3:
        return
    target = os.path.join(test_files, "enums.pyx")

    include_dirs = autowrap.parse_and_generate_code(
        ["enums.pxd"], root=test_files, target=target, debug=True
    )

    mod = autowrap.Utils.compile_and_import(
        "enummodule",
        [
            target,
        ],
        include_dirs,
    )

    foo = mod.Foo()
    my_enum = mod.Foo.MyEnum
    assert "Testing Enum documentation." in my_enum.__doc__
    myenum_a = mod.Foo.MyEnum.A
    myenum2_a = mod.Foo.MyEnum2.A
    assert foo.enumToInt(myenum_a) == 1
    with pytest.raises(AssertionError):
        foo.enumToInt(myenum2_a)


def test_number_conv():
    target = os.path.join(test_files, "number_conv.pyx")

    include_dirs = autowrap.parse_and_generate_code(
        ["number_conv.pxd"], root=test_files, target=target, debug=True
    )

    mod = autowrap.Utils.compile_and_import(
        "number_conv",
        [
            target,
        ],
        include_dirs,
    )

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
    m = autowrap.Utils.compile_and_import(
        "m",
        [
            target,
        ],
        include_dirs,
    )
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


def test_inherited():
    target = os.path.join(test_files, "inherited.pyx")
    include_dirs = autowrap.parse_and_generate_code(
        ["inherited.pxd"], root=test_files, target=target, debug=True
    )

    mod = autowrap.Utils.compile_and_import(
        "inheritedmodule",
        [
            target,
        ],
        include_dirs,
    )
    print(mod.__name__)
    i = mod.InheritedInt()
    assert i.foo() == 1
    assert i.bar() == 0
    assert i.getBase() == 1
    assert i.getBaseZ() == 0


def test_templated():
    target = os.path.join(test_files, "templated_wrapper.pyx")

    decls, instance_map = autowrap.parse(["templated.pxd"], root=test_files)

    co = autowrap.Code.Code()
    co.add(
        """def special(self):
             |    return "hi" """
    )

    methods = dict(T=co)

    include_dirs = autowrap.generate_code(
        decls, instance_map, target=target, debug=True, manual_code=methods
    )

    cpp_source = os.path.join(test_files, "templated.cpp")
    cpp_sources = []

    twrapped = autowrap.Utils.compile_and_import("twrapped", [target] + cpp_sources, include_dirs)
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

    # Test (wrap-attached) free functions = old way to wrap static functions (can only be called with class)
    if int(str(cython_version).split(".")[0]) < 3:
        assert templated.computeEight() == 8
        assert templated_o.computeEight() == 8
    assert twrapped.Templated.computeEight() == 8
    assert twrapped.Templated_other.computeEight() == 8

    # Test static functions (can be called with or without object)
    assert templated.computeSeven() == 7
    assert templated_o.computeSeven() == 7
    assert twrapped.Templated.computeSeven() == 7
    assert twrapped.Templated_other.computeSeven() == 7


def test_gil_unlock():
    target = os.path.join(test_files, "gil_testing_wrapper.pyx")
    include_dirs = autowrap.parse_and_generate_code(
        ["gil_testing.pxd"], root=test_files, target=target, debug=True
    )

    wrapped = autowrap.Utils.compile_and_import(
        "gtwrapped",
        [
            target,
        ],
        include_dirs,
    )
    g = wrapped.GilTesting(b"Jack")
    g.do_something(b"How are you?")
    assert g.get_greetings() == b"Hello Jack, How are you?"


def test_automatic_string_conversion():
    target = os.path.join(test_files, "libcpp_utf8_string_test.pyx")
    include_dirs = autowrap.parse_and_generate_code(
        ["libcpp_utf8_string_test.pxd"], root=test_files, target=target, debug=True
    )

    wrapped = autowrap.Utils.compile_and_import(
        "libcpp_utf8_string_wrapped",
        [
            target,
        ],
        include_dirs,
    )
    h = wrapped.Hello()

    input_bytes = b"J\xc3\xbcrgen"
    input_unicode = b"J\xc3\xbcrgen".decode("utf-8")

    expected = b"Hello J\xc3\xbcrgen"

    msg = h.get(input_bytes)
    assert isinstance(msg, bytes)
    assert msg == expected

    msg = h.get(input_unicode)
    assert isinstance(msg, bytes)
    assert msg == expected

    input_greet_bytes = b"Hall\xc3\xb6chen"
    input_greet_unicode = input_greet_bytes.decode("utf-8")

    expected = b"Hall\xc3\xb6chen J\xc3\xbcrgen"

    msg = h.get_more({"greet": input_greet_unicode, "name": input_bytes})
    assert isinstance(msg, bytes)
    assert msg == expected


def test_automatic_output_string_conversion():
    target = os.path.join(test_files, "libcpp_utf8_output_string_test.pyx")
    include_dirs = autowrap.parse_and_generate_code(
        ["libcpp_utf8_output_string_test.pxd"],
        root=test_files,
        target=target,
        debug=True,
    )

    wrapped = autowrap.Utils.compile_and_import(
        "libcpp_utf8_output_string_wrapped",
        [
            target,
        ],
        include_dirs,
    )
    h = wrapped.LibCppUtf8OutputStringTest()

    input_bytes = b"J\xc3\xbcrgen"
    input_unicode = b"J\xc3\xbcrgen".decode("utf-8")

    expected = b"Hello J\xc3\xbcrgen".decode("utf-8")
    expected_type = str
    if sys.version_info[0] < 3:
        expected_type = unicode

    msg = h.get(input_bytes)
    assert isinstance(msg, expected_type)
    assert msg == expected

    msg = h.get(input_unicode)
    assert isinstance(msg, expected_type)
    assert msg == expected
