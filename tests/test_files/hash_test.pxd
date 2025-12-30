# cython: language_level=3
from libcpp.string cimport string as libcpp_string
from libcpp cimport bool

cdef extern from "hash_test.hpp":

    # Test case 1: Expression-based hash (old behavior, regression test)
    cdef cppclass ExprHashClass:
        # wrap-hash:
        #   getValue()
        #
        ExprHashClass()
        ExprHashClass(int value, libcpp_string name)
        ExprHashClass(ExprHashClass)  # wrap-ignore

        int getValue()
        libcpp_string getName()

        bool operator==(ExprHashClass)
        bool operator!=(ExprHashClass)


    # Test case 2: std::hash-based hash (new behavior)
    cdef cppclass StdHashClass:
        # wrap-hash:
        #   std
        #
        StdHashClass()
        StdHashClass(int id, libcpp_string label)
        StdHashClass(StdHashClass)  # wrap-ignore

        int getId()
        libcpp_string getLabel()

        bool operator==(StdHashClass)
        bool operator!=(StdHashClass)


    # Test case 3: Template class with std::hash
    cdef cppclass TemplatedHashClass[T]:
        # wrap-hash:
        #   std
        #
        # wrap-instances:
        #   TemplatedHashInt := TemplatedHashClass[int]
        #
        TemplatedHashClass()
        TemplatedHashClass(T data)
        TemplatedHashClass(TemplatedHashClass[T])  # wrap-ignore

        T getData()

        bool operator==(TemplatedHashClass[T])
        bool operator!=(TemplatedHashClass[T])
