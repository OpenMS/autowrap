# cython: language_level=3
"""
Declaration file for ArrayWrappers module.
This allows other Cython modules to import the wrapper classes and factory functions.
"""

from libcpp.vector cimport vector as libcpp_vector
from libcpp cimport bool as cbool
from libc.stdint cimport int8_t, int16_t, int32_t, int64_t, uint8_t, uint16_t, uint32_t, uint64_t

# Owning wrapper classes (hold libcpp_vector directly)
cdef class ArrayWrapperFloat:
    cdef libcpp_vector[float] vec

cdef class ArrayWrapperDouble:
    cdef libcpp_vector[double] vec

cdef class ArrayWrapperInt8:
    cdef libcpp_vector[int8_t] vec

cdef class ArrayWrapperInt16:
    cdef libcpp_vector[int16_t] vec

cdef class ArrayWrapperInt32:
    cdef libcpp_vector[int32_t] vec

cdef class ArrayWrapperInt64:
    cdef libcpp_vector[int64_t] vec

cdef class ArrayWrapperUInt8:
    cdef libcpp_vector[uint8_t] vec

cdef class ArrayWrapperUInt16:
    cdef libcpp_vector[uint16_t] vec

cdef class ArrayWrapperUInt32:
    cdef libcpp_vector[uint32_t] vec

cdef class ArrayWrapperUInt64:
    cdef libcpp_vector[uint64_t] vec

# Non-owning view classes (hold raw pointer + size + owner)
cdef class ArrayViewFloat:
    cdef float* ptr
    cdef size_t _size
    cdef object owner
    cdef cbool readonly

cdef class ArrayViewDouble:
    cdef double* ptr
    cdef size_t _size
    cdef object owner
    cdef cbool readonly

cdef class ArrayViewInt8:
    cdef int8_t* ptr
    cdef size_t _size
    cdef object owner
    cdef cbool readonly

cdef class ArrayViewInt16:
    cdef int16_t* ptr
    cdef size_t _size
    cdef object owner
    cdef cbool readonly

cdef class ArrayViewInt32:
    cdef int32_t* ptr
    cdef size_t _size
    cdef object owner
    cdef cbool readonly

cdef class ArrayViewInt64:
    cdef int64_t* ptr
    cdef size_t _size
    cdef object owner
    cdef cbool readonly

cdef class ArrayViewUInt8:
    cdef uint8_t* ptr
    cdef size_t _size
    cdef object owner
    cdef cbool readonly

cdef class ArrayViewUInt16:
    cdef uint16_t* ptr
    cdef size_t _size
    cdef object owner
    cdef cbool readonly

cdef class ArrayViewUInt32:
    cdef uint32_t* ptr
    cdef size_t _size
    cdef object owner
    cdef cbool readonly

cdef class ArrayViewUInt64:
    cdef uint64_t* ptr
    cdef size_t _size
    cdef object owner
    cdef cbool readonly

# Factory functions for creating views from C level
cdef ArrayViewFloat _create_view_float(float* ptr, size_t size, object owner, cbool readonly)
cdef ArrayViewDouble _create_view_double(double* ptr, size_t size, object owner, cbool readonly)
cdef ArrayViewInt8 _create_view_int8(int8_t* ptr, size_t size, object owner, cbool readonly)
cdef ArrayViewInt16 _create_view_int16(int16_t* ptr, size_t size, object owner, cbool readonly)
cdef ArrayViewInt32 _create_view_int32(int32_t* ptr, size_t size, object owner, cbool readonly)
cdef ArrayViewInt64 _create_view_int64(int64_t* ptr, size_t size, object owner, cbool readonly)
cdef ArrayViewUInt8 _create_view_uint8(uint8_t* ptr, size_t size, object owner, cbool readonly)
cdef ArrayViewUInt16 _create_view_uint16(uint16_t* ptr, size_t size, object owner, cbool readonly)
cdef ArrayViewUInt32 _create_view_uint32(uint32_t* ptr, size_t size, object owner, cbool readonly)
cdef ArrayViewUInt64 _create_view_uint64(uint64_t* ptr, size_t size, object owner, cbool readonly)
