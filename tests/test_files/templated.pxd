# cython: language_level=2
from libcpp cimport bool
from libcpp.string cimport string as libcpp_string
from libcpp.vector cimport vector as libcpp_vector

cdef extern from "templated.hpp":

    cdef cppclass T:
        T() 
        T(int)
        T(T) # wrap-ignore
        int get()

    cdef cppclass T2:
        T2() 
        T2(int)
        T2(T2) # wrap-ignore
        int get()

    cdef cppclass Templated[X]:

        # wrap-instances:
        #   Templated := Templated[T]
        #   Templated_other := Templated[T2]

        X _x
        float f # wrap-as:f_att
        libcpp_vector[X] xi 

        Templated(X)
        Templated(Templated[X]) # wrap-ignore
        X get()
        float getF()
        int summup(libcpp_vector[Templated[X]] & v)
        libcpp_vector[Templated[X]] reverse(libcpp_vector[Templated[X]]& v)
        int getTwice(Templated[X])
        Templated[X] passs(Templated[X] v)
        bool operator==(Templated[X] other)

    cdef cppclass Y:
        Y()
        libcpp_vector[Templated[T]] passs(libcpp_vector[Templated[T]] v)

cdef extern from "templated.hpp" namespace "Templated<T2>":

    int computeSeven() nogil except + # wrap-attach:Templated_other

cdef extern from "templated.hpp" namespace "Templated<T>":

    int computeSeven() nogil except + # wrap-attach:Templated

