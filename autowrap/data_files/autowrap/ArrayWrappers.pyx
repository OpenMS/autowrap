# cython: language_level=3
# cython: embedsignature=True
"""
Generic array wrapper classes with buffer protocol support.

This module provides owning wrappers and non-owning views for all numeric types.
The classes implement the Python buffer protocol, allowing zero-copy integration
with numpy and other buffer-aware Python libraries.

Supported types: float, double, int8, int16, int32, int64, uint8, uint16, uint32, uint64
Views can be either writable or readonly based on the readonly flag.
"""

from cpython.buffer cimport PyBUF_FORMAT, PyBUF_ND, PyBUF_STRIDES, PyBUF_WRITABLE
from cpython cimport Py_buffer
from libcpp.vector cimport vector as libcpp_vector
from libcpp cimport bool as cbool
from libc.stdint cimport int8_t, int16_t, int32_t, int64_t, uint8_t, uint16_t, uint32_t, uint64_t
cimport cython

# Import the C++ classes
from ArrayWrapper cimport ArrayWrapper as CppArrayWrapper
from ArrayWrapper cimport ArrayView as CppArrayView

#############################################################################
# Owning Wrapper Classes
#############################################################################


cdef class ArrayWrapperFloat:
    """
    Owning wrapper for std::vector<float> with buffer protocol support.
    
    This class owns its data and can be converted to numpy arrays.
    """
    cdef CppArrayWrapper[float]* _cpp_wrapper
    
    def __cinit__(self):
        self._cpp_wrapper = new CppArrayWrapper[float]()
    
    def __dealloc__(self):
        del self._cpp_wrapper
    
    def __init__(self, size=0):
        if size > 0:
            self._cpp_wrapper.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self._cpp_wrapper.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self._cpp_wrapper.size()
    
    def set_data(self, libcpp_vector[float]& data):
        """Set data by swapping with a C++ vector."""
        self._cpp_wrapper.set_data(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        shape[0] = self._cpp_wrapper.size()
        strides[0] = sizeof(float)
        
        buffer.buf = <char*>self._cpp_wrapper.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(float)
        buffer.readonly = 0
        buffer.format = 'f' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(float)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayWrapperDouble:
    """
    Owning wrapper for std::vector<double> with buffer protocol support.
    
    This class owns its data and can be converted to numpy arrays.
    """
    cdef CppArrayWrapper[double]* _cpp_wrapper
    
    def __cinit__(self):
        self._cpp_wrapper = new CppArrayWrapper[double]()
    
    def __dealloc__(self):
        del self._cpp_wrapper
    
    def __init__(self, size=0):
        if size > 0:
            self._cpp_wrapper.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self._cpp_wrapper.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self._cpp_wrapper.size()
    
    def set_data(self, libcpp_vector[double]& data):
        """Set data by swapping with a C++ vector."""
        self._cpp_wrapper.set_data(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        shape[0] = self._cpp_wrapper.size()
        strides[0] = sizeof(double)
        
        buffer.buf = <char*>self._cpp_wrapper.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(double)
        buffer.readonly = 0
        buffer.format = 'd' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(double)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayWrapperInt8:
    """
    Owning wrapper for std::vector<int8_t> with buffer protocol support.
    
    This class owns its data and can be converted to numpy arrays.
    """
    cdef CppArrayWrapper[int8_t]* _cpp_wrapper
    
    def __cinit__(self):
        self._cpp_wrapper = new CppArrayWrapper[int8_t]()
    
    def __dealloc__(self):
        del self._cpp_wrapper
    
    def __init__(self, size=0):
        if size > 0:
            self._cpp_wrapper.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self._cpp_wrapper.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self._cpp_wrapper.size()
    
    def set_data(self, libcpp_vector[int8_t]& data):
        """Set data by swapping with a C++ vector."""
        self._cpp_wrapper.set_data(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        shape[0] = self._cpp_wrapper.size()
        strides[0] = sizeof(int8_t)
        
        buffer.buf = <char*>self._cpp_wrapper.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(int8_t)
        buffer.readonly = 0
        buffer.format = 'b' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int8_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayWrapperInt16:
    """
    Owning wrapper for std::vector<int16_t> with buffer protocol support.
    
    This class owns its data and can be converted to numpy arrays.
    """
    cdef CppArrayWrapper[int16_t]* _cpp_wrapper
    
    def __cinit__(self):
        self._cpp_wrapper = new CppArrayWrapper[int16_t]()
    
    def __dealloc__(self):
        del self._cpp_wrapper
    
    def __init__(self, size=0):
        if size > 0:
            self._cpp_wrapper.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self._cpp_wrapper.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self._cpp_wrapper.size()
    
    def set_data(self, libcpp_vector[int16_t]& data):
        """Set data by swapping with a C++ vector."""
        self._cpp_wrapper.set_data(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        shape[0] = self._cpp_wrapper.size()
        strides[0] = sizeof(int16_t)
        
        buffer.buf = <char*>self._cpp_wrapper.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(int16_t)
        buffer.readonly = 0
        buffer.format = 'h' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int16_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayWrapperInt32:
    """
    Owning wrapper for std::vector<int32_t> with buffer protocol support.
    
    This class owns its data and can be converted to numpy arrays.
    """
    cdef CppArrayWrapper[int32_t]* _cpp_wrapper
    
    def __cinit__(self):
        self._cpp_wrapper = new CppArrayWrapper[int32_t]()
    
    def __dealloc__(self):
        del self._cpp_wrapper
    
    def __init__(self, size=0):
        if size > 0:
            self._cpp_wrapper.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self._cpp_wrapper.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self._cpp_wrapper.size()
    
    def set_data(self, libcpp_vector[int32_t]& data):
        """Set data by swapping with a C++ vector."""
        self._cpp_wrapper.set_data(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        shape[0] = self._cpp_wrapper.size()
        strides[0] = sizeof(int32_t)
        
        buffer.buf = <char*>self._cpp_wrapper.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(int32_t)
        buffer.readonly = 0
        buffer.format = 'i' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int32_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayWrapperInt64:
    """
    Owning wrapper for std::vector<int64_t> with buffer protocol support.
    
    This class owns its data and can be converted to numpy arrays.
    """
    cdef CppArrayWrapper[int64_t]* _cpp_wrapper
    
    def __cinit__(self):
        self._cpp_wrapper = new CppArrayWrapper[int64_t]()
    
    def __dealloc__(self):
        del self._cpp_wrapper
    
    def __init__(self, size=0):
        if size > 0:
            self._cpp_wrapper.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self._cpp_wrapper.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self._cpp_wrapper.size()
    
    def set_data(self, libcpp_vector[int64_t]& data):
        """Set data by swapping with a C++ vector."""
        self._cpp_wrapper.set_data(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        shape[0] = self._cpp_wrapper.size()
        strides[0] = sizeof(int64_t)
        
        buffer.buf = <char*>self._cpp_wrapper.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(int64_t)
        buffer.readonly = 0
        buffer.format = 'q' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int64_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayWrapperUInt8:
    """
    Owning wrapper for std::vector<uint8_t> with buffer protocol support.
    
    This class owns its data and can be converted to numpy arrays.
    """
    cdef CppArrayWrapper[uint8_t]* _cpp_wrapper
    
    def __cinit__(self):
        self._cpp_wrapper = new CppArrayWrapper[uint8_t]()
    
    def __dealloc__(self):
        del self._cpp_wrapper
    
    def __init__(self, size=0):
        if size > 0:
            self._cpp_wrapper.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self._cpp_wrapper.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self._cpp_wrapper.size()
    
    def set_data(self, libcpp_vector[uint8_t]& data):
        """Set data by swapping with a C++ vector."""
        self._cpp_wrapper.set_data(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        shape[0] = self._cpp_wrapper.size()
        strides[0] = sizeof(uint8_t)
        
        buffer.buf = <char*>self._cpp_wrapper.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(uint8_t)
        buffer.readonly = 0
        buffer.format = 'B' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint8_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayWrapperUInt16:
    """
    Owning wrapper for std::vector<uint16_t> with buffer protocol support.
    
    This class owns its data and can be converted to numpy arrays.
    """
    cdef CppArrayWrapper[uint16_t]* _cpp_wrapper
    
    def __cinit__(self):
        self._cpp_wrapper = new CppArrayWrapper[uint16_t]()
    
    def __dealloc__(self):
        del self._cpp_wrapper
    
    def __init__(self, size=0):
        if size > 0:
            self._cpp_wrapper.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self._cpp_wrapper.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self._cpp_wrapper.size()
    
    def set_data(self, libcpp_vector[uint16_t]& data):
        """Set data by swapping with a C++ vector."""
        self._cpp_wrapper.set_data(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        shape[0] = self._cpp_wrapper.size()
        strides[0] = sizeof(uint16_t)
        
        buffer.buf = <char*>self._cpp_wrapper.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(uint16_t)
        buffer.readonly = 0
        buffer.format = 'H' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint16_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayWrapperUInt32:
    """
    Owning wrapper for std::vector<uint32_t> with buffer protocol support.
    
    This class owns its data and can be converted to numpy arrays.
    """
    cdef CppArrayWrapper[uint32_t]* _cpp_wrapper
    
    def __cinit__(self):
        self._cpp_wrapper = new CppArrayWrapper[uint32_t]()
    
    def __dealloc__(self):
        del self._cpp_wrapper
    
    def __init__(self, size=0):
        if size > 0:
            self._cpp_wrapper.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self._cpp_wrapper.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self._cpp_wrapper.size()
    
    def set_data(self, libcpp_vector[uint32_t]& data):
        """Set data by swapping with a C++ vector."""
        self._cpp_wrapper.set_data(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        shape[0] = self._cpp_wrapper.size()
        strides[0] = sizeof(uint32_t)
        
        buffer.buf = <char*>self._cpp_wrapper.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(uint32_t)
        buffer.readonly = 0
        buffer.format = 'I' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint32_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayWrapperUInt64:
    """
    Owning wrapper for std::vector<uint64_t> with buffer protocol support.
    
    This class owns its data and can be converted to numpy arrays.
    """
    cdef CppArrayWrapper[uint64_t]* _cpp_wrapper
    
    def __cinit__(self):
        self._cpp_wrapper = new CppArrayWrapper[uint64_t]()
    
    def __dealloc__(self):
        del self._cpp_wrapper
    
    def __init__(self, size=0):
        if size > 0:
            self._cpp_wrapper.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self._cpp_wrapper.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self._cpp_wrapper.size()
    
    def set_data(self, libcpp_vector[uint64_t]& data):
        """Set data by swapping with a C++ vector."""
        self._cpp_wrapper.set_data(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        shape[0] = self._cpp_wrapper.size()
        strides[0] = sizeof(uint64_t)
        
        buffer.buf = <char*>self._cpp_wrapper.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(uint64_t)
        buffer.readonly = 0
        buffer.format = 'Q' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint64_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


#############################################################################
# Non-owning View Classes
#############################################################################


cdef class ArrayViewFloat:
    """
    Non-owning view wrapper for float arrays with buffer protocol support.
    
    This class does NOT own its data. The readonly flag controls write access.
    """
    cdef CppArrayView[float]* _cpp_view
    cdef object _owner
    cdef cbool _readonly
    
    def __cinit__(self, float* ptr, size_t size, object owner=None, cbool readonly=False):
        self._cpp_view = new CppArrayView[float](ptr, size, readonly)
        self._owner = owner
        self._readonly = readonly
    
    def __dealloc__(self):
        del self._cpp_view
    
    def size(self):
        """Get the size of the view."""
        return self._cpp_view.size()
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self._readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        if (flags & PyBUF_WRITABLE) and self._readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        shape[0] = self._cpp_view.size()
        strides[0] = sizeof(float)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(float)
        buffer.readonly = 1 if self._readonly else 0
        buffer.format = 'f' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(float)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewDouble:
    """
    Non-owning view wrapper for double arrays with buffer protocol support.
    
    This class does NOT own its data. The readonly flag controls write access.
    """
    cdef CppArrayView[double]* _cpp_view
    cdef object _owner
    cdef cbool _readonly
    
    def __cinit__(self, double* ptr, size_t size, object owner=None, cbool readonly=False):
        self._cpp_view = new CppArrayView[double](ptr, size, readonly)
        self._owner = owner
        self._readonly = readonly
    
    def __dealloc__(self):
        del self._cpp_view
    
    def size(self):
        """Get the size of the view."""
        return self._cpp_view.size()
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self._readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        if (flags & PyBUF_WRITABLE) and self._readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        shape[0] = self._cpp_view.size()
        strides[0] = sizeof(double)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(double)
        buffer.readonly = 1 if self._readonly else 0
        buffer.format = 'd' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(double)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewInt8:
    """
    Non-owning view wrapper for int8_t arrays with buffer protocol support.
    
    This class does NOT own its data. The readonly flag controls write access.
    """
    cdef CppArrayView[int8_t]* _cpp_view
    cdef object _owner
    cdef cbool _readonly
    
    def __cinit__(self, int8_t* ptr, size_t size, object owner=None, cbool readonly=False):
        self._cpp_view = new CppArrayView[int8_t](ptr, size, readonly)
        self._owner = owner
        self._readonly = readonly
    
    def __dealloc__(self):
        del self._cpp_view
    
    def size(self):
        """Get the size of the view."""
        return self._cpp_view.size()
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self._readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        if (flags & PyBUF_WRITABLE) and self._readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        shape[0] = self._cpp_view.size()
        strides[0] = sizeof(int8_t)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(int8_t)
        buffer.readonly = 1 if self._readonly else 0
        buffer.format = 'b' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int8_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewInt16:
    """
    Non-owning view wrapper for int16_t arrays with buffer protocol support.
    
    This class does NOT own its data. The readonly flag controls write access.
    """
    cdef CppArrayView[int16_t]* _cpp_view
    cdef object _owner
    cdef cbool _readonly
    
    def __cinit__(self, int16_t* ptr, size_t size, object owner=None, cbool readonly=False):
        self._cpp_view = new CppArrayView[int16_t](ptr, size, readonly)
        self._owner = owner
        self._readonly = readonly
    
    def __dealloc__(self):
        del self._cpp_view
    
    def size(self):
        """Get the size of the view."""
        return self._cpp_view.size()
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self._readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        if (flags & PyBUF_WRITABLE) and self._readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        shape[0] = self._cpp_view.size()
        strides[0] = sizeof(int16_t)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(int16_t)
        buffer.readonly = 1 if self._readonly else 0
        buffer.format = 'h' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int16_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewInt32:
    """
    Non-owning view wrapper for int32_t arrays with buffer protocol support.
    
    This class does NOT own its data. The readonly flag controls write access.
    """
    cdef CppArrayView[int32_t]* _cpp_view
    cdef object _owner
    cdef cbool _readonly
    
    def __cinit__(self, int32_t* ptr, size_t size, object owner=None, cbool readonly=False):
        self._cpp_view = new CppArrayView[int32_t](ptr, size, readonly)
        self._owner = owner
        self._readonly = readonly
    
    def __dealloc__(self):
        del self._cpp_view
    
    def size(self):
        """Get the size of the view."""
        return self._cpp_view.size()
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self._readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        if (flags & PyBUF_WRITABLE) and self._readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        shape[0] = self._cpp_view.size()
        strides[0] = sizeof(int32_t)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(int32_t)
        buffer.readonly = 1 if self._readonly else 0
        buffer.format = 'i' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int32_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewInt64:
    """
    Non-owning view wrapper for int64_t arrays with buffer protocol support.
    
    This class does NOT own its data. The readonly flag controls write access.
    """
    cdef CppArrayView[int64_t]* _cpp_view
    cdef object _owner
    cdef cbool _readonly
    
    def __cinit__(self, int64_t* ptr, size_t size, object owner=None, cbool readonly=False):
        self._cpp_view = new CppArrayView[int64_t](ptr, size, readonly)
        self._owner = owner
        self._readonly = readonly
    
    def __dealloc__(self):
        del self._cpp_view
    
    def size(self):
        """Get the size of the view."""
        return self._cpp_view.size()
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self._readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        if (flags & PyBUF_WRITABLE) and self._readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        shape[0] = self._cpp_view.size()
        strides[0] = sizeof(int64_t)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(int64_t)
        buffer.readonly = 1 if self._readonly else 0
        buffer.format = 'q' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int64_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewUInt8:
    """
    Non-owning view wrapper for uint8_t arrays with buffer protocol support.
    
    This class does NOT own its data. The readonly flag controls write access.
    """
    cdef CppArrayView[uint8_t]* _cpp_view
    cdef object _owner
    cdef cbool _readonly
    
    def __cinit__(self, uint8_t* ptr, size_t size, object owner=None, cbool readonly=False):
        self._cpp_view = new CppArrayView[uint8_t](ptr, size, readonly)
        self._owner = owner
        self._readonly = readonly
    
    def __dealloc__(self):
        del self._cpp_view
    
    def size(self):
        """Get the size of the view."""
        return self._cpp_view.size()
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self._readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        if (flags & PyBUF_WRITABLE) and self._readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        shape[0] = self._cpp_view.size()
        strides[0] = sizeof(uint8_t)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(uint8_t)
        buffer.readonly = 1 if self._readonly else 0
        buffer.format = 'B' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint8_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewUInt16:
    """
    Non-owning view wrapper for uint16_t arrays with buffer protocol support.
    
    This class does NOT own its data. The readonly flag controls write access.
    """
    cdef CppArrayView[uint16_t]* _cpp_view
    cdef object _owner
    cdef cbool _readonly
    
    def __cinit__(self, uint16_t* ptr, size_t size, object owner=None, cbool readonly=False):
        self._cpp_view = new CppArrayView[uint16_t](ptr, size, readonly)
        self._owner = owner
        self._readonly = readonly
    
    def __dealloc__(self):
        del self._cpp_view
    
    def size(self):
        """Get the size of the view."""
        return self._cpp_view.size()
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self._readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        if (flags & PyBUF_WRITABLE) and self._readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        shape[0] = self._cpp_view.size()
        strides[0] = sizeof(uint16_t)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(uint16_t)
        buffer.readonly = 1 if self._readonly else 0
        buffer.format = 'H' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint16_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewUInt32:
    """
    Non-owning view wrapper for uint32_t arrays with buffer protocol support.
    
    This class does NOT own its data. The readonly flag controls write access.
    """
    cdef CppArrayView[uint32_t]* _cpp_view
    cdef object _owner
    cdef cbool _readonly
    
    def __cinit__(self, uint32_t* ptr, size_t size, object owner=None, cbool readonly=False):
        self._cpp_view = new CppArrayView[uint32_t](ptr, size, readonly)
        self._owner = owner
        self._readonly = readonly
    
    def __dealloc__(self):
        del self._cpp_view
    
    def size(self):
        """Get the size of the view."""
        return self._cpp_view.size()
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self._readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        if (flags & PyBUF_WRITABLE) and self._readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        shape[0] = self._cpp_view.size()
        strides[0] = sizeof(uint32_t)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(uint32_t)
        buffer.readonly = 1 if self._readonly else 0
        buffer.format = 'I' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint32_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ArrayViewUInt64:
    """
    Non-owning view wrapper for uint64_t arrays with buffer protocol support.
    
    This class does NOT own its data. The readonly flag controls write access.
    """
    cdef CppArrayView[uint64_t]* _cpp_view
    cdef object _owner
    cdef cbool _readonly
    
    def __cinit__(self, uint64_t* ptr, size_t size, object owner=None, cbool readonly=False):
        self._cpp_view = new CppArrayView[uint64_t](ptr, size, readonly)
        self._owner = owner
        self._readonly = readonly
    
    def __dealloc__(self):
        del self._cpp_view
    
    def size(self):
        """Get the size of the view."""
        return self._cpp_view.size()
    
    def is_readonly(self):
        """Check if this is a readonly view."""
        return self._readonly
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        if (flags & PyBUF_WRITABLE) and self._readonly:
            raise BufferError("Cannot create writable buffer from readonly view")
        
        shape[0] = self._cpp_view.size()
        strides[0] = sizeof(uint64_t)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(uint64_t)
        buffer.readonly = 1 if self._readonly else 0
        buffer.format = 'Q' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(uint64_t)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass

