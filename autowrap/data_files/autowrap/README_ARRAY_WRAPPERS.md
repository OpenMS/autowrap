# Array Wrapper Classes with Buffer Protocol Support

This module provides generic array wrapper classes that implement the Python buffer protocol, enabling zero-copy integration with NumPy and other buffer-aware Python libraries.

## Overview

The module provides three types of wrappers:

1. **Owning Wrappers** (`ArrayWrapperFloat`, `ArrayWrapperDouble`, `ArrayWrapperInt`)
   - Own their data via `std::vector`
   - Manage memory lifetime
   - Suitable for functions that return by value

2. **Non-owning Views** (`ArrayViewFloat`, `ArrayViewDouble`, `ArrayViewInt`)
   - Store only pointer + size + owner reference
   - Can be writable or readonly
   - Suitable for functions that return by reference

3. **Const Views** (`ConstArrayViewFloat`, `ConstArrayViewDouble`, `ConstArrayViewInt`)
   - Read-only views
   - Enforce constness via buffer protocol
   - Suitable for const reference returns

## File Structure

- `ArrayWrapper.hpp` - C++ template implementations
- `ArrayWrapper.pxd` - Cython declarations for C++ classes
- `ArrayWrappers.pyx` - Python-facing Cython wrapper classes with buffer protocol

## Usage Patterns

### Pattern 1: Owning Wrapper (Return by Value)

Use when your C++ function returns `std::vector<T>` by value.

```cython
# In your .pyx wrapper file
from ArrayWrappers import ArrayWrapperDouble
import numpy as np

cdef class MyClass:
    def get_data_copy(self):
        # C++ returns std::vector<double> by value
        cdef libcpp_vector[double] cpp_data = self.inst.get().getData()
        
        # Create owning wrapper
        cdef ArrayWrapperDouble wrapper = ArrayWrapperDouble()
        wrapper.set_data(cpp_data)  # Transfer ownership via swap
        
        # Convert to numpy array
        np_arr = np.asarray(wrapper)
        np_arr.base = wrapper  # Keep wrapper alive
        return np_arr
```

### Pattern 2: Mutable View (Return by Non-const Reference)

Use when your C++ function returns `std::vector<T>&` (non-const reference).

```cython
from ArrayWrappers import ArrayViewDouble
import numpy as np

cdef class MyClass:
    def get_data_view(self):
        # C++ returns std::vector<double>& (non-const reference)
        cdef libcpp_vector[double]& cpp_data = self.inst.get().getMutableData()
        
        # Create non-owning view
        cdef ArrayViewDouble view = ArrayViewDouble(
            &cpp_data[0],           # pointer to data
            cpp_data.size(),        # size
            owner=self,             # keep C++ object alive
            readonly=False          # allow writes
        )
        
        # Convert to numpy array
        np_arr = np.asarray(view)
        np_arr.base = view  # Keep view (and owner) alive
        return np_arr
```

**Important**: Modifications to the numpy array will modify the C++ data!

### Pattern 3: Const View (Return by Const Reference)

Use when your C++ function returns `const std::vector<T>&`.

```cython
from ArrayWrappers import ConstArrayViewDouble
import numpy as np

cdef class MyClass:
    def get_const_data_view(self):
        # C++ returns const std::vector<double>&
        cdef const libcpp_vector[double]& cpp_data = self.inst.get().getConstData()
        
        # Create readonly view
        cdef ConstArrayViewDouble view = ConstArrayViewDouble(
            &cpp_data[0],           # pointer to data
            cpp_data.size(),        # size
            owner=self              # keep C++ object alive
        )
        
        # Convert to numpy array (readonly)
        np_arr = np.asarray(view)
        np_arr.base = view
        return np_arr
```

**Important**: The numpy array will be read-only!

## Type Mapping

| C++ Type | Wrapper Class | NumPy dtype | Buffer Format |
|----------|---------------|-------------|---------------|
| `float` | `ArrayWrapperFloat` / `ArrayViewFloat` | `float32` | `'f'` |
| `double` | `ArrayWrapperDouble` / `ArrayViewDouble` | `float64` | `'d'` |
| `int` | `ArrayWrapperInt` / `ArrayViewInt` | `int32` | `'i'` |

## Lifetime Management

### For Owning Wrappers
The wrapper owns the data, so you must keep the wrapper alive while using the numpy array:
```python
wrapper = ArrayWrapperDouble(size=10)
arr = np.asarray(wrapper)
arr.base = wrapper  # IMPORTANT: keeps wrapper alive
```

### For Views
The view must keep its owner alive, and the numpy array must keep the view alive:
```python
view = ArrayViewDouble(ptr, size, owner=cpp_object)
arr = np.asarray(view)
arr.base = view  # Keeps view alive, which keeps owner alive
```

## Comparison with Existing Conversion

This provides an alternative to the existing `libcpp_vector_as_np` conversion provider:

| Feature | `libcpp_vector_as_np` | Array Wrappers |
|---------|----------------------|----------------|
| Ownership | Always copies data | Can choose: copy or view |
| Zero-copy | No | Yes (for views) |
| Lifetime | Automatic (Python owns) | Manual (must manage refs) |
| Type flexibility | Limited | Full buffer protocol |
| Use case | Simple, safe | Advanced, performance-critical |

## Summary Table

| Variant | Owning? | Writing in numpy? | Lifetime safety | Use case |
|---------|---------|-------------------|-----------------|----------|
| `ArrayWrapper[T]` (owning) | Yes | Yes | Safe, wrapper is owner | Return-by-value, ownership transfer |
| `ArrayView[T]` (non-owning) | No | Yes/No (configurable) | Tie `.base` to owner/view | Return class internal views |
| `ConstArrayView[T]` (readonly) | No | No (readonly) | Tie `.base` to owner/view | Const reference returns |

## Safety Considerations

1. **Always set `.base` attribute**: This is critical for lifetime management
2. **For views**: The owner MUST remain alive while the view is in use
3. **For const views**: Attempting to get a writable buffer will raise `BufferError`
4. **Thread safety**: Not thread-safe by default (same as `std::vector`)

## Performance

- **Owning wrappers**: One copy when transferring from C++ to Python
- **Views**: Zero-copy, direct access to C++ memory
- **Buffer protocol**: Minimal overhead for numpy integration

## Examples

See:
- `tests/test_files/array_wrappers/array_wrapper_test.hpp` - C++ test class
- `tests/test_files/array_wrappers/array_wrapper_demo.pyx` - Usage examples
- `tests/test_array_wrappers.py` - Comprehensive test suite

## Future Extensions

Possible enhancements:
- Support for more numeric types (uint32, int64, etc.)
- 2D/multi-dimensional array support
- Stride support for non-contiguous data
- Integration with autowrap code generator
