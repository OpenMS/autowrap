# cython: language_level=2

cdef extern from "D.h":

    cdef cppclass D[F, G]:
        # wrap-inherits:
        #  B[G]
        #  C[F]
        #
        # wrap-instances:
        #  D1 := D[float,int]
        #  D2 := D[int,float]
        pass
