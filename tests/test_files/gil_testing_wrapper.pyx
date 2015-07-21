#cython: c_string_encoding=ascii  # for cython>=0.19
from  libcpp.string  cimport string as libcpp_string
from  libcpp.set     cimport set as libcpp_set
from  libcpp.vector  cimport vector as libcpp_vector
from  libcpp.pair    cimport pair as libcpp_pair
from  libcpp.map     cimport map  as libcpp_map
from  smart_ptr cimport shared_ptr
from  AutowrapRefHolder cimport AutowrapRefHolder
from  libcpp cimport bool
from  libc.string cimport const_char
from cython.operator cimport dereference as deref, preincrement as inc, address as address
from gil_testing cimport GilTesting as _GilTesting
cdef extern from "autowrap_tools.hpp":
    char * _cast_const_away(char *) 

cdef class GilTesting:

    cdef shared_ptr[_GilTesting] inst

    def __dealloc__(self):
         self.inst.reset()

    
    def do_something(self, bytes in_0 ):
        assert isinstance(in_0, bytes), 'arg in_0 wrong type'
        cdef const_char * input_in_0 = <const_char *> in_0
        with nogil:
            self.inst.get().do_something(input_in_0)
    
    def get_greetings(self):
        cdef const_char  * _r = _cast_const_away(self.inst.get().get_greetings())
        py_result = <const_char *>(_r)
        return py_result
    
    def __init__(self, bytes in_0 ):
        assert isinstance(in_0, bytes), 'arg in_0 wrong type'
        cdef const_char * input_in_0 = <const_char *> in_0
        self.inst = shared_ptr[_GilTesting](new _GilTesting(input_in_0)) 
