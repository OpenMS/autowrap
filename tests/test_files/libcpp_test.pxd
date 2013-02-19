from libcpp.string cimport string as libcpp_string
from libcpp.set cimport set as libcpp_set
from libcpp.vector cimport vector as libcpp_vector
from libcpp.pair  cimport pair  as libcpp_pair 

cdef extern from "libcpp_test.hpp":

    cdef enum EEE:
        A, B

    cdef cppclass LibCppTest:
        LibCppTest()
        LibCppTest(int ii)
        LibCppTest(LibCppTest) # wrap-ignore

        int  get()

        libcpp_pair[int,libcpp_string] twist(libcpp_pair[libcpp_string, int])
        libcpp_vector[int] process(libcpp_vector[int] &)

        libcpp_pair[int, int] process2(libcpp_pair[int, int] &)
        libcpp_pair[LibCppTest, int] process3(libcpp_pair[LibCppTest, int] &)
        libcpp_pair[int, LibCppTest] process4(libcpp_pair[int, LibCppTest] &)
        libcpp_pair[LibCppTest, LibCppTest] process5(libcpp_pair[LibCppTest, LibCppTest] &)

        libcpp_vector[libcpp_pair[int,double]] process6(libcpp_vector[libcpp_pair[int,double]] &)

        libcpp_pair[int, EEE] process7(libcpp_pair[EEE, int] &)
        libcpp_vector[EEE] process8(libcpp_vector[EEE] &)
