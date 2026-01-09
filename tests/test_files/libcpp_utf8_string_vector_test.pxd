# cython: language_level=3
from libcpp.string cimport string as libcpp_string
from libcpp.vector cimport vector as libcpp_vector

# Note: We use libcpp_string (not libcpp_utf8_string) because the UTF-8
# converters do NOT work inside containers like std::vector.
# See StdStringUnicodeConverter in ConversionProvider.py.

cdef extern from "libcpp_utf8_string_vector_test.hpp":
    cdef cppclass Utf8StringVectorTest:
        Utf8StringVectorTest()
        libcpp_vector[libcpp_string] get_greetings()
        int total_length(libcpp_vector[libcpp_string])
        void append_greeting(libcpp_vector[libcpp_string] &)
