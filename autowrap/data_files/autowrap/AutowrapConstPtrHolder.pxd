
cdef extern from "autowrap_tools.hpp" namespace "autowrap":

    cdef cppclass AutowrapConstPtrHolder[T]:

        AutowrapConstPtrHolder()
        AutowrapConstPtrHolder(const T *)
        const T * get()
        void assign(const T *)


