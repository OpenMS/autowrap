from libcpp.string cimport string as libcpp_string
from libcpp.vector cimport vector as libcpp_vector
from libc.string cimport const_char

from minimal_td cimport *


cdef extern from "minimal.hpp":


    cdef enum ABCorD:
        # wrap-attach:
        #   Minimal
        A, B=2, C, D


    cdef cppclass Minimal:
        Minimal()
        Minimal(int)
        Minimal(libcpp_vector[int])
        Minimal(Minimal &)

        int m_accessible
        int m_const # wrap-constant

        int get()
        libcpp_string compute(libcpp_string)
        Int compute(int number1, int number2)
        int compute(Int number)
        float compute(float number)
        int compute_int(int)
        int compute_int()
        char * pass_charptr(char *) # has const char * in orig, !
        const_char * pass_const_charptr(const_char *)
        libcpp_string compute_str(libcpp_string what)
        int compute_charp(char * what)
        int run(Minimal & ref)
        int run2(Minimal *p)
        Minimal create()
        Minimal & getRef()   # wrap-ignore


        unsigned int test_special_converter(unsigned int)

        void setVector(libcpp_vector[Minimal])
        libcpp_vector[Minimal] getVector()

        int test2Lists(libcpp_vector[Minimal], libcpp_vector[int])

        libcpp_vector[Minimal].iterator begin() # wrap-iter-begin:__iter__(Minimal)
        libcpp_vector[Minimal].iterator end()   # wrap-iter-end:__iter__(Minimal)

        int operator()(Minimal) # wrap-cast:toInt

        int size()
        int operator[](size_t index) #wrap-upper-limit:size()

        int sumup(libcpp_vector[int] what)
        int call(libcpp_vector[Minimal] what) # ref-arg-out:0
        int call2(libcpp_vector[libcpp_string] & what)
        libcpp_vector[libcpp_string] message()
        libcpp_vector[Minimal] create_two()
        int operator==(Minimal &)
        ABCorD enumTest(ABCorD)

        Minimal operator+(Minimal)
        Minimal operator*(Minimal)
        # cython does not support declaration of operator+= yet
        Minimal iadd(Minimal) # wrap-as:operator+=

    int top_function(int)
    int sumup(libcpp_vector[int] what)

cdef extern from "minimal.hpp" namespace "Minimal":

    long int run_static(long int) # wrap-attach:Minimal

