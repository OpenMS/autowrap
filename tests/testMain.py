import pdb
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

def test_from_command_line():
    import os
    old_dir = os.path.abspath(os.getcwd())
    os.chdir("test_files")
    args =  ["pxds/*.pxd", "--out", "out.pyx", "--addons=/addons",
                                                    "--converters=converters"]
    from autowrap.Main import _main
    try:
        _main(args)
    finally:
        os.chdir(old_dir)

def test_run():

    from autowrap.Main import run
    from autowrap.Utils import compile_and_import

    import glob
    import os
    print os.getcwd()

    pxds = glob.glob("test_files/pxds/*.pxd")
    assert pxds

    addons = glob.glob("test_files/addons/*.pyx")
    assert addons

    converters = ["test_files/converters"]

    extra_includes = ["test_files/includes"]
    includes = run(pxds, addons, converters, "test_files/out.pyx",
            extra_includes)

    mod = compile_and_import("out", ["test_files/out.cpp"], includes)

    ih = mod.IntHolder()
    ih.set_(3)
    assert ih.get() == 3

    # automatic IntHolder <-> int conversions:
    b = mod.B()
    b.set_(7)
    assert b.get() == 7

    # test iter wrapping
    ih, = list(b)
    assert ih.get() == 7

    # manually generated method
    assert b.super_get(3) == 4

    # uses extra cimport for M_PI
    assert abs(b.get_pi()-3.141) < 0.001

    # type without automatic conversion:
    c = mod.C()
    fh = mod.FloatHolder(2.0)
    c.set_(fh)
    assert c.get().get() == 2.0

    fh, = list(c)
    assert fh.get() == 2.0

    # manual class:
    assert mod.CC.cc == 3

    assert mod.SharedPtrTestInt().sum_values(ih, ih) == 14

    mod.SharedPtrTestFloat().set_inner_value(fh, 12.0)
    assert fh.get() == 12.0



