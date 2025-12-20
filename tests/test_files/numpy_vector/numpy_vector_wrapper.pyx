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
from  libcpp.pair     cimport pair as libcpp_pair
from  libcpp.map      cimport map  as libcpp_map
from  libcpp.unordered_map cimport unordered_map as libcpp_unordered_map
from  libcpp.unordered_set cimport unordered_set as libcpp_unordered_set
from  libcpp.deque    cimport deque as libcpp_deque
from  libcpp.list     cimport list as libcpp_list
from  libcpp.optional cimport optional as libcpp_optional
from  libcpp.string_view cimport string_view as libcpp_string_view
from  libcpp          cimport bool
from  libc.string     cimport const_char
from  cython.operator cimport dereference as deref, preincrement as inc, address as address
from  AutowrapRefHolder      cimport AutowrapRefHolder
from  AutowrapPtrHolder      cimport AutowrapPtrHolder
from  AutowrapConstPtrHolder cimport AutowrapConstPtrHolder
from  libcpp.memory   cimport shared_ptr
cimport numpy as np
import numpy as np
cimport numpy as numpy
import numpy as numpy
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
    
    def sumVector(self, object data ):
        """
        sumVector(self, data: numpy.ndarray ) -> float
        """
        assert (isinstance(data, numpy.ndarray) or hasattr(data, '__len__')), 'arg data wrong type'
        # Convert 1D numpy array to C++ vector
        cdef object data_arr = numpy.asarray(data, dtype=numpy.float64)
        cdef libcpp_vector[double] * v0 = new libcpp_vector[double]()
        cdef size_t i_0
        v0.reserve(data_arr.shape[0])
        for i_0 in range(data_arr.shape[0]):
            v0.push_back(<double>data_arr[i_0])
        cdef double _r = self.inst.get().sumVector(deref(v0))
        del v0
        py_result = <double>_r
        return py_result
    
    def createVector(self,  size ):
        """
        createVector(self, size: int ) -> numpy.ndarray
        """
        assert isinstance(size, int) and size >= 0, 'arg size wrong type'
    
        _r = self.inst.get().createVector((<size_t>size))
        # Convert C++ vector to 1D numpy array
        cdef size_t n_py_result = _r.size()
        cdef object py_result = numpy.empty(n_py_result, dtype=numpy.float64)
        cdef size_t i_py_result
        for i_py_result in range(n_py_result):
            py_result[i_py_result] = <double>_r[i_py_result]
        return py_result
    
    def multiplyVector(self, object data , double factor ):
        """
        multiplyVector(self, data: numpy.ndarray , factor: float ) -> None
        """
        assert (isinstance(data, numpy.ndarray) or hasattr(data, '__len__')), 'arg data wrong type'
        assert isinstance(factor, float), 'arg factor wrong type'
        # Convert 1D numpy array to C++ vector
        cdef object data_arr = numpy.asarray(data, dtype=numpy.float64)
        cdef libcpp_vector[double] * v0 = new libcpp_vector[double]()
        cdef size_t i_0
        v0.reserve(data_arr.shape[0])
        for i_0 in range(data_arr.shape[0]):
            v0.push_back(<double>data_arr[i_0])
    
        self.inst.get().multiplyVector(deref(v0), (<double>factor))
        del v0
    
    def sumIntVector(self, object data ):
        """
        sumIntVector(self, data: numpy.ndarray ) -> int
        """
        assert (isinstance(data, numpy.ndarray) or hasattr(data, '__len__')), 'arg data wrong type'
        # Convert 1D numpy array to C++ vector
        cdef object data_arr = numpy.asarray(data, dtype=numpy.int32)
        cdef libcpp_vector[int] * v0 = new libcpp_vector[int]()
        cdef size_t i_0
        v0.reserve(data_arr.shape[0])
        for i_0 in range(data_arr.shape[0]):
            v0.push_back(<int>data_arr[i_0])
        cdef int _r = self.inst.get().sumIntVector(deref(v0))
        del v0
        py_result = <int>_r
        return py_result
    
    def createFloatVector(self,  size ):
        """
        createFloatVector(self, size: int ) -> numpy.ndarray
        """
        assert isinstance(size, int) and size >= 0, 'arg size wrong type'
    
        _r = self.inst.get().createFloatVector((<size_t>size))
        # Convert C++ vector to 1D numpy array
        cdef size_t n_py_result = _r.size()
        cdef object py_result = numpy.empty(n_py_result, dtype=numpy.float32)
        cdef size_t i_py_result
        for i_py_result in range(n_py_result):
            py_result[i_py_result] = <float>_r[i_py_result]
        return py_result
    
    def create2DVector(self,  rows ,  cols ):
        """
        create2DVector(self, rows: int , cols: int ) -> numpy.ndarray
        """
        assert isinstance(rows, int) and rows >= 0, 'arg rows wrong type'
        assert isinstance(cols, int) and cols >= 0, 'arg cols wrong type'
    
    
        _r = self.inst.get().create2DVector((<size_t>rows), (<size_t>cols))
        # Convert nested C++ vector to 2D numpy array
        cdef size_t n_rows = _r.size()
        cdef size_t n_cols = _r[0].size() if n_rows > 0 else 0
        cdef object py_result = numpy.empty((n_rows, n_cols), dtype=numpy.float64)
        cdef size_t i, j
        for i in range(n_rows):
            for j in range(n_cols):
                py_result[i, j] = <double>_r[i][j]
        return py_result
    
    def sum2DVector(self, object data ):
        """
        sum2DVector(self, data: numpy.ndarray ) -> float
        """
        assert (isinstance(data, numpy.ndarray) or (hasattr(data, '__len__') and len(data) > 0 and hasattr(data[0], '__len__'))), 'arg data wrong type'
        # Convert 2D numpy array to nested C++ vector
        cdef object data_arr = numpy.asarray(data, dtype=numpy.float64)
        cdef libcpp_vector[libcpp_vector[double]] * v0 = new libcpp_vector[libcpp_vector[double]]()
        cdef size_t i_0, j_0
        cdef libcpp_vector[double] row_0
        for i_0 in range(data_arr.shape[0]):
            row_0 = libcpp_vector[double]()
            for j_0 in range(data_arr.shape[1]):
                row_0.push_back(<double>data_arr[i_0, j_0])
            v0.push_back(row_0)
        cdef double _r = self.inst.get().sum2DVector(deref(v0))
        del v0
        py_result = <double>_r
        return py_result 
