from libcpp.vector cimport vector as libcpp_vector
from libcpp cimport bool as cbool
from libc.stdint cimport int8_t, int16_t, int32_t, int64_t, uint8_t, uint16_t, uint32_t, uint64_t

cdef extern from "ArrayWrapper.hpp" namespace "autowrap":
    
    # Owning wrapper class
    cdef cppclass ArrayWrapper[T]:
        ArrayWrapper()
        ArrayWrapper(size_t size)
        ArrayWrapper(size_t size, T value)
        ArrayWrapper(libcpp_vector[T]&& vec)
        ArrayWrapper(const libcpp_vector[T]& vec)
        
        T* data()
        size_t size()
        void resize(size_t new_size)
        void set_data(libcpp_vector[T]& other)
        libcpp_vector[T]& get_vector()
    
    # Non-owning view class (now handles both const and non-const with readonly flag)
    cdef cppclass ArrayView[T]:
        ArrayView()
        ArrayView(T* ptr, size_t size, cbool readonly)
        ArrayView(const T* ptr, size_t size)
        
        T* data()
        size_t size()
        cbool is_readonly()
