autowrap
========

Generates Python Extension modules from Cythons PXD files.

This module uses the Cython "header" .pxd files to automatically generate
Cython input (.pyx) files. It does so by parsing the header files and possibly
annotations in the header files to generate correct Cython code. For an
example, please have a look at `examples/int_holder.h` and
`example/int_holder.pxd` which together form the input to the program.

Simple example
---------------------

Assuming you want to wrap the following C++ class

```c++
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
```


you could generate the following `.pxd` file and run autowrap

```cython
cdef extern from "int_holder.hpp":
    cdef cppclass IntHolder:
        int i_
        IntHolder(int i)
        IntHolder(IntHolder & i)
        int add(IntHolder o)
```


which will generate Cython code that allows direct access to the public
internal variable `i_` as well as to the two constructors and the public `add`
method.

Compiling 
-------------

To compile the above examples to .pyx and .cpp files, go to the `./example`
folder and run

    $ autowrap --out py_int_holder.pyx int_holder.pxd

which will generate files `py_int_holder.pyx` and `py_int_holder.cpp`
which you can compile using the following file `setup.py` which we
provide in `example/setup.py`:

```python
import os, pkg_resources
from distutils.core import setup, Extension
from Cython.Distutils import build_ext

data_dir = pkg_resources.resource_filename("autowrap", "data_files")
include_dir = os.path.join(data_dir, "autowrap")

ext = Extension("py_int_holder",
                sources = ['py_int_holder.cpp'],
                language="c++",
                include_dirs = [include_dir, data_dir],
               )

setup(cmdclass={'build_ext':build_ext},
      name="py_int_holder",
      version="0.0.1",
      ext_modules = [ext]
     )
```

You can build the final Python extension module by running

    $ python setup.py build_ext --inplace

And you can use the final module running

```python
    >>> import py_int_holder
    >>> ih = py_int_holder.IntHolder(42)
    >>> print ih.i_
    42
    >>> print ih.add(ih)
    84
```

To get some insight how `autowrap` works, you can inspect files
`py_int_holder.pyx` and `py_int_holder.cpp`. Note how you can get direct access
to public members such as `i_` and can use public methods such as `add`
directly on the object.

More complex example
---------------------

Assuming you want to wrap the following C++ class

```c++
    template <typename TemplateType>
    class TemplateClassName {
      public:
        TemplateType myInner_;
        TemplateClassName(TemplateType i): myInner_(i) {};
        void process_data(double & ret_1, double & ret_2)
        {
            ret_1 += 20.0;
            ret_2 += 40.0;
        }
    };
```

you could generate the following .pyx file and run autowrap (see below for a list of all directives)

```cython
    cdef extern from "libcpp_test.hpp":
        # example where no instance exists with the base class name
        # we should make sure that no Python class "TemplateClassName" is generated
        # NOTE: the text after "wrap-doc" will appear in the Python __doc__ string
        cdef cppclass TemplateClassName[TemplateType]:
            # wrap-instances:
            #   TemplatedWithFloat := TemplateClassName[float]
            #   TemplatedWithDouble := TemplateClassName[double]
            #
            # wrap-doc:
            #   TemplatedClass for double and float, 
            #   useful for processing foobars

            TemplateType myInner_
            TemplateClassName(TemplateType i)

            void process_data(double ret_1, double ret_2)
```

which will generate Cython code that allows direct access to the public
internal variable `myInner_` as well as to the two constructors and the
`process_data` function.

Directives
----------

A number of directives allow the user to modify the behavior of autowrap, which
are generally added as a comment after a function or class declaration. All
directives can be used as `wrap-XXX:argument` with the argument being optional
for some directives. You can combine directives easily for classes (see above)
and for methods by putting them on the same line. The currently supported
directives are:

- `wrap-ignore`: Will not create a wrapper for this function or class (e.g. abstract base class that needs to be known to Cython but cannot be wrapped)
- `wrap-iter-begin`: For begin iterators
- `wrap-iter-end`: For end iterators
- `wrap-attach`: Attach to a specific class (can be used for static functions or nested classes)
- `wrap-pass-constructor`: Create a special constructor that cannot be called
  (e.g. can be used on the default constructor if in C++ an argument is
  required for the constructor)
- `wrap-doc`: Injection of a true Python docstring for function or class, e.g. `wrap-doc:Some important docstring`
- `wrap-as`: Wrap with a different name, e.g. `wrap-as:NewName`
- `wrap-constant`: Useful for constant properties that should have `__get__` but no `__set__`
- `wrap-upper-limit`: Can be used to check input argument of type int (e.g. for operator[]) to make sure the input integer does not exceed the limit
- `wrap-cast`: Wrap casting functions such as `double operator()(MyObject)`
- `wrap-inherits`: Inherit methods from parent classes (see below for example) 
- `wrap-instances`: Wrap specific template instances (see below for example)
- `wrap-manual-memory`: will allow the user to provide manual memory management
  of `self.inst`, therefore the class will not provide the automated
  `__dealloc__` and inst attribute (but their presence is still expected).
  This is useful if you cannot use the shared-ptr approach to store a reference
  to the C++ class (as with singletons for example).
