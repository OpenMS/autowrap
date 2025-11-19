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
from  libcpp          cimport bool
from  libc.string     cimport const_char
from  cython.operator cimport dereference as deref, preincrement as inc, address as address
from  AutowrapRefHolder      cimport AutowrapRefHolder
from  AutowrapPtrHolder      cimport AutowrapPtrHolder
from  AutowrapConstPtrHolder cimport AutowrapConstPtrHolder
from  smart_ptr       cimport shared_ptr
from map_wrapped_keys cimport Person as _Person
from map_wrapped_keys cimport Score as _Score
from map_wrapped_keys cimport ScoreTracker as _ScoreTracker

cdef extern from "autowrap_tools.hpp":
    char * _cast_const_away(char *) 

cdef class Person:
    """
    Cython implementation of _Person

     A person with an ID that can be used as a map key
    """

    cdef shared_ptr[_Person] inst

    def __dealloc__(self):
         self.inst.reset()

    
    property id_:
        def __set__(self, int id_):
        
            self.inst.get().id_ = (<int>id_)
        
    
        def __get__(self):
            cdef int _r = self.inst.get().id_
            py_result = <int>_r
            return py_result
    
    def __copy__(self):
       cdef Person rv = Person.__new__(Person)
       rv.inst = shared_ptr[_Person](new _Person(deref(self.inst.get())))
       return rv
    
    def __deepcopy__(self, memo):
       cdef Person rv = Person.__new__(Person)
       rv.inst = shared_ptr[_Person](new _Person(deref(self.inst.get())))
       return rv
    
    def _init_0(self):
        """
        _init_0(self) -> None
        """
        self.inst = shared_ptr[_Person](new _Person())
    
    def _init_1(self, int id ):
        """
        _init_1(self, id: int ) -> None
        """
        assert isinstance(id, int), 'arg id wrong type'
    
        self.inst = shared_ptr[_Person](new _Person((<int>id)))
    
    def _init_2(self, Person in_0 ):
        """
        _init_2(self, in_0: Person ) -> None
        """
        assert isinstance(in_0, Person), 'arg in_0 wrong type'
    
        self.inst = shared_ptr[_Person](new _Person((deref(in_0.inst.get()))))
    
    def __init__(self, *args , **kwargs):
        """
        .. rubric:: Overload:
        .. py:function:: __init__(self, ) -> None
          :noindex:
        
        .. rubric:: Overload:
        .. py:function:: __init__(self, id: int ) -> None
          :noindex:
        
        .. rubric:: Overload:
        .. py:function:: __init__(self, in_0: Person ) -> None
          :noindex:
    
        """
        if not args:
             self._init_0(*args)
        elif (len(args)==1) and (isinstance(args[0], int)):
             self._init_1(*args)
        elif (len(args)==1) and (isinstance(args[0], Person)):
             self._init_2(*args)
        else:
               raise Exception('can not handle type of %s' % (args,)) 

cdef class Score:
    """
    Cython implementation of _Score

     A score value
    """

    cdef shared_ptr[_Score] inst

    def __dealloc__(self):
         self.inst.reset()

    
    property value_:
        def __set__(self, int value_):
        
            self.inst.get().value_ = (<int>value_)
        
    
        def __get__(self):
            cdef int _r = self.inst.get().value_
            py_result = <int>_r
            return py_result
    
    def __copy__(self):
       cdef Score rv = Score.__new__(Score)
       rv.inst = shared_ptr[_Score](new _Score(deref(self.inst.get())))
       return rv
    
    def __deepcopy__(self, memo):
       cdef Score rv = Score.__new__(Score)
       rv.inst = shared_ptr[_Score](new _Score(deref(self.inst.get())))
       return rv
    
    def _init_0(self):
        """
        _init_0(self) -> None
        """
        self.inst = shared_ptr[_Score](new _Score())
    
    def _init_1(self, int value ):
        """
        _init_1(self, value: int ) -> None
        """
        assert isinstance(value, int), 'arg value wrong type'
    
        self.inst = shared_ptr[_Score](new _Score((<int>value)))
    
    def _init_2(self, Score in_0 ):
        """
        _init_2(self, in_0: Score ) -> None
        """
        assert isinstance(in_0, Score), 'arg in_0 wrong type'
    
        self.inst = shared_ptr[_Score](new _Score((deref(in_0.inst.get()))))
    
    def __init__(self, *args , **kwargs):
        """
        .. rubric:: Overload:
        .. py:function:: __init__(self, ) -> None
          :noindex:
        
        .. rubric:: Overload:
        .. py:function:: __init__(self, value: int ) -> None
          :noindex:
        
        .. rubric:: Overload:
        .. py:function:: __init__(self, in_0: Score ) -> None
          :noindex:
    
        """
        if not args:
             self._init_0(*args)
        elif (len(args)==1) and (isinstance(args[0], int)):
             self._init_1(*args)
        elif (len(args)==1) and (isinstance(args[0], Score)):
             self._init_2(*args)
        else:
               raise Exception('can not handle type of %s' % (args,)) 

