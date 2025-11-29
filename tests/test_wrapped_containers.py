"""
Tests for STL containers of wrapped classes and nested containers.

This test file verifies that autowrap correctly handles:
- vector<WrappedClass> (by value)
- set<WrappedClass> (by value)
- map<int, WrappedClass>, map<WrappedClass, int>
- Nested containers: vector<vector<WrappedClass>> (input only)
- map<WrappedClass, vector<int>>
"""
from __future__ import print_function
from __future__ import absolute_import

import pytest
import os

import autowrap.DeclResolver
import autowrap.CodeGenerator
import autowrap.PXDParser
import autowrap.Utils
import autowrap

test_files = os.path.join(os.path.dirname(__file__), "test_files")


@pytest.fixture(scope="module")
def wrapped_container_module():
    """Compile and import the wrapped_container_test module."""
    # Note: output file must have different name than input .pxd to avoid
    # Cython "redeclared" errors when both files are in the include path
    target = os.path.join(test_files, "wrapped_container_wrapper.pyx")

    include_dirs = autowrap.parse_and_generate_code(
        ["wrapped_container_test.pxd"], root=test_files, target=target, debug=True
    )

    module = autowrap.Utils.compile_and_import(
        "wrapped_container_wrapper",
        [target],
        include_dirs,
    )
    return module


class TestVectorOfWrappedClass:
    """Tests for vector<Item> (wrapped class by value)."""

    def test_vector_items_sum(self, wrapped_container_module):
        """Test passing vector<Item> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(10)
        item2 = m.Item(20)
        item3 = m.Item(30)
        items = [item1, item2, item3]

        result = t.sumVectorItems(items)
        assert result == 60  # 10 + 20 + 30

    def test_vector_items_create(self, wrapped_container_module):
        """Test returning vector<Item>."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        items = t.createVectorItems(3)
        assert len(items) == 3
        assert items[0].value_ == 0
        assert items[1].value_ == 10
        assert items[2].value_ == 20

    def test_vector_items_append(self, wrapped_container_module):
        """Test modifying vector<Item> in place."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        items = [m.Item(1), m.Item(2)]
        assert len(items) == 2

        t.appendToVector(items, 100)
        assert len(items) == 3
        assert items[2].value_ == 100

    def test_vector_items_empty(self, wrapped_container_module):
        """Test with empty vector."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        items = []
        result = t.sumVectorItems(items)
        assert result == 0


class TestSetOfWrappedClass:
    """Tests for set<Item> (wrapped class by value)."""

    def test_set_items_sum(self, wrapped_container_module):
        """Test passing set<Item> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(10)
        item2 = m.Item(20)
        item3 = m.Item(30)
        items = {item1, item2, item3}

        result = t.sumSetItems(items)
        assert result == 60

    def test_set_items_create(self, wrapped_container_module):
        """Test returning set<Item>."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        items = t.createSetItems(3)
        assert len(items) == 3
        values = sorted([item.value_ for item in items])
        assert values == [0, 10, 20]


class TestMapWithWrappedClassValue:
    """Tests for map<int, Item>."""

    def test_map_int_to_item_sum(self, wrapped_container_module):
        """Test passing map<int, Item> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(100)
        item2 = m.Item(200)
        map_data = {1: item1, 2: item2}

        result = t.sumMapValues(map_data)
        assert result == 300

    def test_map_int_to_item_create(self, wrapped_container_module):
        """Test returning map<int, Item>."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        result = t.createMapIntToItem(3)
        assert len(result) == 3
        assert result[0].value_ == 0
        assert result[1].value_ == 10
        assert result[2].value_ == 20

    def test_map_int_to_item_lookup(self, wrapped_container_module):
        """Test looking up Item by key in map."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(100)
        item2 = m.Item(200)
        item3 = m.Item(300)
        map_data = {1: item1, 5: item2, 10: item3}

        # Lookup existing keys
        assert t.lookupMapIntToItem(map_data, 1) == 100
        assert t.lookupMapIntToItem(map_data, 5) == 200
        assert t.lookupMapIntToItem(map_data, 10) == 300

        # Lookup missing key
        assert t.lookupMapIntToItem(map_data, 999) == -1

    def test_map_int_to_item_has_key(self, wrapped_container_module):
        """Test checking if key exists in map."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(100)
        item2 = m.Item(200)
        map_data = {1: item1, 2: item2}

        assert t.hasKeyMapIntToItem(map_data, 1) is True
        assert t.hasKeyMapIntToItem(map_data, 2) is True
        assert t.hasKeyMapIntToItem(map_data, 3) is False
        assert t.hasKeyMapIntToItem(map_data, 999) is False


