#include <list>
#include <iostream>

template<class T>
class X
{
    private: T i;

    public: X(T i) {
        std::cout << "    cons called with " << this << " " << i << std::endl;
        this->i = i;
    }
    public: X(): i(0) {
    }

    public: X(const X<T> & x) {
        std::cout << "    copy cons called with " << this
                  << " " << &x << " " << x.i << std::endl;
        this->i = x.i;
    }

    public: ~X()
    {
        std::cout << "    decons called for " << this << std::endl;
    }

    public: X<T> operator+(X<T> & other)
    {
        return X<T>(this->i + other.i);
    }

    public: operator T()
    {
        return this->i;
    }



};


template<class T>
class XContainer: public std::list<X<T> > {

    public: std::list<X<T>  > fun(std::list<X<T> > arg )
    {
        std::cout << "  start fun" << std::endl;
        XContainer<int> result;
        std::cout << "  start loopt" << std::endl;
        for (typename XContainer<int>::iterator it = arg.begin();
                                                it != arg.end(); ++it)
        {
            result.push_back(*it);
        }
        std::cout << "  end fun " << std::endl;
        return result;

    };

    public: std::list<X<T> > gun(std::list<X<T> > & arg )
    {
        std::cout << "  start gun" << std::endl;
        XContainer<int> result;
        std::cout << "  start loopt" << std::endl;
        for (typename XContainer<int>::iterator it = arg.begin();
                                                it != arg.end(); ++it)
        {
            result.push_back(*it);
        }
        std::cout << "  end gun " << std::endl;
        return result;

    };

};
