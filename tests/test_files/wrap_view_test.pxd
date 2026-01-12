# cython: language_level=3
from libcpp.string cimport string as libcpp_string
from libcpp.vector cimport vector as libcpp_vector


cdef extern from "wrap_view_test.hpp":

    cdef cppclass Inner:
        # wrap-view
        int value
        libcpp_string name

        Inner() except +
        Inner(int) except +
        Inner(int, libcpp_string) except +
        Inner(Inner&) except +  # Copy constructor

        int getValue()
        void setValue(int)
        libcpp_string getName()
        void setName(libcpp_string)


    cdef cppclass Outer:
        # wrap-view
        Inner inner_member

        Outer() except +
        Outer(int) except +
        Outer(Outer&) except +  # Copy constructor

        # Mutable reference getter - wrap-ignore on main class (ref returns not supported)
        # view class should return InnerView
        Inner & getInner()  # wrap-ignore

        # Const reference getter - wrap-ignore on main class
        const Inner & getConstInner()  # wrap-ignore

        # Value getter - returns copy (this one works)
        Inner getInnerCopy()

        # Mutable reference with argument - wrap-ignore on main class
        Inner & getItemAt(int index)  # wrap-ignore

        void addItem(Inner item)
        int itemCount()
        int getInnerValue()


    cdef cppclass Container:
        # wrap-view
        Container() except +

        # Returns mutable reference to Outer - wrap-ignore on main class
        Outer & getOuter()  # wrap-ignore

        int getNestedValue()
