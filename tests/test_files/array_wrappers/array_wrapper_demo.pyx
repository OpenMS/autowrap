# cython: language_level=3
# cython: embedsignature=True
"""
Demonstration of using ArrayWrapper and ArrayView classes.

This shows the recommended patterns for:
1. Returning owning wrappers for value/copy returns
2. Returning views for reference returns
3. Using const views for read-only access
"""

from libcpp.vector cimport vector as libcpp_vector
from libcpp.memory cimport shared_ptr
cimport numpy as np
import numpy as np

# Import the C++ test class
from array_wrapper_test cimport ArrayWrapperTest as _ArrayWrapperTest

# Import the array wrapper classes
import sys
sys.path.insert(0, '/home/runner/work/autowrap/autowrap/autowrap/data_files/autowrap')

# We'll use these wrapper classes (they would be compiled separately)
# For now, we'll demonstrate the pattern


cdef class ArrayWrapperTestPython:
    """
    Python wrapper for ArrayWrapperTest that demonstrates proper usage
    of ArrayWrapper and ArrayView classes.
    """
    cdef shared_ptr[_ArrayWrapperTest] inst
    
    def __init__(self):
        self.inst = shared_ptr[_ArrayWrapperTest](new _ArrayWrapperTest())
    
    def get_data_copy_as_array(self, size_t size):
        """
        Get a copy of data as numpy array (owning wrapper pattern).
        
        This demonstrates the pattern for functions that return by value.
        The data is copied into a Python-owned numpy array.
        """
        cdef libcpp_vector[double] cpp_data = self.inst.get().getDataCopy(size)
        
        # Convert to numpy array (copy)
        cdef size_t n = cpp_data.size()
        cdef np.ndarray[np.float64_t, ndim=1] result = np.empty(n, dtype=np.float64)
        
        if n > 0:
            for i in range(n):
                result[i] = cpp_data[i]
        
        return result
    
    def get_const_ref_as_array(self):
        """
        Get const reference data as numpy array (read-only copy).
        
        Since the data is const, we make a copy to avoid lifetime issues.
        For a true view, we would use ConstArrayView wrapper.
        """
        cdef const libcpp_vector[double]& cpp_data = self.inst.get().getConstRefData()
        
        # Convert to numpy array (copy for safety)
        cdef size_t n = cpp_data.size()
        cdef np.ndarray[np.float64_t, ndim=1] result = np.empty(n, dtype=np.float64)
        
        if n > 0:
            for i in range(n):
                result[i] = cpp_data[i]
        
        return result
    
    def get_mutable_ref_as_array(self):
        """
        Get mutable reference data as numpy array (writable copy).
        
        For true zero-copy views, this would use ArrayView wrapper
        with proper lifetime management (keeping self alive).
        For now, we copy for safety.
        """
        cdef libcpp_vector[double]& cpp_data = self.inst.get().getMutableRefData()
        
        # Convert to numpy array (copy for safety)
        cdef size_t n = cpp_data.size()
        cdef np.ndarray[np.float64_t, ndim=1] result = np.empty(n, dtype=np.float64)
        
        if n > 0:
            for i in range(n):
                result[i] = cpp_data[i]
        
        return result
    
    def sum_internal_data(self):
        """Get sum of internal data (to verify modifications)."""
        return self.inst.get().sumInternalData()
    
    def sum_float_data(self):
        """Get sum of float data."""
        return self.inst.get().sumFloatData()
    
    def sum_int_data(self):
        """Get sum of int data."""
        return self.inst.get().sumIntData()
