#cython: language_level=2
from int_container_class cimport X as X_, XContainer as XContainer_
from cython.operator import dereference as deref


cdef class Xint:

    cdef X_[int] * inst

    def __cinit__(self):
        self.inst = NULL

    def __init__(self, *v):
        if len(v):
            if isinstance(v[0], int):
                self._set_(new X_[int](<int>v[0]))

    def __add__(Xint self, Xint other):
        cdef X_[int] * arg0 = self.inst
        cdef X_[int] * arg1 = other.inst
        cdef rv = newX(new X_[int](arg0[0]+arg1[0]))
        return rv


    def getValue(self):
        return <int>self.inst[0]


    cdef _set_(self, X_[int] * x):
        if self.inst != NULL:
            del self.inst
        self.inst = x

cdef newX(X_[int] * rv):
    cdef Xint rr = Xint()
    rr._set_(rv)
    return rr

cdef class XContainerInt:

    cdef XContainer_[int] * inst

    def __cinit__(self):
        self.inst = new XContainer_[int]()

    def push_back(self, Xint o):
        self.inst.push_back(deref(o.inst))

    def size(self):
        return self.inst.size()

