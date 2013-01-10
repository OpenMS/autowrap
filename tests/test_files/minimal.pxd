from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector

cdef extern from "minimal.hpp":

    cdef enum ABCorD:
        A, B=2, C, D

    cdef cppclass Minimal:
        Minimal()
        Minimal(int)
        Minimal(std_vector[int])
        Minimal(Minimal &)
        std_string compute(std_string)
        int compute(int number1, int number2)
        int compute(int number)
        float compute(float number)
        int compute_int(int)
        int compute_int()
        char * pass_charptr(char *) # has const char * in orig, !
        std_string compute_str(std_string what)
        int compute_charp(char * what)
        int run(Minimal & ref)
        int run2(Minimal *p)
        Minimal create()
        Minimal & getRef()   # wrap-ignore
        
        unsigned int test_special_converter(unsigned int)

        void setVector(std_vector[Minimal])
        std_vector[Minimal] getVector()

        std_vector[Minimal].iterator begin() # wrap-iter-begin:__iter__(Minimal)
        std_vector[Minimal].iterator end()   # wrap-iter-end:__iter__(Minimal)

        int sumup(std_vector[int] what)
        int call(std_vector[Minimal] what) # ref-arg-out:0
        int call2(std_vector[std_string] & what)
        std_vector[std_string] message()
        std_vector[Minimal] create_two()
        int operator==(Minimal &)
        ABCorD enumTest(ABCorD)
