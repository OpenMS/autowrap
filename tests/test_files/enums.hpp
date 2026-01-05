/**
 * =============================================================================
 * Example: C++ Enums in Different Namespaces
 * =============================================================================
 *
 * This file demonstrates C++ code with enums that have the same name but exist
 * in different scopes (class Foo and namespace Foo2). See enums.pxd for how to
 * wrap these with autowrap to avoid naming conflicts in Python.
 *
 * C++ Structure:
 *   - Foo::MyEnum     (scoped enum inside class Foo)
 *   - Foo::MyEnum2    (second enum inside class Foo)
 *   - Foo2::MyEnum    (scoped enum inside namespace Foo2 - same name as Foo::MyEnum)
 *
 * =============================================================================
 */

#include <string>

// Class with nested scoped enums
class Foo
{
public:
    // First enum - will be accessible as Foo.MyEnum in Python
    enum class MyEnum
    {
      A, B, C
    };

    // Second enum in same class - will be accessible as Foo.MyEnum2 in Python
    enum class MyEnum2
    {
      A, B, C
    };

    // Method that accepts MyEnum - demonstrates type-safe enum usage
    // In Python, passing Foo2.MyEnum.A will raise AssertionError (wrong type)
    int enumToInt(MyEnum e)
    {
       switch(e)
       {
          case MyEnum::A : return 1;
          case MyEnum::B : return 2;
          case MyEnum::C : return 3;
       }
       return 0; // unreachable, but silences compiler warning
    };

    // Overloaded methods accepting different enum types - tests overload resolution
    // Python should correctly dispatch based on the enum type passed
    std::string process(MyEnum e) { return "MyEnum"; }
    std::string process(MyEnum2 e) { return "MyEnum2"; }
};

// Separate namespace with an enum of the same name as Foo::MyEnum
// This demonstrates the namespace collision problem that autowrap solves
namespace Foo2
{
    // This enum has the same name "MyEnum" as Foo::MyEnum
    // In Python, it will be accessible as Foo2.MyEnum (no conflict)
    enum class MyEnum
    {
      A, C, D
    };
};
