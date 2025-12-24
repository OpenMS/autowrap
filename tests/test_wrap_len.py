"""
Tests for the wrap-len annotation feature.

This test file verifies that autowrap correctly handles the wrap-len annotation
which generates the Python __len__ special method for wrapped C++ classes.

Test cases include:
- Basic wrap-len with size() method
- wrap-len with different method names (length(), count(), getSize())
- Container without wrap-len annotation (should NOT have __len__)
- wrap-len with wrap-ignored size() method (should still work)
- wrap-len with template classes
- wrap-len choosing between multiple potential methods
- Edge cases: empty containers, zero length
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
def wrap_len_module():
    """Compile and import the wrap_len_test module."""
    target = os.path.join(test_files, "generated", "wrap_len_wrapper.pyx")

    include_dirs = autowrap.parse_and_generate_code(
        ["wrap_len_test.pxd"], root=test_files, target=target, debug=True
    )

    module = autowrap.Utils.compile_and_import(
        "wrap_len_wrapper",
        [target],
        include_dirs,
    )
    return module


class TestBasicWrapLen:
    """Tests for basic wrap-len functionality with size() method."""

    def test_len_returns_correct_value(self, wrap_len_module):
        """Test that len() returns the correct size."""
        m = wrap_len_module
        container = m.BasicContainer(5)
        assert len(container) == 5

    def test_len_after_add(self, wrap_len_module):
        """Test len() updates after adding elements."""
        m = wrap_len_module
        container = m.BasicContainer()
        assert len(container) == 0

        container.add(10)
        assert len(container) == 1

        container.add(20)
        container.add(30)
        assert len(container) == 3

    def test_len_after_clear(self, wrap_len_module):
        """Test len() returns 0 after clearing."""
        m = wrap_len_module
        container = m.BasicContainer(10)
        assert len(container) == 10

        container.clear()
        assert len(container) == 0

    def test_len_with_empty_container(self, wrap_len_module):
        """Test len() with empty container."""
        m = wrap_len_module
        container = m.BasicContainer()
        assert len(container) == 0

    def test_len_in_boolean_context(self, wrap_len_module):
        """Test container in boolean context (relies on __len__)."""
        m = wrap_len_module

        empty = m.BasicContainer()
        non_empty = m.BasicContainer(3)

        # In Python, objects with __len__ returning 0 are falsy
        assert not empty  # Should be falsy (len == 0)
        assert non_empty  # Should be truthy (len > 0)


class TestLengthMethod:
    """Tests for wrap-len with length() method instead of size()."""

    def test_length_method(self, wrap_len_module):
        """Test wrap-len using length() method."""
        m = wrap_len_module
        container = m.LengthContainer()
        assert len(container) == 0

        container.append(b"hello")
        assert len(container) == 1

        container.append(b"world")
        assert len(container) == 2

    def test_length_int_return_type(self, wrap_len_module):
        """Test that int return type works correctly."""
        m = wrap_len_module
        container = m.LengthContainer()

        # Add multiple items
        for i in range(100):
            container.append(b"item")

        assert len(container) == 100


class TestCountMethod:
    """Tests for wrap-len with count() method."""

    def test_count_method(self, wrap_len_module):
        """Test wrap-len using count() method."""
        m = wrap_len_module
        container = m.CountContainer(5)
        assert len(container) == 5

    def test_count_increment_decrement(self, wrap_len_module):
        """Test len() after increment/decrement operations."""
        m = wrap_len_module
        container = m.CountContainer(10)
        assert len(container) == 10

        container.increment()
        assert len(container) == 11

        container.decrement()
        container.decrement()
        assert len(container) == 9

    def test_count_unsigned_int_return(self, wrap_len_module):
        """Test that unsigned int return type works correctly."""
        m = wrap_len_module
        container = m.CountContainer(0)
        assert len(container) == 0

        # Can't decrement below 0 (unsigned)
        container.decrement()
        assert len(container) == 0


class TestNoWrapLenAnnotation:
    """Tests for containers WITHOUT wrap-len annotation."""

    def test_no_len_method(self, wrap_len_module):
        """Test that container without wrap-len has no __len__."""
        m = wrap_len_module
        container = m.NoLenContainer()

        # Should NOT have __len__ method
        assert not hasattr(container, '__len__')

        # len() should raise TypeError
        with pytest.raises(TypeError):
            len(container)

    def test_size_method_still_accessible(self, wrap_len_module):
        """Test that size() method is still callable without __len__."""
        m = wrap_len_module
        container = m.NoLenContainer()
        container.push(1.0)
        container.push(2.0)

        # size() method should work
        assert container.size() == 2


class TestIgnoredSizeMethod:
    """Tests for wrap-len when size() method is wrap-ignored."""

    def test_len_works_with_ignored_size(self, wrap_len_module):
        """Test that __len__ works even when size() is wrap-ignored."""
        m = wrap_len_module
        container = m.IgnoredSizeContainer(5)

        # __len__ should work (calls C++ directly)
        assert len(container) == 5

    def test_size_method_not_exposed(self, wrap_len_module):
        """Test that size() method is NOT exposed in Python."""
        m = wrap_len_module
        container = m.IgnoredSizeContainer(5)

        # size() should NOT be accessible (wrap-ignore)
        assert not hasattr(container, 'size')

    def test_len_updates_correctly(self, wrap_len_module):
        """Test that len() updates correctly with ignored size()."""
        m = wrap_len_module
        container = m.IgnoredSizeContainer()
        assert len(container) == 0

        container.add(100)
        container.add(200)
        assert len(container) == 2


class TestGetSizeMethod:
    """Tests for wrap-len with getSize() method naming convention."""

    def test_get_size_method(self, wrap_len_module):
        """Test wrap-len using getSize() method."""
        m = wrap_len_module
        container = m.GetSizeContainer(42)
        assert len(container) == 42

    def test_get_size_set_size(self, wrap_len_module):
        """Test len() after setSize()."""
        m = wrap_len_module
        container = m.GetSizeContainer()
        assert len(container) == 0

        container.setSize(100)
        assert len(container) == 100

        container.setSize(0)
        assert len(container) == 0


class TestEmptyContainer:
    """Tests for container that always returns 0."""

    def test_always_empty(self, wrap_len_module):
        """Test container that always returns 0 for size."""
        m = wrap_len_module
        container = m.EmptyContainer()
        assert len(container) == 0

    def test_empty_is_falsy(self, wrap_len_module):
        """Test that empty container is falsy in boolean context."""
        m = wrap_len_module
        container = m.EmptyContainer()
        assert not container  # Should be falsy


class TestTemplateContainer:
    """Tests for wrap-len with template classes."""

    def test_int_template_container(self, wrap_len_module):
        """Test wrap-len with int template instantiation."""
        m = wrap_len_module
        container = m.IntTemplateContainer()
        assert len(container) == 0

        container.add(1)
        container.add(2)
        container.add(3)
        assert len(container) == 3

    def test_string_template_container(self, wrap_len_module):
        """Test wrap-len with string template instantiation."""
        m = wrap_len_module
        container = m.StringTemplateContainer()
        assert len(container) == 0

        container.add(b"hello")
        container.add(b"world")
        assert len(container) == 2


class TestDualLenContainer:
    """Tests for container with both size() and length() methods."""

    def test_wrap_len_chooses_correct_method(self, wrap_len_module):
        """Test that wrap-len uses the specified method (length())."""
        m = wrap_len_module
        container = m.DualLenContainer(5)

        # wrap-len is configured to use length() which returns size * 2
        assert len(container) == 10  # 5 * 2

        # The size() method should still return actual size
        assert container.size() == 5

    def test_dual_len_after_add(self, wrap_len_module):
        """Test dual len container after adding elements."""
        m = wrap_len_module
        container = m.DualLenContainer()

        assert len(container) == 0
        assert container.size() == 0

        container.add(1)
        assert len(container) == 2  # length() = size * 2
        assert container.size() == 1

        container.add(2)
        container.add(3)
        assert len(container) == 6  # length() = 3 * 2
        assert container.size() == 3


class TestLenWithIterableProtocol:
    """Tests for __len__ interaction with other container protocols."""

    def test_len_consistent_with_iteration(self, wrap_len_module):
        """Test that len() is consistent with number of elements."""
        m = wrap_len_module
        container = m.BasicContainer(10)

        # len() should match number of gettable elements
        assert len(container) == 10
        for i in range(len(container)):
            # Should be able to get all elements without error
            val = container.get(i)
            assert val == i

    def test_len_in_list_comprehension_context(self, wrap_len_module):
        """Test using len() in list comprehension."""
        m = wrap_len_module
        container = m.BasicContainer(5)

        # Using len() to iterate
        values = [container.get(i) for i in range(len(container))]
        assert values == [0, 1, 2, 3, 4]


class TestLenEdgeCases:
    """Edge cases and corner cases for __len__."""

    def test_large_size(self, wrap_len_module):
        """Test with large container size."""
        m = wrap_len_module
        container = m.BasicContainer(10000)
        assert len(container) == 10000

    def test_len_type_is_int(self, wrap_len_module):
        """Test that len() returns an int."""
        m = wrap_len_module
        container = m.BasicContainer(5)
        result = len(container)
        assert isinstance(result, int)

    def test_multiple_len_calls(self, wrap_len_module):
        """Test that multiple len() calls return consistent results."""
        m = wrap_len_module
        container = m.BasicContainer(42)

        # Multiple calls should return same value
        for _ in range(100):
            assert len(container) == 42

    def test_len_on_multiple_instances(self, wrap_len_module):
        """Test len() on multiple container instances."""
        m = wrap_len_module

        c1 = m.BasicContainer(5)
        c2 = m.BasicContainer(10)
        c3 = m.BasicContainer(15)

        assert len(c1) == 5
        assert len(c2) == 10
        assert len(c3) == 15

        # Modifying one shouldn't affect others
        c1.add(100)
        assert len(c1) == 6
        assert len(c2) == 10
        assert len(c3) == 15
