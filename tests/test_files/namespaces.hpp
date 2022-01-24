namespace A
{
    class Foo
    {
    public:
        class Bar
        {
        public:
            class Baz
            {
            public:
              int a = 0;
            };
            int a = 1;
        };
        int a = 2;
    };
}

namespace B
{
    class Foo
    {
    public:
        int a = 3;
    };
}