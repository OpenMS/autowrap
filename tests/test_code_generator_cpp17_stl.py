"""
C++17 STL Container Support Tests
=================================

This module tests autowrap's support for C++17 STL containers. These containers
are automatically converted between Python and C++ types:

Container Mappings:
    std::unordered_map<K,V>  <->  Python dict    (hash-based, O(1) average lookup)
    std::unordered_set<T>    <->  Python set     (hash-based, O(1) average lookup)
    std::deque<T>            <->  Python list    (double-ended queue)
    std::list<T>             <->  Python list    (doubly-linked list)
    std::optional<T>         <->  Python T|None  (nullable values)
    std::string_view         <->  Python bytes   (non-owning string reference)

Usage Examples:
    # Returning containers from C++
    result = obj.getUnorderedMap()        # Returns Python dict
    result = obj.getUnorderedSet()        # Returns Python set

    # Passing containers to C++
    obj.processMap({b"key": 42})          # Pass Python dict
    obj.processSet({1, 2, 3})             # Pass Python set

    # Hash-based lookups (O(1) average)
    value = obj.lookupMap(my_dict, b"key")    # Direct key lookup
    exists = obj.hasKey(my_dict, b"key")      # Check key exists
    found = obj.findInSet(my_set, item)       # Set membership test

    # Optional values
    result = obj.getOptional(True)    # Returns value or None
    obj.processOptional(None)         # Pass None for empty optional

Note: Requires C++17 compilation flag (-std=c++17) for optional and string_view.
"""
from __future__ import print_function
from __future__ import absolute_import

import os
import pytest
import autowrap
import autowrap.Utils

test_files = os.path.join(os.path.dirname(__file__), "test_files")


