class IntHolder {
    public:
        int i_;
        IntHolder(int i): i_(i) {};
        IntHolder(const IntHolder & i): i_(i.i_) {};
        int add(const IntHolder & other) 
        {
            return i_ + other.i_;
        }
};
