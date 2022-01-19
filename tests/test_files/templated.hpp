#include <vector>

class T 
{
    private:
        int _i;
    public:
        T(): _i(0) {}

        T(const T& t){
        _i = t._i;
        };

        T(int i): _i(i) { };
        int get() const {
            return _i;
        }

        bool operator==(const T& other)
        {
            return this->_i == other._i;
        }
};

class T2 
{
    private:
        int _j;
    public:
        T2(): _j(0) {}

        T2(const T2& t){
        _j = t._j;
        };

        T2(int j): _j(j) { };
        int get() const {
            return _j + 1;
        }

        bool operator==(const T2& other)
        {
            return this->_j == other._j;
        }
};

template <class X>
class Templated {

    public:
        X _x;
        float f;
        std::vector<X> xi;

    public:

        Templated(X x): _x(x), f(11.0) { };

        Templated(const Templated<X> & t): _x(t._x), f(11.0) { };

        float getF() const
        {
            return f;
        }

        X get() const
        {
            return _x;
        }

        int getTwice(const Templated<X> &ti) const
        {
            return ti.get().get();
        }


        int summup(std::vector<Templated<X> > &v)
        {
            int sum = 0;
            for (typename std::vector<Templated<X> >::const_iterator it=v.begin(); it != v.end(); ++it)
            {
                sum += it->get().get();
            }
            v.push_back(Templated(X(11)));
            return sum;

        };
        std::vector<Templated<X> > reverse(std::vector<Templated<X> > &v)
        {
            return std::vector<Templated<X> >(v.rbegin(), v.rend());
        };

        Templated<X> passs(Templated<X> v)
        {
            return v;
        }
        bool operator==(const Templated<X>  & other)
        {
            return this->get() == other.get();
        }

        static int computeSeven() 
        {
            return 7;
        }

        static int computeEight()
        {
            return 8;
        }

};


class Y  {

    public:
        std::vector<Templated<T> > passs(std::vector<Templated<T> > x)
        {
            return x;
        };

};

class Z  {

    public:
        std::vector<std::vector<T>::iterator> assigned_scores{};
};


