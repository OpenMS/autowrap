
cdef extern from "boost/smart_ptr/shared_ptr.hpp" namespace "boost":

    cdef cppclass shared_ptr[T]:
        shared_ptr()
        shared_ptr(T*)
        void swap(shared_ptr&)
        void reset()
        T* get() nogil
        int unique()
        int use_count()

cdef extern from "boost/smart_ptr/make_shared.hpp" namespace "boost":
    shared_ptr[T] make_shared[T](...) except +