#include "minimal.hpp"

int Minimal::compute(int i) {
    return i+1;
}
int Minimal::compute_int(int i) {
    return compute(i);
}

std::string Minimal::compute(std::string s){
    return std::string(s.rbegin(), s.rend());
}

std::string Minimal::compute_str(std::string s){
    return compute(s);
}
