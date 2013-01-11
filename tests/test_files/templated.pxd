from libcpp.string cimport string as libcpp_string
from libcpp.vector cimport vector as libcpp_vector

cdef extern from "templated.hpp":

    cdef cppclass T:
        T(int)
        T(T) # wrap-ignore
        int get()

    cdef cppclass Templated[X]:
        # wrap-instances:
        #   Templated[T]
        Templated(X)
        X get()
