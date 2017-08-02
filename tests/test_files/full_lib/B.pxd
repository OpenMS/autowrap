from libcpp.string cimport string as libcpp_string
from libcpp.set cimport set as libcpp_set
from libcpp.vector cimport vector as libcpp_vector
from libcpp cimport bool
from libcpp.pair  cimport pair  as libcpp_pair 
from libcpp.map  cimport map  as libcpp_map 
from smart_ptr cimport shared_ptr

cdef extern from "B.hpp":

    cdef enum testB:
        BB, BBB

    cdef cppclass B_second:
        int i_
        B_second(int i)
        B_second(B_second & i)

    cdef cppclass Bklass:
        int i_
        Bklass(int i)
        Bklass(Bklass & i)

