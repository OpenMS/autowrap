template = """

from distutils.core import setup, Extension

import sys
import pprint

from Cython.Distutils import build_ext

ext = Extension("test_files/out.cpp", language="c++",
        include_dirs = %(include_dirs)r,
        extra_compile_args = [],
        extra_link_args = [],
        )

setup(cmdclass = {'build_ext' : build_ext},
      name="test_main",
      version="0.0.1",
      ext_modules = [ext]
     )

"""

def test_run():
    from autowrap.Main import run
    from autowrap.Utils import compile_and_import

    import glob

    pxds = glob.glob("test_files/pxds/*.pxd")
    assert pxds

    addons = glob.glob("test_files/addons/*.pyx")
    assert addons

    converters = glob.glob("test_files/converters/*.py")
    assert converters

    includes = run(pxds, addons, converters, "test_files/out.pyx")

    includes.append("test_files/includes")

    mod = compile_and_import("out", ["test_files/out.cpp"], includes)

    ih = mod.IntHolder()
    ih.set_(3)
    assert ih.get() == 3

    b = mod.B()
    b.set_(ih)
    assert b.get().get() == 3

    assert b.super_get(3) == 4



