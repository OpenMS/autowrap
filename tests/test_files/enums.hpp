class Foo
{
public:
    enum class MyEnum
    {
      A,B,C
    };

    enum class MyEnum2
    {
      A,B,C
    };

    int enumToInt(MyEnum e)
    {
       switch(e)
       {
          case MyEnum::A : return 1;
          case MyEnum::B : return 2;
          case MyEnum::C : return 3;
       }
    };
};

namespace Foo2
{

    enum class MyEnum
    {
      A,C,D
    };
};
