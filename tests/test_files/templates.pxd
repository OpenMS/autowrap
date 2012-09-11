from libcpp.list cimport list

cdef extern from "Templates.hpp":

    cdef cppclass Templates[A,B]:
        # wrap-instances:
        #    TemplatesInt[int,int]
        #    TemplatesMixed[int,float]
        Templates(A a, B b)
        A getA()
        B getB()
        A overloaded()
        B overloaded()
        void convert(list[A] arg0, list[B] & arg1)


