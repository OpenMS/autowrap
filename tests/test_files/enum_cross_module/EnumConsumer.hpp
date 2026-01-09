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

/**
 * StatusTracker: Tests cross-module getter→setter roundtrip.
 *
 * This class lives in EnumConsumer module but uses enums from EnumProvider
 * for BOTH getter AND setter methods. This tests the scenario where:
 *   tracker.setStatus(tracker.getStatus())
 * must work correctly across module boundaries.
 */
class StatusTracker {
public:
    StatusTracker() : status_(Task::TaskStatus::PENDING), priority_(Priority::LOW) {}

    // Getter and setter for class-attached enum (Task::TaskStatus)
    void setStatus(Task::TaskStatus s) { status_ = s; }
    Task::TaskStatus getStatus() const { return status_; }

    // Getter and setter for standalone enum (Priority)
    void setPriority(Priority p) { priority_ = p; }
    Priority getPriority() const { return priority_; }

private:
    Task::TaskStatus status_;
    Priority priority_;
};

#endif // ENUM_CONSUMER_HPP
