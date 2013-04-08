autowrap
========

Generates Python Extension modules from Cythons PXD files

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

