#include <string>
#include <vector>

class Utf8VectorTest {
    public:
        Utf8VectorTest(){}

        std::vector<std::string> get_greetings() const {
            return {"Hello", "World", "Привет", "你好"};
        }

        std::vector<std::string> echo(const std::vector<std::string>& input) const {
            return input;
        }

        size_t count_strings(const std::vector<std::string>& input) const {
            return input.size();
        }
};
