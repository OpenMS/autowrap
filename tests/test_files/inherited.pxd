# cython: language_level=2

cdef extern from "inherited.hpp":

    cdef cppclass Base[A]:
        # wrap-instances:
        #    BaseInt := Base[int]
        #    BaseDouble := Base[double]
        Base()
        A a
        A foo()


    cdef cppclass BaseZ:
        BaseZ()
        int a
        int bar()

    ## TODO we cannot inherit properties/members automatically yet in autowrap (desirable?)

    cdef cppclass Inherited[A](Base[A], BaseZ):
        # wrap-instances:
        #    InheritedInt := Inherited[int]
        #
        # wrap-inherits:
        #    Base[A]
        #    BaseZ
        Inherited()
        A getBase()
        int getBaseZ()

    ## TODO cannot wrap-inherit from any of Base since there will be a clash of int foo() and double foo()
    ##  and our calling code does not make a difference from which base class this comes from
    # def foo(self):
    #     """Cython signature: int foo()"""
    #     cdef int _r = self.inst.get().foo()
    #     py_result = <int>_r
    #     return py_result

    cdef cppclass InheritedTwo[A,B](Base[A], Base[B], BaseZ):
        # wrap-instances:
        #    InheritedIntDbl := InheritedTwo[int,double]
        #
        # wrap-inherits:
        #    BaseZ
        InheritedTwo()
        A getBase()
        B getBaseB()
        int getBaseZ()