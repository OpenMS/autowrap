import autowrap.DeclResolver
import autowrap.CodeGenerator
import autowrap.PXDParser
import autowrap.Utils
import autowrap

import os
import copy

from utils import expect_exception

test_files = os.path.join(os.path.dirname(__file__), "test_files")

def test_shared_ptr():


    target = os.path.join(test_files, "shared_ptr_test.pyx")
    include_dirs = autowrap.CodeGenerator.fixed_include_dirs() + [test_files]
    m = autowrap.Utils.compile_and_import("m", [target, ],
                                                include_dirs)
    assert m.__name__ == "m"

    h1 = m.Holder("uwe")
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

def test_minimal():

    from autowrap.ConversionProvider import (TypeConverterBase,
                                             special_converters)

    class SpecialIntConverter(TypeConverterBase):

        def get_base_types(self):
            return "int",

        def matches(self, cpp_type):
            return  cpp_type.is_unsigned

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

    include_dirs = autowrap.parse_and_generate_code("minimal.pxd",
                                root=test_files, target=target,  debug=True)

    cpp_source = os.path.join(test_files, "minimal.cpp")

    wrapped = autowrap.Utils.compile_and_import("wrapped", [target, cpp_source],
                                                include_dirs)
    os.remove(target)
    assert wrapped.__name__ == "wrapped"

    minimal=wrapped.Minimal()

    assert minimal.compute(3) == 4
    # overloaded for float:
    assert minimal.compute(0.0) == 42.0

    assert minimal.compute(1, 2) == 3
    assert minimal.compute_int(4) == 5
    assert minimal.compute("uwe") == "ewu"
    assert minimal.compute_str("emzed") == "dezme"

    assert minimal.compute_int() == 42

    # the c++ code of test_special_converter returns the same value, but
    # our special converter above modifies the function, so:
    assert minimal.test_special_converter(0) == 1

    expect_exception(lambda: minimal.compute(None))()

    assert minimal.compute_charp("uwe") == 3

    assert minimal.run(minimal) == 4
    assert minimal.run2(minimal) == 5

    assert minimal.create().compute(3) == 4

    assert minimal.sumup([1,2,3]) == 6


    m2 = wrapped.Minimal(-1)
    assert m2.compute(3) == 3

    assert wrapped.ABCorD.A == 0
    assert wrapped.ABCorD.B == 2
    assert wrapped.ABCorD.C == 3
    assert wrapped.ABCorD.D == 4


    in_ = [m2, minimal]
    i, modified = minimal.call(in_)   # input ref arg
    assert i==1
    assert len(modified) == 3
    assert m2 == modified[0]
    assert minimal == modified[1]
    assert m2 == modified[2]

    m3 = copy.copy(m2)
    assert m3 == m2

    m3 = wrapped.Minimal([1,2,3])
    assert m3.compute(0) == 4

    in_ = ["a", "bc"]
    assert  m3.call2(in_) == 3
    assert in_ == ["a", "bc", "hi"]

    msg, = m3.message()
    assert msg == "hello"

    m1, m2 = m3.create_two()
    assert m1.compute(42) == 42
    assert m2.compute(42) == 43

    assert m2.enumTest(wrapped.ABCorD.A) == wrapped.ABCorD.A

    expect_exception(lambda: m2.enumTest(1))()

    m2.setVector([m2,m1,m3])
    a, b, c = m2.getVector()
    assert a == m2
    assert b == m1
    assert c == m3

    a, b, c = list(m2) # call __iter__
    assert a == m2
    assert b == m1
    assert c == m3

    assert m2.test2Lists([m1], [1,2]) == 3

    assert m1==m1


def test_templated():

    target = os.path.join(test_files, "templated_wrapper.pyx")

    include_dirs = autowrap.parse_and_generate_code("templated.pxd",
                                root=test_files, target=target,  debug=True)

    cpp_source = os.path.join(test_files, "templated.cpp")
    cpp_sources = []

    twrapped = autowrap.Utils.compile_and_import("twrapped",
                                                [target] + cpp_sources,
                                                include_dirs)
    os.remove(target)
    assert twrapped.__name__ == "twrapped"

    t = twrapped.T(42)
    templated = twrapped.Templated(t)
    assert templated.get().get() == 42

    in_ = [templated, templated]
    assert templated.summup(in_) == 42+42
    __, __, tn = in_
    assert tn.get().get() == 11

    tn, __, __ = templated.reverse(in_)
    assert tn.get().get() == 11

    y = twrapped.Y()
    _, __, tn = y.passs(in_)
    assert tn.get().get() == 11



# todo: wrapped tempaltes as input of free functions and mehtods of other
# # classes
#
#


if __name__ == "__main__":
    testMinimal()





