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



This module uses the Cython "header" .pxd files to automatically generate
Cython input (.pyx) files. It does so by parsing the header files and possibly
annotations in the header files to generate correct Cython code. For an
example, please have a look at tests/test_files/libcpp_test.hpp and
tests/test_files/libcpp_test.pxd which together form the input to the program.

Simple example
---------------------

Assuming you want to wrap the following C++ class

    class Int {
        public:
            int i_;
            Int(int i): i_(i) { };
            Int(const Int & i): i_(i.i_) { };
    };

you could generate the following .pyx file and run autowrap

    cdef extern from "libcpp_test.hpp":
        cdef cppclass Int:
            int i_
            Int(int i)
            Int(Int & i)

which will generate Cython code that allows direct access to the public
internal variable `i_` as well as to the two constructors.

Compiling 
-------------
To compile the above examples to .pyx (assuming your .pxd file is called
`test.pxd` and the C++ header file `libcpp_test.hpp`), run the following in
python:

    import autowrap
    print autowrap.__path__ # to get the path for $AUTOWRAP_PATH
    debug_output = False
    output_file = "testlibrary.pyx"
    autowrap.parse_and_generate_code(["test.pxd"], ".", output_file,  debug_output)

and you should get a file `output.pyx` which you can then feed into Cython.

Unfortunately, for the next steps to work, Cython also expects the two pxd
files `smart_ptr.pxd` and `AutowrapRefHolder.pxd` to be present, which you can
find in `./autowrap/data_files/` and need to copy to your folder first before
executing Cython:

    cp /$AUTOWRAP_PATH/data_files/smart_ptr.pxd .
    cp /$AUTOWRAP_PATH/data_files/AutowrapRefHolder.pxd .
    cython --cplus testlibrary.pyx 

Compiling the .cpp depends of course on your system, one example could be

    gcc -pthread -fno-strict-aliasing -DNDEBUG -g -fwrapv -O2 -Wall -fPIC \
    -I/usr/lib/python2.7/dist-packages/numpy/core/include \
    -I/$AUTOWRAP_PATH/data_files/boost -I/$AUTOWRAP_PATH/data_files  \
    -I/usr/include/python2.7 -c testlibrary.cpp -o testlibrary.o

    g++ -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions -Wl,-Bsymbolic-functions \
    -Wl,-z,relro testlibrary.o -o testlibrary.so -Wl,-s

Once this is done, you can write in Python: 

    import testlibrary
    myint = testlibrary.Int(5)

Of course there are smarter ways to do the compilation process (for example with distutils), have a look at 
[http://docs.cython.org/src/reference/compilation.html](http://docs.cython.org/src/reference/compilation.html)

More complex example
---------------------

Assuming you want to wrap the following C++ class

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

you could generate the following .pyx file and run autowrap

    cdef extern from "libcpp_test.hpp":
        # example where no instance exists with the base class name
        # we should make sure that no Python class "TemplateClassName" is generated
        cdef cppclass TemplateClassName[TemplateType]:
            # wrap-instances:
            #   TemplatedWithFloat := TemplateClassName[float]
            #   TemplatedWithDouble := TemplateClassName[double]
            TemplateType myInner_
            TemplateClassName(TemplateType i)
            void process_data(double & ret_1, double & ret_2) #wrap-return:return(ret_1, ret_2)

which will generate Cython code that allows direct access to the public
internal variable `myInner_` as well as to the two constructors and the `process_data` function.

Annotations
---------------------
autowrap understands the following annotations for methods (put after the
corresponding method as a comment):

- `# wrap-ignore`  
Autowrap will not wrap this method (it may still be important for Cython to
have this method in the .pxd file)

- `# wrap-return:return(a,b)`  
Will return the tuple of variables a and b after processing

autowrap understands the following annotations for classes (put after the
class with one indent):

- `# wrap-inherits:  
   #  SuperClassA  
   #  SuperClassB`

Assuming that the current class inherits from SuperClassA and SuperClassB,
this will add methods from SuperClassA and SuperClassB to the class in
question.

- `# wrap-instances:  
   #  ClassA := TemplatedClass[A]  
   #  ClassB := TemplatedClass[B]`

This will create two Python objects, ClassA and ClassB which are derived from
TemplatedClass but with different template arguments (note that Cython does
not handle integer templates).

