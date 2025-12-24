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


def test_minimal():
    from autowrap.ConversionProvider import TypeConverterBase, special_converters

    class SpecialIntConverter(TypeConverterBase):
        def get_base_types(self):
            return ("int",)

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

    target = os.path.join(test_files, "generated", "minimal_wrapper.pyx")
    include_dirs = autowrap.parse_and_generate_code(
        ["minimal.pxd", "minimal_td.pxd"], root=test_files, target=target, debug=True
    )
    cpp_source = os.path.join(test_files, "minimal.cpp")
    wrapped = autowrap.Utils.compile_and_import("wrapped", [target, cpp_source], include_dirs)
    os.remove(target)
    assert wrapped.__name__ == "wrapped"

    minimal = wrapped.Minimal()

    assert len(minimal.compute.__doc__) == 681

    assert len(minimal.run.__doc__) == 143

    # test members
    assert minimal.m_accessible == 0
    assert minimal.m_const == -1
    assert minimal.m_constdef == -1

    minimal.m_accessible = 10
    assert minimal.m_accessible == 10

    minimal.m_bool = True
    assert isinstance(minimal.m_bool, bool)
    assert minimal.m_bool == True

    try:
        minimal.m_const = 10
        assert False
    except AttributeError:
        # That is what we expected, cant modify a const member
        pass

    try:
        minimal.m_constdef = 10
        assert False
    except AttributeError:
        # That is what we expected, cant modify a const member
        pass

    assert minimal.compute(3) == 4
    # overloaded for float:
    assert minimal.compute(0.0) == 42.0

    assert minimal.compute(1, 2) == 3
    assert minimal.compute_int(4) == 5
    assert minimal.compute(b"uwe") == b"ewu"
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

    (msg,) = m3.message()
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

    c, b, a = list(reversed(m2))  # call __reversed__
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

    # Was OverflowError, but now we check positivity for unsigned ints
    with pytest.raises(AssertionError):
        print(m2[-1])

    with pytest.raises(IndexError):
        print(m2[3])

    # operator add
    assert wrapped.Minimal(1) + wrapped.Minimal(2) == wrapped.Minimal(3)

    m1 = wrapped.Minimal(1)
    m1 += m1
    assert m1 == wrapped.Minimal(2)

    m1 = wrapped.Minimal(1)
    m1 = m1 + m1
    assert m1 == wrapped.Minimal(2)

    # operator sub
    assert wrapped.Minimal(5) - wrapped.Minimal(2) == wrapped.Minimal(3)

    m1 = wrapped.Minimal(1)
    m1 -= m1
    assert m1 == wrapped.Minimal(0)

    # operator mult
    assert wrapped.Minimal(5) * wrapped.Minimal(2) == wrapped.Minimal(10)

    m1 = wrapped.Minimal(3)
    m1 *= m1
    m2 = m1 * m1
    assert m1 == wrapped.Minimal(9)
    assert m2 == wrapped.Minimal(81)

    # operator div
    assert wrapped.Minimal(10) / wrapped.Minimal(2) == wrapped.Minimal(5)

    m1 = wrapped.Minimal(3)
    m1 /= m1
    assert m1 == wrapped.Minimal(1)

    # operator mod
    assert wrapped.Minimal(10) % wrapped.Minimal(2) == wrapped.Minimal(0)
    assert wrapped.Minimal(10) % wrapped.Minimal(3) == wrapped.Minimal(1)

    m1 = wrapped.Minimal(10)
    m2 = wrapped.Minimal(2)
    m1 %= m2
    assert m1 == wrapped.Minimal(0)

    m3 = wrapped.Minimal(11)
    m4 = wrapped.Minimal(3)
    m3 %= m4
    assert m3 == wrapped.Minimal(2)

    # operator lshift
    assert wrapped.Minimal(10) << wrapped.Minimal(2) == wrapped.Minimal(40)

    m1 = wrapped.Minimal(10)
    m2 = wrapped.Minimal(1)
    m1 <<= m2
    assert m1 == wrapped.Minimal(20)

    # operator rshift
    assert wrapped.Minimal(10) >> wrapped.Minimal(2) == wrapped.Minimal(2)

    m1 = wrapped.Minimal(10)
    m2 = wrapped.Minimal(1)
    m1 >>= m2
    assert m1 == wrapped.Minimal(5)

    # operator and (bitwise)
    assert wrapped.Minimal(0b1100) & wrapped.Minimal(0b1010) == wrapped.Minimal(0b1000)

    m1 = wrapped.Minimal(0b1111)
    m2 = wrapped.Minimal(0b1010)
    m1 &= m2
    assert m1 == wrapped.Minimal(0b1010)

    # operator or (bitwise)
    assert wrapped.Minimal(0b1100) | wrapped.Minimal(0b1010) == wrapped.Minimal(0b1110)

    m1 = wrapped.Minimal(0b1000)
    m2 = wrapped.Minimal(0b0010)
    m1 |= m2
    assert m1 == wrapped.Minimal(0b1010)

    # operator xor (bitwise)
    assert wrapped.Minimal(0b1100) ^ wrapped.Minimal(0b1010) == wrapped.Minimal(0b0110)

    m1 = wrapped.Minimal(0b1111)
    m2 = wrapped.Minimal(0b0101)
    m1 ^= m2
    assert m1 == wrapped.Minimal(0b1010)
