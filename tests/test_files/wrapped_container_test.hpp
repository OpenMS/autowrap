#ifndef WRAPPED_CONTAINER_TEST_HPP
#define WRAPPED_CONTAINER_TEST_HPP

#include <vector>
#include <map>
#include <set>
#include <unordered_map>
#include <unordered_set>
#include <list>
#include <deque>
#include <string>
#include <utility>
#include <functional>

// A simple wrapped class used in containers
class Item {
public:
    int value_;
    std::string name_;

    Item() : value_(0), name_("") {}
    Item(int v) : value_(v), name_("item") {}
    Item(int v, const std::string& n) : value_(v), name_(n) {}
    Item(const Item& other) : value_(other.value_), name_(other.name_) {}

    // Required for use as map key and set element
    bool operator<(const Item& other) const {
        return value_ < other.value_;
    }
    bool operator==(const Item& other) const {
        return value_ == other.value_ && name_ == other.name_;
    }
    bool operator!=(const Item& other) const {
        return !(*this == other);
    }

    int getValue() const { return value_; }
    void setValue(int v) { value_ = v; }
    std::string getName() const { return name_; }

    // For Python __hash__ - returns combined hash of both members
    size_t getHashValue() const {
        size_t h1 = std::hash<int>()(value_);
        size_t h2 = std::hash<std::string>()(name_);
        return h1 ^ (h2 << 1);
    }
};

// Hash function for Item - required for unordered_map/unordered_set
// Uses both value_ and name_ members for hash computation
namespace std {
    template<>
    struct hash<Item> {
        size_t operator()(const Item& item) const {
            // Combine hashes of both members using XOR and bit shifting
            size_t h1 = std::hash<int>()(item.value_);
            size_t h2 = std::hash<std::string>()(item.name_);
            return h1 ^ (h2 << 1);  // Combine hashes
        }
    };
}

// Test class with methods that use containers of wrapped classes
class WrappedContainerTest {
public:
    WrappedContainerTest() {}

    // ========================================
    // VECTOR OF WRAPPED CLASS (by value)
    // ========================================

    int sumVectorItems(std::vector<Item>& items) {
        int sum = 0;
        for (const auto& item : items) {
            sum += item.value_;
        }
        return sum;
    }

    std::vector<Item> createVectorItems(int count) {
        std::vector<Item> result;
        for (int i = 0; i < count; ++i) {
            result.push_back(Item(i * 10, "item_" + std::to_string(i)));
        }
        return result;
    }

    void appendToVector(std::vector<Item>& items, int value) {
        items.push_back(Item(value));
    }

    // ========================================
    // SET OF WRAPPED CLASS (by value)
    // ========================================

    int sumSetItems(std::set<Item>& items) {
        int sum = 0;
        for (const auto& item : items) {
            sum += item.value_;
        }
        return sum;
    }

    std::set<Item> createSetItems(int count) {
        std::set<Item> result;
        for (int i = 0; i < count; ++i) {
            result.insert(Item(i * 10));
        }
        return result;
    }

    // ========================================
    // MAP WITH WRAPPED CLASS AS VALUE
    // ========================================

    int sumMapValues(std::map<int, Item>& m) {
        int sum = 0;
        for (const auto& kv : m) {
            sum += kv.second.value_;
        }
        return sum;
    }

    std::map<int, Item> createMapIntToItem(int count) {
        std::map<int, Item> result;
        for (int i = 0; i < count; ++i) {
            result[i] = Item(i * 10);
        }
        return result;
    }

    // ========================================
    // MAP WITH WRAPPED CLASS AS KEY
    // ========================================

    int sumMapKeys(std::map<Item, int>& m) {
        int sum = 0;
        for (const auto& kv : m) {
            sum += kv.first.value_;
        }
        return sum;
    }

    std::map<Item, int> createMapItemToInt(int count) {
        std::map<Item, int> result;
        for (int i = 0; i < count; ++i) {
            result[Item(i)] = i * 10;
        }
        return result;
    }

    // ========================================
    // NESTED CONTAINERS: vector<vector<Item>>
    // ========================================

    int sumNestedVector(std::vector<std::vector<Item>>& nested) {
        int sum = 0;
        for (auto& inner : nested) {
            for (const auto& item : inner) {
                sum += item.value_;
            }
        }
        return sum;
    }

    void appendToNestedVector(std::vector<std::vector<Item>>& nested) {
        for (auto& inner : nested) {
            inner.push_back(Item(999));
        }
    }

    // ========================================
    // MAP WITH WRAPPED KEY AND VECTOR VALUE (primitives only)
    // ========================================

    int sumMapItemToVecInt(std::map<Item, std::vector<int>>& m) {
        int sum = 0;
        for (auto& kv : m) {
            sum += kv.first.value_;
            for (int v : kv.second) {
                sum += v;
            }
        }
        return sum;
    }

