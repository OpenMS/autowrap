#Generated with autowrap 0.23.0 and Cython (Parser) 3.2.1
#cython: c_string_encoding=ascii
#cython: embedsignature=False
from  enum            import Enum as _PyEnum
from  cpython         cimport Py_buffer
from  cpython         cimport bool as pybool_t
from  libcpp.string   cimport string as libcpp_string
from  libcpp.string   cimport string as libcpp_utf8_string
from  libcpp.string   cimport string as libcpp_utf8_output_string
from  libcpp.set      cimport set as libcpp_set
from  libcpp.vector   cimport vector as libcpp_vector
from  libcpp.pair     cimport pair as libcpp_pair
from  libcpp.map      cimport map  as libcpp_map
from  libcpp          cimport bool
from  libc.string     cimport const_char
from  cython.operator cimport dereference as deref, preincrement as inc, address as address
from  AutowrapRefHolder      cimport AutowrapRefHolder
from  AutowrapPtrHolder      cimport AutowrapPtrHolder
from  AutowrapConstPtrHolder cimport AutowrapConstPtrHolder
from  smart_ptr       cimport shared_ptr
from inherited cimport Base as _Base
from inherited cimport Base as _Base
from inherited cimport BaseZ as _BaseZ
from inherited cimport Inherited as _Inherited
from inherited cimport InheritedTwo as _InheritedTwo

cdef extern from "autowrap_tools.hpp":
    char * _cast_const_away(char *) 

cdef class BaseDouble:
    """
    Cython implementation of _Base[double]
    """

    cdef shared_ptr[_Base[double]] inst

    def __dealloc__(self):
         self.inst.reset()

    
    property a:
        def __set__(self, double a):
        
            self.inst.get().a = (<double>a)
        
    
        def __get__(self):
            cdef double _r = self.inst.get().a
            py_result = <double>_r
            return py_result
    
    def __init__(self):
        """
        __init__(self) -> None
        """
        self.inst = shared_ptr[_Base[double]](new _Base[double]())
    
    def foo(self):
        """
        foo(self) -> float
        """
        cdef double _r = self.inst.get().foo()
        py_result = <double>_r
        return py_result 

cdef class BaseInt:
    """
    Cython implementation of _Base[int]
    """

    cdef shared_ptr[_Base[int]] inst

    def __dealloc__(self):
         self.inst.reset()

    
    property a:
        def __set__(self, int a):
        
            self.inst.get().a = (<int>a)
        
    
        def __get__(self):
            cdef int _r = self.inst.get().a
            py_result = <int>_r
            return py_result
    
    def __init__(self):
        """
        __init__(self) -> None
        """
        self.inst = shared_ptr[_Base[int]](new _Base[int]())
    
    def foo(self):
        """
        foo(self) -> int
        """
        cdef int _r = self.inst.get().foo()
        py_result = <int>_r
        return py_result 

cdef class BaseZ:
    """
    Cython implementation of _BaseZ
    """

    cdef shared_ptr[_BaseZ] inst

    def __dealloc__(self):
         self.inst.reset()

    
    property a:
        def __set__(self, int a):
        
            self.inst.get().a = (<int>a)
        
    
        def __get__(self):
            cdef int _r = self.inst.get().a
            py_result = <int>_r
            return py_result
    
    def __init__(self):
        """
        __init__(self) -> None
        """
        self.inst = shared_ptr[_BaseZ](new _BaseZ())
    
    def bar(self):
        """
        bar(self) -> int
        """
        cdef int _r = self.inst.get().bar()
        py_result = <int>_r
        return py_result 

cdef class InheritedInt:
    """
    Cython implementation of _Inherited[int]
      -- Inherits from ['Base[A]', 'BaseZ']
    """

    cdef shared_ptr[_Inherited[int]] inst

    def __dealloc__(self):
         self.inst.reset()

    
    def __init__(self):
        """
        __init__(self) -> None
        """
        self.inst = shared_ptr[_Inherited[int]](new _Inherited[int]())
    
    def getBase(self):
        """
        getBase(self) -> int
        """
        cdef int _r = self.inst.get().getBase()
        py_result = <int>_r
        return py_result
    
    def getBaseZ(self):
        """
        getBaseZ(self) -> int
        """
        cdef int _r = self.inst.get().getBaseZ()
        py_result = <int>_r
        return py_result
    
    def foo(self):
        """
        foo(self) -> int
        """
        cdef int _r = self.inst.get().foo()
        py_result = <int>_r
        return py_result
    
    def bar(self):
        """
        bar(self) -> int
        """
        cdef int _r = self.inst.get().bar()
        py_result = <int>_r
        return py_result 

cdef class InheritedIntDbl:
    """
    Cython implementation of _InheritedTwo[int,double]
      -- Inherits from ['BaseZ']
    """

    cdef shared_ptr[_InheritedTwo[int,double]] inst

    def __dealloc__(self):
         self.inst.reset()

    
    def __init__(self):
        """
        __init__(self) -> None
        """
        self.inst = shared_ptr[_InheritedTwo[int,double]](new _InheritedTwo[int,double]())
    
    def getBase(self):
        """
        getBase(self) -> int
        """
        cdef int _r = self.inst.get().getBase()
        py_result = <int>_r
        return py_result
    
    def getBaseB(self):
        """
        getBaseB(self) -> float
        """
        cdef double _r = self.inst.get().getBaseB()
        py_result = <double>_r
        return py_result
    
    def getBaseZ(self):
        """
        getBaseZ(self) -> int
        """
        cdef int _r = self.inst.get().getBaseZ()
        py_result = <int>_r
        return py_result
    
    def bar(self):
        """
        bar(self) -> int
        """
        cdef int _r = self.inst.get().bar()
        py_result = <int>_r
        return py_result 