- `wrap-hash`: If the produced class should be hashable, give a hint which
  method should be used for this. This method will be called on the C++ object
  and fed into the Python "hash" function. This implies the class also provides
  a `operator==` function.  Note that the only requirement for a hash function is
  that equal objects produce equal values.
- `wrap-with-no-gil`: Autowrap will release the GIL (Global interpreter lock)
  before calling this method, so that it does not block other Python threads.
  It is advised to release the GIL for long running, expensive calls into
  native code which does not manipulate python objects. 

### Method Directives

Method directives are added using Python comments after a method declaration:

```
  size_t countSomething(libcpp_vector[double] inpVec) # wrap-ignore
```

This will skip wrapping the function `countSomething`

Example declaration for releasing the GIL (in the pxd):

```
    void Compile() nogil # wrap-with-no-gil
```

Example for multiple wrap statements in a method directive:

```
    size_t countSomething(libcpp_vector[double] inpVec) nogil # wrap-attach:Counter wrap-as:count 
```
    
In addition you have to declare the function as nogil. For further details see 
http://docs.cython.org/src/userguide/external_C_code.html


### Class Directives

Directives for classes are put after the class with one indent and an empty
line between two directives:

```
        cdef cppclass TemplatedClass[U,V]:
            # wrap-inherits:
            #    C[U]
            #    D
            #
            # wrap-instances:
            #   TC_int_float := TemplatedClass[int, float]
            #   TC_pure := TemplatedClass[int, int]
            #
            # wrap-hash:
            #   getName().c_str()
```

This will create two Python objects `TC_int_float` which wraps `TemplatedClass[int, float]` and
a Python class `TC_pure` which wraps `TemplatedClass[int,int]`.
If you wrap a C++ class without template parameters you can omit
the 'wrap-instances' annotation. In this case the name of the Python
class is the same as the name of the C++ class.

Additionally, TemplatedClass[U,V] gets additional methods from C[U] and from D without having to re-declare them.

Finally, the object is hashable in Python (assuming it has a function `getName()` that returns a string).

### Docstrings

Docstrings can be added to classes and methods using the `wrap-doc` statement. Multi line docs are supported with
empty lines and indentation. Note that every line of the docstring needs to begin with # and two spaces, even the empty lines.
Methods still support single line doctrings directly after the declaration. However, if there is a multi line docstring it is
taken with priority.

```
    cdef cppclass Counter:
        # wrap-doc:
        #  Multi line docstring for class
        #    with indentation
        #  
        #  and empty line

        size_t count(libcpp_vector[double] inpVec) # wrap-doc:Single line docstring that will be overwritten by multi line wrap-doc
        # wrap-doc:
        #  Multi line docstring for method
        #    with indentation
        #  
        #  and empty line
```

Test examples
-------------

The tests provide several examples on how to wrap tricky C++ constructs, see for example 

- [minimal.pxd](../tests/test_files/minimal.pxd) for a class example that uses static methods, pointers, operators ([], +=, \*, etc) and iterators
- [libcpp_stl_test.pxd](../tests/test_files/libcpp_stl_test.pxd) for examples using the STL 
- [libcpp_test.pxd](../tests/test_files/libcpp_test.pxd) for a set of C++ functions that use abstract base classes
- [libcpp_utf8_string_test.pxd](../tests/test_files/libcpp_utf8_string_test.pxd) for an example using UTF8 strings
- [templated.pxd](../tests/test_files/templated.pxd) for an example using templated classes

Further examples
----------------

For further examples with full integration into a build process, you could look
at the OpenMS project and the associated build process, which uses a CMakeLists.txt file
(https://github.com/OpenMS/OpenMS/blob/develop/src/pyOpenMS/CMakeLists.txt)
which then calls a script building the cpp files
(https://github.com/OpenMS/OpenMS/blob/develop/src/pyOpenMS/create_cpp_extension.py)
using the `autowrap.Main.create_wrapper_code` directly. Next, the package is
built by calling `setup.py`.

Larger projects
--------------

By default, autowrap will produce a single `.pyx` file which contains a wrapper
for every class and function provided to autowrap. This has the advantage that
a single module is produced which contains all the wrapped classes and methods.
However, for larger projects, this can lead to large .cpp files and problems
with compilation. It is thus possible to change the default behavior of
autowrap and split up the compilation into multiple units where each unit
contains some of the projects classes. For an example on how to do this, see
`./tests/test_full_library.py`.

