from smart_ptr cimport shared_ptr
from libcpp.string cimport string as std_string
from cython.operator cimport dereference as deref


cdef class Holder:

    cdef shared_ptr[std_string] inst

    def __init__(self, str what):
        cdef std_string p = <std_string> what
        self.inst = shared_ptr[std_string](new std_string(p))

    def count(self):
        return self.inst.use_count()


    def getRef(self):
        cdef Holder res = Holder.__new__(Holder)
        res.inst = self.inst
        return res

    def getCopy(self):
        cdef Holder res = Holder.__new__(Holder)
        res.inst = shared_ptr[std_string](new std_string(deref(self.inst.get())))
        return res

    def addX(self):
        self.inst.get().push_back("x")

    def size(self):
        return self.inst.get().size()
