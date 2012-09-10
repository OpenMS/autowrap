
cdef extern from "Minimal.hpp":

    cdef cppclass Minimal:
        Minimal(int a)
        int getA()
        unsigned int method0(unsigned int input)
        float method1(float input)
        double method2(double input)
        char method3(char input)

        void overloaded(int inp)
        void overloaded(float inp)


