#cython: language_level=3
from cython.operator cimport dereference as deref, preincrement as preinc
from libcpp.list cimport list as cpplist



cdef class IterTest:

    cdef cpplist[int] * inst

    def __cinit__(self):
        self.inst = NULL

    def __dealloc__(self):
        print("dealloc called")
        if self.inst != NULL:
            del self.inst

    cdef _init(self, cpplist[int] * inst):
        self.inst = inst # new cpplist[int]()

    def add(self, int i):
        self.inst.push_back(i)

    def __iter__(self):
        assert self.inst != NULL

        it = self.inst.begin()
        while it != self.inst.end():
            yield <int> deref(it)
            preinc(it)

cdef inline create(list li):
    result = IterTest()
    result._init(new cpplist[int]())
    for i in li:
        result.add(i)
    return result


cdef inline conv1(cpplist[int] & ii):
    return [ <int>i for i in ii ]

cdef inline conv2(list ii):
    cdef cpplist[int] rv
    for i in ii:
        rv.push_back(<int> i)
    return rv

def run(list x):
    cdef cpplist[int] xv = conv2(x)
    xv.reverse()
    return conv1(xv)

def run2(list x):
    return create(x)





