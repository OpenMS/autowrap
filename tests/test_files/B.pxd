# cython: language_level=2

cdef extern from "B.h":

    cdef cppclass B[X]:
        # wrap-ignore
        # wrap-inherits:
        #     A[X]
        X BIdentity(X)
