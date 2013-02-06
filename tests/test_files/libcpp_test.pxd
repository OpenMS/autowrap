from libcpp.string cimport string as libcpp_string
from libcpp.vector cimport vector as libcpp_vector
from libcpp.pair  cimport pair  as libcpp_pair 

cdef extern from "libcpp_test.hpp":

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