    // ========================================
    // MAP WITH WRAPPED CLASS AS BOTH KEY AND VALUE
    // ========================================

    int sumMapBoth(std::map<Item, Item>& m) {
        int sum = 0;
        for (const auto& kv : m) {
            sum += kv.first.value_ + kv.second.value_;
        }
        return sum;
    }

    std::map<Item, Item> createMapItemToItem(int count) {
        std::map<Item, Item> result;
        for (int i = 0; i < count; ++i) {
            result[Item(i)] = Item(i * 100);
        }
        return result;
    }

    // ========================================
    // UNORDERED_MAP WITH WRAPPED CLASS AS KEY
    // ========================================

    int sumUnorderedMapKeys(std::unordered_map<Item, int>& m) {
        int sum = 0;
        for (const auto& kv : m) {
            sum += kv.first.value_;
        }
        return sum;
    }

    std::unordered_map<Item, int> createUnorderedMapItemToInt(int count) {
        std::unordered_map<Item, int> result;
        for (int i = 0; i < count; ++i) {
            result[Item(i)] = i * 10;
        }
        return result;
    }

    // ========================================
    // UNORDERED_MAP WITH WRAPPED CLASS AS VALUE
    // ========================================

    int sumUnorderedMapValues(std::unordered_map<int, Item>& m) {
        int sum = 0;
        for (const auto& kv : m) {
            sum += kv.second.value_;
        }
        return sum;
    }

    std::unordered_map<int, Item> createUnorderedMapIntToItem(int count) {
        std::unordered_map<int, Item> result;
        for (int i = 0; i < count; ++i) {
            result[i] = Item(i * 10);
        }
        return result;
    }

    // ========================================
    // UNORDERED_MAP WITH WRAPPED CLASS AS BOTH KEY AND VALUE
    // ========================================

    int sumUnorderedMapBoth(std::unordered_map<Item, Item>& m) {
        int sum = 0;
        for (const auto& kv : m) {
            sum += kv.first.value_ + kv.second.value_;
        }
        return sum;
    }

    std::unordered_map<Item, Item> createUnorderedMapItemToItem(int count) {
        std::unordered_map<Item, Item> result;
        for (int i = 0; i < count; ++i) {
            result[Item(i)] = Item(i * 100);
        }
        return result;
    }

    // ========================================
    // UNORDERED_MAP WITH WRAPPED KEY AND VECTOR VALUE (primitives only)
    // ========================================

    int sumUnorderedMapItemToVecInt(std::unordered_map<Item, std::vector<int>>& m) {
        int sum = 0;
        for (auto& kv : m) {
            sum += kv.first.value_;
            for (int v : kv.second) {
                sum += v;
            }
        }
        return sum;
    }

    // ========================================
    // LIST OF WRAPPED CLASS (by value)
    // ========================================

    int sumListItems(std::list<Item>& items) {
        int sum = 0;
        for (const auto& item : items) {
            sum += item.value_;
        }
        return sum;
    }

    std::list<Item> createListItems(int count) {
        std::list<Item> result;
        for (int i = 0; i < count; ++i) {
            result.push_back(Item(i * 10, "item_" + std::to_string(i)));
        }
        return result;
    }

    // ========================================
    // DEQUE OF WRAPPED CLASS (by value)
    // ========================================

    int sumDequeItems(std::deque<Item>& items) {
        int sum = 0;
        for (const auto& item : items) {
            sum += item.value_;
        }
        return sum;
    }

    std::deque<Item> createDequeItems(int count) {
        std::deque<Item> result;
        for (int i = 0; i < count; ++i) {
            result.push_back(Item(i * 10, "item_" + std::to_string(i)));
        }
        return result;
    }

    // ========================================
    // UNORDERED_SET OF WRAPPED CLASS (by value)
    // ========================================

    int sumUnorderedSetItems(std::unordered_set<Item>& items) {
        int sum = 0;
        for (const auto& item : items) {
            sum += item.value_;
        }
        return sum;
    }

    std::unordered_set<Item> createUnorderedSetItems(int count) {
        std::unordered_set<Item> result;
        for (int i = 0; i < count; ++i) {
            result.insert(Item(i * 10));
        }
        return result;
    }

    // ========================================
    // NESTED CONTAINERS: list<vector<int>>
    // ========================================

    int sumListOfVectors(std::list<std::vector<int>>& data) {
        int sum = 0;
        for (const auto& vec : data) {
            for (int v : vec) {
                sum += v;
            }
        }
        return sum;
    }

    // ========================================
    // NESTED CONTAINERS: deque<vector<int>>
    // ========================================

    int sumDequeOfVectors(std::deque<std::vector<int>>& data) {
        int sum = 0;
        for (const auto& vec : data) {
            for (int v : vec) {
                sum += v;
            }
        }
        return sum;
    }
};

#endif // WRAPPED_CONTAINER_TEST_HPP
