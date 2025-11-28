# cython: language_level=3
cdef extern from "abc.hpp":

    cdef cppclass Base[X]:
        # wrap-ignore
        void base_fun(X)
