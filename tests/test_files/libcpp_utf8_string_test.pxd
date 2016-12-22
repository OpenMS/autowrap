from libcpp.string cimport string as libcpp_utf8_string
from libcpp.string cimport string as libcpp_string
from libcpp.map cimport map as libcpp_map

cdef extern from "libcpp_utf8_string_test.hpp":
    cdef cppclass Hello:
        Hello()
        libcpp_string get(libcpp_utf8_string)
        libcpp_string get_more(libcpp_map[libcpp_utf8_string, libcpp_utf8_string])