from libcpp.string cimport string as libcpp_string
from libcpp.set cimport set as libcpp_set
from libcpp.vector cimport vector as libcpp_vector
from libcpp.pair  cimport pair  as libcpp_pair 
from libcpp.map  cimport map  as libcpp_map 
from smart_ptr cimport shared_ptr

cdef extern from "libcpp_stl_test.hpp":

    cdef cppclass IntWrapper:
        int i_
        IntWrapper(IntWrapper&)
        IntWrapper(int i)

    cdef cppclass LibCppSTLTest:
        LibCppSTLTest()

        int process_1_set(libcpp_set[IntWrapper*] & in_)
        libcpp_set[IntWrapper*] process_2_set(IntWrapper* in_)

        int process_3_vector(libcpp_vector[ shared_ptr[IntWrapper] ] & in_)
        libcpp_vector[ shared_ptr[IntWrapper] ] process_4_vector(shared_ptr[IntWrapper] & in_)

        int process_5_vector(libcpp_vector[IntWrapper*] & in_)
        libcpp_vector[IntWrapper*] process_6_vector(IntWrapper* in_)

