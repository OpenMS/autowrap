# cython: language_level=3

cdef extern from "Cycle2.h":

    cdef cppclass Cycle2:
        # wrap-inherits:
        #     Cycle0
        pass
