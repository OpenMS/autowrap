from libcpp.string cimport string as libcpp_string
from libcpp.set cimport set as libcpp_set
from libcpp.vector cimport vector as libcpp_vector
from libcpp.pair  cimport pair  as libcpp_pair
from libcpp.map  cimport map  as libcpp_map
from libcpp cimport bool

cdef extern from "iteratorwrapper.hpp":

    cdef cppclass IteratorWrapper[I,V]:
        # wrap-instances:
        #  ScoreTypeRef := IteratorWrapper[SetIter, ScoreType]
        IteratorWrapper()
        IteratorWrapper(IteratorWrapper[I,V])
        V get()


cdef extern from "scoretype.hpp":
    ctypedef libcpp_set[ScoreType].iterator SetIter

    cdef cppclass ScoreType:
        ScoreType()
        ScoreType(bool higher_better, libcpp_string name)
        ScoreType(ScoreType)
        bool higher_better
        libcpp_string name

    cdef cppclass ProcessingSoftware:
        ProcessingSoftware()
        libcpp_vector[IteratorWrapper[SetIter, ScoreType]] assigned_scores

