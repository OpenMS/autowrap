#include <vector>

template<class U>
class Holder {
    private: U i_;
    public:
    Holder(): i_(0) { };
    Holder(const Holder<U> & other): i_(other.i_) { };
    Holder(U i): i_(i) { };
    U get() { return i_ ;};
    void set(U i) { i_ = i; };
};

template <class U>
class Outer {
    private: Holder<U> i_;
             std::vector<Holder<U> > container;
    public:
    Outer(): i_(), container() {
    };
    Outer(const Outer<U> & other): i_(other.i_), container(other.container) { };
    Holder<U> get() { return i_; };
    void set(Holder<U> i) { i_ = i;
        container.clear();
        container.push_back(i);
    };

    typename std::vector<Holder<U> >::iterator begin() { 
        return container.begin();
    };
    typename std::vector<Holder<U> >::iterator end() {
        return container.end();
    };
};

