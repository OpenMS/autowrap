# cython: language_level=3
# cython: embedsignature=True
"""
Generic array wrapper classes with buffer protocol support.

This module provides owning wrappers and non-owning views for all numeric types.
The classes implement the Python buffer protocol, allowing zero-copy integration
with numpy and other buffer-aware Python libraries.

Owning wrappers directly hold a std::vector.
Views directly hold a raw pointer + size + owner reference.

Supported types: float, double, int8, int16, int32, int64, uint8, uint16, uint32, uint64
Views can be either writable or readonly based on the readonly flag.
"""

from cpython.buffer cimport PyBUF_FORMAT, PyBUF_ND, PyBUF_STRIDES, PyBUF_WRITABLE
from cpython cimport Py_buffer
from libcpp.vector cimport vector as libcpp_vector
from libcpp cimport bool as cbool
from libc.stdint cimport int8_t, int16_t, int32_t, int64_t, uint8_t, uint16_t, uint32_t, uint64_t
cimport cython


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
        
        
        self._shape_val = self.vec.size()
        self._strides_val = sizeof(float)
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = self._shape_val * sizeof(float)
        buffer.readonly = 0
        buffer.format = FORMAT_FLOAT if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(float)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


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
        
        
        self._shape_val = self.vec.size()
        self._strides_val = sizeof(double)
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = self._shape_val * sizeof(double)
        buffer.readonly = 0
        buffer.format = FORMAT_DOUBLE if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(double)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


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
        
        
        self._shape_val = self.vec.size()
        self._strides_val = sizeof(int8_t)
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = self._shape_val * sizeof(int8_t)
        buffer.readonly = 0
        buffer.format = FORMAT_INT8 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int8_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


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
        
        
        self._shape_val = self.vec.size()
        self._strides_val = sizeof(int16_t)
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = self._shape_val * sizeof(int16_t)
        buffer.readonly = 0
        buffer.format = FORMAT_INT16 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int16_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


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
        
        
        self._shape_val = self.vec.size()
        self._strides_val = sizeof(int32_t)
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = self._shape_val * sizeof(int32_t)
        buffer.readonly = 0
        buffer.format = FORMAT_INT32 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int32_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


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
        
        
        self._shape_val = self.vec.size()
        self._strides_val = sizeof(int64_t)
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = self._shape_val * sizeof(int64_t)
        buffer.readonly = 0
        buffer.format = FORMAT_INT64 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int64_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


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
        
        
        self._shape_val = self.vec.size()
        self._strides_val = sizeof(uint8_t)
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = self._shape_val * sizeof(uint8_t)
        buffer.readonly = 0
        buffer.format = FORMAT_UINT8 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint8_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


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
        
        
        self._shape_val = self.vec.size()
        self._strides_val = sizeof(uint16_t)
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = self._shape_val * sizeof(uint16_t)
        buffer.readonly = 0
        buffer.format = FORMAT_UINT16 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint16_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


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
        
        
        self._shape_val = self.vec.size()
        self._strides_val = sizeof(uint32_t)
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = self._shape_val * sizeof(uint32_t)
        buffer.readonly = 0
        buffer.format = FORMAT_UINT32 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint32_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


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
        
        
        self._shape_val = self.vec.size()
        self._strides_val = sizeof(uint64_t)
        
        buffer.buf = <char*>self.vec.data()
        buffer.obj = self
        buffer.len = self._shape_val * sizeof(uint64_t)
        buffer.readonly = 0
        buffer.format = FORMAT_UINT64 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint64_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


#############################################################################
# Non-owning View Classes (directly hold raw pointer)
#############################################################################


