
cdef extern from "autowrap_tools.hpp" namespace "autowrap":

    cdef cppclass AutowrapPtrHolder[T]:

        AutowrapPtrHolder()
        AutowrapPtrHolder(T *)
        T * get()
        void assign(T *)


