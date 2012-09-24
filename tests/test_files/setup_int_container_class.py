from distutils.core import setup, Extension
#from Cython.Distutils import build_ext
from setuptools import setup, Extension


from Cython.Compiler.Main import compile, default_options

default_options["cplus"]= 1
r = compile("int_container_class.pyx")
assert r.num_errors == 0

ext = Extension("int_container_class", sources = [ "int_container_class.cpp"], language="c++",
        extra_compile_args = [])

setup(#cmdclass = {'build_ext' : build_ext},
      name="int_container_class",
      version="0.0.1",
      ext_modules = [ext]
     )
