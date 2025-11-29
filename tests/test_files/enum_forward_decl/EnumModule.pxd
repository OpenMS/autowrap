# cython: language_level=3
#
# Test file for scoped enum forward declaration regression test.
#
# This file is part of a two-module test scenario that verifies autowrap
# correctly handles scoped enums (C++11 enum class) in multi-module builds.
#
# The key issue being tested:
# - Scoped enums are wrapped as Python Enum classes (class Foo(_PyEnum))
# - They should NOT generate `cdef class` forward declarations in .pxd files
# - If they did, other modules trying to cimport them would fail
#
# See test_enum_class_forward_declaration() in test_code_generator.py for details.
#

cdef extern from "EnumModule.hpp":

    # Scoped enum (C++11 enum class)
    # This gets wrapped as a Python Enum class, NOT a Cython cdef class.
    # Therefore, it should NOT have a `cdef class Status: pass` forward
    # declaration in the generated .pxd file.
    cpdef enum class Status:
        OK
        ERROR
        PENDING

    cdef cppclass StatusHandler:
        StatusHandler()
        int statusToInt(Status s)
        Status intToStatus(int i)
