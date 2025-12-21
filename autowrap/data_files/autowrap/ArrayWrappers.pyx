# cython: language_level=3
# cython: embedsignature=True
"""
Generic array wrapper classes with buffer protocol support.

This module provides owning wrappers for all numeric types.
The classes implement the Python buffer protocol, allowing zero-copy integration
with numpy and other buffer-aware Python libraries.

Owning wrappers directly hold a std::vector and transfer ownership via swap.
For reference returns, Cython memory views are used instead (see ConversionProvider).

Supported types: float, double, int8, int16, int32, int64, uint8, uint16, uint32, uint64
"""

from cpython.buffer cimport PyBUF_FORMAT, PyBUF_ND, PyBUF_STRIDES, PyBUF_WRITABLE
from cpython cimport Py_buffer
from libcpp.vector cimport vector as libcpp_vector
from libcpp cimport bool as cbool
from libc.stdint cimport int8_t, int16_t, int32_t, int64_t, uint8_t, uint16_t, uint32_t, uint64_t
cimport cython
from libc.stdlib cimport malloc, free


# Static format strings for buffer protocol
cdef char* FORMAT_FLOAT = b'f'
cdef char* FORMAT_DOUBLE = b'd'
cdef char* FORMAT_INT8 = b'b'
cdef char* FORMAT_INT16 = b'h'
cdef char* FORMAT_INT32 = b'i'
cdef char* FORMAT_INT64 = b'q'
cdef char* FORMAT_UINT8 = b'B'
cdef char* FORMAT_UINT16 = b'H'
cdef char* FORMAT_UINT32 = b'I'
cdef char* FORMAT_UINT64 = b'Q'

#############################################################################
# Owning Wrapper Classes (directly hold libcpp_vector)
#############################################################################


