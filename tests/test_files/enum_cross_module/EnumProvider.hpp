/**
 * Test file for cross-module scoped enum imports.
 *
 * This file defines scoped enums that will be used across multiple Cython modules
 * to test the create_foreign_enum_imports() functionality.
 */

#ifndef ENUM_PROVIDER_HPP
#define ENUM_PROVIDER_HPP

// Standalone scoped enum (no wrap-attach)
// Should be imported as: from EnumProvider import Priority
enum class Priority {
    LOW = 0,
    MEDIUM = 1,
    HIGH = 2
};

// Class with attached enum
class Task {
public:
    // Scoped enum attached to Task class (with wrap-attach)
    // Should be imported as: from EnumProvider import _PyTaskStatus
    enum class TaskStatus {
        PENDING = 0,
        RUNNING = 1,
        COMPLETED = 2,
        FAILED = 3
    };

    Task() : status_(TaskStatus::PENDING), priority_(Priority::MEDIUM) {}

    void setStatus(TaskStatus s) { status_ = s; }
    TaskStatus getStatus() const { return status_; }

    void setPriority(Priority p) { priority_ = p; }
    Priority getPriority() const { return priority_; }

private:
    TaskStatus status_;
    Priority priority_;
};

#endif // ENUM_PROVIDER_HPP
