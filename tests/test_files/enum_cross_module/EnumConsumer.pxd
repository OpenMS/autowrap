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

    # StatusTracker: Tests cross-module getter→setter roundtrip
    # This class has getter AND setter for enums from EnumProvider,
    # testing that tracker.setStatus(tracker.getStatus()) works.
    cdef cppclass StatusTracker:
        StatusTracker()
        void setStatus(Task_TaskStatus s)
        Task_TaskStatus getStatus()
        void setPriority(Priority p)
        Priority getPriority()
