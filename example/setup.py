
from distutils.core import setup, Extension

from Cython.Distutils import build_ext
import pkg_resources

data_dir = pkg_resources.resource_filename("autowrap", "data_files")

ext = Extension("py_int_holder",
                sources = ['py_int_holder.cpp'],
                language="c++",
                include_dirs = [data_dir],
               )

setup(cmdclass={'build_ext':build_ext},
      name="py_int_holder",
      version="0.0.1",
      ext_modules = [ext]
     )