class TestMapWithWrappedClassKey:
    """Tests for map<Item, int>."""

    def test_map_item_to_int_sum(self, wrapped_container_module):
        """Test passing map<Item, int> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(10)
        item2 = m.Item(20)
        map_data = {item1: 100, item2: 200}

        result = t.sumMapKeys(map_data)
        assert result == 30  # 10 + 20 (sum of keys)

    def test_map_item_to_int_create(self, wrapped_container_module):
        """Test returning map<Item, int>."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        result = t.createMapItemToInt(3)
        assert len(result) == 3
        # Values should be 0, 10, 20 for keys with value_ 0, 1, 2
        keys_values = [(k.value_, v) for k, v in result.items()]
        keys_values.sort()
        assert keys_values == [(0, 0), (1, 10), (2, 20)]


class TestNestedVectorOfWrappedClass:
    """Tests for vector<vector<Item>> (input only - output not supported)."""

    def test_nested_vector_sum(self, wrapped_container_module):
        """Test passing vector<vector<Item>> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        inner1 = [m.Item(1), m.Item(2)]
        inner2 = [m.Item(3), m.Item(4)]
        nested = [inner1, inner2]

        result = t.sumNestedVector(nested)
        assert result == 10  # 1 + 2 + 3 + 4

    def test_nested_vector_modify(self, wrapped_container_module):
        """Test modifying vector<vector<Item>> in place."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        inner1 = [m.Item(1)]
        inner2 = [m.Item(2)]
        nested = [inner1, inner2]

        t.appendToNestedVector(nested)
        # Each inner vector should have Item(999) appended
        assert len(nested[0]) == 2
        assert len(nested[1]) == 2
        assert nested[0][1].value_ == 999
        assert nested[1][1].value_ == 999


class TestMapWithWrappedClassBoth:
    """Tests for map<Item, Item> - wrapped class as both key and value."""

    def test_map_item_to_item_sum(self, wrapped_container_module):
        """Test passing map<Item, Item> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        key1 = m.Item(1)
        val1 = m.Item(100)
        key2 = m.Item(2)
        val2 = m.Item(200)
        map_data = {key1: val1, key2: val2}

        result = t.sumMapBoth(map_data)
        assert result == 303  # (1 + 100) + (2 + 200)

    def test_map_item_to_item_create(self, wrapped_container_module):
        """Test returning map<Item, Item>."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        result = t.createMapItemToItem(3)
        assert len(result) == 3
        # Keys have value_ 0, 1, 2 and values have value_ 0, 100, 200
        for key, val in result.items():
            assert val.value_ == key.value_ * 100


