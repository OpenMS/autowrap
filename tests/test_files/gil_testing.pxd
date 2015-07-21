from libc.string cimport const_char

cdef extern from "gil_testing.hpp":
    cdef cppclass ClassUsingTheGil:
        ClassUsingTheGil(const_char*)
        void do_something(const_char*) nogil # wrap-with-no-gil
