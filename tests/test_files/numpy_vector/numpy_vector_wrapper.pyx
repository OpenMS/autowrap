#Generated with autowrap 0.24.1 and Cython (Parser) 3.2.3
#cython: c_string_encoding=ascii
#cython: embedsignature=False
from  enum            import IntEnum as _PyEnum
from  cpython         cimport Py_buffer
from  cpython         cimport bool as pybool_t
from  libcpp.string   cimport string as libcpp_string
from  libcpp.string   cimport string as libcpp_utf8_string
from  libcpp.string   cimport string as libcpp_utf8_output_string
from  libcpp.set      cimport set as libcpp_set
from  libcpp.vector   cimport vector as libcpp_vector
from  libcpp.vector   cimport vector as libcpp_vector_as_np
from  libcpp.pair     cimport pair as libcpp_pair
from  libcpp.map      cimport map  as libcpp_map
from  libcpp.unordered_map cimport unordered_map as libcpp_unordered_map
from  libcpp.unordered_set cimport unordered_set as libcpp_unordered_set
from  libcpp.deque    cimport deque as libcpp_deque
from  libcpp.list     cimport list as libcpp_list
from  libcpp.optional cimport optional as libcpp_optional
from  libcpp.string_view cimport string_view as libcpp_string_view
from  libcpp          cimport bool
from  libc.string     cimport const_char, memcpy
from  cython.operator cimport dereference as deref, preincrement as inc, address as address
from  AutowrapRefHolder      cimport AutowrapRefHolder
from  AutowrapPtrHolder      cimport AutowrapPtrHolder
from  AutowrapConstPtrHolder cimport AutowrapConstPtrHolder
from  libcpp.memory   cimport shared_ptr
cimport numpy as np
import numpy as np
cimport numpy as numpy
import numpy as numpy
from cpython.ref cimport Py_INCREF
# Inlined ArrayWrapper classes for buffer protocol support (value returns)
# Reference returns use Cython memory views instead
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
from numpy_vector_test cimport NumpyVectorTest as _NumpyVectorTest

cdef extern from "autowrap_tools.hpp":
    char * _cast_const_away(char *) 

