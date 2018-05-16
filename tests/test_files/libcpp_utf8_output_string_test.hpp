#include <string>
#include <sstream>
#include <map>


class LibCppUtf8OutputStringTest {
    public:
        LibCppUtf8OutputStringTest(){}

        std::string get(const std::string& s) const {
            std::string msg = "Hello " + s;
            return msg;
        }
};
