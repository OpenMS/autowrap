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
from minimal_td cimport Int
from minimal cimport ABCorD as _ABCorD
from minimal cimport run_static as _run_static_minimal
from minimal cimport sumup as _sumup_minimal
from minimal cimport top_function as _top_function_minimal
from minimal cimport Minimal as _Minimal
cdef extern from "autowrap_tools.hpp":
    char * _cast_const_away(char *)
cdef extern from "autowrap_tools.hpp":
    void _iadd(_Minimal *, _Minimal *)

def __static_Minimal_run_static( in_0 ):
    assert isinstance(in_0, (int, long)), 'arg in_0 wrong type'

    cdef long int _r = _run_static_minimal((<long int>in_0))
    py_result = <long int>_r
    return py_result

def sumup(list what ):
    assert isinstance(what, list) and all(isinstance(elemt_rec, (int, long)) for elemt_rec in what), 'arg what wrong type'
    cdef libcpp_vector[int] v0 = what
    cdef int _r = _sumup_minimal(v0)
    
    py_result = <int>_r
    return py_result

def top_function( in_0 ):
    assert isinstance(in_0, (int, long)), 'arg in_0 wrong type'

    cdef int _r = _top_function_minimal((<int>in_0))
    py_result = <int>_r
    return py_result 

cdef class Minimal:

    cdef shared_ptr[_Minimal] inst

    def __dealloc__(self):
         self.inst.reset()

    
    def toInt(self):
        cdef int _r = <int>(deref(self.inst.get()))
        py_res = <int>_r
        return py_res
    
    def compute_charp(self, bytes what ):
        assert isinstance(what, bytes), 'arg what wrong type'
    
        cdef int _r = self.inst.get().compute_charp((<char *>what))
        py_result = <int>_r
        return py_result
    
    def pass_const_charptr(self, bytes in_0 ):
        assert isinstance(in_0, bytes), 'arg in_0 wrong type'
    
        cdef const_char  * _r = _cast_const_away(self.inst.get().pass_const_charptr((<const_char *>in_0)))
        py_result = <const_char *>(_r)
        return py_result
    
    def message(self):
        _r = self.inst.get().message()
        cdef list py_result = _r
        return py_result
    
    def __copy__(self):
       cdef Minimal rv = Minimal.__new__(Minimal)
       rv.inst = shared_ptr[_Minimal](new _Minimal(deref(self.inst.get())))
       return rv
    
    def _init_0(self):
        self.inst = shared_ptr[_Minimal](new _Minimal())
    
    def _init_1(self,  in_0 ):
        assert isinstance(in_0, (int, long)), 'arg in_0 wrong type'
    
        self.inst = shared_ptr[_Minimal](new _Minimal((<int>in_0)))
    
    def _init_2(self, list in_0 ):
        assert isinstance(in_0, list) and all(isinstance(elemt_rec, (int, long)) for elemt_rec in in_0), 'arg in_0 wrong type'
        cdef libcpp_vector[int] v0 = in_0
        self.inst = shared_ptr[_Minimal](new _Minimal(v0))
        
    
    def __init__(self, *args):
        if not args:
             self._init_0(*args)
        elif (len(args)==1) and (isinstance(args[0], (int, long))):
             self._init_1(*args)
        elif (len(args)==1) and (isinstance(args[0], list) and all(isinstance(elemt_rec, (int, long)) for elemt_rec in args[0])):
             self._init_2(*args)
        else:
               raise Exception('can not handle type of %s' % (args,))
    
    def sumup(self, list what ):
        assert isinstance(what, list) and all(isinstance(elemt_rec, (int, long)) for elemt_rec in what), 'arg what wrong type'
        cdef libcpp_vector[int] v0 = what
        cdef int _r = self.inst.get().sumup(v0)
        
        py_result = <int>_r
        return py_result
    
    def run2(self, Minimal p ):
        assert isinstance(p, Minimal), 'arg p wrong type'
    
        cdef int _r = self.inst.get().run2((p.inst.get()))
        py_result = <int>_r
        return py_result
    
    def __iadd__(Minimal self, Minimal other not None):
        cdef _Minimal * this = self.inst.get()
        cdef _Minimal * that = other.inst.get()
        _iadd(this, that)
        return self
    
    def test2Lists(self, list in_0 , list in_1 ):
        assert isinstance(in_0, list) and all(isinstance(elemt_rec, Minimal) for elemt_rec in in_0), 'arg in_0 wrong type'
        assert isinstance(in_1, list) and all(isinstance(elemt_rec, (int, long)) for elemt_rec in in_1), 'arg in_1 wrong type'
        cdef libcpp_vector[_Minimal] * v0 = new libcpp_vector[_Minimal]()
        cdef Minimal item0
        for item0 in in_0:
            v0.push_back(deref(item0.inst.get()))
        cdef libcpp_vector[int] v1 = in_1
        cdef int _r = self.inst.get().test2Lists(deref(v0), v1)
        
        del v0
        py_result = <int>_r
        return py_result
    
    def pass_charptr(self, bytes in_0 ):
        assert isinstance(in_0, bytes), 'arg in_0 wrong type'
    
        cdef char  * _r = _cast_const_away(self.inst.get().pass_charptr((<char *>in_0)))
        py_result = <char *>(_r)
        return py_result
    
    def create(self):
        cdef _Minimal * _r = new _Minimal(self.inst.get().create())
        cdef Minimal py_result = Minimal.__new__(Minimal)
        py_result.inst = shared_ptr[_Minimal](_r)
        return py_result
    
    def getVector(self):
        _r = self.inst.get().getVector()
        py_result = []
        cdef libcpp_vector[_Minimal].iterator it__r = _r.begin()
        cdef Minimal item_py_result
        while it__r != _r.end():
           item_py_result = Minimal.__new__(Minimal)
           item_py_result.inst = shared_ptr[_Minimal](new _Minimal(deref(it__r)))
           py_result.append(item_py_result)
           inc(it__r)
        return py_result
    
    def call(self, list what ):
        assert isinstance(what, list) and all(isinstance(elemt_rec, Minimal) for elemt_rec in what), 'arg what wrong type'
        cdef libcpp_vector[_Minimal] * v0 = new libcpp_vector[_Minimal]()
        cdef Minimal item0
        for item0 in what:
            v0.push_back(deref(item0.inst.get()))
        cdef int _r = self.inst.get().call(deref(v0))
        del v0
        py_result = <int>_r
        return py_result
    
    def size(self):
        cdef int _r = self.inst.get().size()
        py_result = <int>_r
        return py_result
    
    def run(self, Minimal ref ):
        assert isinstance(ref, Minimal), 'arg ref wrong type'
    
        cdef int _r = self.inst.get().run((deref(ref.inst.get())))
        py_result = <int>_r
        return py_result
    
    def get(self):
        cdef int _r = self.inst.get().get()
        py_result = <int>_r
        return py_result
    
    def __add__(Minimal self, Minimal other not None):
        cdef _Minimal  * this = self.inst.get()
        cdef _Minimal * that = other.inst.get()
        cdef _Minimal added = deref(this) + deref(that)
        cdef Minimal result = Minimal.__new__(Minimal)
        result.inst = shared_ptr[_Minimal](new _Minimal(added))
        return result
    
    def _compute_int_0(self,  in_0 ):
        assert isinstance(in_0, (int, long)), 'arg in_0 wrong type'
    
        cdef int _r = self.inst.get().compute_int((<int>in_0))
        py_result = <int>_r
        return py_result
    
    def _compute_int_1(self):
        cdef int _r = self.inst.get().compute_int()
        py_result = <int>_r
        return py_result
    
    def compute_int(self, *args):
        if (len(args)==1) and (isinstance(args[0], (int, long))):
            return self._compute_int_0(*args)
        elif not args:
            return self._compute_int_1(*args)
        else:
               raise Exception('can not handle type of %s' % (args,))
    
    def __getitem__(self,  in_0 ):
        assert isinstance(in_0, (int, long)), 'arg in_0 wrong type'
    
        if (<int>in_0) < 0:
            raise IndexError("invalid index %d" % (<int>in_0))
        if (<int>in_0) >= self.inst.get().size():
            raise IndexError("invalid index %d" % (<int>in_0))
        cdef int _r = deref(self.inst.get())[(<int>in_0)]
        py_result = <int>_r
        return py_result
    
    def test_special_converter(self, int in_0 ):
        assert isinstance(in_0, int), 'arg in_0 wrong type'
    
        cdef unsigned int _r = self.inst.get().test_special_converter((1 + <int>in_0))
        py_result = <int>_r
        return py_result
    
    def setVector(self, list in_0 ):
        assert isinstance(in_0, list) and all(isinstance(elemt_rec, Minimal) for elemt_rec in in_0), 'arg in_0 wrong type'
        cdef libcpp_vector[_Minimal] * v0 = new libcpp_vector[_Minimal]()
        cdef Minimal item0
        for item0 in in_0:
            v0.push_back(deref(item0.inst.get()))
        self.inst.get().setVector(deref(v0))
        del v0
    
    def _compute_0(self, bytes in_0 ):
        assert isinstance(in_0, bytes), 'arg in_0 wrong type'
    
        cdef libcpp_string _r = self.inst.get().compute((<libcpp_string>in_0))
        py_result = <libcpp_string>_r
        return py_result
    
    def _compute_1(self,  number1 ,  number2 ):
        assert isinstance(number1, (int, long)), 'arg number1 wrong type'
        assert isinstance(number2, (int, long)), 'arg number2 wrong type'
    
    
        cdef int _r = self.inst.get().compute((<int>number1), (<int>number2))
        py_result = <int>_r
        return py_result
    
    def _compute_2(self,  number ):
        assert isinstance(number, (int, long)), 'arg number wrong type'
    
        cdef int _r = self.inst.get().compute((<int>number))
        py_result = <int>_r
        return py_result
    
    def _compute_3(self, float number ):
        assert isinstance(number, float), 'arg number wrong type'
    
        cdef float _r = self.inst.get().compute((<float>number))
        py_result = <float>_r
        return py_result
    
    def compute(self, *args):
        if (len(args)==1) and (isinstance(args[0], bytes)):
            return self._compute_0(*args)
        elif (len(args)==2) and (isinstance(args[0], (int, long))) and (isinstance(args[1], (int, long))):
            return self._compute_1(*args)
        elif (len(args)==1) and (isinstance(args[0], (int, long))):
            return self._compute_2(*args)
        elif (len(args)==1) and (isinstance(args[0], float)):
            return self._compute_3(*args)
        else:
               raise Exception('can not handle type of %s' % (args,))
    
    def call2(self, list what ):
        assert isinstance(what, list) and all(isinstance(elemt_rec, bytes) for elemt_rec in what), 'arg what wrong type'
        cdef libcpp_vector[libcpp_string] v0 = what
        cdef int _r = self.inst.get().call2(v0)
        what[:] = v0
        py_result = <int>_r
        return py_result
    
    def compute_str(self, bytes what ):
        assert isinstance(what, bytes), 'arg what wrong type'
    
        cdef libcpp_string _r = self.inst.get().compute_str((<libcpp_string>what))
        py_result = <libcpp_string>_r
        return py_result
    
    def create_two(self):
        _r = self.inst.get().create_two()
        py_result = []
        cdef libcpp_vector[_Minimal].iterator it__r = _r.begin()
        cdef Minimal item_py_result
        while it__r != _r.end():
           item_py_result = Minimal.__new__(Minimal)
           item_py_result.inst = shared_ptr[_Minimal](new _Minimal(deref(it__r)))
           py_result.append(item_py_result)
           inc(it__r)
        return py_result
    
    def enumTest(self, int in_0 ):
        assert in_0 in [0, 2, 3, 4], 'arg in_0 wrong type'
    
        cdef _ABCorD _r = self.inst.get().enumTest((<_ABCorD>in_0))
        py_result = <int>_r
        return py_result
    
    def __richcmp__(self, other, op):
        if op not in (2,):
           op_str = {0: '<', 1: '<=', 2: '==', 3: '!=', 4: '>', 5: '>='}[op]
           raise Exception("comparions operator %s not implemented" % op_str)
        if not isinstance(other, Minimal):
            return False
        cdef Minimal other_casted = other
        cdef Minimal self_casted = self
        if op==2:
            return deref(self_casted.inst.get()) == deref(other_casted.inst.get())
    
    def __iter__(self):
        it = self.inst.get().begin()
        cdef Minimal out
        while it != self.inst.get().end():
            out = Minimal.__new__(Minimal)
            out.inst = shared_ptr[_Minimal](new _Minimal(deref(it)))
            yield out
            inc(it)
    ABCorD = __ABCorD
    run_static = __static_Minimal_run_static 

cdef class __ABCorD:
    A = 0
    B = 2
    C = 3
    D = 4 
