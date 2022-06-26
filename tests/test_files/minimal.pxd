# cython: language_level=2
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
        const int m_constdef

        int get()
        libcpp_string compute(libcpp_string)
        Int compute(int number1, int number2) # wrap-doc:This method is essential for foobar
        int compute(Int number)
        float compute(float number)
        int compute_int(int)
        int compute_int()
        char * pass_charptr(char *) # has const char * in orig, !
        const_char * pass_const_charptr(const_char *)
        libcpp_string compute_str(libcpp_string what)
        int compute_charp(char * what)
        # Note how both run3 and run4 have the same implementation - declaring
        # it const in Cython will not affect the result!
        int run(Minimal & ref)
        # wrap-doc:
        #  Test for Multiline Comment
        #    with indentation
        #  
        #  and empty line
        
        int run2(Minimal *p)
        int run3(Minimal & ref)
        int run4(const Minimal & ref) # attention here!
        Minimal create()
        Minimal & getRef()   # wrap-ignore


        unsigned int test_special_converter(unsigned int)

        void setVector(libcpp_vector[Minimal]) # wrap-doc:Sets vector
        libcpp_vector[Minimal] getVector() # wrap-doc:Gets vector

        int test2Lists(const libcpp_vector[Minimal]&, libcpp_vector[int])

        libcpp_vector[Minimal].iterator begin() # wrap-iter-begin:__iter__(Minimal)
        libcpp_vector[Minimal].iterator end()   # wrap-iter-end:__iter__(Minimal)

        libcpp_vector[Minimal].reverse_iterator rbegin() # wrap-iter-begin:__reversed__(Minimal)
        libcpp_vector[Minimal].reverse_iterator rend()   # wrap-iter-end:__reversed__(Minimal)

        int operator()(Minimal) # wrap-cast:toInt

        int size()
        int operator[](size_t index) #wrap-upper-limit:size()

        # Note how both call, call2 and call3 have the same implementation -
        # however, declaring it const in Cython will affect the result since it
        # will not get copied back!
        int sumup(libcpp_vector[int]& what)
        int call(libcpp_vector[Minimal] what) # ref-arg-out:0
        int call2(libcpp_vector[Minimal]& what) # ref-arg-out:0
        int call3(const libcpp_vector[Minimal]& what) # ref-arg-out:0
        int call4(int & what)
        int call_str(libcpp_vector[libcpp_string] & what)
        libcpp_vector[libcpp_string] message()
        libcpp_vector[Minimal] create_two()
        int operator==(Minimal &)
        ABCorD enumTest(ABCorD)

        Minimal operator+(Minimal)
        Minimal operator*(Minimal)
        Minimal operator-(Minimal)
        Minimal operator/(Minimal)
        Minimal operator%(Minimal)

        # cython does not support declaration of operator+= yet
        Minimal iadd(Minimal) # wrap-as:operator+=
        Minimal isub(Minimal) # wrap-as:operator-=
        Minimal imul(Minimal) # wrap-as:operator*=
        Minimal itruediv(Minimal) # wrap-as:operator/=
        Minimal imod(Minimal) # wrap-as:operator%=

    int top_function(int)
    int sumup(libcpp_vector[int] what)

cdef extern from "minimal.hpp" namespace "Minimal":

    long int run_static(long int) # wrap-attach:Minimal

    long int run_static(long int, bool) # wrap-attach:Minimal wrap-as:run_static_extra_arg

