from distutils.core import setup, Extension
from Cython.Distutils import build_ext


ext = Extension("itertest", sources = [ "itertest.pyx"], language="c++",
        extra_compile_args = [])

setup(cmdclass = {'build_ext' : build_ext},
      ext_modules = [ext]
     )
