// test GIL unlocking

#include <string>

class ClassUsingTheGil{
  public:

    ClassUsingTheGil (const char* name): name_(name), greetings_() {}

    void do_something (const char* msg) {
        greetings_ = "hello ";
        greetings_.append(name_);
        greetings_.append(", ");
        greetings_.append(msg);
    }

    const char* get_greetings() {
        return greetings_.c_str();
    }

  private:
    std::string name_;
    std::string greetings_;
};