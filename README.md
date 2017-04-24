autowrap [![Build Status](https://travis-ci.org/uweschmitt/autowrap.svg?branch=master)](https://travis-ci.org/uweschmitt/autowrap)
========



Generates Python Extension modules from [Cython][] PXD files.

Introduction
------------

One important application of [Cython][] is to wrap C++ classes for using them
in Python. As [Cython][]s syntax is quite similar to the syntax of Python
writing a wrapper can be learned easily. Further [Cython][] prevents you from
many typical errors which might get in your way if you write such a wrapper in
C++.


This wrapping process typically consist of four steps:

  1. Rewrite parts of the header files of your C++ library in so called `.pxd`
  files. These give [Cython][] information for calling the library and for
  error checking the code written in the following step.

  2. Write [Cython][] code which wraps the C++ library. This code resists in
  one or more `.pyx` files.

  3. Translate these `.pyx` files to C++ code with [Cython][].

  4. Use [distutils][] to compile and link the C++ code to the final  Python
  extension module.

Depending on the size of your library step 2 can be tedious and the code will
consist of many similar code blocks with only minor differences.

This is where `autowrap` comes into play: `autowrap` replaces step 2 by
analyzing the `.pxd` files with [Cython][]s own parser and generating correct
code for step 3.  In order to steer and configure this process the `.pxd` files
can be annotated using special formatted comments. 

The main work which remains is writing the `.pxd` files. This is comparable to
the declarations you have to provide if you use
[SIP](http://www.riverbankcomputing.com/software/sip) or
[SWIG](http://swig.org).


Documentation
-------------

We assume that you installed `autowrap` already, so running

    $ autowrap --help

does not fail.

Please see [docs/README.md](docs/README.md) for further documentation.

Features
--------

   - Wrapping of template classes with their public methods and
     attributes,enums, free functions and static methods.

   - Included converters from Python data types to (many) STL containers and
     back.  As this is version 0.2, not all STL containers are supported. We
     plan full support of nested STL containers.

   - Manually written [Cython][] code can be incorporated for wrapping code
     which `autowrap` can not handle (yet), and for enriching the API of the
     wrapped library. As this is done by writing [Cython][] instead of C/C++
     code, we get all benefits which [Cython][] shows compared to C/C++.

     Writing a code generator for handling all thinkable APIs is hard, and
     results in a difficult and hard to understand code base. We prefer a
     maintainable code generator which handles 95% of all use cases, where the
     remaining 5% are still wrapped manually.

   - For achieving a pythonic API, converters for library specific data types
     can be implemented easily.  These converters are written in Python and
     [Cython][], not in C/C++ code using the C-API of CPython. 

   - `autowrap` relies on [Cython][], so we get  automatic conversion of C++
     exceptions to Python exceptions and wrapper code with correct reference
     counting. Using [distutils][] we do not have to care to much about the
     build process on the targeted platform.

   - Support for generating some special methods, as `__getitem__`, `__copy__`
     and numerical comparison operators.


Credits
-------

Many thanks go to:

   - [Hannes Roest](http://github.com/hroest), ETH Zürich, for contributing new
     ideas, patches, fruitful discussions and writing the first draft of this
     README.

   - [Lars Gustav Malmström](http://www.imsb.ethz.ch/researchgroup/malars), ETH
     Zürich, for getting the ball rolling.

   - The developers of [Cython][] for providing such a powerful and high
     quality tool.

   - Thanks to https://github.com/hendrik-cliqz for implementing the "no-gil" annotation.


[Cython]: http://cython.org
[distutils]: http://docs.python.org/2/distutils/
