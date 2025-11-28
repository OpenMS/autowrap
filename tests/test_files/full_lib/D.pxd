from libcpp.string cimport string as libcpp_string
from libcpp.set cimport set as libcpp_set
from libcpp.vector cimport vector as libcpp_vector
from libcpp cimport bool
from libcpp.pair  cimport pair  as libcpp_pair 
from libcpp.map  cimport map  as libcpp_map 
from libcpp.memory cimport shared_ptr

from B cimport *

cdef extern from "D.hpp":

    cdef cppclass D_second:
        int i_
        D_second(int i)
        D_second(D_second & i)
        void runB(B_second & i)

    cdef cppclass Dklass:
        int i_
        Dklass(int i)
        Dklass(Dklass & i)

