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
        int compute(int number)
        int compute(int number1, int number2)
        std_string compute(std_string)
        int compute_int(int)
        int compute_int()
        std_string compute_str(std_string what)
        int compute_charp(char * what)
        int run(Minimal & ref)  
        int run2(Minimal *p)
        Minimal create()  

        int sumup(std_vector[int] what)
        int call(std_vector[Minimal] & what) # ref-arg-out:0
        int call2(std_vector[std_string] & what)
        std_vector[std_string] message()
        std_vector[Minimal] create_two()
        int operator==(Minimal &)
        ABCorD enumTest(ABCorD)

           
