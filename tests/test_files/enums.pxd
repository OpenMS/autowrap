# cython: language_level=2

cdef extern from "enums.hpp":
     cdef cppclass Foo:

        int enumToInt(Foo_MyEnum e)

cdef extern from "enums.hpp":
     cdef cppclass Foo2:
         pass


cdef extern from "enums.hpp" namespace "Foo":

    cpdef enum class Foo_MyEnum "Foo::MyEnum":
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

    cpdef enum class Foo_MyEnum2 "Foo::MyEnum2":
        # wrap-attach:
        #  Foo
        #
        # wrap-as:
        #  MyEnum2
        A
        B
        C

cdef extern from "enums.hpp" namespace "Foo2":

    cpdef enum class Foo2_MyEnum "Foo2::MyEnum":
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

