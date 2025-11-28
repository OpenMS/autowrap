"""
Tests for new STL container support in autowrap.
Tests: unordered_map, unordered_set, deque, list, optional, string_view
"""
from __future__ import print_function
from __future__ import absolute_import

import os
import pytest
import autowrap
import autowrap.Utils

test_files = os.path.join(os.path.dirname(__file__), "test_files")


def test_new_stl_code_generation():
    """Test code generation for new STL containers."""
    target = os.path.join(test_files, "new_stl_test.pyx")

    include_dirs = autowrap.parse_and_generate_code(
        ["new_stl_test.pxd"], root=test_files, target=target, debug=True
    )

    # Read the generated file to verify converters worked
    with open(target) as f:
        pyx_content = f.read()

    # Check that all imports are present
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

    # Check that all methods are generated
    assert "def getUnorderedMap(" in pyx_content, \
        "getUnorderedMap method should be generated"
    assert "def sumUnorderedMapValues(" in pyx_content, \
        "sumUnorderedMapValues method should be generated"
    assert "def getUnorderedSet(" in pyx_content, \
        "getUnorderedSet method should be generated"
    assert "def sumUnorderedSet(" in pyx_content, \
        "sumUnorderedSet method should be generated"
    assert "def getDeque(" in pyx_content, \
        "getDeque method should be generated"
    assert "def sumDeque(" in pyx_content, \
        "sumDeque method should be generated"
    assert "def doubleDequeElements(" in pyx_content, \
        "doubleDequeElements method should be generated"
    assert "def getList(" in pyx_content, \
        "getList method should be generated"
    assert "def sumList(" in pyx_content, \
        "sumList method should be generated"
    assert "def doubleListElements(" in pyx_content, \
        "doubleListElements method should be generated"
    assert "def getOptionalValue(" in pyx_content, \
        "getOptionalValue method should be generated"
    assert "def unwrapOptional(" in pyx_content, \
        "unwrapOptional method should be generated"
    assert "def getStringViewLength(" in pyx_content, \
        "getStringViewLength method should be generated"
    assert "def stringViewToString(" in pyx_content, \
        "stringViewToString method should be generated"

    # Check optional-specific patterns
    assert "has_value()" in pyx_content, \
        "optional should use has_value() check"

    # Compile and import for runtime tests
    mod = autowrap.Utils.compile_and_import(
        "new_stl_test_module",
        [target],
        include_dirs,
    )

    # Create the test object (class name is _NewSTLTest due to pxd naming)
    obj = mod._NewSTLTest()

    # Test unordered_map
    result_map = obj.getUnorderedMap()
    assert isinstance(result_map, dict), "unordered_map should return dict"
    assert result_map == {b"one": 1, b"two": 2, b"three": 3}, \
        f"Unexpected map result: {result_map}"

    sum_result = obj.sumUnorderedMapValues({b"a": 10, b"b": 20})
    assert sum_result == 30, f"sumUnorderedMapValues returned {sum_result}"

    # Test unordered_set
    result_set = obj.getUnorderedSet()
    assert isinstance(result_set, set), "unordered_set should return set"
    assert result_set == {1, 2, 3, 4, 5}, f"Unexpected set result: {result_set}"

    sum_set_result = obj.sumUnorderedSet({10, 20, 30})
    assert sum_set_result == 60, f"sumUnorderedSet returned {sum_set_result}"

    # Test deque
    result_deque = obj.getDeque()
    assert isinstance(result_deque, list), "deque should return list"
    assert result_deque == [10, 20, 30, 40], f"Unexpected deque result: {result_deque}"

    sum_deque_result = obj.sumDeque([5, 10, 15])
    assert sum_deque_result == 30, f"sumDeque returned {sum_deque_result}"

    # Test deque mutable reference (cleanup code)
    deque_data = [1, 2, 3, 4]
    obj.doubleDequeElements(deque_data)
    assert deque_data == [2, 4, 6, 8], f"doubleDequeElements should modify list in place: {deque_data}"

    # Test list (std::list)
    result_list = obj.getList()
    assert isinstance(result_list, list), "std::list should return list"
    expected_list = [1.1, 2.2, 3.3]
    for i, (r, e) in enumerate(zip(result_list, expected_list)):
        assert abs(r - e) < 0.0001, f"Unexpected list value at {i}: {r} vs {e}"

    sum_list_result = obj.sumList([1.0, 2.0, 3.0])
    assert abs(sum_list_result - 6.0) < 0.0001, f"sumList returned {sum_list_result}"

    # Test list mutable reference (cleanup code)
    list_data = [1.0, 2.0, 3.0]
    obj.doubleListElements(list_data)
    expected_doubled = [2.0, 4.0, 6.0]
    for i, (r, e) in enumerate(zip(list_data, expected_doubled)):
        assert abs(r - e) < 0.0001, f"doubleListElements should modify list in place: {list_data}"

    # Test optional
    opt_with_value = obj.getOptionalValue(True)
    assert opt_with_value == 42, f"Optional with value should return 42, got {opt_with_value}"

    opt_without_value = obj.getOptionalValue(False)
    assert opt_without_value is None, f"Optional without value should return None, got {opt_without_value}"

    unwrap_result = obj.unwrapOptional(100)
    assert unwrap_result == 100, f"unwrapOptional(100) returned {unwrap_result}"

    # Test passing None for empty optional
    unwrap_none_result = obj.unwrapOptional(None)
    assert unwrap_none_result == -1, f"unwrapOptional(None) returned {unwrap_none_result}"

    # Test string_view
    length = obj.getStringViewLength(b"hello")
    assert length == 5, f"getStringViewLength('hello') returned {length}"

    string_result = obj.stringViewToString(b"test")
    assert string_result == b"test", \
        f"stringViewToString('test') returned {string_result}"