cdef class ScoreTracker:
    """
    Cython implementation of _ScoreTracker

     Tracks scores for people using maps with wrapped types
    """

    cdef shared_ptr[_ScoreTracker] inst

    def __dealloc__(self):
         self.inst.reset()

    
    def __init__(self):
        """
        __init__(self) -> None
        """
        self.inst = shared_ptr[_ScoreTracker](new _ScoreTracker())
    
    def get_person_scores(self):
        """
        get_person_scores(self) -> Dict[Person, int]
         Get scores with Person as key (wrapped type) and int as value
        """
        _r = self.inst.get().get_person_scores()
        py_result = dict()
        cdef libcpp_map[_Person, int].iterator it__r = _r.begin()
        cdef Person itemk_py_result
        while it__r != _r.end():
           #py_result[deref(<_Person *> (<Person> key).inst.get())] = <int>(deref(it__r).second)
           itemk_py_result = Person.__new__(Person)
           itemk_py_result.inst = shared_ptr[_Person](new _Person((deref(it__r)).first))
           # py_result[deref(<_Person *> (<Person> key).inst.get())] = <int>(deref(it__r).second)
           py_result[itemk_py_result] = <int>(deref(it__r).second)
           inc(it__r)
        return py_result
    
    def get_id_scores(self):
        """
        get_id_scores(self) -> Dict[int, Score]
         Get scores with int as key and Score as value (wrapped type)
        """
        _r = self.inst.get().get_id_scores()
        py_result = dict()
        cdef libcpp_map[int, _Score].iterator it__r = _r.begin()
        cdef Score item_py_result
        while it__r != _r.end():
           item_py_result = Score.__new__(Score)
           item_py_result.inst = shared_ptr[_Score](new _Score((deref(it__r)).second))
           py_result[<int>(deref(it__r).first)] = item_py_result
           inc(it__r)
        return py_result
    
    def get_full_scores(self):
        """
        get_full_scores(self) -> Dict[Person, Score]
         Get scores with both Person (wrapped type) as key and Score (wrapped type) as value
        """
        _r = self.inst.get().get_full_scores()
        py_result = dict()
        cdef libcpp_map[_Person, _Score].iterator it__r = _r.begin()
        cdef Person itemk_py_result
        cdef Score itemv_py_result
        while it__r != _r.end():
           itemk_py_result = Person.__new__(Person)
           itemk_py_result.inst = shared_ptr[_Person](new _Person((deref(it__r)).first))
           itemv_py_result = Score.__new__(Score)
           itemv_py_result.inst = shared_ptr[_Score](new _Score((deref(it__r)).second))
           py_result[itemk_py_result] = itemv_py_result
           inc(it__r)
        return py_result
    
    def sum_scores(self, dict scores ):
        """
        sum_scores(self, scores: Dict[Person, Score] ) -> int
         Sum all scores from a map with wrapped types as both key and value
        """
        assert isinstance(scores, dict) and all(isinstance(k, Person) for k in scores.keys()) and all(isinstance(v, Score) for v in scores.values()), 'arg scores wrong type'
        cdef libcpp_map[_Person, _Score] * v0 = new libcpp_map[_Person, _Score]()
        for key, value in scores.items():
        
        
            deref(v0)[ deref(<_Person *> (<Person> key).inst.get()) ] = deref((<Score>value).inst.get())
        
        
        cdef int _r = self.inst.get().sum_scores(deref(v0))
        replace = dict()
        cdef libcpp_map[_Person, _Score].iterator it_scores = v0.begin()
        cdef Person itemk_scores
        cdef Score itemv_scores
        while it_scores != v0.end():
           itemk_scores = Person.__new__(Person)
           itemk_scores.inst = shared_ptr[_Person](new _Person((deref(it_scores)).first))
           itemv_scores = Score.__new__(Score)
           itemv_scores.inst = shared_ptr[_Score](new _Score((deref(it_scores)).second))
           replace[itemk_scores] = itemv_scores
           inc(it_scores)
        scores.clear()
        scores.update(replace)
        del v0
        py_result = <int>_r
        return py_result 
