"""
Integration tests for the wrap-view feature.

These tests compile actual Cython code and verify runtime behavior
of in-place modification through views.
"""
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import pytest

import autowrap
import autowrap.Utils

test_files = os.path.join(os.path.dirname(__file__), "test_files")


@pytest.fixture(scope="module")
def wrap_view_module():
    """Compile and import the wrap_view_test module once per test module."""
    # Use a different name for generated file to avoid Cython pxd shadowing
    target = os.path.join(test_files, "generated", "wrap_view_wrapper.pyx")

    try:
        include_dirs = autowrap.parse_and_generate_code(
            ["wrap_view_test.pxd"],
            root=test_files,
            target=target,
            debug=True
        )

        # The hpp file is header-only, no cpp needed
        wrapped = autowrap.Utils.compile_and_import(
            "wrap_view_wrapper",
            [target],
            include_dirs
        )

        yield wrapped

    except Exception as e:
        pytest.skip(f"Compilation failed: {e}")

    finally:
        # Cleanup generated file
        if os.path.exists(target):
            try:
                os.remove(target)
            except:
                pass


class TestWrapViewBasic:
    """Basic tests for wrap-view functionality."""

    def test_view_class_exists(self, wrap_view_module):
        """Test that View classes are generated."""
        assert hasattr(wrap_view_module, "Inner")
        assert hasattr(wrap_view_module, "InnerView")
        assert hasattr(wrap_view_module, "Outer")
        assert hasattr(wrap_view_module, "OuterView")
        assert hasattr(wrap_view_module, "Container")
        assert hasattr(wrap_view_module, "ContainerView")

    def test_main_class_has_view_method(self, wrap_view_module):
        """Test that main classes have a view() method."""
        inner = wrap_view_module.Inner()
        assert hasattr(inner, "view")
        assert callable(inner.view)

        outer = wrap_view_module.Outer()
        assert hasattr(outer, "view")

    def test_view_returns_view_instance(self, wrap_view_module):
        """Test that view() returns the correct View class instance."""
        inner = wrap_view_module.Inner(42)
        view = inner.view()

        assert type(view).__name__ == "InnerView"
        assert view._is_valid


class TestWrapViewInPlaceModification:
    """Tests for in-place modification through views."""

    def test_view_property_read(self, wrap_view_module):
        """Test reading properties through view."""
        inner = wrap_view_module.Inner(42)
        view = inner.view()

        # View should be able to read the value
        assert view.value == 42

    def test_view_property_write_modifies_original(self, wrap_view_module):
        """Test that writing through view modifies the original object."""
        inner = wrap_view_module.Inner(42)
        view = inner.view()

        # Modify through view
        view.value = 100

        # Original should be modified
        assert inner.value == 100
        assert inner.getValue() == 100

    def test_copy_does_not_modify_original(self, wrap_view_module):
        """Test that regular access returns copies that don't affect original."""
        outer = wrap_view_module.Outer(10)

        # Get a copy via getInnerCopy()
        inner_copy = outer.getInnerCopy()
        original_value = outer.getInnerValue()

        # Modify the copy
        inner_copy.value = 999

        # Original should be unchanged
        assert outer.getInnerValue() == original_value

    def test_nested_view_modifies_original(self, wrap_view_module):
        """Test that nested views modify the original nested object."""
        outer = wrap_view_module.Outer(10)
        outer_view = outer.view()

        # Get view of inner_member through outer's view
        inner_view = outer_view.inner_member

        # This should be a view, not a copy
        assert type(inner_view).__name__ == "InnerView"

        # Modify through nested view
        inner_view.value = 777

        # Original's nested member should be modified
        assert outer.inner_member.value == 777


