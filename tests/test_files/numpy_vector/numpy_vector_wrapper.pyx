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
from ArrayWrappers cimport (
    ArrayWrapperFloat, ArrayWrapperDouble,
    ArrayWrapperInt8, ArrayWrapperInt16, ArrayWrapperInt32, ArrayWrapperInt64,
    ArrayWrapperUInt8, ArrayWrapperUInt16, ArrayWrapperUInt32, ArrayWrapperUInt64,
    ArrayViewFloat, ArrayViewDouble,
    ArrayViewInt8, ArrayViewInt16, ArrayViewInt32, ArrayViewInt64,
    ArrayViewUInt8, ArrayViewUInt16, ArrayViewUInt32, ArrayViewUInt64,
    _create_view_float, _create_view_double,
    _create_view_int8, _create_view_int16, _create_view_int32, _create_view_int64,
    _create_view_uint8, _create_view_uint16, _create_view_uint32, _create_view_uint64
)
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
        # Convert C++ vector reference to numpy array VIEW (zero-copy)
        cdef double* _ptr_py_result = _r.data()
        cdef size_t _size_py_result = _r.size()
        cdef ArrayViewDouble _view_py_result = _create_view_double(
            _ptr_py_result,
            _size_py_result,
            owner=self,
            readonly=True
        )
        cdef object py_result = numpy.asarray(_view_py_result)
        py_result.base = _view_py_result
        return py_result
    
    def getMutableRefVector(self):
        """
        getMutableRefVector(self) -> numpy.ndarray[numpy.float64_t, ndim=1]
        """
        _r = self.inst.get().getMutableRefVector()
        # Convert C++ vector reference to numpy array VIEW (zero-copy)
        cdef double* _ptr_py_result = _r.data()
        cdef size_t _size_py_result = _r.size()
        cdef ArrayViewDouble _view_py_result = _create_view_double(
            _ptr_py_result,
            _size_py_result,
            owner=self,
            readonly=False
        )
        cdef object py_result = numpy.asarray(_view_py_result)
        py_result.base = _view_py_result
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
        py_result.base = _wrapper_py_result
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
        py_result.base = _wrapper_py_result
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
