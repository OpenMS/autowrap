# cython: language_level=3
from libc.string cimport const_char

cdef extern from "gil_testing.hpp":
    cdef cppclass GilTesting:
        GilTesting(const_char*)
        void do_something(const_char*) nogil # wrap-with-no-gil
        const_char* get_greetings()
