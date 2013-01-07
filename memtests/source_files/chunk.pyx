from libcpp.string cimport string as std_string
from libcpp.vector cimport vector as std_vector
from cython.operator cimport dereference as deref, preincrement as inc, address as address
from chunk cimport Chunk as _Chunk
cdef class Chunk:
    cdef _Chunk * inst
    def __dealloc__(self):
        if self.inst:
            del self.inst
    def __copy__(self):
       cdef Chunk rv = Chunk.__new__(Chunk)
       rv.inst = new _Chunk(deref(self.inst))
       return rv
    def _init_0(self):
        self.inst = new _Chunk()
    def _init_1(self, int debug ):
        assert isinstance(debug, int), 'arg debug invalid'
    
        self.inst = new _Chunk((<int>debug))
    def __init__(self, *args):
        if not args:
             self._init_0(*args)
        elif (len(args)==1) and (isinstance(args[0], int)):
             self._init_1(*args)
        else:
            raise Exception('can not handle %s' % (args,))
    def getRef(self):
        cdef _Chunk _r = self.inst.getRef()
        cdef Chunk py_result = Chunk.__new__(Chunk)
        py_result.inst = new _Chunk(_r)
        return py_result
    def getCopy(self):
        cdef _Chunk _r = self.inst.getCopy()
        cdef Chunk py_result = Chunk.__new__(Chunk)
        py_result.inst = new _Chunk(_r)
        return py_result
    def create(self, int n ):
        assert isinstance(n, int), 'arg n invalid'
    
        cdef std_vector[_Chunk] _r = self.inst.create((<int>n))
        py_result = []
        cdef std_vector[_Chunk].iterator it__r = _r.begin()
        cdef Chunk item_py_result
        while it__r != _r.end():
           item_py_result = Chunk.__new__(Chunk)
           item_py_result.inst = new _Chunk(deref(it__r))
           py_result.append(item_py_result)
           inc(it__r)
        return py_result
    def copy(self, list in_0 ):
        assert isinstance(in_0, list) and all(isinstance(li, Chunk) for li in in_0), 'arg in_0 invalid'
        cdef std_vector[_Chunk] * v0 = new std_vector[_Chunk]()
        cdef Chunk item
        for item in in_0:
           v0.push_back(deref(item.inst))
        cdef std_vector[_Chunk] _r = self.inst.copy(deref(v0))
        py_result = []
        cdef std_vector[_Chunk].iterator it__r = _r.begin()
        cdef Chunk item_py_result
        while it__r != _r.end():
           item_py_result = Chunk.__new__(Chunk)
           item_py_result.inst = new _Chunk(deref(it__r))
           py_result.append(item_py_result)
           inc(it__r)
        return py_result


