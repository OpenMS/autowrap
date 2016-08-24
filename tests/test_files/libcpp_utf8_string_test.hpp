#include <string>


class Hello {
    public:

        Hello(){}
        std::string get(const std::string& s) const {
            std::string msg = "Hello " + s;
                return msg;
        }
};