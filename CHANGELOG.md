autowrap 0.24.0 (unreleased)

Support for std::map with wrapped types as both keys and values! Previously, autowrap could only handle maps with wrapped types as keys OR values, but not both. This limitation has been removed.

New features:
- std::map<WrappedType1, WrappedType2> now fully supported
- Example added demonstrating the new capability
- Tests added to verify the functionality

autowrap 0.23.0

Support for Cython 3.1! This means the removal of some py2 compatibility code, no more python distinction between long and int, some fixes to multiline comment processing.