cdef class ArrayViewFloat:
    """
    Non-owning view wrapper for float arrays with buffer protocol support.
    
    This class does NOT own its data - it only holds a pointer and size.
    The 'owner' object must be kept alive while this view exists.
    The readonly flag controls write access.
    
    Use the factory function _create_view_float to create instances.
    
    Example:
        # From C++ reference
        view = _create_view_float(vec.data(), vec.size(), owner=self, readonly=False)
        arr = np.asarray(view)
        arr.base = view  # Keep view (and owner) alive
    """
    
    def __cinit__(self):
        self.ptr = NULL
        self._size = 0
        self.owner = None
        self.readonly = False
    
    def size(self):
        """Get the size of the view."""
        return self._size
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self.readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        
        
        if self.ptr == NULL:
            raise ValueError("ArrayView not initialized")
        
        if (flags & PyBUF_WRITABLE) and self.readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        self._shape_val = self._size
        self._strides_val = sizeof(float)
        
        buffer.buf = <char*>self.ptr
        buffer.obj = self
        buffer.len = self._size * sizeof(float)
        buffer.readonly = 1 if self.readonly else 0
        buffer.format = FORMAT_FLOAT if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(float)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewDouble:
    """
    Non-owning view wrapper for double arrays with buffer protocol support.
    
    This class does NOT own its data - it only holds a pointer and size.
    The 'owner' object must be kept alive while this view exists.
    The readonly flag controls write access.
    
    Use the factory function _create_view_double to create instances.
    
    Example:
        # From C++ reference
        view = _create_view_double(vec.data(), vec.size(), owner=self, readonly=False)
        arr = np.asarray(view)
        arr.base = view  # Keep view (and owner) alive
    """
    
    def __cinit__(self):
        self.ptr = NULL
        self._size = 0
        self.owner = None
        self.readonly = False
    
    def size(self):
        """Get the size of the view."""
        return self._size
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self.readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        
        
        if self.ptr == NULL:
            raise ValueError("ArrayView not initialized")
        
        if (flags & PyBUF_WRITABLE) and self.readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        self._shape_val = self._size
        self._strides_val = sizeof(double)
        
        buffer.buf = <char*>self.ptr
        buffer.obj = self
        buffer.len = self._size * sizeof(double)
        buffer.readonly = 1 if self.readonly else 0
        buffer.format = FORMAT_DOUBLE if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(double)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewInt8:
    """
    Non-owning view wrapper for int8_t arrays with buffer protocol support.
    
    This class does NOT own its data - it only holds a pointer and size.
    The 'owner' object must be kept alive while this view exists.
    The readonly flag controls write access.
    
    Use the factory function _create_view_int8 to create instances.
    
    Example:
        # From C++ reference
        view = _create_view_int8(vec.data(), vec.size(), owner=self, readonly=False)
        arr = np.asarray(view)
        arr.base = view  # Keep view (and owner) alive
    """
    
    def __cinit__(self):
        self.ptr = NULL
        self._size = 0
        self.owner = None
        self.readonly = False
    
    def size(self):
        """Get the size of the view."""
        return self._size
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self.readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        
        
        if self.ptr == NULL:
            raise ValueError("ArrayView not initialized")
        
        if (flags & PyBUF_WRITABLE) and self.readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        self._shape_val = self._size
        self._strides_val = sizeof(int8_t)
        
        buffer.buf = <char*>self.ptr
        buffer.obj = self
        buffer.len = self._size * sizeof(int8_t)
        buffer.readonly = 1 if self.readonly else 0
        buffer.format = FORMAT_INT8 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int8_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewInt16:
    """
    Non-owning view wrapper for int16_t arrays with buffer protocol support.
    
    This class does NOT own its data - it only holds a pointer and size.
    The 'owner' object must be kept alive while this view exists.
    The readonly flag controls write access.
    
    Use the factory function _create_view_int16 to create instances.
    
    Example:
        # From C++ reference
        view = _create_view_int16(vec.data(), vec.size(), owner=self, readonly=False)
        arr = np.asarray(view)
        arr.base = view  # Keep view (and owner) alive
    """
    
    def __cinit__(self):
        self.ptr = NULL
        self._size = 0
        self.owner = None
        self.readonly = False
    
    def size(self):
        """Get the size of the view."""
        return self._size
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self.readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        
        
        if self.ptr == NULL:
            raise ValueError("ArrayView not initialized")
        
        if (flags & PyBUF_WRITABLE) and self.readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        self._shape_val = self._size
        self._strides_val = sizeof(int16_t)
        
        buffer.buf = <char*>self.ptr
        buffer.obj = self
        buffer.len = self._size * sizeof(int16_t)
        buffer.readonly = 1 if self.readonly else 0
        buffer.format = FORMAT_INT16 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int16_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewInt32:
    """
    Non-owning view wrapper for int32_t arrays with buffer protocol support.
    
    This class does NOT own its data - it only holds a pointer and size.
    The 'owner' object must be kept alive while this view exists.
    The readonly flag controls write access.
    
    Use the factory function _create_view_int32 to create instances.
    
    Example:
        # From C++ reference
        view = _create_view_int32(vec.data(), vec.size(), owner=self, readonly=False)
        arr = np.asarray(view)
        arr.base = view  # Keep view (and owner) alive
    """
    
    def __cinit__(self):
        self.ptr = NULL
        self._size = 0
        self.owner = None
        self.readonly = False
    
    def size(self):
        """Get the size of the view."""
        return self._size
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self.readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        
        
        if self.ptr == NULL:
            raise ValueError("ArrayView not initialized")
        
        if (flags & PyBUF_WRITABLE) and self.readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        self._shape_val = self._size
        self._strides_val = sizeof(int32_t)
        
        buffer.buf = <char*>self.ptr
        buffer.obj = self
        buffer.len = self._size * sizeof(int32_t)
        buffer.readonly = 1 if self.readonly else 0
        buffer.format = FORMAT_INT32 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int32_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewInt64:
    """
    Non-owning view wrapper for int64_t arrays with buffer protocol support.
    
    This class does NOT own its data - it only holds a pointer and size.
    The 'owner' object must be kept alive while this view exists.
    The readonly flag controls write access.
    
    Use the factory function _create_view_int64 to create instances.
    
    Example:
        # From C++ reference
        view = _create_view_int64(vec.data(), vec.size(), owner=self, readonly=False)
        arr = np.asarray(view)
        arr.base = view  # Keep view (and owner) alive
    """
    
    def __cinit__(self):
        self.ptr = NULL
        self._size = 0
        self.owner = None
        self.readonly = False
    
    def size(self):
        """Get the size of the view."""
        return self._size
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self.readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        
        
        if self.ptr == NULL:
            raise ValueError("ArrayView not initialized")
        
        if (flags & PyBUF_WRITABLE) and self.readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        self._shape_val = self._size
        self._strides_val = sizeof(int64_t)
        
        buffer.buf = <char*>self.ptr
        buffer.obj = self
        buffer.len = self._size * sizeof(int64_t)
        buffer.readonly = 1 if self.readonly else 0
        buffer.format = FORMAT_INT64 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int64_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewUInt8:
    """
    Non-owning view wrapper for uint8_t arrays with buffer protocol support.
    
    This class does NOT own its data - it only holds a pointer and size.
    The 'owner' object must be kept alive while this view exists.
    The readonly flag controls write access.
    
    Use the factory function _create_view_uint8 to create instances.
    
    Example:
        # From C++ reference
        view = _create_view_uint8(vec.data(), vec.size(), owner=self, readonly=False)
        arr = np.asarray(view)
        arr.base = view  # Keep view (and owner) alive
    """
    
    def __cinit__(self):
        self.ptr = NULL
        self._size = 0
        self.owner = None
        self.readonly = False
    
    def size(self):
        """Get the size of the view."""
        return self._size
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self.readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        
        
        if self.ptr == NULL:
            raise ValueError("ArrayView not initialized")
        
        if (flags & PyBUF_WRITABLE) and self.readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        self._shape_val = self._size
        self._strides_val = sizeof(uint8_t)
        
        buffer.buf = <char*>self.ptr
        buffer.obj = self
        buffer.len = self._size * sizeof(uint8_t)
        buffer.readonly = 1 if self.readonly else 0
        buffer.format = FORMAT_UINT8 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint8_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewUInt16:
    """
    Non-owning view wrapper for uint16_t arrays with buffer protocol support.
    
    This class does NOT own its data - it only holds a pointer and size.
    The 'owner' object must be kept alive while this view exists.
    The readonly flag controls write access.
    
    Use the factory function _create_view_uint16 to create instances.
    
    Example:
        # From C++ reference
        view = _create_view_uint16(vec.data(), vec.size(), owner=self, readonly=False)
        arr = np.asarray(view)
        arr.base = view  # Keep view (and owner) alive
    """
    
    def __cinit__(self):
        self.ptr = NULL
        self._size = 0
        self.owner = None
        self.readonly = False
    
    def size(self):
        """Get the size of the view."""
        return self._size
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self.readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        
        
        if self.ptr == NULL:
            raise ValueError("ArrayView not initialized")
        
        if (flags & PyBUF_WRITABLE) and self.readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        self._shape_val = self._size
        self._strides_val = sizeof(uint16_t)
        
        buffer.buf = <char*>self.ptr
        buffer.obj = self
        buffer.len = self._size * sizeof(uint16_t)
        buffer.readonly = 1 if self.readonly else 0
        buffer.format = FORMAT_UINT16 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint16_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewUInt32:
    """
    Non-owning view wrapper for uint32_t arrays with buffer protocol support.
    
    This class does NOT own its data - it only holds a pointer and size.
    The 'owner' object must be kept alive while this view exists.
    The readonly flag controls write access.
    
    Use the factory function _create_view_uint32 to create instances.
    
    Example:
        # From C++ reference
        view = _create_view_uint32(vec.data(), vec.size(), owner=self, readonly=False)
        arr = np.asarray(view)
        arr.base = view  # Keep view (and owner) alive
    """
    
    def __cinit__(self):
        self.ptr = NULL
        self._size = 0
        self.owner = None
        self.readonly = False
    
    def size(self):
        """Get the size of the view."""
        return self._size
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self.readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        
        
        if self.ptr == NULL:
            raise ValueError("ArrayView not initialized")
        
        if (flags & PyBUF_WRITABLE) and self.readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        self._shape_val = self._size
        self._strides_val = sizeof(uint32_t)
        
        buffer.buf = <char*>self.ptr
        buffer.obj = self
        buffer.len = self._size * sizeof(uint32_t)
        buffer.readonly = 1 if self.readonly else 0
        buffer.format = FORMAT_UINT32 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint32_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewUInt64:
    """
    Non-owning view wrapper for uint64_t arrays with buffer protocol support.
    
    This class does NOT own its data - it only holds a pointer and size.
    The 'owner' object must be kept alive while this view exists.
    The readonly flag controls write access.
    
    Use the factory function _create_view_uint64 to create instances.
    
    Example:
        # From C++ reference
        view = _create_view_uint64(vec.data(), vec.size(), owner=self, readonly=False)
        arr = np.asarray(view)
        arr.base = view  # Keep view (and owner) alive
    """
    
    def __cinit__(self):
        self.ptr = NULL
        self._size = 0
        self.owner = None
        self.readonly = False
    
    def size(self):
        """Get the size of the view."""
        return self._size
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self.readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        
        
        if self.ptr == NULL:
            raise ValueError("ArrayView not initialized")
        
        if (flags & PyBUF_WRITABLE) and self.readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        self._shape_val = self._size
        self._strides_val = sizeof(uint64_t)
        
        buffer.buf = <char*>self.ptr
        buffer.obj = self
        buffer.len = self._size * sizeof(uint64_t)
        buffer.readonly = 1 if self.readonly else 0
        buffer.format = FORMAT_UINT64 if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        if flags & PyBUF_ND:
            buffer.shape = &self._shape_val
        else:
            buffer.shape = NULL
        if flags & PyBUF_STRIDES:
            buffer.strides = &self._strides_val
        else:
            buffer.strides = NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint64_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