class TestMapWithWrappedKeyVectorValue:
    """Tests for map<Item, vector<int>> - wrapped class as key, primitive vector as value."""

    def test_map_item_to_vec_int_sum(self, wrapped_container_module):
        """Test passing map<Item, vector<int>> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(10)
        item2 = m.Item(20)
        map_data = {item1: [1, 2, 3], item2: [4, 5]}

        result = t.sumMapItemToVecInt(map_data)
        # Keys: 10 + 20 = 30
        # Values: 1+2+3+4+5 = 15
        assert result == 45


class TestUnorderedMapWithWrappedClassKey:
    """Tests for unordered_map<Item, int> - wrapped class as key."""

    def test_unordered_map_item_to_int_sum(self, wrapped_container_module):
        """Test passing unordered_map<Item, int> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(10)
        item2 = m.Item(20)
        map_data = {item1: 100, item2: 200}

        result = t.sumUnorderedMapKeys(map_data)
        assert result == 30  # 10 + 20 (sum of keys)

    def test_unordered_map_item_to_int_create(self, wrapped_container_module):
        """Test returning unordered_map<Item, int>."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        result = t.createUnorderedMapItemToInt(3)
        assert len(result) == 3
        # Values should be 0, 10, 20 for keys with value_ 0, 1, 2
        keys_values = [(k.value_, v) for k, v in result.items()]
        keys_values.sort()
        assert keys_values == [(0, 0), (1, 10), (2, 20)]


class TestUnorderedMapWithWrappedClassValue:
    """Tests for unordered_map<int, Item> - wrapped class as value."""

    def test_unordered_map_int_to_item_sum(self, wrapped_container_module):
        """Test passing unordered_map<int, Item> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(100)
        item2 = m.Item(200)
        map_data = {1: item1, 2: item2}

        result = t.sumUnorderedMapValues(map_data)
        assert result == 300

    def test_unordered_map_int_to_item_create(self, wrapped_container_module):
        """Test returning unordered_map<int, Item>."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        result = t.createUnorderedMapIntToItem(3)
        assert len(result) == 3
        assert result[0].value_ == 0
        assert result[1].value_ == 10
        assert result[2].value_ == 20

    def test_unordered_map_int_to_item_lookup(self, wrapped_container_module):
        """Test looking up Item by key in unordered_map (hash-based O(1) lookup)."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(100)
        item2 = m.Item(200)
        item3 = m.Item(300)
        map_data = {1: item1, 5: item2, 10: item3}

        # Lookup existing keys - tests hash-based access
        assert t.lookupUnorderedMapIntToItem(map_data, 1) == 100
        assert t.lookupUnorderedMapIntToItem(map_data, 5) == 200
        assert t.lookupUnorderedMapIntToItem(map_data, 10) == 300

        # Lookup missing key
        assert t.lookupUnorderedMapIntToItem(map_data, 999) == -1

    def test_unordered_map_int_to_item_has_key(self, wrapped_container_module):
        """Test checking if key exists in unordered_map (hash-based O(1) lookup)."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(100)
        item2 = m.Item(200)
        map_data = {1: item1, 2: item2}

        assert t.hasKeyUnorderedMapIntToItem(map_data, 1) is True
        assert t.hasKeyUnorderedMapIntToItem(map_data, 2) is True
        assert t.hasKeyUnorderedMapIntToItem(map_data, 3) is False
        assert t.hasKeyUnorderedMapIntToItem(map_data, 999) is False


class TestUnorderedMapWithWrappedClassBoth:
    """Tests for unordered_map<Item, Item> - wrapped class as both key and value."""

    def test_unordered_map_item_to_item_sum(self, wrapped_container_module):
        """Test passing unordered_map<Item, Item> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        key1 = m.Item(1)
        val1 = m.Item(100)
        key2 = m.Item(2)
        val2 = m.Item(200)
        map_data = {key1: val1, key2: val2}

        result = t.sumUnorderedMapBoth(map_data)
        assert result == 303  # (1 + 100) + (2 + 200)

    def test_unordered_map_item_to_item_create(self, wrapped_container_module):
        """Test returning unordered_map<Item, Item>."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        result = t.createUnorderedMapItemToItem(3)
        assert len(result) == 3
        # Keys have value_ 0, 1, 2 and values have value_ 0, 100, 200
        for key, val in result.items():
            assert val.value_ == key.value_ * 100


class TestUnorderedMapWithWrappedKeyVectorValue:
    """Tests for unordered_map<Item, vector<int>> - wrapped class as key, primitive vector as value."""

    def test_unordered_map_item_to_vec_int_sum(self, wrapped_container_module):
        """Test passing unordered_map<Item, vector<int>> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(10)
        item2 = m.Item(20)
        map_data = {item1: [1, 2, 3], item2: [4, 5]}

        result = t.sumUnorderedMapItemToVecInt(map_data)
        # Keys: 10 + 20 = 30
        # Values: 1+2+3+4+5 = 15
        assert result == 45


class TestListOfWrappedClass:
    """Tests for list<Item> (wrapped class by value)."""

    def test_list_items_sum(self, wrapped_container_module):
        """Test passing list<Item> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(10)
        item2 = m.Item(20)
        item3 = m.Item(30)
        items = [item1, item2, item3]

        result = t.sumListItems(items)
        assert result == 60  # 10 + 20 + 30

    def test_list_items_create(self, wrapped_container_module):
        """Test returning list<Item>."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        items = t.createListItems(3)
        assert len(items) == 3
        assert items[0].value_ == 0
        assert items[1].value_ == 10
        assert items[2].value_ == 20


class TestDequeOfWrappedClass:
    """Tests for deque<Item> (wrapped class by value)."""

    def test_deque_items_sum(self, wrapped_container_module):
        """Test passing deque<Item> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(10)
        item2 = m.Item(20)
        item3 = m.Item(30)
        items = [item1, item2, item3]

        result = t.sumDequeItems(items)
        assert result == 60  # 10 + 20 + 30

    def test_deque_items_create(self, wrapped_container_module):
        """Test returning deque<Item>."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        items = t.createDequeItems(3)
        assert len(items) == 3
        assert items[0].value_ == 0
        assert items[1].value_ == 10
        assert items[2].value_ == 20


