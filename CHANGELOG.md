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
