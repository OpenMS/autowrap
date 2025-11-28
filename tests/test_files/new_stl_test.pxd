# cython: language_level=3
#
# ============================================================================
# Example PXD file demonstrating new STL container support in autowrap.
#
# This file shows how to declare C++ functions using the following C++17
# STL containers:
#   - std::unordered_map<K,V>  -> Python dict
#   - std::unordered_set<T>    -> Python set
#   - std::deque<T>            -> Python list
#   - std::list<T>             -> Python list
#   - std::optional<T>         -> Python T | None
#   - std::string_view         -> Python bytes/str
#
# Required imports for each container type are shown below.
# Note: Requires C++17 compilation (-std=c++17) for optional and string_view.
# ============================================================================

from libc.stddef cimport size_t
from libcpp cimport bool
from libcpp.string cimport string as libcpp_string
from libcpp.unordered_map cimport unordered_map as libcpp_unordered_map
from libcpp.unordered_set cimport unordered_set as libcpp_unordered_set
from libcpp.deque cimport deque as libcpp_deque
from libcpp.list cimport list as libcpp_list
from libcpp.optional cimport optional as libcpp_optional
from libcpp.string_view cimport string_view as libcpp_string_view

cdef extern from "new_stl_test.hpp":

    cdef cppclass _NewSTLTest "NewSTLTest":
        _NewSTLTest()

        # unordered_map tests
        libcpp_unordered_map[libcpp_string, int] getUnorderedMap()
        int sumUnorderedMapValues(libcpp_unordered_map[libcpp_string, int]& m)
        int lookupUnorderedMap(libcpp_unordered_map[libcpp_string, int]& m, libcpp_string& key)
        bool hasKeyUnorderedMap(libcpp_unordered_map[libcpp_string, int]& m, libcpp_string& key)
        int getValueUnorderedMap(libcpp_unordered_map[libcpp_string, int]& m, libcpp_string& key) except +

        # unordered_set tests
        libcpp_unordered_set[int] getUnorderedSet()
        int sumUnorderedSet(libcpp_unordered_set[int]& s)
        bool hasValueUnorderedSet(libcpp_unordered_set[int]& s, int value)
        size_t countUnorderedSet(libcpp_unordered_set[int]& s, int value)
        int findUnorderedSet(libcpp_unordered_set[int]& s, int value)

        # deque tests
        libcpp_deque[int] getDeque()
        int sumDeque(libcpp_deque[int]& d)
        void doubleDequeElements(libcpp_deque[int]& d)

        # list tests
        libcpp_list[double] getList()
        double sumList(libcpp_list[double]& l)
        void doubleListElements(libcpp_list[double]& l)

        # optional tests
        libcpp_optional[int] getOptionalValue(bool hasValue)
        int unwrapOptional(libcpp_optional[int] opt)

        # string_view tests
        size_t getStringViewLength(libcpp_string_view sv)
        libcpp_string stringViewToString(libcpp_string_view sv)
