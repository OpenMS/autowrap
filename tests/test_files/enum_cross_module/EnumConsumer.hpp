/**
 * Test file for cross-module scoped enum imports.
 *
 * This file uses enums defined in EnumProvider.hpp to test
 * cross-module enum import functionality.
 */

#ifndef ENUM_CONSUMER_HPP
#define ENUM_CONSUMER_HPP

#include "EnumProvider.hpp"

class TaskRunner {
public:
    TaskRunner() {}

    // Method using standalone enum (Priority)
    bool isHighPriority(Priority p) {
        return p == Priority::HIGH;
    }

    // Method using class-attached enum (Task::TaskStatus)
    bool isCompleted(Task::TaskStatus s) {
        return s == Task::TaskStatus::COMPLETED;
    }

    // Method returning standalone enum
    Priority getDefaultPriority() {
        return Priority::MEDIUM;
    }

    // Method returning class-attached enum
    Task::TaskStatus getDefaultStatus() {
        return Task::TaskStatus::PENDING;
    }
};

#endif // ENUM_CONSUMER_HPP
