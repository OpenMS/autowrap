cdef extern from "test.h":

    cdef cppclass Holder[U]:
        # wrap-instances:
        #   IntHolder := Holder[int]
        #   FloatHolder := Holder[float]
        Holder()
        Holder(Holder[U] &) # wrap-ignore
        U get()
        void set(U)  # wrap-as:set_

    cdef cppclass Outer[U]:
        # wrap-instances:
        #  B := Outer[int]
        #  C := Outer[float]
        Outer()
        Outer(Outer &) # wrap-ignore
        Holder[U] get()
        void set(Holder[U] a)  # wrap-as:set_

