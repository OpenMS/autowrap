from libcpp.list cimport list

cdef extern from "Templates.hpp":

    cdef cppclass Templates[A,B]:
        # wrap-instances:
        #    TemplatesInt[int,int]
        #    TemplatesMixed[int,float]
        Templates(A a, B b)
        A getA()
        B getB()
        A overloaded()   # wrap-as:toA
        B overloaded()   # wrap-as:toB
        void convert(list[A] arg0, list[B] & arg1)
        Templates[int,int]      r0(Templates[int, float])
        Templates[int,float]    r1(Templates[int, int])
        Templates[double,float] r2()
        Templates[A,B] r3(A, B)
        void x() # wrap-ignore


