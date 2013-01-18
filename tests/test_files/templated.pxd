from libcpp cimport bool
from libcpp.string cimport string as libcpp_string
from libcpp.vector cimport vector as libcpp_vector

cdef extern from "templated.hpp":

    cdef cppclass T:
        T(int)
        T(T) # wrap-ignore
        int get()

    cdef cppclass Templated[X]:
        # wrap-instances:
        #   Templated := Templated[T]
        Templated(X)
        Templated(Templated[X]) # wrap-ignore
        X get()
        int summup(libcpp_vector[Templated[X]] & v)
        libcpp_vector[Templated[X]] reverse(libcpp_vector[Templated[X]] v)
        int getTwice(Templated[X])
        Templated[X] passs(Templated[X] v)
        bool operator==(Templated[X] other)

    cdef cppclass Y:
        Y()
        libcpp_vector[Templated[T]] passs(libcpp_vector[Templated[T]] v)

