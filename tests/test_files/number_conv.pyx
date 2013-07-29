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
from number_conv cimport add_max_float as _add_max_float_number_conv
from number_conv cimport pass_full_precision as _pass_full_precision_number_conv
from number_conv cimport pass_full_precision_vec as _pass_full_precision_vec_number_conv
cdef extern from "autowrap_tools.hpp":
    char * _cast_const_away(char *)

def add_max_float(double in_0 ):
    assert isinstance(in_0, float), 'arg in_0 wrong type'

    cdef double _r = _add_max_float_number_conv((<double>in_0))
    py_result = <double>_r
    return py_result

def pass_full_precision(double in_0 ):
    assert isinstance(in_0, float), 'arg in_0 wrong type'

    cdef double _r = _pass_full_precision_number_conv((<double>in_0))
    py_result = <double>_r
    return py_result

def pass_full_precision_vec(list in_0 ):
    assert isinstance(in_0, list) and all(isinstance(elemt_rec, float) for elemt_rec in in_0), 'arg in_0 wrong type'
    cdef libcpp_vector[double] v0 = in_0
    _r = _pass_full_precision_vec_number_conv(v0)
    in_0[:] = v0
    cdef list py_result = _r
    return py_result 

