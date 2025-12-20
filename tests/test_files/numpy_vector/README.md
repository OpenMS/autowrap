# NumPy Vector Converter Test Files

This directory contains test files for the `StdVectorAsNumpyConverter` provider.

## Files

- `numpy_vector_test.hpp`: C++ header with test class implementing various vector operations
- `numpy_vector_test.pxd`: Cython PXD file declaring the C++ interface
- (generated) `numpy_vector_wrapper.pyx`: Auto-generated wrapper code

## Test Class: NumpyVectorTest

The test class provides methods to test various aspects of numpy/vector conversion:

### Simple Vector Operations
- `sumVector(vector<double>)` - Takes a 1D array and returns the sum
- `createVector(size_t)` - Creates and returns a 1D array
- `multiplyVector(vector<double>&, double)` - Modifies array in-place

### Different Numeric Types
- `sumIntVector(vector<int>)` - Tests integer arrays
- `createFloatVector(size_t)` - Tests float32 arrays

### Nested Vectors (2D Arrays)
- `create2DVector(size_t, size_t)` - Creates a 2D array
- `sum2DVector(vector<vector<double>>)` - Sums all elements in a 2D array

## Running Tests

```bash
cd /home/runner/work/autowrap/autowrap
python -m pytest tests/test_numpy_vector_converter.py -v
```

## Notes

- All test functions automatically use the registered `StdVectorAsNumpyConverter`
- NumPy must be installed for these tests to work
- The converter is registered in the test file before code generation
