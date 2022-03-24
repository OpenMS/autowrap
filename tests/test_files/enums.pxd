# cython: language_level=2

cdef extern from "enums.hpp":
     cdef cppclass Foo:

        int enumToInt(Foo__MyEnum e)

cdef extern from "enums.hpp":
     cdef cppclass Foo2:
         pass


cdef extern from "enums.hpp" namespace "Foo":

    cpdef enum Foo__MyEnum "Foo::MyEnum":
        # wrap-attach:
        #  Foo
        #
        # wrap-as:
        #  MyEnum
        #
        # wrap-doc:
        #  Testing Enum documentation.
        A
        B
        C

    cpdef enum MyEnum2 "Foo::MyEnum2":
        # wrap-attach:
        #  Foo
        A
        B
        C

cdef extern from "enums.hpp" namespace "Foo2":

    cpdef enum Foo2__MyEnum "Foo2::MyEnum":
        # wrap-attach:
        #  Foo2
        #
        # wrap-as:
        #  MyEnum
        #
        # wrap-doc:
        #  This is a second enum in another namespace.
        A
        C
        D

