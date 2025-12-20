"""
Test C++ class that demonstrates using ArrayWrapper and ArrayView.

This class shows how to:
1. Return owning wrappers for value/copy semantics
2. Return non-owning views for reference semantics  
3. Use const views for read-only access
"""

#pragma once

#include <vector>
#include <numeric>

class ArrayWrapperTest {
private:
    std::vector<double> internal_data_;
    std::vector<float> float_data_;
    std::vector<int> int_data_;

public:
    ArrayWrapperTest() {
        // Initialize some internal data
        internal_data_ = {1.0, 2.0, 3.0, 4.0, 5.0};
        float_data_ = {1.5f, 2.5f, 3.5f};
        int_data_ = {10, 20, 30, 40};
    }
    
    // Return by value - suitable for owning wrapper
    std::vector<double> getDataCopy(size_t size) {
        std::vector<double> result(size);
        std::iota(result.begin(), result.end(), 0.0);
        return result;
    }
    
    // Return const reference - suitable for const view
    const std::vector<double>& getConstRefData() const {
        return internal_data_;
    }
    
    // Return non-const reference - suitable for mutable view
    std::vector<double>& getMutableRefData() {
        return internal_data_;
    }
    
    // Float data
    const std::vector<float>& getFloatData() const {
        return float_data_;
    }
    
    std::vector<float>& getMutableFloatData() {
        return float_data_;
    }
    
    // Int data
    const std::vector<int>& getIntData() const {
        return int_data_;
    }
    
    std::vector<int>& getMutableIntData() {
        return int_data_;
    }
    
    // Compute sum (to verify modifications)
    double sumInternalData() const {
        return std::accumulate(internal_data_.begin(), internal_data_.end(), 0.0);
    }
    
    float sumFloatData() const {
        return std::accumulate(float_data_.begin(), float_data_.end(), 0.0f);
    }
    
    int sumIntData() const {
        return std::accumulate(int_data_.begin(), int_data_.end(), 0);
    }
};
