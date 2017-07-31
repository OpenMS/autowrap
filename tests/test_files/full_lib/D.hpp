#include <vector>
#include <string>
#include <utility>
#include <map>
#include <boost/shared_ptr.hpp>

#include "B.hpp":

#ifndef HEADER_D
#define HEADER_D

class Dklass {
    public:
        int i_;
        Dklass(int i): i_(i) { };
        Dklass(const Dklass & i): i_(i.i_) { };
};

class D_second {
    public:
        int i_;
        D_second(int i): i_(i) { };
        D_second(const D_second & i): i_(i.i_) { };
        void runB(const B_second & arg) { i_ = arg.i_;}
};


#endif
