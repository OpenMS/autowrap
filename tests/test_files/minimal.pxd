from libcpp.string cimport string as std_string

cdef extern from "minimal.hpp":

    cdef cppclass Minimal:
        Minimal()
        int compute(int)
        std_string compute(std_string)



