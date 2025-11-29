/**
 * C++17 STL Container Test Implementation
 * ========================================
 *
 * This file demonstrates C++ functions that use C++17 STL containers.
 * Autowrap automatically generates Python bindings for these functions.
 *
 * Supported Containers:
 *   - std::unordered_map<K,V>  -> Python dict (hash-based, O(1) avg lookup)
 *   - std::unordered_set<T>    -> Python set  (hash-based, O(1) avg lookup)
 *   - std::deque<T>            -> Python list (double-ended queue)
 *   - std::list<T>             -> Python list (doubly-linked list)
 *   - std::optional<T>         -> Python T|None (nullable value)
 *   - std::string_view         -> Python bytes (non-owning string reference)
 *
 * Compilation: Requires -std=c++17 for optional and string_view.
 */

#include <unordered_map>
#include <unordered_set>
#include <deque>
#include <list>
#include <optional>
#include <string_view>
#include <string>
#include <vector>

class Cpp17STLTest {
public:
    Cpp17STLTest() {}

    // =========================================================================
    // std::unordered_map<string, int> - Hash-based dictionary
    // =========================================================================
    // Python: dict with bytes keys and int values
    // Example: {b"one": 1, b"two": 2}

    /// Return a map - demonstrates C++ -> Python dict conversion
    std::unordered_map<std::string, int> getUnorderedMap() {
        std::unordered_map<std::string, int> m;
        m["one"] = 1;
        m["two"] = 2;
        m["three"] = 3;
        return m;
    }

    /// Sum all values - demonstrates Python dict -> C++ iteration
    int sumUnorderedMapValues(const std::unordered_map<std::string, int>& m) {
        int sum = 0;
        for (const auto& p : m) {
            sum += p.second;
        }
        return sum;
    }

    /// Lookup by key using find() - O(1) average time
    /// Returns value or -1 if not found
    int lookupUnorderedMap(const std::unordered_map<std::string, int>& m, const std::string& key) {
        auto it = m.find(key);
        if (it != m.end()) {
            return it->second;
        }
        return -1;
    }

    /// Check if key exists using count() - O(1) average time
    bool hasKeyUnorderedMap(const std::unordered_map<std::string, int>& m, const std::string& key) {
        return m.count(key) > 0;
    }

    /// Get value using at() - throws std::out_of_range if key not found
    int getValueUnorderedMap(const std::unordered_map<std::string, int>& m, const std::string& key) {
        return m.at(key);
    }

    // =========================================================================
    // std::unordered_set<int> - Hash-based set
    // =========================================================================
    // Python: set with int values
    // Example: {1, 2, 3}

    /// Return a set - demonstrates C++ -> Python set conversion
    std::unordered_set<int> getUnorderedSet() {
        return {1, 2, 3, 4, 5};
    }

    /// Sum all values - demonstrates Python set -> C++ iteration
    int sumUnorderedSet(const std::unordered_set<int>& s) {
        int sum = 0;
        for (int v : s) {
            sum += v;
        }
        return sum;
    }

    /// Check membership using count() - O(1) average time
    bool hasValueUnorderedSet(const std::unordered_set<int>& s, int value) {
        return s.count(value) > 0;
    }

    /// Count occurrences (always 0 or 1 for set)
    size_t countUnorderedSet(const std::unordered_set<int>& s, int value) {
        return s.count(value);
    }

    /// Find element using find() - O(1) average time
    /// Returns value or -1 if not found
    int findUnorderedSet(const std::unordered_set<int>& s, int value) {
        auto it = s.find(value);
        if (it != s.end()) {
            return *it;
        }
        return -1;
    }

    // =========================================================================
    // std::deque<int> - Double-ended queue
    // =========================================================================
    // Python: list
    // Note: std::deque allows O(1) insertion/deletion at both ends

    /// Return a deque - demonstrates C++ -> Python list conversion
    std::deque<int> getDeque() {
        return {10, 20, 30, 40};
    }

    /// Sum all values - demonstrates Python list -> C++ deque
    int sumDeque(const std::deque<int>& d) {
        int sum = 0;
        for (int v : d) {
            sum += v;
        }
        return sum;
    }

    /// Modify in place - demonstrates mutable reference handling
    /// Changes are reflected back to the Python list
    void doubleDequeElements(std::deque<int>& d) {
        for (size_t i = 0; i < d.size(); i++) {
            d[i] *= 2;
        }
    }

    // =========================================================================
    // std::list<double> - Doubly-linked list
    // =========================================================================
    // Python: list
    // Note: std::list allows O(1) insertion/deletion anywhere with iterator

    /// Return a list - demonstrates C++ -> Python list conversion
    std::list<double> getList() {
        return {1.1, 2.2, 3.3};
    }

    /// Sum all values - demonstrates Python list -> C++ std::list
    double sumList(const std::list<double>& l) {
        double sum = 0;
        for (double v : l) {
            sum += v;
        }
        return sum;
    }

    /// Modify in place - demonstrates mutable reference handling
    void doubleListElements(std::list<double>& l) {
        for (auto& v : l) {
            v *= 2;
        }
    }

    // =========================================================================
    // std::optional<int> - Nullable value (C++17)
    // =========================================================================
    // Python: int | None
    // Use for values that may or may not be present

    /// Return optional value - demonstrates C++ optional -> Python value/None
    std::optional<int> getOptionalValue(bool hasValue) {
        if (hasValue) {
            return 42;
        }
        return std::nullopt;
    }

    /// Accept optional value - demonstrates Python value/None -> C++ optional
    /// Returns the value or -1 if empty
    int unwrapOptional(std::optional<int> opt) {
        return opt.value_or(-1);
    }

    // =========================================================================
    // std::string_view - Non-owning string reference (C++17)
    // =========================================================================
    // Python: bytes
    // Note: string_view doesn't own the data - source must remain valid

    /// Get string length - demonstrates Python bytes -> C++ string_view
    size_t getStringViewLength(std::string_view sv) {
        return sv.size();
    }

    /// Convert to string - demonstrates string_view -> Python bytes
    std::string stringViewToString(std::string_view sv) {
        return std::string(sv);
    }
};
