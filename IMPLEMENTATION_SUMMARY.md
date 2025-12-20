# Array Wrapper Implementation Summary

## Overview

This implementation adds generic array wrapper classes with Python buffer protocol support to autowrap, enabling zero-copy integration between C++ `std::vector` and NumPy arrays.

## Key Design Decisions

### 1. **No C++ Wrapper Layer**
- **Decision**: Cython classes directly hold `libcpp_vector` or raw pointers
- **Rationale**: Simpler, no extra indirection, Cython can manage C++ types directly
- **Result**: Less code, easier to maintain

### 2. **Bool Member for Constness**
- **Decision**: Use `readonly` bool flag instead of separate `ConstArrayView` classes
- **Rationale**: Reduces code duplication, simpler API
- **Implementation**: `ArrayView` has a `readonly` member that controls buffer protocol behavior

### 3. **Factory Functions for Views**
- **Decision**: Create views using factory functions (`_create_view_*`) instead of `__cinit__`
- **Rationale**: Cython `__cinit__` cannot accept C-level pointers when called from generated code
- **Result**: Factory functions can be called from C level in generated wrappers

### 4. **Owning Wrappers for Value Returns**
- **Decision**: Use `ArrayWrapper` + `swap()` for value returns instead of memcpy
- **Rationale**: The returned vector is already a copy, so just transfer ownership
- **Benefit**: Zero extra copies, efficient memory transfer

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Python/NumPy Layer                                          │
│  - numpy.ndarray                                            │
│  - Uses buffer protocol                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ buffer protocol
┌──────────────────────┴──────────────────────────────────────┐
│ Cython Wrapper Layer (ArrayWrappers.pyx)                    │
│                                                              │
│  ┌────────────────────────┐  ┌─────────────────────────┐   │
│  │ ArrayWrapper[T]        │  │ ArrayView[T]            │   │
│  │ - libcpp_vector[T] vec │  │ - T* ptr                │   │
│  │ - Owns data            │  │ - size_t _size          │   │
│  │                        │  │ - object owner          │   │
│  │                        │  │ - bool readonly         │   │
│  │                        │  │ - Does NOT own data     │   │
│  └────────────────────────┘  └─────────────────────────┘   │
│                                                              │
│  Factory functions: _create_view_*()                        │
└──────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│ C++ Layer                                                    │
│  - std::vector<T>                                           │
│  - Raw memory                                               │
└─────────────────────────────────────────────────────────────┘
```

## Type Coverage

All numeric types are supported:
- **Floating point**: `float`, `double`
- **Signed integers**: `int8_t`, `int16_t`, `int32_t`, `int64_t`
- **Unsigned integers**: `uint8_t`, `uint16_t`, `uint32_t`, `uint64_t`

Each type has:
- An owning wrapper class (e.g., `ArrayWrapperDouble`)
- A view class (e.g., `ArrayViewDouble`)
- A factory function (e.g., `_create_view_double()`)

## Integration with ConversionProvider

The `StdVectorAsNumpyConverter` in `ConversionProvider.py` uses these wrappers:

### For Reference Returns (`const T&` or `T&`)
```cython
# Zero-copy view
cdef double* _ptr = vec.data()
cdef size_t _size = vec.size()
cdef ArrayViewDouble view = _create_view_double(_ptr, _size, owner=self, readonly=True/False)
cdef object arr = numpy.asarray(view)
arr.base = view  # Keep view (and owner) alive
```

### For Value Returns (`T`)
```cython
# Owning wrapper (swap, no extra copy)
cdef ArrayWrapperDouble wrapper = ArrayWrapperDouble()
wrapper.set_data(vec)  # Swaps data, O(1)
cdef object arr = numpy.asarray(wrapper)
arr.base = wrapper  # Keep wrapper alive
```

## Memory Management

### Owning Wrappers
- **Lifetime**: Wrapper owns the data
- **Safety**: Must keep wrapper alive while numpy array is in use (via `.base`)
- **Copies**: One copy when C++ returns by value, then swap (no extra copy)

### Views
- **Lifetime**: View does NOT own data, relies on owner
- **Safety**: Must keep both view AND owner alive (view.owner reference + arr.base)
- **Copies**: Zero copies, direct access to C++ memory

### Lifetime Chain
```
numpy array  -->  .base -->  ArrayView  -->  .owner -->  C++ object
                             (no data)                    (has data)
