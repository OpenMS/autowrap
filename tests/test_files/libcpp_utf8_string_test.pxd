from libcpp.string cimport string as libcpp_utf8_string
from libcpp.string cimport string as libcpp_string


cdef extern from "libcpp_utf8_string_test.hpp":
    cdef cppclass Hello:
        Hello()
        libcpp_string get(libcpp_utf8_string)