#ifndef WRAP_LEN_TEST_HPP
#define WRAP_LEN_TEST_HPP

#include <vector>
#include <string>
#include <cstddef>

// Basic container with size() - used with wrap-len
class BasicContainer {
private:
    std::vector<int> data_;
public:
    BasicContainer() {}
    BasicContainer(int count) {
        for (int i = 0; i < count; ++i) {
            data_.push_back(i);
        }
    }

    size_t size() const { return data_.size(); }
    void add(int value) { data_.push_back(value); }
    void clear() { data_.clear(); }
    int get(size_t index) const { return data_[index]; }
};

// Container with length() method instead of size()
class LengthContainer {
private:
    std::vector<std::string> items_;
public:
    LengthContainer() {}

    int length() const { return static_cast<int>(items_.size()); }
    void append(const std::string& item) { items_.push_back(item); }
    std::string getItem(int index) const { return items_[index]; }
};

// Container with count() method
class CountContainer {
private:
    int count_;
public:
    CountContainer() : count_(0) {}
    CountContainer(int initial) : count_(initial) {}

    unsigned int count() const { return static_cast<unsigned int>(count_); }
    void increment() { count_++; }
    void decrement() { if (count_ > 0) count_--; }
};

// Container with size() but NO wrap-len annotation - should NOT have __len__
class NoLenContainer {
private:
    std::vector<double> values_;
public:
    NoLenContainer() {}

    size_t size() const { return values_.size(); }
    void push(double v) { values_.push_back(v); }
    double sum() const {
        double s = 0;
        for (auto v : values_) s += v;
        return s;
    }
};

// Container where size() is wrap-ignored
// The size method should not be wrapped, but wrap-len should still work
// since it calls the C++ method directly
class IgnoredSizeContainer {
private:
    std::vector<int> data_;
public:
    IgnoredSizeContainer() {}
    IgnoredSizeContainer(int count) {
        for (int i = 0; i < count; ++i) {
            data_.push_back(i * 10);
        }
    }

    // This method is wrap-ignored but wrap-len should still work
    size_t size() const { return data_.size(); }
    void add(int v) { data_.push_back(v); }
    int get(size_t i) const { return data_[i]; }
};

// Container with getSize() - different naming convention
class GetSizeContainer {
private:
    int size_;
public:
    GetSizeContainer() : size_(0) {}
    GetSizeContainer(int s) : size_(s) {}

    size_t getSize() const { return static_cast<size_t>(size_); }
    void setSize(int s) { size_ = s; }
};

// Empty container that always returns 0
class EmptyContainer {
public:
    EmptyContainer() {}
    size_t size() const { return 0; }
};

// Template container
template <typename T>
class TemplateContainer {
private:
    std::vector<T> data_;
public:
    TemplateContainer() {}

    size_t size() const { return data_.size(); }
    void add(const T& value) { data_.push_back(value); }
    T get(size_t index) const { return data_[index]; }
};

// Container with both size() and length() - test that we can choose
class DualLenContainer {
private:
    std::vector<int> data_;
public:
    DualLenContainer() {}
    DualLenContainer(int count) {
        for (int i = 0; i < count; ++i) {
            data_.push_back(i);
        }
    }

    // Returns actual size
    size_t size() const { return data_.size(); }
    // Returns size * 2 (for testing that wrap-len picks the right method)
    size_t length() const { return data_.size() * 2; }
    void add(int v) { data_.push_back(v); }
};

#endif // WRAP_LEN_TEST_HPP
