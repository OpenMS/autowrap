#ifndef WRAP_VIEW_TEST_HPP
#define WRAP_VIEW_TEST_HPP

#include <string>
#include <vector>

/**
 * Inner class that will have a View generated.
 * Used to test in-place modification via views.
 */
class Inner {
public:
    int value;
    std::string name;

    Inner() : value(0), name("default") {}
    Inner(int v) : value(v), name("default") {}
    Inner(int v, const std::string& n) : value(v), name(n) {}

    int getValue() const { return value; }
    void setValue(int v) { value = v; }

    std::string getName() const { return name; }
    void setName(const std::string& n) { name = n; }
};

/**
 * Outer class that contains Inner objects.
 * Used to test nested view access and mutable reference returns.
 */
class Outer {
private:
    Inner inner_;
    std::vector<Inner> items_;

public:
    Outer() : inner_(0), items_() {}
    Outer(int v) : inner_(v), items_() {}

    // Direct member access
    Inner inner_member;

    // Mutable reference getter - should return view on ViewClass
    Inner& getInner() { return inner_; }

    // Const reference getter - should return copy
    const Inner& getConstInner() const { return inner_; }

    // Value getter - returns copy
    Inner getInnerCopy() const { return inner_; }

    // Mutable reference with argument
    Inner& getItemAt(int index) {
        if (index >= static_cast<int>(items_.size())) {
            items_.resize(index + 1);
        }
        return items_[index];
    }

    // Add item to the vector
    void addItem(const Inner& item) {
        items_.push_back(item);
    }

    // Get number of items
    int itemCount() const {
        return static_cast<int>(items_.size());
    }

    // Get the private inner's value (for verification)
    int getInnerValue() const { return inner_.value; }
};

/**
 * Container class for testing deeper nesting.
 */
class Container {
private:
    Outer outer_;

public:
    Container() : outer_(0) {}

    // Mutable reference to Outer
    Outer& getOuter() { return outer_; }

    // Value for verification
    int getNestedValue() const { return outer_.getConstInner().value; }
};

#endif // WRAP_VIEW_TEST_HPP
