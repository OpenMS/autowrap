#include "minimal.hpp"

int Minimal::compute(int i)  const{
    return i+1;
}
int Minimal::compute_int(int i)  const{
    return compute(i);
}

std::string Minimal::compute(std::string s) const{
    return std::string(s.rbegin(), s.rend());
}

std::string Minimal::compute_str(std::string s) const {
    return compute(s);
}

int Minimal::compute_charp(char *p) const
{
    int i=0;
    for (; *p; p++, i++);
    return i;

}
int Minimal::run(const Minimal &inst) const
{
    return inst.compute_int(3);
}


