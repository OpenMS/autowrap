# cython: language_level=3
#
# Test file for scoped enum forward declaration regression test.
#
# This module imports and uses the Status enum from EnumModule to verify
# that cross-module enum usage works correctly.
#
# In the buggy version, this module would fail to compile because:
# 1. EnumModule.pxd declared `cdef class Status: pass`
# 2. But EnumModule.pyx defined `class Status(_PyEnum): ...`
# 3. When this module did `from EnumModule cimport Status`, Cython expected
#    a cdef class but got a regular Python class
#
# See test_enum_class_forward_declaration() in test_code_generator.py for details.
#
from EnumModule cimport Status

cdef extern from "ConsumerModule.hpp":

    cdef cppclass StatusConsumer:
        StatusConsumer()
        bool isOk(Status s)
        Status getDefaultStatus()
