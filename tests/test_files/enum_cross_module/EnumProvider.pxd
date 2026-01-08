# cython: language_level=3
#
# Test file for cross-module scoped enum imports.
#
# This file defines two scoped enums to test create_foreign_enum_imports():
# 1. Priority - standalone enum (no wrap-attach) -> imported as "Priority"
# 2. Task_TaskStatus - attached to Task class (wrap-attach) -> imported as "_PyTaskStatus"
#

cdef extern from "EnumProvider.hpp":

    # Standalone scoped enum - no wrap-attach
    # This should be imported in other modules as: from EnumProvider import Priority
    cpdef enum class Priority:
        LOW
        MEDIUM
        HIGH

    cdef cppclass Task:
        Task()
        void setStatus(Task_TaskStatus s)
        Task_TaskStatus getStatus()
        void setPriority(Priority p)
        Priority getPriority()


cdef extern from "EnumProvider.hpp" namespace "Task":

    # Scoped enum attached to Task class
    # This should be imported in other modules as: from EnumProvider import _PyTaskStatus
    cpdef enum class Task_TaskStatus "Task::TaskStatus":
        # wrap-attach:
        #   Task
        # wrap-as:
        #   TaskStatus
        PENDING
        RUNNING
        COMPLETED
        FAILED
