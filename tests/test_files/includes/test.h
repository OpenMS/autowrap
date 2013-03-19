
class IntHolder {
    private: int i_;
    public:
    IntHolder(): i_(0) { };
    IntHolder(const IntHolder & other): i_(other.i_) { };
    int get() { return i_ ;};
    void set(int i) { i_ = i; };
};

class B {
    private: IntHolder i_;
    public:
    B(): i_() { };
    B(const B & other): i_(other.i_) { };
    IntHolder get() { return i_; };
    void set(IntHolder i) { i_ = i; };
};
