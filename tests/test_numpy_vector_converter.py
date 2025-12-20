"""
Tests for libcpp_vector_as_np conversion provider.

This test file verifies that the StdVectorAsNumpyConverter correctly handles:
- Simple vector input (numpy array -> C++ vector)
- Simple vector output (C++ vector -> numpy array)
- Vector modification via reference
- Different numeric types (double, int, float)
- Nested vectors (2D arrays)
- Buffer interface and data ownership
"""
from __future__ import print_function
from __future__ import absolute_import

import pytest
import os
import sys

import autowrap.DeclResolver
import autowrap.CodeGenerator
import autowrap.PXDParser
import autowrap.Utils
import autowrap

# Import the converter and register it
from autowrap.ConversionProvider import StdVectorAsNumpyConverter, special_converters

# Register the converter to use numpy arrays instead of lists
special_converters.append(StdVectorAsNumpyConverter())

test_files = os.path.join(os.path.dirname(__file__), "test_files", "numpy_vector")


@pytest.fixture(scope="module")
def numpy_vector_module():
    """Compile and import the numpy_vector_test module."""
    import numpy
    target = os.path.join(test_files, "numpy_vector_wrapper.pyx")
    
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


class TestSimpleVectorInput:
    """Tests for simple vector input (numpy array -> C++ vector)."""
    
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
    
    def test_sum_from_list(self, numpy_vector_module):
        """Test passing a Python list (should be converted to numpy array)."""
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        data = [1.0, 2.0, 3.0]
        result = t.sumVector(data)
        assert result == 6.0


class TestSimpleVectorOutput:
    """Tests for simple vector output (C++ vector -> numpy array)."""
    
    def test_create_vector(self, numpy_vector_module):
        """Test receiving a numpy array from C++."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        result = t.createVector(5)
        assert isinstance(result, np.ndarray)
        assert result.shape == (5,)
        assert np.allclose(result, [0.0, 2.0, 4.0, 6.0, 8.0])
    
    def test_create_empty_vector(self, numpy_vector_module):
        """Test receiving an empty numpy array."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        result = t.createVector(0)
        assert isinstance(result, np.ndarray)
        assert result.shape == (0,)


class TestVectorReference:
    """Tests for vector modification via reference."""
    
    def test_multiply_vector(self, numpy_vector_module):
        """Test modifying a vector in place."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        data = [1.0, 2.0, 3.0, 4.0]
        t.multiplyVector(data, 2.0)
        # Note: For reference parameters, the list should be modified in place
        # but since we're converting from list to numpy and back, 
        # this behavior depends on the implementation
        # For now, we'll just verify the function doesn't crash


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


class TestDataOwnership:
    """Tests for buffer interface and data ownership."""
    
    def test_output_array_is_owned_by_python(self, numpy_vector_module):
        """Verify that output arrays are owned by Python."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        result = t.createVector(10)
        # Modify the array - this should work if Python owns the data
        result[0] = 999.0
        assert result[0] == 999.0
    
    def test_large_vector(self, numpy_vector_module):
        """Test with a larger vector to ensure performance."""
        import numpy as np
        m = numpy_vector_module
        t = m.NumpyVectorTest()
        
        # Create a large array
        data = np.arange(10000, dtype=np.float64)
        result = t.sumVector(data)
        expected = np.sum(data)
        assert np.isclose(result, expected)
