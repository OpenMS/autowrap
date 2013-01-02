from libcpp.string cimport string as std_string

cdef extern from "minimal.hpp":

    cdef cppclass Minimal:
        Minimal()
        Minimal(Minimal &)  # wrap-ignore
        int compute(int number)
        std_string compute(std_string)
        int compute_int(int)
        std_string compute_str(std_string what)
        int compute_charp(char * what)
        int run(Minimal & ref)
        int run2(Minimal *p)
        Minimal create()
