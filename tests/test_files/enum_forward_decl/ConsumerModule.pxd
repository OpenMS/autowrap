# cython: language_level=3
#
# Test file for scoped enum forward declaration issue.
#
# This file imports the Status enum from EnumModule and uses it
# in a consumer class.
#
from EnumModule cimport Status

cdef extern from "ConsumerModule.hpp":

    cdef cppclass StatusConsumer:
        StatusConsumer()
        bool isOk(Status s)
        Status getDefaultStatus()
