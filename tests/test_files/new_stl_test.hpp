/**
 * Test file for new STL container support in autowrap.
 * Tests: unordered_map, unordered_set, deque, list, optional, string_view
 */

#include <unordered_map>
#include <unordered_set>
#include <deque>
#include <list>
#include <optional>
#include <string_view>
#include <string>
#include <vector>

class NewSTLTest {
public:
    NewSTLTest() {}

    // =========================================================================
    // std::unordered_map tests
    // =========================================================================

    std::unordered_map<std::string, int> getUnorderedMap() {
        std::unordered_map<std::string, int> m;
        m["one"] = 1;
        m["two"] = 2;
        m["three"] = 3;
        return m;
    }

    int sumUnorderedMapValues(const std::unordered_map<std::string, int>& m) {
        int sum = 0;
        for (const auto& p : m) {
            sum += p.second;
        }
        return sum;
    }

    // =========================================================================
    // std::unordered_set tests
    // =========================================================================

    std::unordered_set<int> getUnorderedSet() {
        return {1, 2, 3, 4, 5};
    }

    int sumUnorderedSet(const std::unordered_set<int>& s) {
        int sum = 0;
        for (int v : s) {
            sum += v;
        }
        return sum;
    }

    // =========================================================================
    // std::deque tests
    // =========================================================================

    std::deque<int> getDeque() {
        return {10, 20, 30, 40};
    }

    int sumDeque(const std::deque<int>& d) {
        int sum = 0;
        for (int v : d) {
            sum += v;
        }
        return sum;
    }

    // Mutable reference test - doubles each element
    void doubleDequeElements(std::deque<int>& d) {
        for (size_t i = 0; i < d.size(); i++) {
            d[i] *= 2;
        }
    }

    // =========================================================================
    // std::list tests
    // =========================================================================

    std::list<double> getList() {
        return {1.1, 2.2, 3.3};
    }

    double sumList(const std::list<double>& l) {
        double sum = 0;
        for (double v : l) {
            sum += v;
        }
        return sum;
    }

    // Mutable reference test - doubles each element
    void doubleListElements(std::list<double>& l) {
        for (auto& v : l) {
            v *= 2;
        }
    }

    // =========================================================================
    // std::optional tests
    // =========================================================================

    std::optional<int> getOptionalValue(bool hasValue) {
        if (hasValue) {
            return 42;
        }
        return std::nullopt;
    }

    int unwrapOptional(std::optional<int> opt) {
        return opt.value_or(-1);
    }

    // =========================================================================
    // std::string_view tests
    // =========================================================================

    size_t getStringViewLength(std::string_view sv) {
        return sv.size();
    }

    std::string stringViewToString(std::string_view sv) {
        return std::string(sv);
    }
};
