# cython: language_level=3
from libcpp.string cimport string as libcpp_string
from libcpp.set cimport set as libcpp_set
from libcpp.vector cimport vector as libcpp_vector
from libcpp cimport bool
from libcpp.pair  cimport pair  as libcpp_pair 
from libcpp.map  cimport map  as libcpp_map 
from smart_ptr cimport shared_ptr

ctypedef unsigned int UInt

cdef extern from "libcpp_test.hpp":

    cdef enum EEE:
        A, B

    cdef cppclass Int:
        int i_
        Int(int i)
        Int(Int & i)

    ## Abstract base class and two implementations 
    cdef cppclass AbstractBaseClass:
        # wrap-ignore
        # ABSTRACT class
        int i_
        int get()
        # AbstractBaseClass(AbstractBaseClass) # wrap-ignore

    cdef cppclass ABS_Impl1(AbstractBaseClass):
        # wrap-inherits:
        #  AbstractBaseClass
        # ABS_Impl1(ABS_Impl1)
        ABS_Impl1() # wrap-pass-constructor
        ABS_Impl1(int i)

    cdef cppclass ABS_Impl2(AbstractBaseClass):
        # wrap-inherits:
        #  AbstractBaseClass
        # ABS_Impl2(ABS_Impl2)
        ABS_Impl2() # wrap-pass-constructor
        ABS_Impl2(int i) # wrap-ignore


    cdef cppclass LibCppTest:
        # wrap-hash:
        #  get()
        #
        # wrap-doc:
        #  This is some class doc
        #  Pretty cool stuff! 
        #  -----
        #  With a trick, we can even get multiple paragraphs, allowing us to
        #  write much longer documentation.
        #

        LibCppTest()
        LibCppTest(int ii)
        LibCppTest(LibCppTest) # wrap-ignore

        bool operator==(LibCppTest)
        bool operator!=(LibCppTest)

        libcpp_vector[Int] * integer_vector_ptr
        Int * integer_ptr

        int get() #wrap-as:gett wrap-doc:getting access to an integer

        libcpp_pair[int,libcpp_string] twist(libcpp_pair[libcpp_string, int]) #wrap-doc:Dont forget this stuff here!
        libcpp_vector[int] process(libcpp_vector[int] &)

        libcpp_pair[int, int] process2(libcpp_pair[int, int] &)
        libcpp_pair[LibCppTest, int] process3(libcpp_pair[LibCppTest, int] &)
        libcpp_pair[int, LibCppTest] process4(libcpp_pair[int, LibCppTest] &)
        libcpp_pair[LibCppTest, LibCppTest] process5(libcpp_pair[LibCppTest, LibCppTest] &)

        libcpp_vector[libcpp_pair[int,double]] process6(libcpp_vector[libcpp_pair[int,double]] & what)

        libcpp_pair[int, EEE] process7(libcpp_pair[EEE, int] &)
        libcpp_vector[EEE] process8(libcpp_vector[EEE] &)

        libcpp_set[int] process9(libcpp_set[int] &)
        libcpp_set[EEE] process10(libcpp_set[EEE] &)
        libcpp_set[LibCppTest] process11(libcpp_set[LibCppTest] &)

        libcpp_map[int, float] process12(int i, float f)
        libcpp_map[EEE, int] process13(EEE e, int i)
        libcpp_map[int, EEE] process14(EEE e, int i)

        libcpp_map[long int, LibCppTest] process15(int ii)

        float process16(libcpp_map[int, float] in_)
        float process17(libcpp_map[EEE, float] in_)

        int process18(libcpp_map[int, LibCppTest] in_)

        void  process19(libcpp_map[int, LibCppTest] & in_)
        void  process20(libcpp_map[int, float] & in_)

        void  process21(libcpp_map[int, float] & in_, libcpp_map[int,int] & arg2)
        void  process211(libcpp_map[int, float] & in_, libcpp_map[libcpp_string, libcpp_vector[int] ] & arg2)
        void  process212(libcpp_map[int, float] & in_, libcpp_map[libcpp_string, libcpp_vector[ libcpp_vector[int] ] ] & arg2)
        # void  process213(libcpp_map[int, float] & in_, libcpp_map[libcpp_string, libcpp_vector[ libcpp_vector[Int] ] ] & arg2)
        void  process214(libcpp_map[int, float] & in_, libcpp_map[libcpp_string, libcpp_vector[ libcpp_pair[int, int] ] ] & arg2)
        void  process22(libcpp_set[int] &, libcpp_set[float] &)
        void  process23(libcpp_vector[int] &, libcpp_vector[float] &)
        void  process24(libcpp_pair[int, float] & in_, libcpp_pair[int,int] & arg2)

        int   process25(libcpp_vector[Int] in_)
        int   process26(libcpp_vector[libcpp_vector[Int]] in_)
        int   process27(libcpp_vector[libcpp_vector[libcpp_vector[Int]]] in_)
        int   process28(libcpp_vector[libcpp_vector[libcpp_vector[libcpp_vector[Int]]]] in_)

        void  process29(libcpp_vector[libcpp_vector[Int]] & in_)
        void  process30(libcpp_vector[libcpp_vector[libcpp_vector[libcpp_vector[Int]]]] & in_)

        int   process31(libcpp_vector[int] in_)
        int   process32(libcpp_vector[libcpp_vector[int]] in_)

        int   process33(shared_ptr[Int] in_)
        shared_ptr[Int] process34(shared_ptr[Int] in_)
        shared_ptr[const Int] process35(shared_ptr[Int] in_)

        int   process36(Int* in_)
        Int*   process37(Int* in_)

        libcpp_vector[libcpp_vector[UInt]] process38(int)

        # Wrap a const return value
        const Int* process39(Int* in_)

        # Wrap an abstract base class
        # int process40(AbstractBaseClass* in_)
        int process40(ABS_Impl1* in_)
        int process40(ABS_Impl2* in_)
