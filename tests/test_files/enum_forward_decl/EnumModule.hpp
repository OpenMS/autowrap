/**
 * Test file for scoped enum forward declaration issue.
 *
 * This file defines a scoped enum (enum class) that will be wrapped
 * and used across multiple Cython modules.
 */

#ifndef ENUM_MODULE_HPP
#define ENUM_MODULE_HPP

// Scoped enum (C++11 enum class)
enum class Status {
    OK = 0,
    ERROR = 1,
    PENDING = 2
};

class StatusHandler {
public:
    StatusHandler() {}

    // Method that takes a scoped enum
    int statusToInt(Status s) {
        return static_cast<int>(s);
    }

    // Method that returns a scoped enum
    Status intToStatus(int i) {
        return static_cast<Status>(i);
    }
};

#endif // ENUM_MODULE_HPP