#############################################################################
# Factory Functions for Creating Views from C Level
#############################################################################


cdef ArrayViewFloat _create_view_float(float* ptr, size_t size, object owner, cbool readonly):
    """Factory function to create ArrayViewFloat from C-level code."""
    cdef ArrayViewFloat view = ArrayViewFloat.__new__(ArrayViewFloat)
    view.ptr = ptr
    view._size = size
    view.owner = owner
    view.readonly = readonly
    return view


cdef ArrayViewDouble _create_view_double(double* ptr, size_t size, object owner, cbool readonly):
    """Factory function to create ArrayViewDouble from C-level code."""
    cdef ArrayViewDouble view = ArrayViewDouble.__new__(ArrayViewDouble)
    view.ptr = ptr
    view._size = size
    view.owner = owner
    view.readonly = readonly
    return view


cdef ArrayViewInt8 _create_view_int8(int8_t* ptr, size_t size, object owner, cbool readonly):
    """Factory function to create ArrayViewInt8 from C-level code."""
    cdef ArrayViewInt8 view = ArrayViewInt8.__new__(ArrayViewInt8)
    view.ptr = ptr
    view._size = size
    view.owner = owner
    view.readonly = readonly
    return view


cdef ArrayViewInt16 _create_view_int16(int16_t* ptr, size_t size, object owner, cbool readonly):
    """Factory function to create ArrayViewInt16 from C-level code."""
    cdef ArrayViewInt16 view = ArrayViewInt16.__new__(ArrayViewInt16)
    view.ptr = ptr
    view._size = size
    view.owner = owner
    view.readonly = readonly
    return view


