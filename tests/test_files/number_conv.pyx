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
from number_conv cimport add_max_float as _add_max_float_number_conv
cdef extern from "autowrap_tools.hpp":
    char * _cast_const_away(char *)

def add_max_float(float in_0 ):
    assert isinstance(in_0, float), 'arg in_0 wrong type'

    cdef double _r = _add_max_float_number_conv((<double>in_0))
    py_result = <double>_r
    return py_result 

