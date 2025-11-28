# cython: language_level=3

cdef extern from "Cycle0.h":

    cdef cppclass Cycle0:
        # wrap-inherits:
        #     Cycle1
        pass
