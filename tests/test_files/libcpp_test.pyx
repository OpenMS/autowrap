from  libcpp.string  cimport string as libcpp_string
from  libcpp.vector  cimport vector as libcpp_vector
from  libcpp.pair    cimport pair as libcpp_pair
from  libcpp cimport bool
from  libc.stdint  cimport *
from  libc.stddef  cimport *
from smart_ptr cimport shared_ptr
cimport numpy as np
import numpy as np
from cython.operator cimport dereference as deref, preincrement as inc, address as address
from libcpp_test cimport LibCppTest as _LibCppTest
cdef extern from "autowrap_tools.hpp":
    char * _cast_const_away(char *) 
cdef class LibCppTest:
    cdef shared_ptr[_LibCppTest] inst
    def __dealloc__(self):
         self.inst.reset()
    def process5(self, list in_0 ):
        assert isinstance(in_0, list) and len(in_0) == 2 and isinstance(in_0[0], LibCppTest) and isinstance(in_0[1], LibCppTest), 'arg in_0 invalid'
        cdef libcpp_pair[_LibCppTest, _LibCppTest] v0
        v0.first = deref((<LibCppTest>in_0[0]).inst.get())
        v0.second = deref((<LibCppTest>in_0[1]).inst.get())
        _r = self.inst.get().process5(v0)
        cdef LibCppTest temp1 = LibCppTest.__new__(LibCppTest)
        temp1.inst = shared_ptr[_LibCppTest](new _LibCppTest(v0.first))
        cdef LibCppTest temp2 = LibCppTest.__new__(LibCppTest)
        temp2.inst = shared_ptr[_LibCppTest](new _LibCppTest(v0.second))
        in_0[:] = [temp1, temp2]
        cdef LibCppTest out1 = LibCppTest.__new__(LibCppTest)
        out1.inst = shared_ptr[_LibCppTest](new _LibCppTest(_r.first))
        cdef LibCppTest out2 = LibCppTest.__new__(LibCppTest)
        out2.inst = shared_ptr[_LibCppTest](new _LibCppTest(_r.second))
        cdef list py_result = [out1, out2]
        return py_result
    def get(self):
        cdef int _r = self.inst.get().get()
        py_result = <int>_r
        return py_result
    def process(self, list in_0 ):
        assert isinstance(in_0, list) and all(isinstance(li, int) for li in in_0), 'arg in_0 invalid'
        cdef libcpp_vector[int] v0 = in_0
        _r = self.inst.get().process(v0)
        in_0[:] = v0
        cdef list py_result = _r
        return py_result
    def twist(self, list in_0 ):
        assert isinstance(in_0, list) and len(in_0) == 2 and isinstance(in_0[0], str) and isinstance(in_0[1], int), 'arg in_0 invalid'
        cdef libcpp_pair[libcpp_string, int] v0
        v0.first = in_0[0]
        v0.second = in_0[1]
        _r = self.inst.get().twist(v0)
        cdef list py_result = [_r.first, _r.second]
        return py_result
    def process4(self, list in_0 ):
        assert isinstance(in_0, list) and len(in_0) == 2 and isinstance(in_0[0], int) and isinstance(in_0[1], LibCppTest), 'arg in_0 invalid'
        cdef libcpp_pair[int, _LibCppTest] v0
        v0.first = in_0[0]
        v0.second = deref((<LibCppTest>in_0[1]).inst.get())
        _r = self.inst.get().process4(v0)
        cdef LibCppTest temp2 = LibCppTest.__new__(LibCppTest)
        temp2.inst = shared_ptr[_LibCppTest](new _LibCppTest(v0.second))
        in_0[:] = [v0.first, temp2]
        cdef LibCppTest out2 = LibCppTest.__new__(LibCppTest)
        out2.inst = shared_ptr[_LibCppTest](new _LibCppTest(_r.second))
        cdef list py_result = [_r.first, out2]
        return py_result
    def process3(self, list in_0 ):
        assert isinstance(in_0, list) and len(in_0) == 2 and isinstance(in_0[0], LibCppTest) and isinstance(in_0[1], int), 'arg in_0 invalid'
        cdef libcpp_pair[_LibCppTest, int] v0
        v0.first = deref((<LibCppTest>in_0[0]).inst.get())
        v0.second = in_0[1]
        _r = self.inst.get().process3(v0)
        cdef LibCppTest temp1 = LibCppTest.__new__(LibCppTest)
        temp1.inst = shared_ptr[_LibCppTest](new _LibCppTest(v0.first))
        in_0[:] = [temp1, v0.second]
        cdef LibCppTest out1 = LibCppTest.__new__(LibCppTest)
        out1.inst = shared_ptr[_LibCppTest](new _LibCppTest(_r.first))
        cdef list py_result = [out1, _r.second]
        return py_result
    def process2(self, list in_0 ):
        assert isinstance(in_0, list) and len(in_0) == 2 and isinstance(in_0[0], int) and isinstance(in_0[1], int), 'arg in_0 invalid'
        cdef libcpp_pair[int, int] v0
        v0.first = in_0[0]
        v0.second = in_0[1]
        _r = self.inst.get().process2(v0)
        in_0[:] = [v0.first, v0.second]
        cdef list py_result = [_r.first, _r.second]
        return py_result
    def _init_0(self):
        self.inst = shared_ptr[_LibCppTest](new _LibCppTest())
    def _init_1(self, int ii ):
        assert isinstance(ii, int), 'arg ii invalid'
    
        self.inst = shared_ptr[_LibCppTest](new _LibCppTest((<int>ii)))
    def __init__(self, *args):
        if not args:
             self._init_0(*args)
        elif (len(args)==1) and (isinstance(args[0], int)):
             self._init_1(*args)
        else:
               raise Exception('can not handle %s' % (args,)) 

