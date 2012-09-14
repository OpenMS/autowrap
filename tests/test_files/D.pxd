
cdef extern from "D.h":

    cdef cppclass D[F, G]:
        # wrap-inherits:
        #  B[G]
        #  C[F]
        #
        # wrap-instances:
        #  D1[float,int]
        #  D2[int,float]
        pass
