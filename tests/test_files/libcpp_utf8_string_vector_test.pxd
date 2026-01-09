# cython: language_level=3
from libcpp.string cimport string as libcpp_utf8_output_string
from libcpp.string cimport string as libcpp_utf8_string
from libcpp.vector cimport vector as libcpp_vector

cdef extern from "libcpp_utf8_string_vector_test.hpp":
    cdef cppclass Utf8VectorTest:
        Utf8VectorTest()
        libcpp_vector[libcpp_utf8_output_string] get_greetings()
        libcpp_vector[libcpp_utf8_output_string] echo(libcpp_vector[libcpp_utf8_string])
        size_t count_strings(libcpp_vector[libcpp_utf8_string])
