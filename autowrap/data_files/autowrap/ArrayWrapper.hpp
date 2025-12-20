#pragma once

#include <vector>
#include <cstddef>

namespace autowrap {

/**
 * Owning wrapper for std::vector that implements Python buffer protocol.
 * This class owns its data and manages the lifetime of the underlying vector.
 * 
 * Template parameter T should be a numeric type (float, double, int, etc.)
 */
template <typename T>
class ArrayWrapper {
private:
    std::vector<T> vec_;

public:
    ArrayWrapper() : vec_() {}
    
    explicit ArrayWrapper(size_t size) : vec_(size) {}
    
    ArrayWrapper(size_t size, T value) : vec_(size, value) {}
    
    // Move constructor
    ArrayWrapper(std::vector<T>&& vec) : vec_(std::move(vec)) {}
    
    // Copy constructor
    ArrayWrapper(const std::vector<T>& vec) : vec_(vec) {}
    
    // Get data pointer
    T* data() { return vec_.data(); }
    const T* data() const { return vec_.data(); }
    
    // Get size
    size_t size() const { return vec_.size(); }
    
    // Resize
    void resize(size_t new_size) { vec_.resize(new_size); }
    
    // Set data by swapping
    void set_data(std::vector<T>& other) { vec_.swap(other); }
    
    // Get reference to internal vector
    std::vector<T>& get_vector() { return vec_; }
    const std::vector<T>& get_vector() const { return vec_; }
};

/**
 * Non-owning view wrapper that provides a view into existing data.
 * This class does NOT own its data and relies on the owner to keep data alive.
 * 
 * Template parameter T should be a numeric type (float, double, int, etc.)
 */
template <typename T>
class ArrayView {
private:
    T* ptr_;
    size_t size_;
    bool readonly_;

public:
    ArrayView() : ptr_(nullptr), size_(0), readonly_(true) {}
    
    ArrayView(T* ptr, size_t size, bool readonly = false)
        : ptr_(ptr), size_(size), readonly_(readonly) {}
    
    // Get data pointer
    T* data() { return ptr_; }
    const T* data() const { return ptr_; }
    
    // Get size
    size_t size() const { return size_; }
    
    // Check if readonly
    bool is_readonly() const { return readonly_; }
};

/**
 * Const (read-only) view wrapper.
 * This is a specialization for const data.
 */
template <typename T>
class ConstArrayView {
private:
    const T* ptr_;
    size_t size_;

public:
    ConstArrayView() : ptr_(nullptr), size_(0) {}
    
    ConstArrayView(const T* ptr, size_t size)
        : ptr_(ptr), size_(size) {}
    
    // Get data pointer (const only)
    const T* data() const { return ptr_; }
    
    // Get size
    size_t size() const { return size_; }
    
    // Always readonly
    bool is_readonly() const { return true; }
};

} // namespace autowrap
