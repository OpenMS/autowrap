# cython: language_level=3
# cython: embedsignature=True
"""
Generic array wrapper classes with buffer protocol support.

This module provides:
- ArrayWrapperFloat/Double/Int: Owning wrappers that manage their own data
- ArrayViewFloat/Double/Int: Non-owning views into existing data
- ConstArrayViewFloat/Double/Int: Read-only views into existing data

These classes implement the Python buffer protocol, allowing them to be
used with numpy and other buffer-aware Python libraries without copying data.
"""

from cpython.buffer cimport PyBUF_FORMAT, PyBUF_ND, PyBUF_STRIDES, PyBUF_WRITABLE
from cpython cimport Py_buffer
from libcpp.vector cimport vector as libcpp_vector
from libcpp cimport bool as cbool
cimport cython

# Import the C++ classes
from ArrayWrapper cimport ArrayWrapper as CppArrayWrapper
from ArrayWrapper cimport ArrayView as CppArrayView
from ArrayWrapper cimport ConstArrayView as CppConstArrayView

# Define fused types for numeric types
ctypedef fused numeric_type:
    float
    double
    int
    long

#############################################################################
# Owning Wrapper Classes
#############################################################################

cdef class ArrayWrapperFloat:
    """
    Owning wrapper for std::vector<float> with buffer protocol support.
    
    This class owns its data and can be converted to numpy arrays.
    The numpy array will be a view into this wrapper's data, so the
    wrapper must be kept alive while the numpy array is in use.
    
    Example:
        wrapper = ArrayWrapperFloat(size=10)
        arr = np.asarray(wrapper)
        arr.base = wrapper  # Keep wrapper alive
    """
    cdef CppArrayWrapper[float]* _cpp_wrapper
    
    def __cinit__(self):
        self._cpp_wrapper = new CppArrayWrapper[float]()
    
    def __dealloc__(self):
        del self._cpp_wrapper
    
    def __init__(self, size=0):
        """
        Initialize with optional size.
        
        Args:
            size: Initial size of the array (default: 0)
        """
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
        """
        Initialize with optional size.
        
        Args:
            size: Initial size of the array (default: 0)
        """
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


cdef class ArrayWrapperInt:
    """
    Owning wrapper for std::vector<int> with buffer protocol support.
    
    This class owns its data and can be converted to numpy arrays.
    """
    cdef CppArrayWrapper[int]* _cpp_wrapper
    
    def __cinit__(self):
        self._cpp_wrapper = new CppArrayWrapper[int]()
    
    def __dealloc__(self):
        del self._cpp_wrapper
    
    def __init__(self, size=0):
        """
        Initialize with optional size.
        
        Args:
            size: Initial size of the array (default: 0)
        """
        if size > 0:
            self._cpp_wrapper.resize(size)
    
    def resize(self, size_t new_size):
        """Resize the array."""
        self._cpp_wrapper.resize(new_size)
    
    def size(self):
        """Get the current size."""
        return self._cpp_wrapper.size()
    
    def set_data(self, libcpp_vector[int]& data):
        """Set data by swapping with a C++ vector."""
        self._cpp_wrapper.set_data(data)
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        shape[0] = self._cpp_wrapper.size()
        strides[0] = sizeof(int)
        
        buffer.buf = <char*>self._cpp_wrapper.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(int)
        buffer.readonly = 0
        buffer.format = 'i' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


#############################################################################
# Non-owning View Classes
#############################################################################

