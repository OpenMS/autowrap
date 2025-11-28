autowrap
========

Generates Python Extension modules from Cythons PXD files.

This module uses the Cython "header" .pxd files to automatically generate
Cython input (.pyx) files. It does so by parsing the header files and possibly
annotations in the header files to generate correct Cython code. For an
example, please have a look at `examples/int_holder.h` and
`example/int_holder.pxd` which together form the input to the program.

Requirements
------------

- Python ≥ 3.9
- Cython ≥ 3.1

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
>>> print(ih.i_)
42
>>> print(ih.add(ih))
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

High Level Overview
--------------
Broadly speaking, the autowrap process consists of two steps:
1. `DeclResolver` uses the `PXDParser` to parse files
2. `CodeGenerator` generates code

## Parsing

The process is kicked off by the autowrap `parse` function. This method takes
a list of files and a root directory as required parameters and optional parameters
for designating the number of prcesses to use and the cython warning level. The
method calls `DeclResolver#resolve_decls_from_files` with the given parameters.

Depending on the number of processes passed to the `parse` function, the
`resolve_decls_from_files` method calls either a single or multi threaded method
which calls the `PXDParser#parse_pxd_file` method on each given file.

The method `parse_pxd_file` uses the file path passed ot it to build Cython
`Context` and `Pipeline` objects. These objects are used to create a `root`
object. This object is passed to an `iter_bodies` method which extracts all the
Cython `node` objects present in the .pyx file. These objects are used as keys
to find the appropriate `BaseDecl` class for each node. These `BaseDecl` objects
are put into a Python list and passed back to the calling `DeclResolver` method (either
the `resolve_decls_from_files_single_thread` or `resolve_decls_from_files_multi_thread`
method), which then passes `decls` to the private method `DeclResolver#_resolve_decls`.

The `_resolve_decls` method starts by organizing each `BaseDecl` object by its
specific subclass (e.g., `CTypeDefDecl`, `EnumDecl`, etc). The method then handles
the data processing specific to each type of declaration and puts them into a list
of `Resolved*` objects (`ResolvedEnum` for example). The method also creates a dictionary
object called `instance_mapping` which contains class instantiations. Finally, the
`_resolve_decls` method returns a tuple of the resolved declaration objects and
`instance_mapping` dict.

## Code Generation

### Building a `CodeGenerator` object

The second part of the process is to call the autowrap `generate_code` method. This
method takes the list of resolved declaration objects and `instance_mapping` dict
generated from the `parse` method. The `generate_code` method also requires a
`target` argument for designating the name and path of the .pyx file to be generated.

The `gerneate_code` method builds a `CodeGenerator` object with its inputs. This object's
constructor first does some preprocessing to file paths and set other configurations.
Then, it gets all the classes, enums, functions, and typedefs of resolved declarations
and puts them into a Python list called `resolved`. It then builds an `instance_mapping`
instance attribute from both the `instance_mapping` argument passed to it, as well as
instances extracted from the resolved typedefs.

The constructor then checks for items in the `allDecl` argument. This argument will
have items in it if the user is parsing many files instead of just one. When this is
the case, the `CodeGenerator` constructor builds an `all_resolved` list which contains
instances of resolved classes, enums, functions, and typdefs from both the `resolved`
list, and the `allDecl` object.

Finally, the `CodeGenerator` constructor instantiates an instance variable called `cr`,
which stands for _container registry_ by calling the
`ConversionProvider#setup_converter_registry` method. This method takes lists of classes
and enums to wrap, as well as an instance map. From these values, the method creates
a new instance of the `ConverterRegistry` method and calls its `register` method on
each supported type of converter supported by autowrap.

The `register` method builds a hash containing the base type of declarations to be
converted as keys and maps the appropriate converter class to that key. For example,
a `void` declaration maps to a `VoidConverter`.

### Creating a .pyx file
Once the `CodeGenerator` object has been built, the `generate_code` method t hen calls
the object's `create_pyx_file` method. This method is responsible for actually generating
the Cython code. It starts by setting up the cimport paths by calling its own
`setup_cimport_paths` method. This method finds the exact location of each .pxd file
of the `cpp_decl` objects of each resolved declaration object of the `CodeGenerator` class.

This method sets the `CodeGenerator` object's `pxd_import_path` instance attribute to the
location of the .pxd file. The method also ensures that all .pxd files are located in one
directory, then sets the `pxd_dir` instance attribute as that directory.

With the cimport paths set, the `create_pyx_file` can then create the cimports by calling
the `create_cimports` method. This method first imports standard and extra modules if
they were designated in the `CodeGenerator` constructor.

Then, the `create_cimports` method instantiates a `Code` object. Then, the method iterates
through each item in its `all_resolved` attribute and adds lines of code to the `Code`
object, which interpolates local variables into parts of the pseudo code strings prefixed
with a `$` character. Finally, the `create_cimports` method appends that code to the
`CodeGenerator`'s `top_level_code` attribute.

With the cimports created, the `create_pyx_file` method creates the foreign cimports,
other classes created by autowrap, by callings the `create_foreign_cimports` method.
This method creates a `Code` object and generates a line of code for every extra
module that needs to be imported.

The next step in the `create_pyx_file` is to create includes, which it does by calling
the `create_includes` method. This method again builds a `Code` object that appends a
line for including a cdef line in the `top_level_code` attribute.

Next, the `create_pyx_file` method calls the appropriate wrapper method for classes,
enums, and free functions. These methods generate the Cython code necessary to
wrap those items and does so by creating `Code` objects and appending interpolated
strings into them.

As one last bit of preparation, the `create_pyx_file` method then resolves any
extra classes not resolved in the previous steps.

Finally, the `create_pyx_file` begins writing code to the .pyx file. It does this
by calling the `render` function on each `Code` object in its `top_level_code` and
`top_level_pyx_code` attributes. This `render` method builds a list of Cython code
expressions with proper indentation.

Finally, the `create_pyx_file` method creates files objects and writes the generated
pyi, pyx, and pxd code to their relevant files.

Finally, back in the autowrap `__init__` file, the `generate_code` method gathers
the include directories by calling `CodeGenerator`'s `get_include_dirs` method. This
method returns a list of packaged resources from the Cython code generated in the previous
steps. This value is then returned by the `generate_code` method, completing the second step.
