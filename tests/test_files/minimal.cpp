#include "minimal.hpp"

Minimal::Minimal() : _i(0)
{
}

Minimal::Minimal(int i) : _i(i)
{
}

Minimal::Minimal(const Minimal &m): _i(0)
{
}


int Minimal::compute(int i)  const{
    return i+_i + 1;
}
int Minimal::compute_int(int i)  const{
    return compute(i);
}

int Minimal::compute_int()  const{
    return compute(41);
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
int Minimal::run(const Minimal &ref) const
{
    return ref.compute_int(3);
}

int Minimal::run2(Minimal * inst) const
{
    return inst->compute_int(4);
}

Minimal Minimal::create() const
{
    Minimal result;
    return result;
}


int Minimal::sumup(std::vector<int> what) const {
    int sum = 0;
    for (std::vector<int>::const_iterator it = what.begin(); it != what.end(); ++it)
        sum += *it;
    return sum;
}

