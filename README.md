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

