#Generated with autowrap 0.23.0 and Cython (Parser) 3.2.1
#cython: c_string_encoding=ascii
#cython: embedsignature=False
from  enum            import Enum as _PyEnum
from  cpython         cimport Py_buffer
from  cpython         cimport bool as pybool_t
from  libcpp.string   cimport string as libcpp_string
from  libcpp.string   cimport string as libcpp_utf8_string
from  libcpp.string   cimport string as libcpp_utf8_output_string
from  libcpp.set      cimport set as libcpp_set
from  libcpp.vector   cimport vector as libcpp_vector
from  libcpp.pair     cimport pair as libcpp_pair
from  libcpp.map      cimport map  as libcpp_map
from  libcpp.unordered_map cimport unordered_map as libcpp_unordered_map
from  libcpp.unordered_set cimport unordered_set as libcpp_unordered_set
from  libcpp.deque    cimport deque as libcpp_deque
from  libcpp.list     cimport list as libcpp_list
from  libcpp.optional cimport optional as libcpp_optional
from  libcpp.string_view cimport string_view as libcpp_string_view
from  libcpp          cimport bool
from  libc.string     cimport const_char
from  cython.operator cimport dereference as deref, preincrement as inc, address as address
from  AutowrapRefHolder      cimport AutowrapRefHolder
from  AutowrapPtrHolder      cimport AutowrapPtrHolder
from  AutowrapConstPtrHolder cimport AutowrapConstPtrHolder
from  libcpp.memory   cimport shared_ptr
from cpp17_stl_test cimport _Cpp17STLTest as __Cpp17STLTest

cdef extern from "autowrap_tools.hpp":
    char * _cast_const_away(char *) 

