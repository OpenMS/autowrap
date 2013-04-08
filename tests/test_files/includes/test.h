
template<class U>
class Holder {
    private: U i_;
    public:
    Holder(): i_(0) { };
    Holder(const Holder<U> & other): i_(other.i_) { };
    U get() { return i_ ;};
    void set(U i) { i_ = i; };
};

template <class U>
class Outer {
    private: Holder<U> i_;
    public:
    Outer(): i_() { };
    Outer(const Outer<U> & other): i_(other.i_) { };
    Holder<U> get() { return i_; };
    void set(Holder<U> i) { i_ = i; };
};

