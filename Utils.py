

template = """

from distutils.core import setup, Extension
#from setuptools import setup, Extension

from Cython.Compiler.Main import compile, default_options, build_ext

#default_options["cplus"]= 1
#r = compile("%(name)s.pyx")
#assert r.num_errors == 0

ext = Extension("%(name)s", sources = [ "%(name)s.cpp"], language="c++",
        extra_compile_args = [])

setup(cmdclass = {'build_ext' : build_ext},
      name="int_container_class",
      version="0.0.1",
      ext_modules = [ext]
     )

"""

print template % dict(name="o")
