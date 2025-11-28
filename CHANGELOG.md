autowrap 0.24.0 (unreleased)

- Support for enums with the same name in different C++ namespaces using
  scoped enum declarations with `wrap-as` annotation for renaming
- Support for arbitrary key types in `operator[]` (getitem/setitem), not
  just integer types like `size_t`

autowrap 0.23.0

Support for Cython 3.1! This means the removal of some py2 compatibility code, no more python distinction between long and int, some fixes to multiline comment processing.
