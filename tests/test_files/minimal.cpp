#include <iostream>
#include "minimal.hpp"

Minimal::Minimal() : _i(0), _mi(), m_accessible(0)
{
}

Minimal::Minimal(std::vector<int> const & ii): _mi(), m_accessible(0)
{
    _i = ii.size();
}

Minimal::Minimal(int i) : _i(i), _mi(), m_accessible(0)
{
}

Minimal::Minimal(const Minimal &m)
{
    _i = m._i;
    _mi = m._mi;
    m_accessible = m.m_accessible;
}


int Minimal::compute(int i)  const{
    return i+_i + 1;
}

float Minimal::compute(float i)  const{
    return i+_i + 42.0;
}
const char * Minimal::pass_const_charptr(const char * p)  const{
    return p;
}

char * Minimal::pass_charptr(char * p)  const{
    return p;
}
unsigned int Minimal::test_special_converter(unsigned int l) const
{
    return l; // does nothing, but the convert will !
}

int Minimal::compute(int i, int j)  const{
    return i+j;
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
int Minimal::run3(Minimal &ref) const
{
    ref += ref; 
    return ref.compute_int(3);
}
int Minimal::run4(Minimal &ref) const
{
    ref += ref; 
    return ref.compute_int(3);
}

Minimal Minimal::create() const
{
    Minimal result;
    return result;
}

Minimal & Minimal::getRef()
{
    return *this;
}

int Minimal::sumup(const std::vector<int> & what) const {
    int sum = 0;
    for (std::vector<int>::const_iterator it = what.begin(); it != what.end(); ++it)
        sum += *it;
    return sum;
}
int Minimal::call(std::vector<Minimal> & arg) const
{
    int sum = 0;
    for (std::vector<Minimal>::const_iterator it = arg.begin(); it != arg.end(); ++it)
        sum += it->compute(0);

    arg.push_back(arg.at(0));
    return sum;
}

int Minimal::call2(std::vector<Minimal> & arg) const
{
    int sum = 0;
    for (std::vector<Minimal>::const_iterator it = arg.begin(); it != arg.end(); ++it)
        sum += it->compute(0);

    arg.push_back(arg.at(0));
    return sum;
}


int Minimal::call3(std::vector<Minimal> & arg) const
{
    int sum = 0;
    for (std::vector<Minimal>::const_iterator it = arg.begin(); it != arg.end(); ++it)
        sum += it->compute(0);

    arg.push_back(arg.at(0));
    return sum;
}

int Minimal::call4(int & arg) const
{
  arg += 1;
  return arg;
}

int Minimal::call_str(std::vector<std::string> & arg) const
{
    int sum = 0;
    for (std::vector<std::string>::const_iterator it = arg.begin(); it != arg.end(); ++it)
        sum += it->size();
    std::string n("hi");
    arg.push_back(n);
    return sum;
}

std::vector<std::string> Minimal::message() const {
    std::vector<std::string> rv;
    std::string s1("hello");
    rv.push_back(s1);
    return rv;
}
std::vector<Minimal> Minimal::create_two() const{
    std::vector<Minimal> rv;
    Minimal m(-1), mm(0);
    rv.push_back(m);
    rv.push_back(mm);
    return rv;

}

bool Minimal::operator==(const Minimal &other) const
{
    return this->_i == other._i;
}

enum ABCorD Minimal::enumTest(enum ABCorD i) const
{
    return i;
}

void Minimal::setVector(std::vector<Minimal> in)
{
    this->_mi = in;
};

std::vector<Minimal> Minimal::getVector() const
{
    return this->_mi;
};

int Minimal::test2Lists(const std::vector<Minimal> & v1, const std::vector<int> & v2 ) const
{
    return v1.size() + v2.size();
};

std::vector<Minimal>::iterator Minimal::begin()
{
    return this->_mi.begin();
}
std::vector<Minimal>::iterator Minimal::end()
{
    return this->_mi.end();
}

long int Minimal::run_static(long int i, bool)
{
    return i*4;
}


int top_function(int i)
{
    return i*2;
};

int sumup(std::vector<int> & what) {
    int sum = 0;
    for (std::vector<int>::const_iterator it = what.begin(); it != what.end(); ++it)
        sum += *it;
    return sum;
}
