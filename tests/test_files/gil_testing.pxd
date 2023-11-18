# cython: language_level=2
from libc.string cimport const_char
from libcpp.string cimport string as libcpp_string

cdef extern from "gil_testing.hpp":
    cdef cppclass GilTesting:
        GilTesting(const_char*)
        void do_something(const_char*) nogil # wrap-with-no-gil
        const_char* get_greetings()
        void do_something2(libcpp_string s) nogil  # wrap-with-no-gil
