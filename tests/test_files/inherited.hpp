template<typename A>
class Base
{
public:
    Base<A>() = default;
    A a = 1;
    A foo()
    {
        return a;
    }
};

class BaseZ
{
public:
    BaseZ() = default;
    int a = 0;
    // TODO needs different name, otherwise clashes when both are inherited from
    //  Think about if this can be caught in autowrap
    int bar()
    {
        return a;
    }
};

template<typename A>
class Inherited: public Base<A>, public BaseZ
{
public:
    Inherited<A>(): Base<A>(), BaseZ(){};

    A getBase()
    {
        return Base<A>::a;
    }

    int getBaseZ()
    {
        return BaseZ::a;
    }
};

template<typename A, typename B>
class InheritedTwo: public Base<A>, public Base<B>, public BaseZ
{
public:
    InheritedTwo<A,B>(): Base<A>(), Base<B>(), BaseZ(){};

    A getBase()
    {
        return Base<A>::a;
    }

    B getBaseB()
    {
        return Base<B>::a;
    }

    int getBaseZ()
    {
        return BaseZ::a;
    }
};

