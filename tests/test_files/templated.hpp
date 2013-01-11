#include <string>
#include <vector>

class T 
{
    private:
        int _i;
    public:
        T(const T& t){
        _i = t._i;
        };

        T(int i): _i(i) { };
        int get() const {
            return _i;
        }
};

template <class X>
class Templated {

    private:
        X _x;

    public:

        Templated(X x): _x(x) { };

        X get() const
        {
            return _x;
        }

};
