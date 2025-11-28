from libcpp.string cimport string as libcpp_string
from libcpp.set cimport set as libcpp_set
from libcpp.vector cimport vector as libcpp_vector
from libcpp cimport bool
from libcpp.pair  cimport pair  as libcpp_pair 
from libcpp.map  cimport map  as libcpp_map 
from libcpp.memory cimport shared_ptr

cdef extern from "C.hpp":

    cdef cppclass C_second:
        int i_
        C_second(int i)
        C_second(C_second & i)

    cdef cppclass Cklass:
        int i_
        Cklass(int i)
        Cklass(Cklass & i)

