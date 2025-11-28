# cython: language_level=3

cdef extern from "A.h":

    cdef cppclass A[U]:
        # wrap-ignore
        void Afun(U, int)