cdef class _Cpp17STLTest:
    """
    Cython implementation of __Cpp17STLTest
    """

    cdef shared_ptr[__Cpp17STLTest] inst

    def __dealloc__(self):
         self.inst.reset()

    
    def __init__(self):
        """
        __init__(self) -> None
        """
        self.inst = shared_ptr[__Cpp17STLTest](new __Cpp17STLTest())
    
    def getUnorderedMap(self):
        """
        getUnorderedMap(self) -> Dict[bytes, int]
        """
        _r = self.inst.get().getUnorderedMap()
        py_result = dict()
        cdef libcpp_unordered_map[libcpp_string, int].iterator it__r = _r.begin()
        while it__r != _r.end():
           py_result[<libcpp_string>(deref(it__r).first)] = <int>(deref(it__r).second)
           inc(it__r)
        return py_result
    
    def sumUnorderedMapValues(self, dict m ):
        """
        sumUnorderedMapValues(self, m: Dict[bytes, int] ) -> int
        """
        assert isinstance(m, dict) and all(isinstance(k, bytes) for k in m.keys()) and all(isinstance(v, int) for v in m.values()), 'arg m wrong type'
        cdef libcpp_unordered_map[libcpp_string, int] * v0 = new libcpp_unordered_map[libcpp_string, int]()
        for _loop_key_m, _loop_value_m in m.items():
            deref(v0)[ <libcpp_string> _loop_key_m ] = <int> _loop_value_m
        cdef int _r = self.inst.get().sumUnorderedMapValues(deref(v0))
        replace = dict()
        cdef libcpp_unordered_map[libcpp_string, int].iterator it_m = v0.begin()
        while it_m != v0.end():
           replace[<libcpp_string> deref(it_m).first] = <int> deref(it_m).second
           inc(it_m)
        m.clear()
        m.update(replace)
        del v0
        py_result = <int>_r
        return py_result
    
    def lookupUnorderedMap(self, dict m , bytes key ):
        """
        lookupUnorderedMap(self, m: Dict[bytes, int] , key: bytes ) -> int
        """
        assert isinstance(m, dict) and all(isinstance(k, bytes) for k in m.keys()) and all(isinstance(v, int) for v in m.values()), 'arg m wrong type'
        assert isinstance(key, bytes), 'arg key wrong type'
        cdef libcpp_unordered_map[libcpp_string, int] * v0 = new libcpp_unordered_map[libcpp_string, int]()
        for _loop_key_m, _loop_value_m in m.items():
            deref(v0)[ <libcpp_string> _loop_key_m ] = <int> _loop_value_m
    
        cdef int _r = self.inst.get().lookupUnorderedMap(deref(v0), (<libcpp_string>key))
        replace = dict()
        cdef libcpp_unordered_map[libcpp_string, int].iterator it_m = v0.begin()
        while it_m != v0.end():
           replace[<libcpp_string> deref(it_m).first] = <int> deref(it_m).second
           inc(it_m)
        m.clear()
        m.update(replace)
        del v0
        py_result = <int>_r
        return py_result
    
    def hasKeyUnorderedMap(self, dict m , bytes key ):
        """
        hasKeyUnorderedMap(self, m: Dict[bytes, int] , key: bytes ) -> bool
        """
        assert isinstance(m, dict) and all(isinstance(k, bytes) for k in m.keys()) and all(isinstance(v, int) for v in m.values()), 'arg m wrong type'
        assert isinstance(key, bytes), 'arg key wrong type'
        cdef libcpp_unordered_map[libcpp_string, int] * v0 = new libcpp_unordered_map[libcpp_string, int]()
        for _loop_key_m, _loop_value_m in m.items():
            deref(v0)[ <libcpp_string> _loop_key_m ] = <int> _loop_value_m
    
        cdef bool _r = self.inst.get().hasKeyUnorderedMap(deref(v0), (<libcpp_string>key))
        replace = dict()
        cdef libcpp_unordered_map[libcpp_string, int].iterator it_m = v0.begin()
        while it_m != v0.end():
           replace[<libcpp_string> deref(it_m).first] = <int> deref(it_m).second
           inc(it_m)
        m.clear()
        m.update(replace)
        del v0
        py_result = <bool>_r
        return py_result
    
    def getValueUnorderedMap(self, dict m , bytes key ):
        """
        getValueUnorderedMap(self, m: Dict[bytes, int] , key: bytes ) -> int
        """
        assert isinstance(m, dict) and all(isinstance(k, bytes) for k in m.keys()) and all(isinstance(v, int) for v in m.values()), 'arg m wrong type'
        assert isinstance(key, bytes), 'arg key wrong type'
        cdef libcpp_unordered_map[libcpp_string, int] * v0 = new libcpp_unordered_map[libcpp_string, int]()
        for _loop_key_m, _loop_value_m in m.items():
            deref(v0)[ <libcpp_string> _loop_key_m ] = <int> _loop_value_m
    
        cdef int _r = self.inst.get().getValueUnorderedMap(deref(v0), (<libcpp_string>key))
        replace = dict()
        cdef libcpp_unordered_map[libcpp_string, int].iterator it_m = v0.begin()
        while it_m != v0.end():
           replace[<libcpp_string> deref(it_m).first] = <int> deref(it_m).second
           inc(it_m)
        m.clear()
        m.update(replace)
        del v0
        py_result = <int>_r
        return py_result
    
    def getUnorderedSet(self):
        """
        getUnorderedSet(self) -> Set[int]
        """
        _r = self.inst.get().getUnorderedSet()
        py_result = set()
        cdef libcpp_unordered_set[int].iterator it__r = _r.begin()
        while it__r != _r.end():
           py_result.add(<int>deref(it__r))
           inc(it__r)
        return py_result
    
    def sumUnorderedSet(self, set s ):
        """
        sumUnorderedSet(self, s: Set[int] ) -> int
        """
        assert isinstance(s, set) and all(isinstance(li, int) for li in s), 'arg s wrong type'
        cdef libcpp_unordered_set[int] * v0 = new libcpp_unordered_set[int]()
        for item0 in s:
           v0.insert(<int> item0)
        cdef int _r = self.inst.get().sumUnorderedSet(deref(v0))
        replace = set()
        cdef libcpp_unordered_set[int].iterator it_s = v0.begin()
        while it_s != v0.end():
           replace.add(<int> deref(it_s))
           inc(it_s)
        s.clear()
        s.update(replace)
        del v0
        py_result = <int>_r
        return py_result
    
    def hasValueUnorderedSet(self, set s , int value ):
        """
        hasValueUnorderedSet(self, s: Set[int] , value: int ) -> bool
        """
        assert isinstance(s, set) and all(isinstance(li, int) for li in s), 'arg s wrong type'
        assert isinstance(value, int), 'arg value wrong type'
        cdef libcpp_unordered_set[int] * v0 = new libcpp_unordered_set[int]()
        for item0 in s:
           v0.insert(<int> item0)
    
        cdef bool _r = self.inst.get().hasValueUnorderedSet(deref(v0), (<int>value))
        replace = set()
        cdef libcpp_unordered_set[int].iterator it_s = v0.begin()
        while it_s != v0.end():
           replace.add(<int> deref(it_s))
           inc(it_s)
        s.clear()
        s.update(replace)
        del v0
        py_result = <bool>_r
        return py_result
    
    def countUnorderedSet(self, set s , int value ):
        """
        countUnorderedSet(self, s: Set[int] , value: int ) -> int
        """
        assert isinstance(s, set) and all(isinstance(li, int) for li in s), 'arg s wrong type'
        assert isinstance(value, int), 'arg value wrong type'
        cdef libcpp_unordered_set[int] * v0 = new libcpp_unordered_set[int]()
        for item0 in s:
           v0.insert(<int> item0)
    
        cdef size_t _r = self.inst.get().countUnorderedSet(deref(v0), (<int>value))
        replace = set()
        cdef libcpp_unordered_set[int].iterator it_s = v0.begin()
        while it_s != v0.end():
           replace.add(<int> deref(it_s))
           inc(it_s)
        s.clear()
        s.update(replace)
        del v0
        py_result = <size_t>_r
        return py_result
    
    def findUnorderedSet(self, set s , int value ):
        """
        findUnorderedSet(self, s: Set[int] , value: int ) -> int
        """
        assert isinstance(s, set) and all(isinstance(li, int) for li in s), 'arg s wrong type'
        assert isinstance(value, int), 'arg value wrong type'
        cdef libcpp_unordered_set[int] * v0 = new libcpp_unordered_set[int]()
        for item0 in s:
           v0.insert(<int> item0)
    
        cdef int _r = self.inst.get().findUnorderedSet(deref(v0), (<int>value))
        replace = set()
        cdef libcpp_unordered_set[int].iterator it_s = v0.begin()
        while it_s != v0.end():
           replace.add(<int> deref(it_s))
           inc(it_s)
        s.clear()
        s.update(replace)
        del v0
        py_result = <int>_r
        return py_result
    
    def getDeque(self):
        """
        getDeque(self) -> List[int]
        """
        _r = self.inst.get().getDeque()
        py_result = [<int>_r.at(i) for i in range(_r.size())]
        return py_result
    
    def sumDeque(self, list d ):
        """
        sumDeque(self, d: List[int] ) -> int
        """
        assert isinstance(d, list) and all(isinstance(li, int) for li in d), 'arg d wrong type'
        cdef libcpp_deque[int] v0
        for item0 in d:
           v0.push_back(<int> item0)
        cdef int _r = self.inst.get().sumDeque(v0)
        d[:] = [<int>v0.at(i) for i in range(v0.size())]
        py_result = <int>_r
        return py_result
    
    def doubleDequeElements(self, list d ):
        """
        doubleDequeElements(self, d: List[int] ) -> None
        """
        assert isinstance(d, list) and all(isinstance(li, int) for li in d), 'arg d wrong type'
        cdef libcpp_deque[int] v0
        for item0 in d:
           v0.push_back(<int> item0)
        self.inst.get().doubleDequeElements(v0)
        d[:] = [<int>v0.at(i) for i in range(v0.size())]
    
    def getList(self):
        """
        getList(self) -> List[float]
        """
        _r = self.inst.get().getList()
        py_result = []
        cdef libcpp_list[double].iterator it__r = _r.begin()
        while it__r != _r.end():
           py_result.append(deref(it__r))
           inc(it__r)
        return py_result
    
    def sumList(self, list l ):
        """
        sumList(self, l: List[float] ) -> float
        """
        assert isinstance(l, list) and all(isinstance(li, float) for li in l), 'arg l wrong type'
        cdef libcpp_list[double] v0
        for item in l:
           v0.push_back(item)
        cdef double _r = self.inst.get().sumList(v0)
        l[:] = []
        cdef libcpp_list[double].iterator it_l = v0.begin()
        while it_l != v0.end():
           l.append(deref(it_l))
           inc(it_l)
        py_result = <double>_r
        return py_result
    
    def doubleListElements(self, list l ):
        """
        doubleListElements(self, l: List[float] ) -> None
        """
        assert isinstance(l, list) and all(isinstance(li, float) for li in l), 'arg l wrong type'
        cdef libcpp_list[double] v0
        for item in l:
           v0.push_back(item)
        self.inst.get().doubleListElements(v0)
        l[:] = []
        cdef libcpp_list[double].iterator it_l = v0.begin()
        while it_l != v0.end():
           l.append(deref(it_l))
           inc(it_l)
    
    def getOptionalValue(self, bool hasValue ):
        """
        getOptionalValue(self, hasValue: bool ) -> Optional[int]
        """
        assert isinstance(hasValue, pybool_t), 'arg hasValue wrong type'
    
        _r = self.inst.get().getOptionalValue((<bool>hasValue))
        if _r.has_value():
           py_result = _r.value()
        else:
           py_result = None
        return py_result
    
    def unwrapOptional(self, object opt ):
        """
        unwrapOptional(self, opt: Optional[int] ) -> int
        """
        assert (opt is None or isinstance(opt, int)), 'arg opt wrong type'
        cdef libcpp_optional[int] v0
        if opt is not None:
           v0 = libcpp_optional[int](<int>opt)
        cdef int _r = self.inst.get().unwrapOptional(v0)
        py_result = <int>_r
        return py_result
    
    def getStringViewLength(self, bytes sv ):
        """
        getStringViewLength(self, sv: bytes ) -> int
        """
        assert isinstance(sv, (bytes, str)), 'arg sv wrong type'
        cdef bytes v0
        if isinstance(sv, str):
           v0 = sv.encode('utf-8')
        else:
           v0 = sv
        cdef size_t _r = self.inst.get().getStringViewLength((<libcpp_string_view>v0))
        py_result = <size_t>_r
        return py_result
    
    def stringViewToString(self, bytes sv ):
        """
        stringViewToString(self, sv: bytes ) -> bytes
        """
        assert isinstance(sv, (bytes, str)), 'arg sv wrong type'
        cdef bytes v0
        if isinstance(sv, str):
           v0 = sv.encode('utf-8')
        else:
           v0 = sv
        cdef libcpp_string _r = self.inst.get().stringViewToString((<libcpp_string_view>v0))
        py_result = <libcpp_string>_r
        return py_result 
