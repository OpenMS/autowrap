/**
 * Test file for scoped enum forward declaration issue.
 *
 * This file defines a class that uses the Status enum from EnumModule.hpp
 * to test cross-module enum usage.
 */

#ifndef CONSUMER_MODULE_HPP
#define CONSUMER_MODULE_HPP

#include "EnumModule.hpp"

class StatusConsumer {
public:
    StatusConsumer() {}

    // Method that uses the Status enum from EnumModule
    bool isOk(Status s) {
        return s == Status::OK;
    }

    // Method that returns the Status enum
    Status getDefaultStatus() {
        return Status::OK;
    }
};

#endif // CONSUMER_MODULE_HPP
