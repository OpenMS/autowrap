from libc.float cimport *

cdef extern from "number_conv.hpp":

    double add_max_float(double)