cdef ArrayViewInt32 _create_view_int32(int32_t* ptr, size_t size, object owner, cbool readonly):
    """Factory function to create ArrayViewInt32 from C-level code."""
    cdef ArrayViewInt32 view = ArrayViewInt32.__new__(ArrayViewInt32)
    view.ptr = ptr
    view._size = size
    view.owner = owner
    view.readonly = readonly
    return view


cdef ArrayViewInt64 _create_view_int64(int64_t* ptr, size_t size, object owner, cbool readonly):
    """Factory function to create ArrayViewInt64 from C-level code."""
    cdef ArrayViewInt64 view = ArrayViewInt64.__new__(ArrayViewInt64)
    view.ptr = ptr
    view._size = size
    view.owner = owner
    view.readonly = readonly
    return view


cdef ArrayViewUInt8 _create_view_uint8(uint8_t* ptr, size_t size, object owner, cbool readonly):
    """Factory function to create ArrayViewUInt8 from C-level code."""
    cdef ArrayViewUInt8 view = ArrayViewUInt8.__new__(ArrayViewUInt8)
    view.ptr = ptr
    view._size = size
    view.owner = owner
    view.readonly = readonly
    return view


cdef ArrayViewUInt16 _create_view_uint16(uint16_t* ptr, size_t size, object owner, cbool readonly):
    """Factory function to create ArrayViewUInt16 from C-level code."""
    cdef ArrayViewUInt16 view = ArrayViewUInt16.__new__(ArrayViewUInt16)
    view.ptr = ptr
    view._size = size
    view.owner = owner
    view.readonly = readonly
    return view


cdef ArrayViewUInt32 _create_view_uint32(uint32_t* ptr, size_t size, object owner, cbool readonly):
    """Factory function to create ArrayViewUInt32 from C-level code."""
    cdef ArrayViewUInt32 view = ArrayViewUInt32.__new__(ArrayViewUInt32)
    view.ptr = ptr
    view._size = size
    view.owner = owner
    view.readonly = readonly
    return view


cdef ArrayViewUInt64 _create_view_uint64(uint64_t* ptr, size_t size, object owner, cbool readonly):
    """Factory function to create ArrayViewUInt64 from C-level code."""
    cdef ArrayViewUInt64 view = ArrayViewUInt64.__new__(ArrayViewUInt64)
    view.ptr = ptr
    view._size = size
    view.owner = owner
    view.readonly = readonly
    return view

