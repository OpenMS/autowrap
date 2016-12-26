#include <string>
#include <sstream>
#include <map>


class Hello {
    public:

        Hello(){}

        std::string get(const std::string& s) const {
            std::string msg = "Hello " + s;
            return msg;
        }

        std::string get_more(std::map<std::string, std::string>& m) const {
            if (m.count("greet") == 0 || m.count("name") == 0) {
                return "Hey, be friendly!";
            }

            std::ostringstream oss;
            oss << m["greet"] << " " << m["name"];

            return oss.str();
        }
};