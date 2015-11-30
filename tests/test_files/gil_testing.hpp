// test GIL unlocking

#include <string>
#include <Python.h>
#include <stdio.h>

class GilTesting{
  public:

    GilTesting (const char* name): name_(name), greetings_() {}

    void do_something (const char* msg) {

      bool has_gil;
#if PY_MAJOR_VERSION >= 3
#if PY_MINOR_VERSION >= 4
        // Python >= 3.4 is easy
        has_gil = PyGILState_Check();
#else
        PyThreadState * tstate = (PyThreadState*)_Py_atomic_load_relaxed(&_PyThreadState_Current);
        has_gil = (tstate && (tstate == PyGILState_GetThisThreadState()));
#endif

#else
        // For Python 2.0
        PyThreadState * tstate = _PyThreadState_Current;
        has_gil = (tstate && (tstate == PyGILState_GetThisThreadState()));
#endif
        if (has_gil) {
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
