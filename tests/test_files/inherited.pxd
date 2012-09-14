
cdef extern from "inherited.hpp":

    cdef cppclass Inherited[A]:
        # wrap-instances:
        #    InheritedInt[int]
        #
        # wrap-inherits:
        #    Base[A]
        #    Base0
        pass
