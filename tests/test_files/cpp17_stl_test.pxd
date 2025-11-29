# cython: language_level=3
#
# =============================================================================
# C++17 STL Container Declarations for Autowrap
# =============================================================================
#
# This PXD file demonstrates how to declare C++ functions that use C++17 STL
# containers. Autowrap automatically generates Python bindings with proper
# type conversions.
#
# Container Type Mappings:
# ------------------------
#   C++ Type                    Python Type     Notes
#   -------------------------   -------------   --------------------------------
#   std::unordered_map<K,V>     dict            Hash-based, O(1) avg lookup
#   std::unordered_set<T>       set             Hash-based, O(1) avg lookup
#   std::deque<T>               list            Double-ended queue
#   std::list<T>                list            Doubly-linked list
#   std::optional<T>            T | None        Nullable value (C++17)
#   std::string_view            bytes           Non-owning string ref (C++17)
#
# Required Cython Imports:
# ------------------------
#   from libcpp.unordered_map cimport unordered_map as libcpp_unordered_map
#   from libcpp.unordered_set cimport unordered_set as libcpp_unordered_set
#   from libcpp.deque cimport deque as libcpp_deque
#   from libcpp.list cimport list as libcpp_list
#   from libcpp.optional cimport optional as libcpp_optional
#   from libcpp.string_view cimport string_view as libcpp_string_view
#
# Compilation:
# ------------
#   Requires C++17 flag: -std=c++17 (for optional and string_view)
#
# =============================================================================

from libc.stddef cimport size_t
from libcpp cimport bool
from libcpp.string cimport string as libcpp_string
from libcpp.unordered_map cimport unordered_map as libcpp_unordered_map
from libcpp.unordered_set cimport unordered_set as libcpp_unordered_set
from libcpp.deque cimport deque as libcpp_deque
from libcpp.list cimport list as libcpp_list
from libcpp.optional cimport optional as libcpp_optional
from libcpp.string_view cimport string_view as libcpp_string_view

cdef extern from "cpp17_stl_test.hpp":

    cdef cppclass _Cpp17STLTest "Cpp17STLTest":
        _Cpp17STLTest()

        # =====================================================================
        # std::unordered_map<string, int> - Hash-based dictionary
        # =====================================================================
        # Python usage:
        #   result = obj.getUnorderedMap()           # Returns dict
        #   obj.sumUnorderedMapValues({b"a": 1})     # Pass dict
        #   value = obj.lookupUnorderedMap(d, b"k")  # O(1) key lookup
        #   exists = obj.hasKeyUnorderedMap(d, b"k") # O(1) key check
        # ---------------------------------------------------------------------
        libcpp_unordered_map[libcpp_string, int] getUnorderedMap()
        int sumUnorderedMapValues(libcpp_unordered_map[libcpp_string, int]& m)
        int lookupUnorderedMap(libcpp_unordered_map[libcpp_string, int]& m, libcpp_string& key)
        bool hasKeyUnorderedMap(libcpp_unordered_map[libcpp_string, int]& m, libcpp_string& key)
        int getValueUnorderedMap(libcpp_unordered_map[libcpp_string, int]& m, libcpp_string& key) except +

        # =====================================================================
        # std::unordered_set<int> - Hash-based set
        # =====================================================================
        # Python usage:
        #   result = obj.getUnorderedSet()           # Returns set
        #   obj.sumUnorderedSet({1, 2, 3})           # Pass set
        #   exists = obj.hasValueUnorderedSet(s, 42) # O(1) membership test
        #   found = obj.findUnorderedSet(s, 42)      # O(1) lookup
        # ---------------------------------------------------------------------
        libcpp_unordered_set[int] getUnorderedSet()
        int sumUnorderedSet(libcpp_unordered_set[int]& s)
        bool hasValueUnorderedSet(libcpp_unordered_set[int]& s, int value)
        size_t countUnorderedSet(libcpp_unordered_set[int]& s, int value)
        int findUnorderedSet(libcpp_unordered_set[int]& s, int value)

        # =====================================================================
        # std::deque<int> - Double-ended queue
        # =====================================================================
        # Python usage:
        #   result = obj.getDeque()                  # Returns list
        #   obj.sumDeque([1, 2, 3])                  # Pass list
        #   obj.doubleDequeElements(data)            # Modifies list in-place
        # ---------------------------------------------------------------------
        libcpp_deque[int] getDeque()
        int sumDeque(libcpp_deque[int]& d)
        void doubleDequeElements(libcpp_deque[int]& d)

        # =====================================================================
        # std::list<double> - Doubly-linked list
        # =====================================================================
        # Python usage:
        #   result = obj.getList()                   # Returns list
        #   obj.sumList([1.0, 2.0])                  # Pass list
        #   obj.doubleListElements(data)             # Modifies list in-place
        # ---------------------------------------------------------------------
        libcpp_list[double] getList()
        double sumList(libcpp_list[double]& l)
        void doubleListElements(libcpp_list[double]& l)

        # =====================================================================
        # std::optional<int> - Nullable value (C++17)
        # =====================================================================
        # Python usage:
        #   result = obj.getOptionalValue(True)      # Returns 42 or None
        #   obj.unwrapOptional(100)                  # Pass value
        #   obj.unwrapOptional(None)                 # Pass empty optional
        # ---------------------------------------------------------------------
        libcpp_optional[int] getOptionalValue(bool hasValue)
        int unwrapOptional(libcpp_optional[int] opt)

        # =====================================================================
        # std::string_view - Non-owning string reference (C++17)
        # =====================================================================
        # Python usage:
        #   length = obj.getStringViewLength(b"hi")  # Pass bytes
        #   result = obj.stringViewToString(b"hi")   # Returns bytes
        # Note: string_view is a non-owning reference - the source must remain
        #       valid during the call.
        # ---------------------------------------------------------------------
        size_t getStringViewLength(libcpp_string_view sv)
        libcpp_string stringViewToString(libcpp_string_view sv)