```

## Buffer Protocol Implementation

Both `ArrayWrapper` and `ArrayView` implement:

```cython
def __getbuffer__(self, Py_buffer *buffer, int flags):
    # Set up buffer with:
    # - buf: pointer to data
    # - len: total bytes
    # - shape: [size]
    # - strides: [itemsize]
    # - format: 'f', 'd', 'i', etc.
    # - readonly: 0 or 1
    
def __releasebuffer__(self, Py_buffer *buffer):
    pass  # No cleanup needed
```

## Usage Patterns Generated by autowrap

### Pattern 1: Value Return
```cython
def get_data(self):
    _r = self.inst.get().getData()  # Returns by value
    # Use owning wrapper
    cdef ArrayWrapperDouble _wrapper_py_result = ArrayWrapperDouble()
    _wrapper_py_result.set_data(_r)
    cdef object py_result = numpy.asarray(_wrapper_py_result)
    py_result.base = _wrapper_py_result
    return py_result
```

### Pattern 2: Const Reference Return  
```cython
def get_const_ref(self):
    _r = self.inst.get().getConstRef()  # Returns const &
    # Use readonly view
    cdef double* _ptr_py_result = _r.data()
    cdef size_t _size_py_result = _r.size()
    cdef ArrayViewDouble _view_py_result = _create_view_double(
        _ptr_py_result, _size_py_result, owner=self, readonly=True
    )
    cdef object py_result = numpy.asarray(_view_py_result)
    py_result.base = _view_py_result
    return py_result
```

### Pattern 3: Non-Const Reference Return
```cython
def get_mutable_ref(self):
    _r = self.inst.get().getMutableRef()  # Returns &
    # Use writable view
    cdef double* _ptr_py_result = _r.data()
    cdef size_t _size_py_result = _r.size()
    cdef ArrayViewDouble _view_py_result = _create_view_double(
        _ptr_py_result, _size_py_result, owner=self, readonly=False
    )
    cdef object py_result = numpy.asarray(_view_py_result)
    py_result.base = _view_py_result
    return py_result
```

## Files Modified/Created

### Created
- `autowrap/data_files/autowrap/ArrayWrappers.pyx` - Main implementation (1300+ lines)
- `autowrap/data_files/autowrap/ArrayWrappers.pxd` - Cython declarations
- `autowrap/data_files/autowrap/README_ARRAY_WRAPPERS.md` - Documentation
- `tests/test_array_wrappers.py` - Test suite
- `tests/test_files/array_wrappers/` - Test examples

### Modified
- `autowrap/ConversionProvider.py` - Updated `StdVectorAsNumpyConverter`
- `autowrap/CodeGenerator.py` - Added ArrayWrapper imports when numpy enabled

### Removed
- `ArrayWrapper.hpp` - Not needed (Cython handles C++ directly)
- `ArrayWrapper.pxd` - Not needed (functionality in ArrayWrappers.pxd)

## Performance Characteristics

| Operation | Old (memcpy) | New (wrapper) | New (view) |
|-----------|--------------|---------------|------------|
| Value return | 1 copy | 1 copy | N/A |
| Const ref return | 1 copy | N/A | 0 copies |
| Non-const ref return | 1 copy | N/A | 0 copies |
| Memory safety | Safe | Safe (with .base) | Safe (with .base) |

## Key Benefits

1. **Zero-copy for references**: Views provide direct access to C++ memory
2. **Efficient value returns**: Swap instead of second copy
3. **Type safety**: Full type coverage for all numeric types
4. **Memory safety**: Proper lifetime management via Python references
5. **Simple implementation**: No C++ layer, all in Cython
6. **Flexible**: Support for both readonly and writable buffers

## Future Enhancements

Potential improvements:
- Multi-dimensional array support (2D, 3D, etc.)
- Strided array support for non-contiguous data
- Support for more types (complex numbers, bool)
- Integration with other array protocols (e.g., `__array_interface__`)
- Optional bounds checking for debug builds
