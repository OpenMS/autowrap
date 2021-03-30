from __future__ import absolute_import, print_function

import os
import glob

import autowrap
import autowrap.Code
import autowrap.CodeGenerator
import autowrap.DeclResolver
import autowrap.Main
import autowrap.PXDParser
import autowrap.Utils

__license__ = """

Copyright (c) 2012-2014, Uwe Schmitt, ETH Zurich, all rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

Neither the name of the mineway GmbH nor the names of its contributors may be
used to endorse or promote products derived from this software without specific
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


test_files = os.path.join(os.path.dirname(__file__), "test_files", "full_lib")


template = """
from distutils.core import setup, Extension

import sys
import pprint

from Cython.Distutils import build_ext

ext = []
ext.append( Extension("moduleCD", sources = ['package/moduleCD.cpp'], language="c++",
        include_dirs = %(include_dirs)r,
        extra_compile_args = %(compile_args)r,
        extra_link_args = %(link_args)r,
        ))
ext.append(Extension("moduleA", sources = ['package/moduleA.cpp'], language="c++",
        include_dirs = %(include_dirs)r,
        extra_compile_args = %(compile_args)r,
        extra_link_args = %(link_args)r,
        ))
ext.append(Extension("moduleB", sources = ['package/moduleB.cpp'], language="c++",
        include_dirs = %(include_dirs)r,
        extra_compile_args = %(compile_args)r,
        extra_link_args = %(link_args)r,
        ))

setup(
      name="package",
      version="0.0.1",
      ext_modules = ext
     )

