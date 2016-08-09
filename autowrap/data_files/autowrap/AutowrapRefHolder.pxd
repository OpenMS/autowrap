
cdef extern from "autowrap_tools.hpp" namespace "autowrap":

    cdef cppclass AutowrapRefHolder[T]:

        AutowrapRefHolder(T &)
        void assign(T &)

