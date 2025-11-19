# Map with Wrapped Types Example

This example demonstrates autowrap's capability to handle `std::map` with wrapped types as keys and/or values.

## What This Example Shows

Prior to this enhancement, autowrap could handle:
- `std::map<int, int>` - Simple types as both key and value
- `std::map<WrappedType, int>` - Wrapped type as key, simple type as value  
- `std::map<int, WrappedType>` - Simple type as key, wrapped type as value

But it could **not** handle:
- `std::map<WrappedType1, WrappedType2>` - Wrapped types as both key and value

This example demonstrates that this limitation has been removed.

## Files

- `map_wrapped_keys.hpp` - C++ header with example classes
- `map_wrapped_keys.pxd` - Cython declaration file for autowrap
- `test_map_wrapped_keys.py` - Script to generate wrapper code

## Classes

### Person
A simple class that can be used as a map key. It has:
- `int id_` - Person identifier
- `operator<` - Required for use as map key

### Score  
A simple class that can be used as a map value. It has:
- `int value_` - Score value

### ScoreTracker
A class with methods demonstrating different map configurations:

1. `get_person_scores()` → `std::map<Person, int>`
   - Wrapped type as key, simple type as value
   
2. `get_id_scores()` → `std::map<int, Score>`
   - Simple type as key, wrapped type as value
   
3. `get_full_scores()` → `std::map<Person, Score>`
   - **Wrapped types as both key and value** ✨ NEW!
   
4. `sum_scores(std::map<Person, Score>&)` → `int`
   - Takes map with wrapped types as both key and value ✨ NEW!

## Running the Example

```bash
python test_map_wrapped_keys.py
```

This will:
1. Generate the Cython wrapper code
2. Save the generated `.pyx` file to the `generated/` directory
3. Display example usage code

## Generated Code

The key part of the generated code for handling maps with both wrapped key and value:

```python
def get_full_scores(self):
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

Both the key and value are properly wrapped in their respective Python wrapper classes.

## Implementation Details

The fix was made in `autowrap/ConversionProvider.py` in the `StdMapConverter.output_conversion()` method. Previously, it raised an exception when both key and value were wrapped types:

```python
# OLD CODE (raised exception)
if (tt_value.base_type in wrapper_classes) and (tt_key.base_type in wrapper_classes):
    raise Exception("Converter can not handle wrapped classes as keys and values in map")
```

Now it properly handles both wrapped key and value by creating temporary Python objects for each:

```python
# NEW CODE (properly handles both)
if (tt_value.base_type in wrapper_classes) and (tt_key.base_type in wrapper_classes):
    # Create wrapper instances for both key and value
    # ... (see implementation for details)
```
