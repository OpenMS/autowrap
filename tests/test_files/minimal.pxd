from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector

cdef extern from "minimal.hpp":

    cdef cppclass Minimal:
        Minimal()  
        Minimal(int)  
        Minimal(std_vector[int])  # wrap-ignore
        Minimal(Minimal &)  # wrap-ignore
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

        int sumup(std_vector[int] what)  # wrap-ignore
        int call(std_vector[Minimal] & what)    # wrap-ignore

    cdef enum ABCorD:
        A, B=2, C, D
           
