# cython: language_level=2
cdef extern from "namespaces.hpp":
    cpdef cppclass A

cdef extern from "namespaces.hpp" namespace "A":
     cdef cppclass A_Foo "A::Foo":
         # wrap-attach:
         #  A
         #
         # wrap-as:
         #  Foo
         cppclass Bar
         int a

cdef extern from "namespaces.hpp" namespace "A::Foo":
    cdef cppclass Bar:
        # wrap-attach:
        #  A_Foo
        cppclass Baz
        int a

cdef extern from "namespaces.hpp" namespace "A::Foo::Bar":
    # wrap-attach:
    #  Bar
    cdef cppclass Baz:
        int a

cdef extern from "namespaces.hpp":
    cpdef cppclass B

cdef extern from "namespaces.hpp" namespace "B":
    cdef cppclass B_Foo "B::Foo":
        # wrap-attach:
        #  B
        #
        # wrap-as:
        #  Foo
        int a