cdef class ArrayWrapperFloat:
    """
    Owning wrapper for std::vector<float> with buffer protocol support.
    
    This class owns its data via a C++ vector and can be converted to numpy arrays.
    The numpy array will be a view into this wrapper's data, so the wrapper
    must be kept alive while the numpy array is in use.
    
    Example:
        wrapper = ArrayWrapperFloat(size=10)
        arr = np.asarray(wrapper)
        arr.base = wrapper  # Keep wrapper alive
    """
    cdef libcpp_vector[float] vec

    def __init__(self, size=0):
        """Initialize with optional size."""
        if size > 0:
            self.vec.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self.vec.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self.vec.size()
    
    def set_data(self, libcpp_vector[float]& data):
        """Set data by swapping with a C++ vector."""
        self.vec.swap(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        # Allocate shape and strides array (2 elements: [shape, strides])
        cdef Py_ssize_t *shape_and_strides = <Py_ssize_t*>malloc(2 * sizeof(Py_ssize_t))
        if shape_and_strides == NULL:
            raise MemoryError("Unable to allocate shape/strides buffer")
        
        shape_and_strides[0] = self.vec.size()  # shape
        shape_and_strides[1] = sizeof(float)  # strides
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = shape_and_strides[0] * sizeof(float)
        buffer.readonly = 0
        if flags & PyBUF_FORMAT:
            buffer.format = FORMAT_FLOAT
        else:
            buffer.format = NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = shape_and_strides
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = shape_and_strides + 1
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(float)
        buffer.internal = <void*>shape_and_strides  # Store pointer so we can free it later
    
    def __releasebuffer__(self, Py_buffer *buffer):
        if <void*>buffer.internal != NULL:
            free(<void*>buffer.internal)
            buffer.internal = NULL


cdef class ArrayWrapperDouble:
    """
    Owning wrapper for std::vector<double> with buffer protocol support.
    
    This class owns its data via a C++ vector and can be converted to numpy arrays.
    The numpy array will be a view into this wrapper's data, so the wrapper
    must be kept alive while the numpy array is in use.
    
    Example:
        wrapper = ArrayWrapperDouble(size=10)
        arr = np.asarray(wrapper)
        arr.base = wrapper  # Keep wrapper alive
    """
    cdef libcpp_vector[double] vec

    def __init__(self, size=0):
        """Initialize with optional size."""
        if size > 0:
            self.vec.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self.vec.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self.vec.size()
    
    def set_data(self, libcpp_vector[double]& data):
        """Set data by swapping with a C++ vector."""
        self.vec.swap(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        # Allocate shape and strides array (2 elements: [shape, strides])
        cdef Py_ssize_t *shape_and_strides = <Py_ssize_t*>malloc(2 * sizeof(Py_ssize_t))
        if shape_and_strides == NULL:
            raise MemoryError("Unable to allocate shape/strides buffer")
        
        shape_and_strides[0] = self.vec.size()  # shape
        shape_and_strides[1] = sizeof(double)  # strides
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = shape_and_strides[0] * sizeof(double)
        buffer.readonly = 0
        if flags & PyBUF_FORMAT:
            buffer.format = FORMAT_DOUBLE
        else:
            buffer.format = NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = shape_and_strides
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = shape_and_strides + 1
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(double)
        buffer.internal = <void*>shape_and_strides  # Store pointer so we can free it later
    
    def __releasebuffer__(self, Py_buffer *buffer):
        if <void*>buffer.internal != NULL:
            free(<void*>buffer.internal)
            buffer.internal = NULL


cdef class ArrayWrapperInt8:
    """
    Owning wrapper for std::vector<int8_t> with buffer protocol support.
    
    This class owns its data via a C++ vector and can be converted to numpy arrays.
    The numpy array will be a view into this wrapper's data, so the wrapper
    must be kept alive while the numpy array is in use.
    
    Example:
        wrapper = ArrayWrapperInt8(size=10)
        arr = np.asarray(wrapper)
        arr.base = wrapper  # Keep wrapper alive
    """
    cdef libcpp_vector[int8_t] vec

    def __init__(self, size=0):
        """Initialize with optional size."""
        if size > 0:
            self.vec.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self.vec.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self.vec.size()
    
    def set_data(self, libcpp_vector[int8_t]& data):
        """Set data by swapping with a C++ vector."""
        self.vec.swap(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        # Allocate shape and strides array (2 elements: [shape, strides])
        cdef Py_ssize_t *shape_and_strides = <Py_ssize_t*>malloc(2 * sizeof(Py_ssize_t))
        if shape_and_strides == NULL:
            raise MemoryError("Unable to allocate shape/strides buffer")
        
        shape_and_strides[0] = self.vec.size()  # shape
        shape_and_strides[1] = sizeof(int8_t)  # strides
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = shape_and_strides[0] * sizeof(int8_t)
        buffer.readonly = 0
        buffer.format = FORMAT_INT8 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = shape_and_strides
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = shape_and_strides + 1
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int8_t)
        buffer.internal = <void*>shape_and_strides  # Store pointer so we can free it later
    
    def __releasebuffer__(self, Py_buffer *buffer):
        if <void*>buffer.internal != NULL:
            free(<void*>buffer.internal)
            buffer.internal = NULL


cdef class ArrayWrapperInt16:
    """
    Owning wrapper for std::vector<int16_t> with buffer protocol support.
    
    This class owns its data via a C++ vector and can be converted to numpy arrays.
    The numpy array will be a view into this wrapper's data, so the wrapper
    must be kept alive while the numpy array is in use.
    
    Example:
        wrapper = ArrayWrapperInt16(size=10)
        arr = np.asarray(wrapper)
        arr.base = wrapper  # Keep wrapper alive
    """
    cdef libcpp_vector[int16_t] vec

    def __init__(self, size=0):
        """Initialize with optional size."""
        if size > 0:
            self.vec.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self.vec.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self.vec.size()
    
    def set_data(self, libcpp_vector[int16_t]& data):
        """Set data by swapping with a C++ vector."""
        self.vec.swap(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        # Allocate shape and strides array (2 elements: [shape, strides])
        cdef Py_ssize_t *shape_and_strides = <Py_ssize_t*>malloc(2 * sizeof(Py_ssize_t))
        if shape_and_strides == NULL:
            raise MemoryError("Unable to allocate shape/strides buffer")
        
        shape_and_strides[0] = self.vec.size()  # shape
        shape_and_strides[1] = sizeof(int16_t)  # strides
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = shape_and_strides[0] * sizeof(int16_t)
        buffer.readonly = 0
        buffer.format = FORMAT_INT16 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = shape_and_strides
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = shape_and_strides + 1
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int16_t)
        buffer.internal = <void*>shape_and_strides  # Store pointer so we can free it later
    
    def __releasebuffer__(self, Py_buffer *buffer):
        if <void*>buffer.internal != NULL:
            free(<void*>buffer.internal)
            buffer.internal = NULL


cdef class ArrayWrapperInt32:
    """
    Owning wrapper for std::vector<int32_t> with buffer protocol support.
    
    This class owns its data via a C++ vector and can be converted to numpy arrays.
    The numpy array will be a view into this wrapper's data, so the wrapper
    must be kept alive while the numpy array is in use.
    
    Example:
        wrapper = ArrayWrapperInt32(size=10)
        arr = np.asarray(wrapper)
        arr.base = wrapper  # Keep wrapper alive
    """
    cdef libcpp_vector[int32_t] vec

    def __init__(self, size=0):
        """Initialize with optional size."""
        if size > 0:
            self.vec.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self.vec.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self.vec.size()
    
    def set_data(self, libcpp_vector[int32_t]& data):
        """Set data by swapping with a C++ vector."""
        self.vec.swap(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        # Allocate shape and strides array (2 elements: [shape, strides])
        cdef Py_ssize_t *shape_and_strides = <Py_ssize_t*>malloc(2 * sizeof(Py_ssize_t))
        if shape_and_strides == NULL:
            raise MemoryError("Unable to allocate shape/strides buffer")
        
        shape_and_strides[0] = self.vec.size()  # shape
        shape_and_strides[1] = sizeof(int32_t)  # strides
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = shape_and_strides[0] * sizeof(int32_t)
        buffer.readonly = 0
        buffer.format = FORMAT_INT32 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = shape_and_strides
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = shape_and_strides + 1
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int32_t)
        buffer.internal = <void*>shape_and_strides  # Store pointer so we can free it later
    
    def __releasebuffer__(self, Py_buffer *buffer):
        if <void*>buffer.internal != NULL:
            free(<void*>buffer.internal)
            buffer.internal = NULL


cdef class ArrayWrapperInt64:
    """
    Owning wrapper for std::vector<int64_t> with buffer protocol support.
    
    This class owns its data via a C++ vector and can be converted to numpy arrays.
    The numpy array will be a view into this wrapper's data, so the wrapper
    must be kept alive while the numpy array is in use.
    
    Example:
        wrapper = ArrayWrapperInt64(size=10)
        arr = np.asarray(wrapper)
        arr.base = wrapper  # Keep wrapper alive
    """
    cdef libcpp_vector[int64_t] vec

    def __init__(self, size=0):
        """Initialize with optional size."""
        if size > 0:
            self.vec.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self.vec.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self.vec.size()
    
    def set_data(self, libcpp_vector[int64_t]& data):
        """Set data by swapping with a C++ vector."""
        self.vec.swap(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        # Allocate shape and strides array (2 elements: [shape, strides])
        cdef Py_ssize_t *shape_and_strides = <Py_ssize_t*>malloc(2 * sizeof(Py_ssize_t))
        if shape_and_strides == NULL:
            raise MemoryError("Unable to allocate shape/strides buffer")
        
        shape_and_strides[0] = self.vec.size()  # shape
        shape_and_strides[1] = sizeof(int64_t)  # strides
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = shape_and_strides[0] * sizeof(int64_t)
        buffer.readonly = 0
        buffer.format = FORMAT_INT64 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = shape_and_strides
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = shape_and_strides + 1
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int64_t)
        buffer.internal = <void*>shape_and_strides  # Store pointer so we can free it later
    
    def __releasebuffer__(self, Py_buffer *buffer):
        if <void*>buffer.internal != NULL:
            free(<void*>buffer.internal)
            buffer.internal = NULL


cdef class ArrayWrapperUInt8:
    """
    Owning wrapper for std::vector<uint8_t> with buffer protocol support.
    
    This class owns its data via a C++ vector and can be converted to numpy arrays.
    The numpy array will be a view into this wrapper's data, so the wrapper
    must be kept alive while the numpy array is in use.
    
    Example:
        wrapper = ArrayWrapperUInt8(size=10)
        arr = np.asarray(wrapper)
        arr.base = wrapper  # Keep wrapper alive
    """
    cdef libcpp_vector[uint8_t] vec

    def __init__(self, size=0):
        """Initialize with optional size."""
        if size > 0:
            self.vec.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self.vec.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self.vec.size()
    
    def set_data(self, libcpp_vector[uint8_t]& data):
        """Set data by swapping with a C++ vector."""
        self.vec.swap(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        # Allocate shape and strides array (2 elements: [shape, strides])
        cdef Py_ssize_t *shape_and_strides = <Py_ssize_t*>malloc(2 * sizeof(Py_ssize_t))
        if shape_and_strides == NULL:
            raise MemoryError("Unable to allocate shape/strides buffer")
        
        shape_and_strides[0] = self.vec.size()  # shape
        shape_and_strides[1] = sizeof(uint8_t)  # strides
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = shape_and_strides[0] * sizeof(uint8_t)
        buffer.readonly = 0
        buffer.format = FORMAT_UINT8 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = shape_and_strides
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = shape_and_strides + 1
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint8_t)
        buffer.internal = <void*>shape_and_strides  # Store pointer so we can free it later
    
    def __releasebuffer__(self, Py_buffer *buffer):
        if <void*>buffer.internal != NULL:
            free(<void*>buffer.internal)
            buffer.internal = NULL


cdef class ArrayWrapperUInt16:
    """
    Owning wrapper for std::vector<uint16_t> with buffer protocol support.
    
    This class owns its data via a C++ vector and can be converted to numpy arrays.
    The numpy array will be a view into this wrapper's data, so the wrapper
    must be kept alive while the numpy array is in use.
    
    Example:
        wrapper = ArrayWrapperUInt16(size=10)
        arr = np.asarray(wrapper)
        arr.base = wrapper  # Keep wrapper alive
    """
    cdef libcpp_vector[uint16_t] vec

    def __init__(self, size=0):
        """Initialize with optional size."""
        if size > 0:
            self.vec.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self.vec.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self.vec.size()
    
    def set_data(self, libcpp_vector[uint16_t]& data):
        """Set data by swapping with a C++ vector."""
        self.vec.swap(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        # Allocate shape and strides array (2 elements: [shape, strides])
        cdef Py_ssize_t *shape_and_strides = <Py_ssize_t*>malloc(2 * sizeof(Py_ssize_t))
        if shape_and_strides == NULL:
            raise MemoryError("Unable to allocate shape/strides buffer")
        
        shape_and_strides[0] = self.vec.size()  # shape
        shape_and_strides[1] = sizeof(uint16_t)  # strides
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = shape_and_strides[0] * sizeof(uint16_t)
        buffer.readonly = 0
        buffer.format = FORMAT_UINT16 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = shape_and_strides
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = shape_and_strides + 1
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint16_t)
        buffer.internal = <void*>shape_and_strides  # Store pointer so we can free it later
    
    def __releasebuffer__(self, Py_buffer *buffer):
        if <void*>buffer.internal != NULL:
            free(<void*>buffer.internal)
            buffer.internal = NULL


cdef class ArrayWrapperUInt32:
    """
    Owning wrapper for std::vector<uint32_t> with buffer protocol support.
    
    This class owns its data via a C++ vector and can be converted to numpy arrays.
    The numpy array will be a view into this wrapper's data, so the wrapper
    must be kept alive while the numpy array is in use.
    
    Example:
        wrapper = ArrayWrapperUInt32(size=10)
        arr = np.asarray(wrapper)
        arr.base = wrapper  # Keep wrapper alive
    """
    cdef libcpp_vector[uint32_t] vec

    def __init__(self, size=0):
        """Initialize with optional size."""
        if size > 0:
            self.vec.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self.vec.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self.vec.size()
    
    def set_data(self, libcpp_vector[uint32_t]& data):
        """Set data by swapping with a C++ vector."""
        self.vec.swap(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        # Allocate shape and strides array (2 elements: [shape, strides])
        cdef Py_ssize_t *shape_and_strides = <Py_ssize_t*>malloc(2 * sizeof(Py_ssize_t))
        if shape_and_strides == NULL:
            raise MemoryError("Unable to allocate shape/strides buffer")
        
        shape_and_strides[0] = self.vec.size()  # shape
        shape_and_strides[1] = sizeof(uint32_t)  # strides
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = shape_and_strides[0] * sizeof(uint32_t)
        buffer.readonly = 0
        buffer.format = FORMAT_UINT32 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = shape_and_strides
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = shape_and_strides + 1
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint32_t)
        buffer.internal = <void*>shape_and_strides  # Store pointer so we can free it later
    
    def __releasebuffer__(self, Py_buffer *buffer):
        if <void*>buffer.internal != NULL:
            free(<void*>buffer.internal)
            buffer.internal = NULL


cdef class ArrayWrapperUInt64:
    """
    Owning wrapper for std::vector<uint64_t> with buffer protocol support.
    
    This class owns its data via a C++ vector and can be converted to numpy arrays.
    The numpy array will be a view into this wrapper's data, so the wrapper
    must be kept alive while the numpy array is in use.
    
    Example:
        wrapper = ArrayWrapperUInt64(size=10)
        arr = np.asarray(wrapper)
        arr.base = wrapper  # Keep wrapper alive
    """
    cdef libcpp_vector[uint64_t] vec

    def __init__(self, size=0):
        """Initialize with optional size."""
        if size > 0:
            self.vec.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self.vec.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self.vec.size()
    
    def set_data(self, libcpp_vector[uint64_t]& data):
        """Set data by swapping with a C++ vector."""
        self.vec.swap(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        # Allocate shape and strides array (2 elements: [shape, strides])
        cdef Py_ssize_t *shape_and_strides = <Py_ssize_t*>malloc(2 * sizeof(Py_ssize_t))
        if shape_and_strides == NULL:
            raise MemoryError("Unable to allocate shape/strides buffer")
        
        shape_and_strides[0] = self.vec.size()  # shape
        shape_and_strides[1] = sizeof(uint64_t)  # strides
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = shape_and_strides[0] * sizeof(uint64_t)
        buffer.readonly = 0
        buffer.format = FORMAT_UINT64 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = shape_and_strides
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = shape_and_strides + 1
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint64_t)
        buffer.internal = <void*>shape_and_strides  # Store pointer so we can free it later
    
    def __releasebuffer__(self, Py_buffer *buffer):
        if <void*>buffer.internal != NULL:
            free(<void*>buffer.internal)
            buffer.internal = NULL