class TestUnorderedSetOfWrappedClass:
    """Tests for unordered_set<Item> (wrapped class by value)."""

    def test_unordered_set_items_sum(self, wrapped_container_module):
        """Test passing unordered_set<Item> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(10)
        item2 = m.Item(20)
        item3 = m.Item(30)
        items = {item1, item2, item3}

        result = t.sumUnorderedSetItems(items)
        assert result == 60

    def test_unordered_set_items_create(self, wrapped_container_module):
        """Test returning unordered_set<Item>."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        items = t.createUnorderedSetItems(3)
        assert len(items) == 3
        values = sorted([item.value_ for item in items])
        assert values == [0, 10, 20]

    def test_unordered_set_has_item(self, wrapped_container_module):
        """Test checking if Item exists in unordered_set (hash-based O(1) membership test)."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(10)
        item2 = m.Item(20)
        item3 = m.Item(30)
        items = {item1, item2, item3}

        # Items that should be found (tests hash function)
        search_item1 = m.Item(10)
        search_item2 = m.Item(20)
        assert t.hasItemUnorderedSet(items, search_item1) is True
        assert t.hasItemUnorderedSet(items, search_item2) is True

        # Item that should NOT be found
        missing_item = m.Item(999)
        assert t.hasItemUnorderedSet(items, missing_item) is False

    def test_unordered_set_find_item(self, wrapped_container_module):
        """Test finding Item in unordered_set and returning its value (hash-based O(1) lookup)."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        item1 = m.Item(10)
        item2 = m.Item(20)
        item3 = m.Item(30)
        items = {item1, item2, item3}

        # Find existing items - tests hash-based lookup
        search_item1 = m.Item(10)
        search_item2 = m.Item(30)
        assert t.findItemUnorderedSet(items, search_item1) == 10
        assert t.findItemUnorderedSet(items, search_item2) == 30

        # Find missing item should return -1
        missing_item = m.Item(999)
        assert t.findItemUnorderedSet(items, missing_item) == -1

    def test_unordered_set_two_member_hash(self, wrapped_container_module):
        """Test that hash function uses both value_ AND name_ members.

        This verifies that items with the same value_ but different name_
        are treated as different items (different hash + equality check).
        """
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        # Create items with same value but different names
        item_alice = m.Item(100, b"alice")
        item_bob = m.Item(100, b"bob")
        item_charlie = m.Item(200, b"charlie")

        items = {item_alice, item_bob, item_charlie}

        # All three should be in the set (even though two have same value_)
        assert len(items) == 3, "Set should have 3 items despite same value_"

        # Search for exact match (value_ AND name_ must match)
        search_alice = m.Item(100, b"alice")
        search_bob = m.Item(100, b"bob")

        assert t.hasItemUnorderedSet(items, search_alice) is True, \
            "Should find alice (100, 'alice')"
        assert t.hasItemUnorderedSet(items, search_bob) is True, \
            "Should find bob (100, 'bob')"

        # Search with wrong name should NOT find item
        # Same value_ but different name_ = different hash/different item
        wrong_name = m.Item(100, b"eve")
        assert t.hasItemUnorderedSet(items, wrong_name) is False, \
            "Should NOT find (100, 'eve') - name doesn't match"

        # Search with wrong value should NOT find item
        wrong_value = m.Item(999, b"alice")
        assert t.hasItemUnorderedSet(items, wrong_value) is False, \
            "Should NOT find (999, 'alice') - value doesn't match"


class TestNestedListOfVectors:
    """Tests for list<vector<int>> - nested containers with primitives."""

    def test_list_of_vectors_sum(self, wrapped_container_module):
        """Test passing list<vector<int>> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        data = [[1, 2, 3], [4, 5], [6]]
        result = t.sumListOfVectors(data)
        assert result == 21  # 1+2+3+4+5+6


class TestNestedDequeOfVectors:
    """Tests for deque<vector<int>> - nested containers with primitives."""

    def test_deque_of_vectors_sum(self, wrapped_container_module):
        """Test passing deque<vector<int>> by reference."""
        m = wrapped_container_module
        t = m.WrappedContainerTest()

        data = [[1, 2, 3], [4, 5], [6]]
        result = t.sumDequeOfVectors(data)
        assert result == 21  # 1+2+3+4+5+6


class TestItemClass:
    """Tests for the Item wrapped class itself."""

    def test_item_constructors(self, wrapped_container_module):
        """Test Item constructors."""
        m = wrapped_container_module

        # Default constructor
        item1 = m.Item()
        assert item1.value_ == 0

        # Single arg constructor
        item2 = m.Item(42)
        assert item2.value_ == 42

        # Two arg constructor
        item3 = m.Item(100, b"test")
        assert item3.value_ == 100
        assert item3.name_ == b"test"

    def test_item_methods(self, wrapped_container_module):
        """Test Item methods."""
        m = wrapped_container_module

        item = m.Item(10, b"myitem")
        assert item.getValue() == 10
        assert item.getName() == b"myitem"

        item.setValue(99)
        assert item.getValue() == 99
        assert item.value_ == 99

    def test_item_copy(self, wrapped_container_module):
        """Test Item copy constructor."""
        m = wrapped_container_module

        item1 = m.Item(42, b"original")
        item2 = m.Item(item1)
        assert item2.value_ == 42
        assert item2.name_ == b"original"

        # Modify original shouldn't affect copy
        item1.value_ = 100
        assert item2.value_ == 42
