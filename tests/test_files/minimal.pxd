
cdef extern from "minimal.hpp":

    cdef cppclass Minimal:
        Minimal()
        int compute(int i)


