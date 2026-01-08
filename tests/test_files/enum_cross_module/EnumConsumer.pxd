# cython: language_level=3
#
# Test file for cross-module scoped enum imports.
#
# This module imports and uses enums from EnumProvider to test
# that create_foreign_enum_imports() generates correct Python imports.
#
from libcpp cimport bool
from EnumProvider cimport Priority, Task_TaskStatus

cdef extern from "EnumConsumer.hpp":

    cdef cppclass TaskRunner:
        TaskRunner()
        bool isHighPriority(Priority p)
        bool isCompleted(Task_TaskStatus s)
        Priority getDefaultPriority()
        Task_TaskStatus getDefaultStatus()
