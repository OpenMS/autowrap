# Using libcpp_vector_as_np Conversion Provider

This document explains how to use the `StdVectorAsNumpyConverter` to wrap C++ `std::vector` types as NumPy arrays instead of Python lists.

## Overview

The `StdVectorAsNumpyConverter` provides automatic conversion between:
- C++ `std::vector<T>` ↔ NumPy `ndarray`
- C++ `std::vector<std::vector<T>>` ↔ NumPy 2D `ndarray`

where T is a numeric type compatible with NumPy (int, float, double, etc.).

## Features

- **Zero-copy when possible**: Uses buffer interface without unnecessary data copies
- **Input and output support**: Works with both function parameters and return values
- **Nested vectors**: Supports 2D arrays via nested vectors
- **Data ownership**: Python owns the output data (no memory leaks)
- **Type safety**: Automatic type checking and conversion

## Usage

### 1. Register the Converter

```python
from autowrap.ConversionProvider import StdVectorAsNumpyConverter, special_converters

# Register the converter before calling parse_and_generate_code
special_converters.append(StdVectorAsNumpyConverter())
```

### 2. Write Your PXD File

```cython
from libcpp.vector cimport vector as libcpp_vector

cdef extern from "mylib.hpp":
    cdef cppclass MyClass:
        # Simple vector input
        double sumVector(libcpp_vector[double] data)
        
        # Simple vector output
        libcpp_vector[double] createVector(size_t size)
        
        # Vector by reference (modifiable)
        void processVector(libcpp_vector[double]& data)
        
        # Nested vectors (2D arrays)
        libcpp_vector[libcpp_vector[double]] getData2D()
        double sum2D(libcpp_vector[libcpp_vector[double]] data)
```

### 3. Generate and Compile

```python
import autowrap
import numpy

# Generate wrapper code with numpy support
decls, instance_map = autowrap.parse(
    ["mylib.pxd"],
    root="path/to/pxd"
)

include_dirs = autowrap.generate_code(
    decls,
    instance_map,
    target="mylib_wrapper.pyx",
    include_numpy=True  # Important!
)

# Add numpy include directories for compilation
include_dirs.append(numpy.get_include())

# Compile
module = autowrap.Utils.compile_and_import(
    "mylib_wrapper",
    ["mylib_wrapper.pyx"],
    include_dirs
)
```

### 4. Use in Python

```python
import numpy as np

obj = module.MyClass()

# Pass NumPy arrays as function arguments
data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
result = obj.sumVector(data)
print(f"Sum: {result}")

# Receive NumPy arrays from C++
vec = obj.createVector(10)
print(f"Type: {type(vec)}")  # <class 'numpy.ndarray'>
print(f"Shape: {vec.shape}")  # (10,)

# Work with 2D arrays
data_2d = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
result = obj.sum2D(data_2d)
print(f"2D Sum: {result}")

# Python lists also work (automatically converted)
result = obj.sumVector([1.0, 2.0, 3.0])
```

## Supported Types

The converter supports the following C++ numeric types:
- `float` → `numpy.float32`
- `double` → `numpy.float64`
- `int` → `numpy.int32`
- `int32_t` → `numpy.int32`
- `int64_t` → `numpy.int64`
- `uint32_t` → `numpy.uint32`
- `uint64_t` → `numpy.uint64`
- `size_t` → `numpy.uint64`
- `long` → `numpy.int64`
- `unsigned int` → `numpy.uint32`
- `bool` → `numpy.bool_`

## Limitations

- Only works with numeric types (no custom classes)
- Nested vectors are limited to 2D (no 3D+ arrays currently)
- Reference parameters for nested vectors may have limitations

## Performance Considerations

- Input conversion: Creates a temporary C++ vector (one copy)
- Output conversion: Creates a new NumPy array (one copy)
- Data is owned by Python after conversion (safe but not zero-copy)
- For very large datasets, consider using the buffer protocol directly (see existing buffer examples in autowrap)

## Example: Complete Workflow

See `tests/test_numpy_vector_converter.py` for a complete working example with:
- Simple vector input/output
- Different numeric types
- Nested vectors (2D arrays)
- Data ownership tests
