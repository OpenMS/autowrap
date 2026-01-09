#include <string>
#include <vector>


class Utf8StringVectorTest {
    public:
        Utf8StringVectorTest(){}

        // Returns a vector of UTF-8 encoded strings
        std::vector<std::string> get_greetings() const {
            std::vector<std::string> result;
            // "Grüß Gott" in UTF-8
            // Using string concatenation to avoid hex escape sequence issues
            result.push_back("Gr\xc3\xbc\xc3\x9f" " Gott");
            // "Jürgen" in UTF-8
            result.push_back("J\xc3\xbc" "rgen");
            // "日本語" (Japanese) in UTF-8
            result.push_back("\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e");
            return result;
        }

        // Accepts a vector of strings and returns total length
        int total_length(const std::vector<std::string>& strings) const {
            int sum = 0;
            for (const auto& s : strings) {
                sum += s.size();
            }
            return sum;
        }

        // Accepts a vector by reference and modifies it
        void append_greeting(std::vector<std::string>& strings) const {
            // "Hallöchen" in UTF-8
            // Using string concatenation to avoid hex escape sequence issues
            strings.push_back("Hall\xc3\xb6" "chen");
        }
};
