cdef extern from "int_holder.hpp":
    cdef cppclass IntHolder:
        int i_
        IntHolder(int i)
        IntHolder(IntHolder & i)
        int add(IntHolder o)
