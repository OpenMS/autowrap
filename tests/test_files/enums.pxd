# cython: language_level=2

cdef extern from "enums.hpp":
     cdef cppclass Foo:

        int enumToInt(MyEnum e)

cdef extern from "enums.hpp" namespace "Foo":

    cpdef enum class MyEnum "Foo::MyEnum":
        # wrap-attach:
        #  Foo
        A
        B
        C

    cpdef enum class MyEnum2 "Foo::MyEnum2":
        # wrap-attach:
        #  Foo
        A
        B
        C