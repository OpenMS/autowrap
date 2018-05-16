from libcpp.string cimport string as libcpp_utf8_output_string

cdef extern from "libcpp_utf8_output_string_test.hpp":
    cdef cppclass LibCppUtf8OutputStringTest:
        LibCppUtf8OutputStringTest()
        libcpp_utf8_output_string get(libcpp_utf8_output_string)
