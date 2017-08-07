#include <vector>
#include <string>
#include <utility>
#include <map>
#include <boost/shared_ptr.hpp>

#ifndef HEADER_A
#define HEADER_A

enum testA {
    AA, AAA
};


class Aklass {
    public:
        int i_;
        Aklass(int i): i_(i) { };
        Aklass(const Aklass & i): i_(i.i_) { };

    enum KlassE { A1, A2, A3};
};

class A_second {
    public:
        int i_;
        A_second(int i): i_(i) { };
        A_second(const A_second & i): i_(i.i_) { };
};


#endif
