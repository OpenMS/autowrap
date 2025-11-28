import os
from importlib.resources import files
from distutils.core import setup, Extension
from Cython.Distutils import build_ext

# Replace pkg_resources.resource_filename("autowrap", "data_files")
data_dir = str(files("autowrap") / "data_files")
include_dir = os.path.join(data_dir, "autowrap")

ext = Extension(
    "py_int_holder",
    sources=["py_int_holder.cpp"],
    language="c++",
    include_dirs=[include_dir, data_dir],
)

ext2 = Extension(
    "py_vec_holder",
    sources=["py_vec_holder.cpp"],
    language="c++",
    include_dirs=[include_dir, data_dir],
)

setup(
    cmdclass={"build_ext": build_ext},
    name="py_int_holder",
    version="0.0.1",
    ext_modules=[ext, ext2],
)
