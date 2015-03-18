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


    class IntHolder {
        public:
            int i_;
            IntHolder(int i): i_(i) { };
            IntHolder(const IntHolder & i): i_(i.i_) { };
    };


you could generate the following .pyd file and run autowrap


    cdef extern from "int_holder.hpp":
        cdef cppclass IntHolder:
            int i_
            IntHolder(int i)
            IntHolder(IntHolder & i)


which will generate Cython code that allows direct access to the public
internal variable `i_` as well as to the two constructors.

Compiling 
-------------

To compile the above examples to .pyx and .cpp files change the directory
to the folder containing `int_holder.hpp` and `int_holder.pxd` and run

    $ autowrap --out py_int_holder.pyx int_holder.pxd

which will generate files `py_int_holder.pyx` and `py_int_holder.cpp`
which you can compile using the following file `setup.py` which we
provide in the `examples` folder:


    from distutils.core import setup, Extension

    import pkg_resources

    data_dir = pkg_resources.resource_filename("autowrap", "data_files")


    from Cython.Distutils import build_ext

    ext = Extension("py_int_holder", sources = ['py_int_holder.cpp'], language="c++",
            extra_compile_args = [],
            include_dirs = [data_dir],
            extra_link_args = [],
            )

    setup(cmdclass = {'build_ext' : build_ext},
        name="py_int_holder",
        version="0.0.1",
        ext_modules = [ext]
        )

You can build the final Python extension module by running

    $ python setup.py build_ext --inplace

And you can use the final module running

    >>> import py_int_holder
    >>> ih = py_int_holder.IntHolder(42)
    >>> print ih.i_
    42


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

- `# wrap-with-no-gil`  
Autowrap will release the GIL (Global interpreter lock) before calling this method,
so that it does not block other python threads. It is advised to release the GIL for
long running, expensive calls into native code which does not manipulate python objects. 

Example declaration (pxd):

    void Compile() nogil # wrap-with-no-gil
    
In addition you have to declare the function as nogil. For further details see 
http://docs.cython.org/src/userguide/external_C_code.html