from libcpp.list cimport *

cdef extern from "int_container_class.hpp":

    cdef cppclass X[T]:
        # wrap-instances:
        #    Xint[int]
        X()             # wrap-ignore
        X(T i)
        X(X[T] &)       # wrap-ignore
        X[T] operator+(X[T] & other)
        T operator ()(X[T] &) # wrap-as:getValue


    cdef cppclass XContainer[T]:
        # wrap-instances:
        #    XContainerInt[int]
        XContainer()
        void push_back(X[T] val)
        int  size()

        list[X[T]] fun(list[X[T]])     # wrap-ignore
        list[X[T]] gun(list[X[T]] &)   # wrap-ignore
