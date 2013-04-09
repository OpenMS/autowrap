autowrap
========

Generates Python Extension modules from [Cythons](http://cython.org) PXD files.

This module uses the Cython "header" `.pxd` files to automatically generate
Cython input `.pyx` files. It does so by parsing the header files and possibly
annotations in the header files to generate correct Cython code.

A Minimal Example
-----------------

We assume that you installed `autowrap` already, so that running

    $ autowrap --help

will not fail.


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

You can build the final Python extension module by running

    $ python setup.py build_ext --inplace

And you can use the final module as follows

    >>> import py_int_holder
    >>> ih = py_int_holder.IntHolder(42)
    >>> print ih.i_
    42
    >>> print ih.add(ih)
    84

Further docs can be found in 'docs/' folder.
