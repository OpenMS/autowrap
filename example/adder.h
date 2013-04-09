template <class U>
class Adder {
    public:
        U arg0, arg1;
        Adder(): arg0(0), arg1(0) { };
        Adder(U i0, U i1): arg0(i0), arg1(i1) { };
        Adder(const Adder & o) : arg0(o.arg0), arg1(o.arg1) { };
        U getSum() {
            return arg0+ arg1;
        }
};
