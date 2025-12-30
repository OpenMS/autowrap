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

