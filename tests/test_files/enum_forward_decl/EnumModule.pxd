# cython: language_level=3
#
# Test file for scoped enum forward declaration issue.
#
# This file declares a scoped enum (cpdef enum class) that will be
# wrapped and used across multiple Cython modules.
#

cdef extern from "EnumModule.hpp":

    # Scoped enum - note: NOT attached to any class
    # This triggers the forward declaration issue
    cpdef enum class Status:
        OK
        ERROR
        PENDING

    cdef cppclass StatusHandler:
        StatusHandler()
        int statusToInt(Status s)
        Status intToStatus(int i)
