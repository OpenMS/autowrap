
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

