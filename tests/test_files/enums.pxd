# cython: language_level=2
#
# =============================================================================
# Example: Wrapping C++ Enums in Different Namespaces
# =============================================================================
#
# This file demonstrates how to wrap C++ enums that have the same name but
# exist in different namespaces (e.g., Foo::MyEnum and Foo2::MyEnum).
#
# THE PROBLEM:
#   When two C++ classes/namespaces define enums with the same name, Cython
#   cannot distinguish them at the module level, causing naming conflicts.
#
# THE SOLUTION:
#   Use a unique Cython identifier with a C++ name string to map to the
#   actual C++ enum, then use wrap-as to expose it with the desired Python name.
#
# PATTERN:
#   cpdef enum class <UniqueID> "<C++::FullName>":
#       # wrap-attach:
#       #   <ClassName>
#       # wrap-as:
#       #   <PythonName>
#
# EXAMPLE:
#   For Foo::MyEnum and Foo2::MyEnum, declare them as:
#     - Foo_MyEnum "Foo::MyEnum"   -> exposed as Foo.MyEnum in Python
#     - Foo2_MyEnum "Foo2::MyEnum" -> exposed as Foo2.MyEnum in Python
#
# IMPORTANT:
#   - Use `cpdef enum class` (not `cpdef enum`) for scoped enums
#   - Scoped enums generate Python Enum classes with proper type checking
#   - The wrap-attach directive attaches the enum to the specified class
#   - The wrap-as directive controls the Python-visible name
#
# RESULT IN PYTHON:
#   foo = Foo()
#   foo.enumToInt(Foo.MyEnum.A)  # Works - correct enum type
#   foo.enumToInt(Foo2.MyEnum.A) # Raises AssertionError - wrong enum type
#
# =============================================================================

cdef extern from "enums.hpp":
     cdef cppclass Foo:
        # Method accepts Foo_MyEnum (which maps to Foo::MyEnum in C++)
        int enumToInt(Foo_MyEnum e)

cdef extern from "enums.hpp":
     cdef cppclass Foo2:
         # Foo2 has no methods, but we still wrap it to attach its enum
         pass


# -----------------------------------------------------------------------------
# Enums in the "Foo" namespace
# -----------------------------------------------------------------------------
cdef extern from "enums.hpp" namespace "Foo":

    # Foo::MyEnum - attached to class Foo, exposed as Foo.MyEnum
    cpdef enum class Foo_MyEnum "Foo::MyEnum":
        # wrap-attach:
        #  Foo
        #
        # wrap-as:
        #  MyEnum
        #
        # wrap-doc:
        #  Testing Enum documentation.
        A
        B
        C

    # Foo::MyEnum2 - a second enum in the same class
    cpdef enum class Foo_MyEnum2 "Foo::MyEnum2":
        # wrap-attach:
        #  Foo
        #
        # wrap-as:
        #  MyEnum2
        A
        B
        C


# -----------------------------------------------------------------------------
# Enums in the "Foo2" namespace
# -----------------------------------------------------------------------------
cdef extern from "enums.hpp" namespace "Foo2":

    # Foo2::MyEnum - same name as Foo::MyEnum but in different namespace
    # Attached to Foo2 class, exposed as Foo2.MyEnum (no conflict with Foo.MyEnum)
    cpdef enum class Foo2_MyEnum "Foo2::MyEnum":
        # wrap-attach:
        #  Foo2
        #
        # wrap-as:
        #  MyEnum
        #
        # wrap-doc:
        #  This is a second enum in another namespace.
        A
        C
        D

