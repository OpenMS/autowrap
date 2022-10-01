# cython: language_level=2
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

    cdef cppclass IntVecWrapper:
        IntVecWrapper()
        IntVecWrapper(IntVecWrapper&)
        libcpp_vector[int] iv_

        int& operator[](size_t index)
        void push_back(int)

    cdef cppclass MapWrapper:
        libcpp_map[int, double] map_
        MapWrapper()
        MapWrapper(MapWrapper&)

    cdef cppclass LibCppSTLVector:

        LibCppSTLVector()
        size_t size()
        IntWrapper& operator[](size_t index) #wrap-upper-limit:size()
        void push_back(const IntWrapper&)

    cdef cppclass LibCppSTLTest:

        LibCppSTLTest()

        int process_1_set(libcpp_set[IntWrapper*] & in_)
        libcpp_set[IntWrapper*] process_2_set(IntWrapper* in_)

        int process_3_vector(libcpp_vector[ shared_ptr[IntWrapper] ] & in_)
        libcpp_vector[ shared_ptr[IntWrapper] ] process_4_vector(shared_ptr[IntWrapper] & in_)

        int process_5_vector(libcpp_vector[IntWrapper*] & in_)
        libcpp_vector[IntWrapper*] process_6_vector(IntWrapper* in_)

        int process_7_map(libcpp_map[IntWrapper, int] & in_)
        libcpp_map[IntWrapper, int] process_8_map(int in_)

        int process_9_map(libcpp_map[int, IntWrapper] & in_)
        libcpp_map[int, IntWrapper] process_10_map(int in_)

        shared_ptr[const IntWrapper] process_11_const()

        int process_12_map(libcpp_map[libcpp_string, IntWrapper ]& in_)
        int process_13_map(libcpp_map[IntWrapper, libcpp_vector[int] ]& in_)

        int process_14_map(libcpp_map[IntWrapper, IntVecWrapper]& in_)
        int process_15_map(libcpp_map[IntWrapper, IntWrapper]& in_)
