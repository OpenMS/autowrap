#ifndef HASH_TEST_HPP
#define HASH_TEST_HPP

#include <string>
#include <functional>

// Class that uses expression-based hash (old behavior)
class ExprHashClass {
private:
    int value_;
    std::string name_;

public:
    ExprHashClass() : value_(0), name_("default") {}
    ExprHashClass(int value, const std::string& name) : value_(value), name_(name) {}
    ExprHashClass(const ExprHashClass& other) : value_(other.value_), name_(other.name_) {}

    int getValue() const { return value_; }
    std::string getName() const { return name_; }

    bool operator==(const ExprHashClass& other) const {
        return value_ == other.value_ && name_ == other.name_;
    }
    bool operator!=(const ExprHashClass& other) const {
        return !(*this == other);
    }
};

// Class that uses std::hash (new behavior)
class StdHashClass {
private:
    int id_;
    std::string label_;

public:
    StdHashClass() : id_(0), label_("") {}
    StdHashClass(int id, const std::string& label) : id_(id), label_(label) {}
    StdHashClass(const StdHashClass& other) : id_(other.id_), label_(other.label_) {}

    int getId() const { return id_; }
    std::string getLabel() const { return label_; }

    bool operator==(const StdHashClass& other) const {
        return id_ == other.id_ && label_ == other.label_;
    }
    bool operator!=(const StdHashClass& other) const {
        return !(*this == other);
    }
};

// std::hash specialization for StdHashClass
namespace std {
    template <>
    struct hash<StdHashClass> {
        size_t operator()(const StdHashClass& obj) const noexcept {
            // Combine id and label hashes
            size_t h1 = std::hash<int>{}(obj.getId());
            size_t h2 = std::hash<std::string>{}(obj.getLabel());
            return h1 ^ (h2 << 1);
        }
    };
}

// Another class with std::hash to test template instantiations
template <typename T>
class TemplatedHashClass {
private:
    T data_;

public:
    TemplatedHashClass() : data_() {}
    TemplatedHashClass(const T& data) : data_(data) {}
    TemplatedHashClass(const TemplatedHashClass& other) : data_(other.data_) {}

    T getData() const { return data_; }

    bool operator==(const TemplatedHashClass<T>& other) const {
        return data_ == other.data_;
    }
    bool operator!=(const TemplatedHashClass<T>& other) const {
        return !(*this == other);
    }
};

// std::hash specialization for TemplatedHashClass<int>
namespace std {
    template <>
    struct hash<TemplatedHashClass<int>> {
        size_t operator()(const TemplatedHashClass<int>& obj) const noexcept {
            return std::hash<int>{}(obj.getData());
        }
    };
}

#endif // HASH_TEST_HPP
