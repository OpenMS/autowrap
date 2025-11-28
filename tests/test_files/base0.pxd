# cython: language_level=3
cdef extern from "abc.hpp":

    cdef cppclass Base0:  # wrap-ignore
        void base0_fun(int)
