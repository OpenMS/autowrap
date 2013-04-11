autowrap
========

Generates Python Extension modules from [Cythons](http://cython.org) PXD files.

Introduction
------------

One important application of [Cython](http://cython.org) is to wrap C++ classes
for using them in Python. As Cythons syntax is quite similar to the syntax of
Python writing a wrapper can be learned easily. Further Cython prevents you
from many typical errors which might get in your way if you write
such a wrapper in C++.


This wrapping process typically consist of four steps:

  1. Rewrite parts of the header files of your C++ library in so called `.pxd`
     files. These give Cython information for calling the
     library and for error checking the code written in the following step.

  2. Write Cython code which wrapps the C++ library. This code resists
     in one or more `.pyx` files.

  3. Translate these `.pyx` files to C++ code with Cython.

  4. Use distutils to compile and link the C++ code to the final  Python
     extension module.

Depending on the size of your library step 2 can be tedious and
the code will consist of many similar code blocks with only minor differences.

This is where autowrap comes into play: autowrap replaces step 2 by
parsing the `.pxd` files and generating correct code for step 3.
In order to steer and configure this process the `.pxd` files can be
annotated using special formatted comments.

The main work which remains is writing the `.pxd` files. This is comparable to
the declarations you have to provide if you use
[SIP](http://www.riverbankcomputing.com/software/sip)
or [SWIG](http://swig.org).


A Minimal Example
-----------------

We assume that you installed `autowrap` already, so that running

    $ autowrap --help

does not fail.


Assuming you want to wrap the following C++ class

    class IntHolder {
        public:
            int i_;
            IntHolder(int i): i_(i) { };
            IntHolder(const IntHolder & i): i_(i.i_) { };
            int add(const IntHolder & other) {
                return i_ + other.i_;
            }
    };

you could create the following `.pxd` file

    cdef extern from "int_holder.hpp":
        cdef cppclass IntHolder:
            int i_
            IntHolder(int i)
            IntHolder(IntHolder & i)
            int add(IntHolder o)

These files are already conttained in the `examples/` folder.

To create files `.pyx` and `.cpp` for wrapping the class `IntHolder`
run

    $ autowrap --out py_int_holder.pyx int_holder.pxd

inside the `examples`folder.  This will generate files `py_int_holder.pyx` and
`py_int_holder.cpp` which you can compile using the following file `setup.py`:


    from distutils.core import setup, Extension
    from Cython.Distutils import build_ext
    import pkg_resources

    data_dir = pkg_resources.resource_filename("autowrap", "data_files")

    ext = Extension("py_int_holder", sources=['py_int_holder.cpp'], language="c++",
            extra_compile_args=[],
            include_dirs=[data_dir],
            extra_link_args=[],
            )

    setup(cmdclass={'build_ext':build_ext},
          name="py_int_holder",
          version="0.0.1",
          ext_modules=[ext]
         )


To get some insight how autowrap works, you can inspect files `py_int_holder.pyx` 
and `py_int_holder.cpp`.

Building the Python extension module now is done by running

    $ python setup.py build_ext --inplace

This module can now be used as follows

    >>> import py_int_holder
    >>> ih = py_int_holder.IntHolder(42)
    >>> print ih.i_
    42
    >>> print ih.add(ih)
    84

Further docs can be found in `docs/` folder.


Credits
-------

Many thanks go to:

   - Hannes Roest, ETH Zürich, for contributing new ideas, patches, and
     fruitful discussions.

   - Lars Gustav Malmström, ETH Zürich for getting the ball rolling.

   - the developers of Cython for contributing such a powerfull and high
     quality tool.