"""


def compile_and_import(names, source_files, include_dirs=None, extra_files=[], **kws):

    if include_dirs is None:
        include_dirs = []

    debug = kws.get("debug")
    import os.path
    import shutil
    import tempfile
    import subprocess
    import sys
    from importlib import import_module

    compile_args = []
    link_args = []
    
    if sys.platform == "darwin":
        compile_args += ["-stdlib=libc++", "-std=c++11"]
        link_args += ["-stdlib=libc++"]

    if sys.platform == "linux" or sys.platform == "linux2":
        compile_args += ["-std=c++11"]

    if sys.platform != "win32":
        compile_args += ["-Wno-unused-but-set-variable"]

    setup_code = template % locals()
    if debug:
        print("\n")
        print("-" * 70)
        print(setup_code)
        print("-" * 70)
        print("\n")

    now = os.getcwd()

    try:
        sys.path.insert(0, now)
        sys.path.insert(0, now+"/package")

        with open("setup.py", "w") as fp:
            fp.write(setup_code)

        assert (
            subprocess.Popen(
                "%s setup.py build_ext --force --inplace" % sys.executable,
                shell=True
            ).wait()
            == 0
        )
        files = glob.iglob("*.so")
        for file in files:
            if os.path.isfile(file):
                shutil.copy2(file, "./package/")

        results = [import_module(name) for name in names]

    finally:
        sys.path = sys.path[1:]
        os.chdir(now)

    print(results)
    return results


def test_full_lib(tmpdir):
    """
    Example with multi-file library and multi-file result.

    This shows a full run through of a case where multiple class files (A, B,
    C, D) with multiple classes in them (Aklass, A_second, etc.) need to be
    wrapped, a total of 10 different entities over 8 header files (4 hpp and 4
    pxd files). Autowrap will generate a .pxd and a .pyx file for each module.

    We decided to wrap the library into three modules, A, B and CD to show the
    capability of autowrap to do that. Note that we have perform multiple steps:

    - Step 1: parse all header files *together* - all pxd files need to be
              parsed together so that declarations are properly resolved.
    - Step 2: Map the different parsed entities to the pxd files and the
              desired modules, we use a master dict here that can be consumed
              by autowrap and specifies which pxd files and which declarations
              make up which module.
    - Step 3: Generate Cython code for each module
    - Step 4: Generate C++ code for each module (note that Step 3 has to be
              completed first before we can start to generate C++ code)
    - Step 5: Compile (run setup.py)

    Note that autowrap gives you full control how many modules you want to
    produce and which classes go into which modules. It automatically generates
    correct cimport statements in each so that dependencies between the modules
    are not an issue.
    """

    curdir = os.getcwd()
    workdir = tmpdir.strpath + "/package"
    os.makedirs(workdir)
    os.chdir(workdir)
    open("__init__.py", "a").close()

    try:

        mnames = ["moduleA", "moduleB", "moduleCD"]

        # Step 1: parse all header files
        PY_NUM_THREADS = 1
        pxd_files = ["A.pxd", "B.pxd", "C.pxd", "D.pxd"]
        full_pxd_files = [os.path.join(test_files, f) for f in pxd_files]
        decls, instance_map = autowrap.parse(
            full_pxd_files, ".", num_processes=int(PY_NUM_THREADS)
        )

        assert len(decls) == 13, len(decls)

        # Step 2: Perform mapping
        pxd_decl_mapping = {}
        for de in decls:
            tmp = pxd_decl_mapping.get(de.cpp_decl.pxd_path, [])
            tmp.append(de)
            pxd_decl_mapping[de.cpp_decl.pxd_path] = tmp

        masterDict = {}
        masterDict[mnames[0]] = {
            "decls": pxd_decl_mapping[full_pxd_files[0]],
            "addons": [],
            "files": [full_pxd_files[0]],
        }
        masterDict[mnames[1]] = {
            "decls": pxd_decl_mapping[full_pxd_files[1]],
            "addons": [],
            "files": [full_pxd_files[1]],
        }
        masterDict[mnames[2]] = {
            "decls": pxd_decl_mapping[full_pxd_files[2]]
            + pxd_decl_mapping[full_pxd_files[3]],
            "addons": [],
            "files": [full_pxd_files[2]] + [full_pxd_files[3]],
        }

        # Step 3: Generate Cython code
        converters = []
        for modname in mnames:
            m_filename = "%s.pyx" % modname
            cimports, manual_code = autowrap.Main.collect_manual_code(
                masterDict[modname]["addons"]
            )
            autowrap.Main.register_converters(converters)
            autowrap_include_dirs = autowrap.generate_code(
                masterDict[modname]["decls"],
                instance_map,
                target=m_filename,
                debug=False,
                manual_code=manual_code,
                extra_cimports=cimports,
                include_boost=True,
                allDecl=masterDict,
                add_relative=True
            )
            masterDict[modname]["inc_dirs"] = autowrap_include_dirs
        os.chdir("..")
        # Step 4: Generate CPP code
        for modname in mnames:
            m_filename = "package/%s.pyx" % modname
            autowrap_include_dirs = masterDict[modname]["inc_dirs"]
            autowrap.Main.run_cython(
                inc_dirs=autowrap_include_dirs, extra_opts=None, out=m_filename
            )

        # Step 5: Compile
        all_pyx_files = ["package/%s.pyx" % modname for modname in mnames]
        all_pxd_files = ["package/%s.pxd" % modname for modname in mnames]
        include_dirs = masterDict[modname]["inc_dirs"]
        moduleA, moduleB, moduleCD = compile_and_import(
            mnames, all_pyx_files, include_dirs, extra_files=all_pxd_files
        )

    finally:
        os.chdir(curdir)

    Aobj = moduleA.Aalias(5)
    Asecond = moduleA.A_second(8)
    assert Asecond.i_ == 8
    assert Aobj.i_ == 5

    assert Aobj.KlassE is not None
    assert Aobj.KlassE.A1 is not None
    assert Aobj.KlassE.A2 is not None
    assert Aobj.KlassE.A3 is not None

    Bobj = moduleB.Bklass(5)
    assert Bobj.i_ == 5  # access through A_second
    Bobj.callA2()
    assert Bobj.i_ == 6  # access through A_second
    Bsecond = moduleB.B_second(8)
    assert Bsecond.i_ == 8
    Bsecond.processA(Aobj)
    assert Bsecond.i_ == 15

    assert Bobj.KlassE is not None
    assert Bobj.KlassE.B1 is not None
    assert Bobj.KlassE.B2 is not None
    assert Bobj.KlassE.B3 is not None
    assert Bobj.KlassKlass is not None

    # there are two different ways to get Bklass::KlassKlass, either through a
    # Bklass object or through the module
    Bobj_kk = Bobj.KlassKlass()
    Bobj_kk.k_ = 14
    assert Bobj_kk.k_ == 14
    Bobj_kk = moduleB.Bklass.KlassKlass()
    Bobj_kk.k_ = 14
    assert Bobj_kk.k_ == 14

    # Check doc string
    assert "Inherits from" in moduleB.Bklass.__doc__
    assert "some doc!" in moduleB.Bklass.__doc__
    assert len(moduleB.Bklass.__doc__) == 92, len(moduleB.Bklass.__doc__)

    Bsecond = moduleB.B_second(8)
    Dsecond = moduleCD.D_second(11)
    assert Dsecond.i_ == 11
    Dsecond.runB(Bsecond)
    assert Dsecond.i_ == 8
