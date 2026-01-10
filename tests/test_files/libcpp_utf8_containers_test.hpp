#include <string>
#include <vector>
#include <set>
#include <map>
#include <unordered_set>
#include <unordered_map>

class Utf8ContainersTest {
    public:
        Utf8ContainersTest(){}

        // Vector tests
        std::vector<std::string> get_vector() const {
            return {"Hello", "Привет", "你好", "مرحبا"};
        }

        std::vector<std::string> echo_vector(const std::vector<std::string>& input) const {
            return input;
        }

        // Set tests
        std::set<std::string> get_set() const {
            return {"Alpha", "Бета", "伽马"};
        }

        std::set<std::string> echo_set(const std::set<std::string>& input) const {
            return input;
        }

        // Map tests - UTF-8 values
        std::map<std::string, std::string> get_map() const {
            return {
                {"greeting", "Привет"},
                {"farewell", "再见"},
                {"thanks", "شكرا"}
            };
        }

        std::map<std::string, std::string> echo_map(
            const std::map<std::string, std::string>& input
        ) const {
            return input;
        }

        // Map with UTF-8 keys
        std::map<std::string, int> get_map_utf8_keys() const {
            return {
                {"один", 1},
                {"二", 2},
                {"três", 3}
            };
        }

        // Unordered set tests
        std::unordered_set<std::string> get_unordered_set() const {
            return {"Set1", "Набор2", "集合3"};
        }

        std::unordered_set<std::string> echo_unordered_set(
            const std::unordered_set<std::string>& input
        ) const {
            return input;
        }

        // Unordered map tests
        std::unordered_map<std::string, std::string> get_unordered_map() const {
            return {
                {"key1", "Значение1"},
                {"key2", "值2"},
                {"key3", "قيمة3"}
            };
        }

        std::unordered_map<std::string, std::string> echo_unordered_map(
            const std::unordered_map<std::string, std::string>& input
        ) const {
            return input;
        }
};
