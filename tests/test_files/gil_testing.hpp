// test GIL unlocking

#include <string>
#include <Python.h>
#include <stdio.h>

extern PyThreadState * _PyThreadState_Current;

class GilTesting{
  public:

    GilTesting (const char* name): name_(name), greetings_() {}

    void do_something (const char* msg) {
        PyThreadState * tstate = _PyThreadState_Current;
        if (tstate && (tstate == PyGILState_GetThisThreadState())) {
            greetings_ = "Hello ";
            greetings_.append(name_);
            greetings_.append(", Sorry the GIL is locked, test failed.");
        } else {
            greetings_ = "Hello ";
            greetings_.append(name_);
            greetings_.append(", ");
            greetings_.append(msg);
        }
    }

    const char* get_greetings() {
        return greetings_.c_str();
    }

  private:
    std::string name_;
    std::string greetings_;
};