cdef class NumpyVectorTest:
    """
    Cython implementation of _NumpyVectorTest
    """

    cdef shared_ptr[_NumpyVectorTest] inst

    def __dealloc__(self):
         self.inst.reset()

    
    def __init__(self):
        """
        __init__(self) -> None
        """
        self.inst = shared_ptr[_NumpyVectorTest](new _NumpyVectorTest())
    
    def getConstRefVector(self):
        """
        getConstRefVector(self) -> numpy.ndarray[numpy.float64_t, ndim=1]
        """
        _r = self.inst.get().getConstRefVector()
        # Convert C++ const vector reference to numpy array VIEW (zero-copy, readonly)
        cdef size_t _size_py_result = _r.size()
        cdef double[:] _view_py_result = <double[:_size_py_result]>_r.data()
        cdef object py_result = numpy.asarray(_view_py_result)
        py_result.setflags(write=False)
        # Set base to owner to keep it alive
        Py_INCREF(self)
        cdef int _err_py_result = numpy.PyArray_SetBaseObject(<numpy.ndarray>py_result, <object>self)
        if _err_py_result != 0:
            raise RuntimeError("Failed to set array base")
        return py_result
    
    def getMutableRefVector(self):
        """
        getMutableRefVector(self) -> numpy.ndarray[numpy.float64_t, ndim=1]
        """
        _r = self.inst.get().getMutableRefVector()
        # Convert C++ vector reference to numpy array VIEW (zero-copy, writable)
        cdef size_t _size_py_result = _r.size()
        cdef double[:] _view_py_result = <double[:_size_py_result]>_r.data()
        cdef object py_result = numpy.asarray(_view_py_result)
        # Set base to owner to keep it alive
        Py_INCREF(self)
        cdef int _err_py_result = numpy.PyArray_SetBaseObject(<numpy.ndarray>py_result, <object>self)
        if _err_py_result != 0:
            raise RuntimeError("Failed to set array base")
        return py_result
    
    def getValueVector(self,  size ):
        """
        getValueVector(self, size: int ) -> numpy.ndarray[numpy.float64_t, ndim=1]
        """
        assert isinstance(size, int) and size >= 0, 'arg size wrong type'
    
        _r = self.inst.get().getValueVector((<size_t>size))
        # Convert C++ vector to numpy array using owning wrapper (data already copied)
        cdef ArrayWrapperDouble _wrapper_py_result = ArrayWrapperDouble()
        _wrapper_py_result.set_data(_r)
        cdef object py_result = numpy.asarray(_wrapper_py_result)
        # Set base to wrapper to keep it alive
        Py_INCREF(_wrapper_py_result)
        cdef int _err_py_result = numpy.PyArray_SetBaseObject(<numpy.ndarray>py_result, <object>_wrapper_py_result)
        if _err_py_result != 0:
            raise RuntimeError("Failed to set array base")
        return py_result
    
    def sumVector(self, numpy.ndarray[numpy.float64_t, ndim=1] data ):
        """
        sumVector(self, data: numpy.ndarray[numpy.float64_t, ndim=1] ) -> float
        """
        assert isinstance(data, numpy.ndarray), 'arg data wrong type'
        # Convert 1D numpy array to C++ vector (fast memcpy)
        cdef libcpp_vector[double] * v0 = new libcpp_vector[double]()
        cdef size_t n_0 = data.shape[0]
        v0.resize(n_0)
        if n_0 > 0:
            memcpy(v0.data(), <void*>numpy.PyArray_DATA(data), n_0 * sizeof(double))
        cdef double _r = self.inst.get().sumVector(deref(v0))
        del v0
        py_result = <double>_r
        return py_result
    
    def sumIntVector(self, numpy.ndarray[numpy.int32_t, ndim=1] data ):
        """
        sumIntVector(self, data: numpy.ndarray[numpy.int32_t, ndim=1] ) -> int
        """
        assert isinstance(data, numpy.ndarray), 'arg data wrong type'
        # Convert 1D numpy array to C++ vector (fast memcpy)
        cdef libcpp_vector[int] * v0 = new libcpp_vector[int]()
        cdef size_t n_0 = data.shape[0]
        v0.resize(n_0)
        if n_0 > 0:
            memcpy(v0.data(), <void*>numpy.PyArray_DATA(data), n_0 * sizeof(int))
        cdef int _r = self.inst.get().sumIntVector(deref(v0))
        del v0
        py_result = <int>_r
        return py_result
    
    def createFloatVector(self,  size ):
        """
        createFloatVector(self, size: int ) -> numpy.ndarray[numpy.float32_t, ndim=1]
        """
        assert isinstance(size, int) and size >= 0, 'arg size wrong type'
    
        _r = self.inst.get().createFloatVector((<size_t>size))
        # Convert C++ vector to numpy array using owning wrapper (data already copied)
        cdef ArrayWrapperFloat _wrapper_py_result = ArrayWrapperFloat()
        _wrapper_py_result.set_data(_r)
        cdef object py_result = numpy.asarray(_wrapper_py_result)
        # Set base to wrapper to keep it alive
        Py_INCREF(_wrapper_py_result)
        cdef int _err_py_result = numpy.PyArray_SetBaseObject(<numpy.ndarray>py_result, <object>_wrapper_py_result)
        if _err_py_result != 0:
            raise RuntimeError("Failed to set array base")
        return py_result
    
    def create2DVector(self,  rows ,  cols ):
        """
        create2DVector(self, rows: int , cols: int ) -> numpy.ndarray[numpy.float64_t, ndim=2]
        """
        assert isinstance(rows, int) and rows >= 0, 'arg rows wrong type'
        assert isinstance(cols, int) and cols >= 0, 'arg cols wrong type'
    
    
        _r = self.inst.get().create2DVector((<size_t>rows), (<size_t>cols))
        # Convert nested C++ vector to 2D numpy array (copy)
        cdef size_t n_rows = _r.size()
        cdef size_t n_cols = _r[0].size() if n_rows > 0 else 0
        cdef object py_result = numpy.empty((n_rows, n_cols), dtype=numpy.float64)
        cdef size_t i, j
        cdef double* row_ptr
        for i in range(n_rows):
            row_ptr = <double*>_r[i].data()
            for j in range(n_cols):
                py_result[i, j] = row_ptr[j]
        return py_result
    
    def sum2DVector(self, numpy.ndarray[numpy.float64_t, ndim=2] data ):
        """
        sum2DVector(self, data: numpy.ndarray[numpy.float64_t, ndim=2] ) -> float
        """
        assert isinstance(data, numpy.ndarray), 'arg data wrong type'
        # Convert 2D numpy array to nested C++ vector
        cdef libcpp_vector[libcpp_vector_as_np[double]] * v0 = new libcpp_vector[libcpp_vector_as_np[double]]()
        cdef size_t i_0, j_0
        cdef libcpp_vector[double] row_0
        for i_0 in range(data.shape[0]):
            row_0 = libcpp_vector[double]()
            for j_0 in range(data.shape[1]):
                row_0.push_back(<double>data[i_0, j_0])
            v0.push_back(row_0)
        cdef double _r = self.inst.get().sum2DVector(deref(v0))
        del v0
        py_result = <double>_r
        return py_result 
