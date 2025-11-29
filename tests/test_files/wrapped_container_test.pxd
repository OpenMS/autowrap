# cython: language_level=3
from libcpp.string cimport string as libcpp_string
from libcpp.vector cimport vector as libcpp_vector
from libcpp.map cimport map as libcpp_map
from libcpp.unordered_map cimport unordered_map as libcpp_unordered_map
from libcpp.set cimport set as libcpp_set
from libcpp.unordered_set cimport unordered_set as libcpp_unordered_set
from libcpp.list cimport list as libcpp_list
from libcpp.deque cimport deque as libcpp_deque
from libcpp.pair cimport pair as libcpp_pair
from libcpp cimport bool

cdef extern from "wrapped_container_test.hpp":

    # A simple wrapped class used in containers
    # wrap-hash and operator== enable Python dict/set lookups with d[item]
    cdef cppclass Item:
        # wrap-hash:
        #   getHashValue()

        int value_
        libcpp_string name_

        Item()
        Item(int v)
        Item(int v, libcpp_string n)
        Item(Item&)

        bool operator==(Item)
        bool operator!=(Item)

        int getValue()
        void setValue(int v)
        libcpp_string getName()
        size_t getHashValue()

    # Test class with methods that use containers of wrapped classes
    cdef cppclass WrappedContainerTest:
        WrappedContainerTest()

        # ========================================
        # VECTOR OF WRAPPED CLASS (by value)
        # These are supported - similar to libcpp_test.pxd process25
        # ========================================
        int sumVectorItems(libcpp_vector[Item]& items)
        libcpp_vector[Item] createVectorItems(int count)
        void appendToVector(libcpp_vector[Item]& items, int value)

        # ========================================
        # SET OF WRAPPED CLASS (by value)
        # Supported - similar to libcpp_test.pxd process11
        # ========================================
        int sumSetItems(libcpp_set[Item]& items)
        libcpp_set[Item] createSetItems(int count)

        # ========================================
        # MAP WITH WRAPPED CLASS AS VALUE
        # Supported - similar to libcpp_test.pxd process15, process19
        # ========================================
        int sumMapValues(libcpp_map[int, Item]& m)
        libcpp_map[int, Item] createMapIntToItem(int count)

        # ========================================
        # MAP WITH WRAPPED CLASS AS KEY
        # Supported - similar to libcpp_stl_test.pxd process_7_map
        # ========================================
        int sumMapKeys(libcpp_map[Item, int]& m)
        libcpp_map[Item, int] createMapItemToInt(int count)

        # ========================================
        # NESTED CONTAINERS: vector<vector<Item>>
        # Input supported, output needs manual handling
        # ========================================
        int sumNestedVector(libcpp_vector[libcpp_vector[Item]]& nested)
        void appendToNestedVector(libcpp_vector[libcpp_vector[Item]]& nested)

        # ========================================
        # MAP WITH WRAPPED KEY AND VECTOR VALUE (primitives only)
        # Supported - similar to libcpp_stl_test.pxd process_13_map
        # ========================================
        int sumMapItemToVecInt(libcpp_map[Item, libcpp_vector[int]]& m)

        # ========================================
        # MAP WITH WRAPPED CLASS AS BOTH KEY AND VALUE
        # ========================================
        int sumMapBoth(libcpp_map[Item, Item]& m)
        libcpp_map[Item, Item] createMapItemToItem(int count)

        # ========================================
        # UNORDERED_MAP WITH WRAPPED CLASS AS KEY
        # ========================================
        int sumUnorderedMapKeys(libcpp_unordered_map[Item, int]& m)
        libcpp_unordered_map[Item, int] createUnorderedMapItemToInt(int count)

        # ========================================
        # UNORDERED_MAP WITH WRAPPED CLASS AS VALUE
        # ========================================
        int sumUnorderedMapValues(libcpp_unordered_map[int, Item]& m)
        libcpp_unordered_map[int, Item] createUnorderedMapIntToItem(int count)

        # ========================================
        # UNORDERED_MAP WITH WRAPPED CLASS AS BOTH KEY AND VALUE
        # ========================================
        int sumUnorderedMapBoth(libcpp_unordered_map[Item, Item]& m)
        libcpp_unordered_map[Item, Item] createUnorderedMapItemToItem(int count)

        # ========================================
        # UNORDERED_MAP WITH WRAPPED KEY AND VECTOR VALUE (primitives only)
        # ========================================
        int sumUnorderedMapItemToVecInt(libcpp_unordered_map[Item, libcpp_vector[int]]& m)

        # ========================================
        # LIST OF WRAPPED CLASS (by value)
        # ========================================
        int sumListItems(libcpp_list[Item]& items)
        libcpp_list[Item] createListItems(int count)

        # ========================================
        # DEQUE OF WRAPPED CLASS (by value)
        # ========================================
        int sumDequeItems(libcpp_deque[Item]& items)
        libcpp_deque[Item] createDequeItems(int count)

        # ========================================
        # UNORDERED_SET OF WRAPPED CLASS (by value)
        # ========================================
        int sumUnorderedSetItems(libcpp_unordered_set[Item]& items)
        libcpp_unordered_set[Item] createUnorderedSetItems(int count)

        # ========================================
        # NESTED CONTAINERS: list<vector<int>>
        # ========================================
        int sumListOfVectors(libcpp_list[libcpp_vector[int]]& data)

        # ========================================
        # NESTED CONTAINERS: deque<vector<int>>
        # ========================================
        int sumDequeOfVectors(libcpp_deque[libcpp_vector[int]]& data)
