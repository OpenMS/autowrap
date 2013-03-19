cdef extern from "test.h":

    cdef cppclass IntHolder:
        IntHolder()
        IntHolder(IntHolder &) # wrap-ignore
        int get()
        void set(int)  # wrap-as:set_

    cdef cppclass B:
        B()
        B(B &) # wrap-ignore
        IntHolder get()
        void set(IntHolder a)  # wrap-as:set_
