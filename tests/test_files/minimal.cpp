#include "minimal.hpp"

int Minimal::compute(int i) {
    return i+1;
}

std::string Minimal::compute(std::string s){
    return std::string(s.rbegin(), s.rend());
}