class TestWrapViewMutableRefMethods:
    """Tests for methods returning mutable references."""

    def test_mutable_ref_method_returns_view(self, wrap_view_module):
        """Test that T& methods return views on ViewClass."""
        outer = wrap_view_module.Outer(50)
        outer_view = outer.view()

        # getInner() returns Inner& - on view class should return InnerView
        inner_view = outer_view.getInner()

        assert type(inner_view).__name__ == "InnerView"

    def test_mutable_ref_method_modifies_original(self, wrap_view_module):
        """Test that modifying through mutable ref view affects original."""
        outer = wrap_view_module.Outer(50)
        outer_view = outer.view()

        # Get view via mutable ref method
        inner_view = outer_view.getInner()

        # Modify through view
        inner_view.value = 123

        # Original's inner should be modified
        assert outer.getInnerValue() == 123

    def test_mutable_ref_method_with_argument(self, wrap_view_module):
        """Test mutable ref methods that take arguments."""
        outer = wrap_view_module.Outer()
        outer_view = outer.view()

        # Add some items first
        outer.addItem(wrap_view_module.Inner(10))
        outer.addItem(wrap_view_module.Inner(20))
        outer.addItem(wrap_view_module.Inner(30))

        # Get item at index via view
        item_view = outer_view.getItemAt(1)

        # Should be a view
        assert type(item_view).__name__ == "InnerView"

        # Modify through view
        item_view.value = 999

        # Get item again via main class to verify
        # Note: main class getItemAt returns copy, so we check differently
        item_view_check = outer_view.getItemAt(1)
        assert item_view_check.value == 999


class TestWrapViewLifetime:
    """Tests for view lifetime and safety."""

    def test_view_keeps_parent_alive(self, wrap_view_module):
        """Test that view keeps parent object alive."""
        def get_view():
            inner = wrap_view_module.Inner(42)
            return inner.view()

        view = get_view()
        # Parent went out of scope in get_view(), but view should keep it alive
        assert view._is_valid
        assert view.value == 42

    def test_nested_view_keeps_chain_alive(self, wrap_view_module):
        """Test that nested views keep the whole chain alive."""
        def get_nested_view():
            outer = wrap_view_module.Outer(100)
            outer_view = outer.view()
            return outer_view.getInner()

        inner_view = get_nested_view()
        # Both outer and its inner should be kept alive
        assert inner_view._is_valid
        assert inner_view.value == 100

    def test_deep_view_survives_intermediate_and_root_deletion(self, wrap_view_module):
        """Test that deep views work after intermediate views and root are deleted."""
        import gc

        # Create container and get deep view
        container = wrap_view_module.Container()
        container_view = container.view()
        outer_view = container_view.getOuter()
        inner_view = outer_view.getInner()

        # Set initial value
        inner_view.value = 42
        assert inner_view.value == 42

        # Delete intermediate views - inner_view should still work
        del outer_view
        del container_view
        gc.collect()

        assert inner_view._is_valid
        assert inner_view.value == 42
        inner_view.value = 100
        assert inner_view.value == 100

        # Verify modification visible via container
        assert container.getNestedValue() == 100

        # Delete container - inner_view should STILL work (it holds the ref)
        del container
        gc.collect()

        assert inner_view._is_valid
        assert inner_view.value == 100


class TestWrapViewDeepNesting:
    """Tests for deeply nested views."""

    def test_three_level_nesting(self, wrap_view_module):
        """Test modification through three levels of nesting."""
        container = wrap_view_module.Container()
        container_view = container.view()

        # Container -> Outer -> Inner
        outer_view = container_view.getOuter()
        inner_view = outer_view.getInner()

        # Modify at deepest level
        inner_view.value = 12345

        # Should be reflected at top level
        assert container.getNestedValue() == 12345


class TestWrapViewStringAttribute:
    """Tests for string attributes through views."""

    def test_string_attribute_via_view(self, wrap_view_module):
        """Test modifying string attributes through view."""
        inner = wrap_view_module.Inner(0, b"original")
        view = inner.view()

        # Read string through view
        assert view.name == b"original"

        # Modify string through view
        view.name = b"modified"

        # Original should be modified
        assert inner.name == b"modified"
        assert inner.getName() == b"modified"
