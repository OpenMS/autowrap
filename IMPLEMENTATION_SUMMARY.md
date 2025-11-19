# Implementation Summary: std::map Support for Wrapped Types

## Problem Statement
autowrap previously could not wrap `std::map` with both keys and values being wrapped types. It would raise an exception:
```
Exception: "Converter can not handle wrapped classes as keys and values in map"
```

## Solution Overview
Implemented proper code generation in `StdMapConverter.output_conversion()` to handle maps with both wrapped keys and wrapped values, following the same pattern already used in `input_conversion()`.

## Changes Made

### 1. Core Implementation (autowrap/ConversionProvider.py)

**Location:** Lines 1100-1127 in `StdMapConverter.output_conversion()`

**Before:**
```python
if (tt_value.base_type in wrapper_classes) and (tt_key.base_type in wrapper_classes):
    raise Exception("Converter can not handle wrapped classes as keys and values in map")
```

**After:**
```python
if (tt_value.base_type in wrapper_classes) and (tt_key.base_type in wrapper_classes):
    # Handle both key and value as wrapped classes
    cy_tt_val = tt_value.base_type
    cy_tt_key_base = tt_key.base_type
    item_val = mangle("itemv_" + output_py_var)
    item_key = mangle("itemk_" + output_py_var)
    code = Code().add(
        """
        |$output_py_var = dict()
        |cdef libcpp_map[$cy_tt_key, $cy_tt_value].iterator $it = $input_cpp_var.begin()
        |cdef $cy_tt_key_base $item_key
        |cdef $cy_tt_val $item_val
        |while $it != $input_cpp_var.end():
        |   $item_key = $cy_tt_key_base.__new__($cy_tt_key_base)
        |   $item_key.inst = shared_ptr[$cy_tt_key](new $cy_tt_key((deref($it)).first))
        |   $item_val = $cy_tt_val.__new__($cy_tt_val)
        |   $item_val.inst = shared_ptr[$cy_tt_value](new $cy_tt_value((deref($it)).second))
        |   $output_py_var[$item_key] = $item_val
        |   inc($it)
        """,
        locals(),
    )
    return code
```

### 2. Tests

#### test_files/libcpp_stl_test.hpp
Added `process_15_map()` function:
```cpp
std::map<IntWrapper, IntVecWrapper> process_15_map(int key_val, int vec_val)
{
    std::map<IntWrapper, IntVecWrapper> res;
    IntWrapper key(key_val);
    IntVecWrapper value;
    value.push_back(vec_val);
    res[key] = value;
    return res;
}
```

#### test_files/libcpp_stl_test.pxd
Added declaration:
```cython
libcpp_map[IntWrapper, IntVecWrapper] process_15_map(int key_val, int vec_val)
```

#### test_code_generator_stllibcpp.py
Added test case:
```python
# Part 9
# Test std::map< Widget, Widget2 > returned from function
res = t.process_15_map(5, 42)
assert len(res) == 1
keys = list(res.keys())
values = list(res.values())
assert keys[0].i_ == 5
assert values[0][0] == 42
```

### 3. Example & Documentation

Created comprehensive example in `example/` directory:

- **map_wrapped_keys.hpp** - C++ classes (Person, Score, ScoreTracker)
- **map_wrapped_keys.pxd** - Cython declarations
- **test_map_wrapped_keys.py** - Script to generate wrapper
- **generated/map_wrapped_keys.pyx** - Generated wrapper code (for reference)
- **README_MAP_WRAPPED.md** - Complete documentation

## Generated Code Example

For a function returning `std::map<Person, Score>`, the generated Python wrapper:

```python
def get_full_scores(self):
    """
    get_full_scores(self) -> Dict[Person, Score]
    """
    _r = self.inst.get().get_full_scores()
    py_result = dict()
    cdef libcpp_map[_Person, _Score].iterator it__r = _r.begin()
    cdef Person itemk_py_result
    cdef Score itemv_py_result
    while it__r != _r.end():
       itemk_py_result = Person.__new__(Person)
       itemk_py_result.inst = shared_ptr[_Person](new _Person((deref(it__r)).first))
       itemv_py_result = Score.__new__(Score)
       itemv_py_result.inst = shared_ptr[_Score](new _Score((deref(it__r)).second))
       py_result[itemk_py_result] = itemv_py_result
       inc(it__r)
    return py_result
```

## Usage Example

```python
import map_wrapped_keys

# Create instances
tracker = map_wrapped_keys.ScoreTracker()
person1 = map_wrapped_keys.Person(10)
person2 = map_wrapped_keys.Person(20)
score1 = map_wrapped_keys.Score(85)
score2 = map_wrapped_keys.Score(90)

# Create and use map with wrapped key and value
scores = {person1: score1, person2: score2}
total = tracker.sum_scores(scores)  # Works!

# Get map from C++
full_scores = tracker.get_full_scores()  # Works!
for person, score in full_scores.items():
    print(f"Person {person.id_} scored {score.value_}")
```

## Test Results

- ✅ All 75 existing tests pass
- ✅ New test for `std::map<WrappedType, WrappedType>` passes
- ✅ CodeQL security scan: 0 alerts
- ✅ Example generation successful

## Technical Details

The implementation follows the existing pattern for input conversion:

1. Create a Python dictionary for the result
2. Iterate through the C++ map using an iterator
3. For each key-value pair:
   - Create a new Python wrapper instance for the key
   - Create a new Python wrapper instance for the value
   - Add the pair to the result dictionary

This ensures proper memory management through Cython's shared_ptr handling and maintains consistency with the rest of the codebase.

## Backwards Compatibility

✅ Fully backwards compatible - all existing functionality preserved.
✅ No breaking changes to the API.
✅ Existing code using maps with simple keys or values continues to work unchanged.

## Security

No security vulnerabilities introduced. CodeQL analysis found 0 alerts.
