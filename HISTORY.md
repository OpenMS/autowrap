autowrap 0.22.7

- automatically generates pyi typestubs next to the pyx files


autowrap 0.22.8

- Added support for missing operators '-', '/', '-=', '*=', '/='
- Refactored special method generation a little, with minor fixes.
- Finished complete support for type stubs for all? generated Cython code

autowrap 0.22.9

- Typing of a majority of classes and functions of the codebase
- Requires python 3.7 instead of 3.6 now
- Support for "const Members" as alternative to "wrap-constant" (experimental)

autowrap 0.22.10

- Revamped docstrings for overloaded methods in generated pyx files. They use RST and sphinx.autodoc syntax now.

autowrap 0.22.11

- Fixes some issues with typing support on python side
- Added a real C++ bool converter. C++ bools in a pxd will now be real booleans
  on python side. Not "just" ints and will also be typed like that.

autowrap 0.22.12


autowrap 0.24.0


New STL Container Support (C++17):

- Added `std::unordered_map<K,V>` converter - maps to Python `dict`
- Added `std::unordered_set<T>` converter - maps to Python `set`
- Added `std::deque<T>` converter - maps to Python `list`
- Added `std::list<T>` converter - maps to Python `list`
- Added `std::optional<T>` converter - maps to Python `T | None`
- Added `std::string_view` converter - maps to Python `bytes`/`str`

Other Changes:

- Updated default C++ standard from C++11 to C++17 for compilation
  (required for `std::optional` and `std::string_view` support)
- Fixed converter architecture to properly handle `None` values for
  `std::optional<T>` input parameters
- Support for enums with the same name in different C++ namespaces using
  scoped enum declarations with `wrap-as` annotation for renaming
- Support for arbitrary key types in `operator[]` (getitem/setitem), not
  just integer types like `size_t`
- Added support for bitwise operators (`&`, `|`, `^`) and in-place bitwise
  operators (`&=`, `|=`, `^=`)

autowrap 0.23.0

Support for Cython 3.1! This means the removal of some py2 compatibility code, no more python distinction between long and int, some fixes to multiline comment processing.

- Dropped support for Cython versions older than 3.0; autowrap now requires Cython ≥ 3.0 and Python ≥ 3.9.


autowrap 0.25.0

NumPy Integration:

- Added buffer protocol wrappers for numpy integration with zero-copy
  support for const reference and value returns
- Added `libcpp_vector_as_np` conversion provider for fast numpy array
  interop using memcpy instead of element-by-element conversion
- ArrayWrapper classes now support additional integer array types
  (Int8-64, UInt8-64) with extra methods (`__init__(size)`, `resize()`, `size()`)

New Features:

- Added `wrap-len` annotation for automatic `__len__()` method generation
  on C++ container classes. Supports `size()`, `length()`, `count()`, and
  `getSize()` method names
- Added `wrap-hash: std` directive to use C++ `std::hash<T>` specializations
  directly for Python `__hash__()` generation
- Fixed ArrayWrapper inlining to place wrappers only in `.pyx` files,
  preventing conflicts with user-defined ArrayWrappers in `.pxd` files



autowrap 0.26.1

