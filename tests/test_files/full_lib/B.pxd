from libcpp.string cimport string as libcpp_string
from libcpp.set cimport set as libcpp_set
from libcpp.vector cimport vector as libcpp_vector
from libcpp cimport bool
from libcpp.pair  cimport pair  as libcpp_pair 
from libcpp.map  cimport map  as libcpp_map 
from smart_ptr cimport shared_ptr
from A cimport *

cdef extern from "B.hpp":

    cdef enum testB:
        BB, BBB

    cdef cppclass B_second:
        int i_
        B_second(int i)
        B_second(B_second & i)
        void processA(Aklass & a)

    cdef cppclass Bklass (A_second):
        # wrap-inherits:
        #  A_second
        #
        # wrap-doc: 
        #  some doc!

        int i_  # we need to copy public member accessors
        Bklass(int i)
        Bklass(Bklass & i)

    cdef enum B_KlassE "Bklass::KlassE":
        #wrap-attach:
        #   Bklass
        #wrap-instances:
        #   KlassE := B_KlassE
        #wrap-as:
        #   KlassE
        B1
        B2
        B3


    cdef cppclass B_KlassKlass "Bklass::KlassKlass":
        #wrap-attach:
        #   Bklass
        #wrap-instances:
        #   KlassKlass := B_KlassKlass
        #wrap-as:
        #   KlassKlass
        B_KlassKlass()
        int k_

