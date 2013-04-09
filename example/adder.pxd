cdef extern from "adder.h":

    cdef cppclass Adder[U]:
        # wrap-instances:
        #   IntAdder := Adder[int]
        #   FloatAdder := Adder[float]

        U arg0
        U arg1
        Adder(U, U)
        Adder(Adder[U] &)
        U getSum()
