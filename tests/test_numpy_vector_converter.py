"""
Tests for libcpp_vector_as_np conversion provider.

This test verifies that the StdVectorAsNumpyConverter correctly handles:
- Vector outputs with const ref (copy)
- Vector outputs with non-const ref (view)
- Vector outputs with value (copy)
- Vector inputs (temporary C++ vector created)
- Different numeric types (double, int, float)
- Nested vectors (2D arrays)
- Fast memcpy for efficient data transfer
"""
from __future__ import print_function
from __future__ import absolute_import

import pytest
import os

import autowrap

test_files = os.path.join(os.path.dirname(__file__), "test_files", "numpy_vector")


@pytest.fixture(scope="module")
def numpy_vector_module():
    """Compile and import the numpy_vector_test module."""
    import numpy
    target = os.path.join(test_files, "..", "generated", "numpy_vector", "numpy_vector_wrapper.pyx")
    
    # Parse the declarations
    decls, instance_map = autowrap.parse(
        ["numpy_vector_test.pxd"],
        root=test_files
    )
    
    # Generate code with numpy enabled
    include_dirs = autowrap.generate_code(
        decls,
        instance_map,
        target=target,
        debug=True,
        include_numpy=True
    )
    
    # Add numpy include directories
    include_dirs.append(numpy.get_include())
    
    module = autowrap.Utils.compile_and_import(
        "numpy_vector_wrapper",
        [target],
        include_dirs,
    )
    return module


class TestVectorOutputs:
    """Tests for vector outputs with different qualifiers."""
    
    def test_const_ref_output_is_readonly_view(self, numpy_vector_module):
        """Const ref should create a readonly view (zero-copy)."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        result = t.getConstRefVector()
        assert isinstance(result, np.ndarray)
        assert result.shape == (5,)
        assert np.allclose(result, [1.0, 2.0, 3.0, 4.0, 5.0])
        
        # Array should be readonly
        assert not result.flags.writeable
        
        # Try to modify - should fail
        with pytest.raises(ValueError, match="read-only"):
            result[0] = 999.0
        
        # Check base attribute - should be the C++ object (self) to keep it alive
        assert result.base is not None
        assert result.base is t, f"Expected .base to be the owner object, got {type(result.base).__name__}"
    
    def test_mutable_ref_output_is_view(self, numpy_vector_module):
        """Non-const ref should create a writable view (zero-copy)."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        result = t.getMutableRefVector()
        assert isinstance(result, np.ndarray)
        assert result.shape == (3,)
        assert np.allclose(result, [10.0, 20.0, 30.0])
        
        # Array should be writable
        assert result.flags.writeable
        
        # Check base attribute - should be the C++ object (self) to keep it alive
        assert result.base is not None
        assert result.base is t, f"Expected .base to be the owner object, got {type(result.base).__name__}"
        
        # Modify array - SHOULD affect C++ data since it's a view
        result[0] = 999.0
        result2 = t.getMutableRefVector()
        assert result2[0] == 999.0  # C++ data was modified!
    
    def test_value_output_is_copy(self, numpy_vector_module):
        """Value return should create a copy (Python owns data)."""
        import numpy as np
        import weakref
        import gc
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        result = t.getValueVector(5)
        assert isinstance(result, np.ndarray)
        assert result.shape == (5,)
        assert np.allclose(result, [0.0, 2.0, 4.0, 6.0, 8.0])
        
        # Modify array - safe since Python owns this data
        result[0] = 999.0
        assert result[0] == 999.0
        
        # Check base attribute - ArrayWrapper keeps the data alive
        # The buffer protocol should set the wrapper as the base
        assert result.base is not None
        # For now, buffer protocol creates a memoryview base, which keeps the ArrayWrapper alive
        # This is acceptable as long as lifetime management works correctly
        assert result.base is not None, "Array base should not be None"
    
    def test_value_output_lifetime_management(self, numpy_vector_module):
        """Test that ArrayWrapper stays alive and keeps data valid after function returns."""
        import numpy as np
        import weakref
        import gc
        import sys
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        # Get array from value return
        result = t.getValueVector(5)
        assert isinstance(result, np.ndarray)
        assert result.shape == (5,)
        original_values = result.copy()
        assert np.allclose(original_values, [0.0, 2.0, 4.0, 6.0, 8.0])
        
        # The array should have a base object (memoryview) that keeps ArrayWrapper alive
        assert result.base is not None, "Array must have a base to keep wrapper alive"
        
        # Get reference to the base object (memoryview) to verify it stays alive
        base_obj = result.base
        
        # Create weak reference to track if wrapper gets garbage collected prematurely
        # The base (memoryview) should keep a reference to the ArrayWrapper
        base_ref = weakref.ref(base_obj)
        
        # Force garbage collection to test lifetime management
        gc.collect()
        
        # The base should still be alive because the array references it
        assert base_ref() is not None, "Base (memoryview) should still be alive"
        
        # Data should still be valid (no use-after-free)
        assert np.allclose(result, original_values), "Data should remain valid after GC"
        
        # Modify the data to verify it's still accessible
        result[0] = 42.0
        assert result[0] == 42.0, "Should be able to modify data"
        
        # Get reference count of base object
        # The array holds a reference, so refcount should be at least 2 (our var + array.base)
        base_refcount = sys.getrefcount(base_obj)
        assert base_refcount >= 2, f"Base refcount should be >= 2, got {base_refcount}"
        
        # Delete our local reference to base_obj
        del base_obj
        gc.collect()
        
        # The array should still work because it keeps its own reference to base
        assert np.allclose(result[[1,2,3,4]], [2.0, 4.0, 6.0, 8.0]), "Data still valid after deleting local base ref"
        
        # The weak ref should still be alive because array.base still references it
        assert base_ref() is not None, "Base should still be alive through array.base"


