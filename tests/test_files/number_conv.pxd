# cython: language_level=2
from libcpp.vector cimport vector as libcpp_vector
from libc.float cimport *

cdef extern from "number_conv.hpp":

    double add_max_float(double)
    double pass_full_precision(double)
    libcpp_vector[double] pass_full_precision_vec(libcpp_vector[double] &)
