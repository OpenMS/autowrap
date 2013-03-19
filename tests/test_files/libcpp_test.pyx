from  libcpp.string  cimport string as libcpp_string
from  libcpp.set     cimport set as libcpp_set
from  libcpp.vector  cimport vector as libcpp_vector
from  libcpp.pair    cimport pair as libcpp_pair
from  libcpp.map     cimport map  as libcpp_map
from  smart_ptr cimport shared_ptr
from  AutowrapRefHolder cimport AutowrapRefHolder
from  libcpp cimport bool
from cython.operator cimport dereference as deref, preincrement as inc, address as address
from libcpp_test cimport EEE as _EEE
from libcpp_test cimport LibCppTest as _LibCppTest
cdef extern from "autowrap_tools.hpp":
    char * _cast_const_away(char *) 

cdef class EEE:
    A = 0
    B = 1 

cdef class LibCppTest:

    cdef shared_ptr[_LibCppTest] inst

    def __dealloc__(self):
         self.inst.reset()

    
    def process(self, list in_0 ):
        assert isinstance(in_0, list) and all(isinstance(li, (int, long)) for li in in_0), 'arg in_0 wrong type'
        cdef libcpp_vector[int] v0 = in_0
        _r = self.inst.get().process(v0)
        in_0[:] = v0
        cdef list py_result = _r
        return py_result
    
    def twist(self, list in_0 ):
        assert isinstance(in_0, list) and len(in_0) == 2 and isinstance(in_0[0], str) and isinstance(in_0[1], (int, long)), 'arg in_0 wrong type'
        cdef libcpp_pair[libcpp_string, int] v0
        v0.first = in_0[0]
        v0.second = in_0[1]
        _r = self.inst.get().twist(v0)
        cdef list py_result = [_r.first, _r.second]
        return py_result
    
    def process19(self, dict in_ ):
        assert isinstance(in_, dict) and all(isinstance(k, (int, long)) for k in in_.keys()) and all(isinstance(v, LibCppTest) for v in in_.values()), 'arg in_ wrong type'
        cdef libcpp_map[int, _LibCppTest] * v0 = new libcpp_map[int, _LibCppTest]()
        for key, value in in_.items():
           deref(v0)[<int> key] = deref((<LibCppTest>value).inst.get())
        self.inst.get().process19(deref(v0))
        replace = dict()
        cdef libcpp_map[int, _LibCppTest].iterator it_in_ = v0.begin()
        cdef LibCppTest item_in_
        while it_in_ != v0.end():
           item_in_ = LibCppTest.__new__(LibCppTest)
           item_in_.inst = shared_ptr[_LibCppTest](new _LibCppTest((deref(it_in_)).second))
           replace[<int> deref(it_in_).first] = item_in_
           inc(it_in_)
        in_.clear()
        in_.update(replace)
        del v0
    
    def process18(self, dict in_ ):
        assert isinstance(in_, dict) and all(isinstance(k, (int, long)) for k in in_.keys()) and all(isinstance(v, LibCppTest) for v in in_.values()), 'arg in_ wrong type'
        cdef libcpp_map[int, _LibCppTest] * v0 = new libcpp_map[int, _LibCppTest]()
        for key, value in in_.items():
           deref(v0)[<int> key] = deref((<LibCppTest>value).inst.get())
        cdef int _r = self.inst.get().process18(deref(v0))
        del v0
        py_result = <int>_r
        return py_result
    
    def process15(self,  ii ):
        assert isinstance(ii, (int, long)), 'arg ii wrong type'
    
        _r = self.inst.get().process15((<int>ii))
        py_result = dict()
        cdef libcpp_map[long int, _LibCppTest].iterator it__r = _r.begin()
        cdef LibCppTest item_py_result
        while it__r != _r.end():
           item_py_result = LibCppTest.__new__(LibCppTest)
           item_py_result.inst = shared_ptr[_LibCppTest](new _LibCppTest((deref(it__r)).second))
           py_result[<long int>(deref(it__r).first)] = item_py_result
           inc(it__r)
        return py_result
    
    def process14(self, int e ,  i ):
        assert e in [0, 1], 'arg e wrong type'
        assert isinstance(i, (int, long)), 'arg i wrong type'
    
    
        _r = self.inst.get().process14((<_EEE>e), (<int>i))
        py_result = dict()
        cdef libcpp_map[int, _EEE].iterator it__r = _r.begin()
        while it__r != _r.end():
           py_result[<int>(deref(it__r).first)] = <_EEE>(deref(it__r).second)
           inc(it__r)
        return py_result
    
    def process17(self, dict in_ ):
        assert isinstance(in_, dict) and all(k in [0, 1] for k in in_.keys()) and all(isinstance(v, float) for v in in_.values()), 'arg in_ wrong type'
        cdef libcpp_map[_EEE, float] * v0 = new libcpp_map[_EEE, float]()
        for key, value in in_.items():
           deref(v0)[<_EEE> key] = <float> value
        cdef float _r = self.inst.get().process17(deref(v0))
        del v0
        py_result = <float>_r
        return py_result
    
    def process16(self, dict in_ ):
        assert isinstance(in_, dict) and all(isinstance(k, (int, long)) for k in in_.keys()) and all(isinstance(v, float) for v in in_.values()), 'arg in_ wrong type'
        cdef libcpp_map[int, float] * v0 = new libcpp_map[int, float]()
        for key, value in in_.items():
           deref(v0)[<int> key] = <float> value
        cdef float _r = self.inst.get().process16(deref(v0))
        del v0
        py_result = <float>_r
        return py_result
    
    def process11(self, set in_0 ):
        assert isinstance(in_0, set) and all(isinstance(li, LibCppTest) for li in in_0), 'arg in_0 wrong type'
        cdef libcpp_set[_LibCppTest] * v0 = new libcpp_set[_LibCppTest]()
        cdef LibCppTest item0
        for item0 in in_0:
           v0.insert(deref(item0.inst.get()))
        _r = self.inst.get().process11(deref(v0))
        replace = set()
        cdef libcpp_set[_LibCppTest].iterator it_in_0 = v0.begin()
        while it_in_0 != v0.end():
           item0 = LibCppTest.__new__(LibCppTest)
           item0.inst = shared_ptr[_LibCppTest](new _LibCppTest(deref(it_in_0)))
           replace.add(item0)
           inc(it_in_0)
        in_0.clear()
        in_0.update(replace)
        del v0
        py_result = set()
        cdef libcpp_set[_LibCppTest].iterator it__r = _r.begin()
        cdef LibCppTest item_py_result
        while it__r != _r.end():
           item_py_result = LibCppTest.__new__(LibCppTest)
           item_py_result.inst = shared_ptr[_LibCppTest](new _LibCppTest(deref(it__r)))
           py_result.add(item_py_result)
           inc(it__r)
        return py_result
    
    def process10(self, set in_0 ):
        assert isinstance(in_0, set) and all(li in [0, 1] for li in in_0), 'arg in_0 wrong type'
        cdef libcpp_set[_EEE] * v0 = new libcpp_set[_EEE]()
        cdef int item0
        for item0 in in_0:
           v0.insert(<_EEE> item0)
        _r = self.inst.get().process10(deref(v0))
        replace = set()
        cdef libcpp_set[_EEE].iterator it_in_0 = v0.begin()
        while it_in_0 != v0.end():
           replace.add(<int> deref(it_in_0))
           inc(it_in_0)
        in_0.clear()
        in_0.update(replace)
        del v0
        py_result = set()
        cdef libcpp_set[_EEE].iterator it__r = _r.begin()
        while it__r != _r.end():
           py_result.add(<int>deref(it__r))
           inc(it__r)
        return py_result
    
    def process13(self, int e ,  i ):
        assert e in [0, 1], 'arg e wrong type'
        assert isinstance(i, (int, long)), 'arg i wrong type'
    
    
        _r = self.inst.get().process13((<_EEE>e), (<int>i))
        py_result = dict()
        cdef libcpp_map[_EEE, int].iterator it__r = _r.begin()
        while it__r != _r.end():
           py_result[<_EEE>(deref(it__r).first)] = <int>(deref(it__r).second)
           inc(it__r)
        return py_result
    
    def process12(self,  i , float f ):
        assert isinstance(i, (int, long)), 'arg i wrong type'
        assert isinstance(f, float), 'arg f wrong type'
    
    
        _r = self.inst.get().process12((<int>i), (<float>f))
        py_result = dict()
        cdef libcpp_map[int, float].iterator it__r = _r.begin()
        while it__r != _r.end():
           py_result[<int>(deref(it__r).first)] = <float>(deref(it__r).second)
           inc(it__r)
        return py_result
    
    def get(self):
        cdef int _r = self.inst.get().get()
        py_result = <int>_r
        return py_result
    
    def process5(self, list in_0 ):
        assert isinstance(in_0, list) and len(in_0) == 2 and isinstance(in_0[0], LibCppTest) and isinstance(in_0[1], LibCppTest), 'arg in_0 wrong type'
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
    
    def process4(self, list in_0 ):
        assert isinstance(in_0, list) and len(in_0) == 2 and isinstance(in_0[0], (int, long)) and isinstance(in_0[1], LibCppTest), 'arg in_0 wrong type'
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
    
    def process7(self, list in_0 ):
        assert isinstance(in_0, list) and len(in_0) == 2 and in_0[0] in [0, 1] and isinstance(in_0[1], (int, long)), 'arg in_0 wrong type'
        cdef libcpp_pair[_EEE, int] v0
        v0.first = (<EEE>in_0[0])
        v0.second = in_0[1]
        _r = self.inst.get().process7(v0)
        in_0[:] = [v0.first, v0.second]
        cdef _EEE out2 = (<_EEE> _r.second)
        cdef list py_result = [_r.first, out2]
        return py_result
    
    def process6(self, list in_0 ):
        assert isinstance(in_0, list) and all(isinstance(li, list) and len(li) == 2 and isinstance(li[0], (int, long)) and isinstance(li[1], float) for li in in_0), 'arg in_0 wrong type'
        cdef libcpp_vector[libcpp_pair[int,double]] v0 = in_0
        _r = self.inst.get().process6(v0)
        in_0[:] = v0
        cdef list py_result = _r
        return py_result
    
    def process3(self, list in_0 ):
        assert isinstance(in_0, list) and len(in_0) == 2 and isinstance(in_0[0], LibCppTest) and isinstance(in_0[1], (int, long)), 'arg in_0 wrong type'
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
        assert isinstance(in_0, list) and len(in_0) == 2 and isinstance(in_0[0], (int, long)) and isinstance(in_0[1], (int, long)), 'arg in_0 wrong type'
        cdef libcpp_pair[int, int] v0
        v0.first = in_0[0]
        v0.second = in_0[1]
        _r = self.inst.get().process2(v0)
        in_0[:] = [v0.first, v0.second]
        cdef list py_result = [_r.first, _r.second]
        return py_result
    
    def process9(self, set in_0 ):
        assert isinstance(in_0, set) and all(isinstance(li, (int, long)) for li in in_0), 'arg in_0 wrong type'
        cdef libcpp_set[int] v0 = in_0
        _r = self.inst.get().process9(v0)
        in_0.clear()
        in_0.update(v0)
        cdef set py_result = _r
        return py_result
    
    def process8(self, list in_0 ):
        assert isinstance(in_0, list) and all(li in [0, 1] for li in in_0), 'arg in_0 wrong type'
        cdef libcpp_vector[_EEE] * v0 = new libcpp_vector[_EEE]()
        cdef int item0
        for item0 in in_0:
           v0.push_back(<_EEE> item0)
        _r = self.inst.get().process8(deref(v0))
        replace = []
        cdef libcpp_vector[_EEE].iterator it_in_0 = v0.begin()
        while it_in_0 != v0.end():
           replace.append(<int> deref(it_in_0))
           inc(it_in_0)
        in_0[:] = replace
        del v0
        py_result = []
        cdef libcpp_vector[_EEE].iterator it__r = _r.begin()
        while it__r != _r.end():
           py_result.append(<int>deref(it__r))
           inc(it__r)
        return py_result
    
    def process24(self, list in_ , list arg2 ):
        assert isinstance(in_, list) and len(in_) == 2 and isinstance(in_[0], (int, long)) and isinstance(in_[1], float), 'arg in_ wrong type'
        assert isinstance(arg2, list) and len(arg2) == 2 and isinstance(arg2[0], (int, long)) and isinstance(arg2[1], (int, long)), 'arg arg2 wrong type'
        cdef libcpp_pair[int, float] v0
        v0.first = in_[0]
        v0.second = in_[1]
        cdef libcpp_pair[int, int] v1
        v1.first = arg2[0]
        v1.second = arg2[1]
        self.inst.get().process24(v0, v1)
        arg2[:] = [v1.first, v1.second]
        in_[:] = [v0.first, v0.second]
    
    def process20(self, dict in_ ):
        assert isinstance(in_, dict) and all(isinstance(k, (int, long)) for k in in_.keys()) and all(isinstance(v, float) for v in in_.values()), 'arg in_ wrong type'
        cdef libcpp_map[int, float] * v0 = new libcpp_map[int, float]()
        for key, value in in_.items():
           deref(v0)[<int> key] = <float> value
        self.inst.get().process20(deref(v0))
        replace = dict()
        cdef libcpp_map[int, float].iterator it_in_ = v0.begin()
        while it_in_ != v0.end():
           replace[<int> deref(it_in_).first] = <float> deref(it_in_).second
           inc(it_in_)
        in_.clear()
        in_.update(replace)
        del v0
    
    def process21(self, dict in_ , dict arg2 ):
        assert isinstance(in_, dict) and all(isinstance(k, (int, long)) for k in in_.keys()) and all(isinstance(v, float) for v in in_.values()), 'arg in_ wrong type'
        assert isinstance(arg2, dict) and all(isinstance(k, (int, long)) for k in arg2.keys()) and all(isinstance(v, (int, long)) for v in arg2.values()), 'arg arg2 wrong type'
        cdef libcpp_map[int, float] * v0 = new libcpp_map[int, float]()
        for key, value in in_.items():
           deref(v0)[<int> key] = <float> value
        cdef libcpp_map[int, int] * v1 = new libcpp_map[int, int]()
        for key, value in arg2.items():
           deref(v1)[<int> key] = <int> value
        self.inst.get().process21(deref(v0), deref(v1))
        replace = dict()
        cdef libcpp_map[int, int].iterator it_arg2 = v1.begin()
        while it_arg2 != v1.end():
           replace[<int> deref(it_arg2).first] = <int> deref(it_arg2).second
           inc(it_arg2)
        arg2.clear()
        arg2.update(replace)
        del v1
        replace = dict()
        cdef libcpp_map[int, float].iterator it_in_ = v0.begin()
        while it_in_ != v0.end():
           replace[<int> deref(it_in_).first] = <float> deref(it_in_).second
           inc(it_in_)
        in_.clear()
        in_.update(replace)
        del v0
    
    def process22(self, set in_0 , set in_1 ):
        assert isinstance(in_0, set) and all(isinstance(li, (int, long)) for li in in_0), 'arg in_0 wrong type'
        assert isinstance(in_1, set) and all(isinstance(li, float) for li in in_1), 'arg in_1 wrong type'
        cdef libcpp_set[int] v0 = in_0
        cdef libcpp_set[float] v1 = in_1
        self.inst.get().process22(v0, v1)
        in_1.clear()
        in_1.update(v1)
        in_0.clear()
        in_0.update(v0)
    
    def process23(self, list in_0 , list in_1 ):
        assert isinstance(in_0, list) and all(isinstance(li, (int, long)) for li in in_0), 'arg in_0 wrong type'
        assert isinstance(in_1, list) and all(isinstance(li, float) for li in in_1), 'arg in_1 wrong type'
        cdef libcpp_vector[int] v0 = in_0
        cdef libcpp_vector[float] v1 = in_1
        self.inst.get().process23(v0, v1)
        in_1[:] = v1
        in_0[:] = v0
    
    def _init_0(self):
        self.inst = shared_ptr[_LibCppTest](new _LibCppTest())
    
    def _init_1(self,  ii ):
        assert isinstance(ii, (int, long)), 'arg ii wrong type'
    
        self.inst = shared_ptr[_LibCppTest](new _LibCppTest((<int>ii)))
    
    def __init__(self, *args):
        if not args:
             self._init_0(*args)
        elif (len(args)==1) and (isinstance(args[0], (int, long))):
             self._init_1(*args)
        else:
               raise Exception('can not handle type of %s' % (args,)) 

