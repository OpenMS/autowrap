# cython: language_level=3
"""
Cython declaration file for ArrayWrappers module.
This allows other Cython modules to import the wrapper classes.
"""

from libcpp.vector cimport vector as libcpp_vector
from libcpp cimport bool as cbool
from libc.stdint cimport int8_t, int16_t, int32_t, int64_t, uint8_t, uint16_t, uint32_t, uint64_t

# Owning wrapper classes
cdef class ArrayWrapperFloat:
    pass

cdef class ArrayWrapperDouble:
    pass

cdef class ArrayWrapperInt8:
    pass

cdef class ArrayWrapperInt16:
    pass

cdef class ArrayWrapperInt32:
    pass

cdef class ArrayWrapperInt64:
    pass

cdef class ArrayWrapperUInt8:
    pass

cdef class ArrayWrapperUInt16:
    pass

cdef class ArrayWrapperUInt32:
    pass

cdef class ArrayWrapperUInt64:
    pass

# Non-owning view classes  
cdef class ArrayViewFloat:
    pass

cdef class ArrayViewDouble:
    pass

cdef class ArrayViewInt8:
    pass

cdef class ArrayViewInt16:
    pass

cdef class ArrayViewInt32:
    pass

cdef class ArrayViewInt64:
    pass

cdef class ArrayViewUInt8:
    pass

cdef class ArrayViewUInt16:
    pass

cdef class ArrayViewUInt32:
    pass

cdef class ArrayViewUInt64:
    pass