def test_cpp17_stl_containers():
    """
    Test C++17 STL container code generation and runtime behavior.

    This test verifies:
    1. Code generation produces correct Cython imports and method signatures
    2. Container conversions work correctly at runtime
    3. Hash-based lookups (find, count, at) work correctly
    4. Mutable references allow in-place modification
    5. Optional values handle None correctly
    """
    target = os.path.join(test_files, "generated", "cpp17_stl_test.pyx")

    include_dirs = autowrap.parse_and_generate_code(
        ["cpp17_stl_test.pxd"], root=test_files, target=target, debug=True
    )

    # Read the generated file to verify converters worked
    with open(target) as f:
        pyx_content = f.read()

    # =========================================================================
    # Verify code generation: check required imports are present
    # =========================================================================
    assert "libcpp.unordered_map" in pyx_content, \
        "unordered_map import should be present"
    assert "libcpp.unordered_set" in pyx_content, \
        "unordered_set import should be present"
    assert "libcpp.deque" in pyx_content, \
        "deque import should be present"
    assert "libcpp.list" in pyx_content, \
        "list import should be present"
    assert "libcpp.optional" in pyx_content, \
        "optional import should be present"
    assert "libcpp.string_view" in pyx_content, \
        "string_view import should be present"

    # Verify all methods are generated
    assert "def getUnorderedMap(" in pyx_content
    assert "def sumUnorderedMapValues(" in pyx_content
    assert "def lookupUnorderedMap(" in pyx_content
    assert "def hasKeyUnorderedMap(" in pyx_content
    assert "def getValueUnorderedMap(" in pyx_content
    assert "def getUnorderedSet(" in pyx_content
    assert "def sumUnorderedSet(" in pyx_content
    assert "def hasValueUnorderedSet(" in pyx_content
    assert "def countUnorderedSet(" in pyx_content
    assert "def findUnorderedSet(" in pyx_content
    assert "def getDeque(" in pyx_content
    assert "def sumDeque(" in pyx_content
    assert "def doubleDequeElements(" in pyx_content
    assert "def getList(" in pyx_content
    assert "def sumList(" in pyx_content
    assert "def doubleListElements(" in pyx_content
    assert "def getOptionalValue(" in pyx_content
    assert "def unwrapOptional(" in pyx_content
    assert "def getStringViewLength(" in pyx_content
    assert "def stringViewToString(" in pyx_content

    # Verify optional uses has_value() check
    assert "has_value()" in pyx_content, \
        "optional should use has_value() check"

    # =========================================================================
    # Compile and run runtime tests
    # =========================================================================
    mod = autowrap.Utils.compile_and_import(
        "cpp17_stl_test_module",
        [target],
        include_dirs,
    )

    obj = mod._Cpp17STLTest()

    # =========================================================================
    # Test: std::unordered_map<string, int> -> Python dict
    # =========================================================================

    # Test returning unordered_map from C++
    result_map = obj.getUnorderedMap()
    assert isinstance(result_map, dict), "unordered_map should return dict"
    assert result_map == {b"one": 1, b"two": 2, b"three": 3}, \
        f"Unexpected map result: {result_map}"

    # Test passing dict to C++ (iteration)
    sum_result = obj.sumUnorderedMapValues({b"a": 10, b"b": 20})
    assert sum_result == 30, f"sumUnorderedMapValues returned {sum_result}"

    # Test hash-based key lookup using find()
    test_map = {b"apple": 100, b"banana": 200, b"cherry": 300}
    lookup_result = obj.lookupUnorderedMap(test_map, b"banana")
    assert lookup_result == 200, \
        f"lookupUnorderedMap('banana') returned {lookup_result}, expected 200"

    lookup_missing = obj.lookupUnorderedMap(test_map, b"grape")
    assert lookup_missing == -1, \
        f"lookupUnorderedMap('grape') should return -1 for missing key"

    # Test hash-based key existence check using count()
    assert obj.hasKeyUnorderedMap(test_map, b"apple") is True, \
        "hasKeyUnorderedMap('apple') should be True"
    assert obj.hasKeyUnorderedMap(test_map, b"grape") is False, \
        "hasKeyUnorderedMap('grape') should be False"

    # Test at() accessor (throws on missing key)
    value_result = obj.getValueUnorderedMap(test_map, b"cherry")
    assert value_result == 300, \
        f"getValueUnorderedMap('cherry') returned {value_result}, expected 300"

    # Verify at() throws exception for missing key
    try:
        obj.getValueUnorderedMap(test_map, b"missing")
        assert False, "getValueUnorderedMap should raise exception for missing key"
    except Exception:
        pass  # Expected - std::out_of_range from at()

    # =========================================================================
    # Test: std::unordered_set<int> -> Python set
    # =========================================================================

    # Test returning unordered_set from C++
    result_set = obj.getUnorderedSet()
    assert isinstance(result_set, set), "unordered_set should return set"
    assert result_set == {1, 2, 3, 4, 5}, f"Unexpected set result: {result_set}"

    # Test passing set to C++ (iteration)
    sum_set_result = obj.sumUnorderedSet({10, 20, 30})
    assert sum_set_result == 60, f"sumUnorderedSet returned {sum_set_result}"

    # Test hash-based membership check using count()
    test_set = {100, 200, 300, 400}
    assert obj.hasValueUnorderedSet(test_set, 200) is True, \
        "hasValueUnorderedSet(200) should be True"
    assert obj.hasValueUnorderedSet(test_set, 999) is False, \
        "hasValueUnorderedSet(999) should be False"

    # Test count() returns 0 or 1
    assert obj.countUnorderedSet(test_set, 300) == 1, \
        "countUnorderedSet(300) should be 1"
    assert obj.countUnorderedSet(test_set, 999) == 0, \
        "countUnorderedSet(999) should be 0"

    # Test hash-based find()
    find_result = obj.findUnorderedSet(test_set, 400)
    assert find_result == 400, \
        f"findUnorderedSet(400) returned {find_result}, expected 400"

    find_missing = obj.findUnorderedSet(test_set, 999)
    assert find_missing == -1, \
        f"findUnorderedSet(999) should return -1 for missing element"

    # =========================================================================
    # Test: std::deque<int> -> Python list
    # =========================================================================

    # Test returning deque from C++
    result_deque = obj.getDeque()
    assert isinstance(result_deque, list), "deque should return list"
    assert result_deque == [10, 20, 30, 40], \
        f"Unexpected deque result: {result_deque}"

    # Test passing list to C++ deque
    sum_deque_result = obj.sumDeque([5, 10, 15])
    assert sum_deque_result == 30, f"sumDeque returned {sum_deque_result}"

    # Test mutable reference: modifications are reflected back to Python
    deque_data = [1, 2, 3, 4]
    obj.doubleDequeElements(deque_data)
    assert deque_data == [2, 4, 6, 8], \
        f"doubleDequeElements should modify list in place: {deque_data}"

    # =========================================================================
    # Test: std::list<double> -> Python list
    # =========================================================================

    # Test returning std::list from C++
    result_list = obj.getList()
    assert isinstance(result_list, list), "std::list should return list"
    expected_list = [1.1, 2.2, 3.3]
    for i, (r, e) in enumerate(zip(result_list, expected_list)):
        assert abs(r - e) < 0.0001, f"Unexpected list value at {i}: {r} vs {e}"

    # Test passing list to C++ std::list
    sum_list_result = obj.sumList([1.0, 2.0, 3.0])
    assert abs(sum_list_result - 6.0) < 0.0001, \
        f"sumList returned {sum_list_result}"

    # Test mutable reference
    list_data = [1.0, 2.0, 3.0]
    obj.doubleListElements(list_data)
    expected_doubled = [2.0, 4.0, 6.0]
    for i, (r, e) in enumerate(zip(list_data, expected_doubled)):
        assert abs(r - e) < 0.0001, \
            f"doubleListElements should modify list in place: {list_data}"

    # =========================================================================
    # Test: std::optional<int> -> Python int | None
    # =========================================================================

    # Test returning optional with value
    opt_with_value = obj.getOptionalValue(True)
    assert opt_with_value == 42, \
        f"Optional with value should return 42, got {opt_with_value}"

    # Test returning empty optional -> None
    opt_without_value = obj.getOptionalValue(False)
    assert opt_without_value is None, \
        f"Optional without value should return None, got {opt_without_value}"

    # Test passing value to optional parameter
    unwrap_result = obj.unwrapOptional(100)
    assert unwrap_result == 100, f"unwrapOptional(100) returned {unwrap_result}"

    # Test passing None for empty optional
    unwrap_none_result = obj.unwrapOptional(None)
    assert unwrap_none_result == -1, \
        f"unwrapOptional(None) returned {unwrap_none_result}"

    # =========================================================================
    # Test: std::string_view -> Python bytes
    # =========================================================================

    # Test passing string_view to C++
    length = obj.getStringViewLength(b"hello")
    assert length == 5, f"getStringViewLength('hello') returned {length}"

    # Test returning string from string_view
    string_result = obj.stringViewToString(b"test")
    assert string_result == b"test", \
        f"stringViewToString('test') returned {string_result}"
