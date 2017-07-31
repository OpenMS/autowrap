#include <vector>
#include <string>
#include <utility>
#include <map>
#include <boost/shared_ptr.hpp>

#ifndef HEADER_C
#define HEADER_C

class Cklass {
    public:
        int i_;
        Cklass(int i): i_(i) { };
        Cklass(const Cklass & i): i_(i.i_) { };
};

class C_second {
    public:
        int i_;
        C_second(int i): i_(i) { };
        C_second(const C_second & i): i_(i.i_) { };
};


#endif
