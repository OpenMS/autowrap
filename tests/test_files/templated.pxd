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

    ctypedef libcpp_vector[T].iterator Ref

    cdef cppclass T2:
        T2() 
        T2(int)
        T2(T2) # wrap-ignore
        int get()

    cdef cppclass Templated[X]:

        # wrap-instances:
        #   Templated := Templated[T]
        #   Templated_other := Templated[T2]

        #Does not work, see below
        #Templated_vec := Templated[libcpp_vector[T]]

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

        @staticmethod
        int computeSeven() nogil except +

    cdef cppclass Y:
        Y()
        libcpp_vector[Templated[T]] passs(libcpp_vector[Templated[T]] v)

    cdef cppclass Z:
        Z()
        libcpp_vector[Ref] assigned_scores # wrap-ignore

        # Does not work since substituting the template in Templated would result in a
        # vec[vec[T]] for the xi member. And __get__ calls output_conversion, which cannot
        # handle recursion at all (not even for vectors only)
        #libcpp_vector[Templated[T]] passs(libcpp_vector[Templated[libcpp_vector[T]]] v)

cdef extern from "templated.hpp" namespace "Templated<T2>":

    int computeEight() nogil except + # wrap-attach:Templated_other

cdef extern from "templated.hpp" namespace "Templated<T>":

    int computeEight() nogil except + # wrap-attach:Templated