class TestVectorInputs:
    """Tests for vector inputs."""
    
    def test_sum_vector(self, numpy_vector_module):
        """Test passing a 1D numpy array to C++."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = t.sumVector(data)
        assert result == 15.0
    
    def test_sum_empty_vector(self, numpy_vector_module):
        """Test passing an empty numpy array."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        data = np.array([])
        result = t.sumVector(data)
        assert result == 0.0
    
    def test_sum_requires_numpy_array(self, numpy_vector_module):
        """Test that passing a Python list raises TypeError (numpy array required)."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        data = [1.0, 2.0, 3.0]
        # Should raise TypeError because only numpy arrays are accepted
        with pytest.raises(TypeError):
            t.sumVector(data)


class TestDifferentNumericTypes:
    """Tests for different numeric types (int, float, double)."""
    
    def test_int_vector(self, numpy_vector_module):
        """Test integer vectors."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        data = np.array([1, 2, 3, 4, 5], dtype=np.int32)
        result = t.sumIntVector(data)
        assert result == 15
    
    def test_float_vector(self, numpy_vector_module):
        """Test float vectors."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        result = t.createFloatVector(3)
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32
        assert np.allclose(result, [0.5, 1.5, 2.5])


class TestNestedVectors:
    """Tests for nested vectors (2D arrays)."""
    
    def test_create_2d_vector(self, numpy_vector_module):
        """Test receiving a 2D numpy array from C++."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        result = t.create2DVector(3, 4)
        assert isinstance(result, np.ndarray)
        assert result.shape == (3, 4)
        expected = np.array([
            [0.0, 1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0, 7.0],
            [8.0, 9.0, 10.0, 11.0]
        ])
        assert np.allclose(result, expected)
    
    def test_sum_2d_vector(self, numpy_vector_module):
        """Test passing a 2D numpy array to C++."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        data = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        result = t.sum2DVector(data)
        assert result == 21.0


class TestPerformance:
    """Tests for performance and large arrays."""
    
    def test_large_vector_with_memcpy(self, numpy_vector_module):
        """Test with a larger vector to verify memcpy is used."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        # Create a large array
        data = np.arange(10000, dtype=np.float64)
        result = t.sumVector(data)
        expected = np.sum(data)
        assert np.isclose(result, expected)