cdef class ArrayViewFloat:
    """
    Non-owning view wrapper for float arrays with buffer protocol support.
    
    This class does NOT own its data. It holds a pointer to existing data
    and an owner reference to keep the data alive.
    
    Example:
        # Create a view of internal C++ data
        view = ArrayViewFloat(ptr, size, owner=cpp_obj, readonly=False)
        arr = np.asarray(view)
        arr.base = view  # Keep view (and owner) alive
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
    
    This class does NOT own its data.
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


cdef class ArrayViewInt:
    """
    Non-owning view wrapper for int arrays with buffer protocol support.
    
    This class does NOT own its data.
    """
    cdef CppArrayView[int]* _cpp_view
    cdef object _owner
    cdef cbool _readonly
    
    def __cinit__(self, int* ptr, size_t size, object owner=None, cbool readonly=False):
        self._cpp_view = new CppArrayView[int](ptr, size, readonly)
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
        strides[0] = sizeof(int)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(int)
        buffer.readonly = 1 if self._readonly else 0
        buffer.format = 'i' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


#############################################################################
# Const (Read-only) View Classes
#############################################################################

cdef class ConstArrayViewFloat:
    """
    Const (read-only) view wrapper for float arrays with buffer protocol support.
    
    This class provides read-only access to existing data.
    """
    cdef CppConstArrayView[float]* _cpp_view
    cdef object _owner
    
    def __cinit__(self, const float* ptr, size_t size, object owner=None):
        self._cpp_view = new CppConstArrayView[float](ptr, size)
        self._owner = owner
    
    def __dealloc__(self):
        del self._cpp_view
    
    def size(self):
        """Get the size of the view."""
        return self._cpp_view.size()
    
    def is_readonly(self):
        """Always returns True."""
        return True
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        if flags & PyBUF_WRITABLE:
            raise BufferError("Cannot create writable buffer from const view")
        
        shape[0] = self._cpp_view.size()
        strides[0] = sizeof(float)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(float)
        buffer.readonly = 1
        buffer.format = 'f' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(float)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ConstArrayViewDouble:
    """
    Const (read-only) view wrapper for double arrays with buffer protocol support.
    
    This class provides read-only access to existing data.
    """
    cdef CppConstArrayView[double]* _cpp_view
    cdef object _owner
    
    def __cinit__(self, const double* ptr, size_t size, object owner=None):
        self._cpp_view = new CppConstArrayView[double](ptr, size)
        self._owner = owner
    
    def __dealloc__(self):
        del self._cpp_view
    
    def size(self):
        """Get the size of the view."""
        return self._cpp_view.size()
    
    def is_readonly(self):
        """Always returns True."""
        return True
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        if flags & PyBUF_WRITABLE:
            raise BufferError("Cannot create writable buffer from const view")
        
        shape[0] = self._cpp_view.size()
        strides[0] = sizeof(double)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(double)
        buffer.readonly = 1
        buffer.format = 'd' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(double)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class ConstArrayViewInt:
    """
    Const (read-only) view wrapper for int arrays with buffer protocol support.
    
    This class provides read-only access to existing data.
    """
    cdef CppConstArrayView[int]* _cpp_view
    cdef object _owner
    
    def __cinit__(self, const int* ptr, size_t size, object owner=None):
        self._cpp_view = new CppConstArrayView[int](ptr, size)
        self._owner = owner
    
    def __dealloc__(self):
        del self._cpp_view
    
    def size(self):
        """Get the size of the view."""
        return self._cpp_view.size()
    
    def is_readonly(self):
        """Always returns True."""
        return True
    
    def __getbuffer__(self, Py_buffer *buffer, int flags):
        cdef Py_ssize_t[1] shape
        cdef Py_ssize_t[1] strides
        
        if flags & PyBUF_WRITABLE:
            raise BufferError("Cannot create writable buffer from const view")
        
        shape[0] = self._cpp_view.size()
        strides[0] = sizeof(int)
        
        buffer.buf = <char*>self._cpp_view.data()
        buffer.obj = self
        buffer.len = shape[0] * sizeof(int)
        buffer.readonly = 1
        buffer.format = 'i' if (flags & PyBUF_FORMAT) else NULL
        buffer.ndim = 1
        buffer.shape = shape if (flags & PyBUF_ND) else NULL
        buffer.strides = strides if (flags & PyBUF_STRIDES) else NULL
        buffer.suboffsets = NULL
        buffer.itemsize = sizeof(int)
        buffer.internal = NULL
    
    def __releasebuffer__(self, Py_buffer *buffer):
        pass
