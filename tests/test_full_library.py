from __future__ import print_function
from __future__ import absolute_import

import pytest

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

import autowrap.DeclResolver
import autowrap.CodeGenerator
import autowrap.PXDParser
import autowrap.Utils
import autowrap.Code
import autowrap.Main
import autowrap

import os
import math
import copy

from .utils import expect_exception

test_files = os.path.join(os.path.dirname(__file__),  "test_files", "full_lib")

template = """
from distutils.core import setup, Extension

import sys
import pprint

from Cython.Distutils import build_ext

ext = []
ext.append( Extension("moduleCD", sources = ['moduleCD.pyx'], language="c++",
        include_dirs = ['/home/hr/projects/autowrap/autowrap/data_files/autowrap', '/home/hr/projects/autowrap/tests/test_files/full_lib'],
        extra_compile_args = ['-Wno-unused-but-set-variable'],
        extra_link_args = [],
        ))
ext.append(Extension("moduleA", sources = ['moduleA.pyx'], language="c++",
        include_dirs = ['/home/hr/projects/autowrap/autowrap/data_files/autowrap', '/home/hr/projects/autowrap/tests/test_files/full_lib'],
        extra_compile_args = ['-Wno-unused-but-set-variable'],
        extra_link_args = [],
        ))
ext.append(Extension("moduleB", sources = ['moduleB.pyx'], language="c++",
        include_dirs = ['/home/hr/projects/autowrap/autowrap/data_files/autowrap', '/home/hr/projects/autowrap/tests/test_files/full_lib'],
        extra_compile_args = ['-Wno-unused-but-set-variable'],
        extra_link_args = [],
        ))

setup(cmdclass = {'build_ext' : build_ext},
      name="moduleCD",
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

    tempdir = tempfile.mkdtemp()
    if debug:
        print("\n")
        print("tempdir=", tempdir)
        print("\n")
    for source_file in source_files:
        shutil.copy(source_file, tempdir)
    for extra_file in extra_files:
        shutil.copy(extra_file, tempdir)

    if sys.platform != "win32":
        compile_args = "'-Wno-unused-but-set-variable'"
    else:
        compile_args = ""

    include_dirs = [os.path.abspath(d) for d in include_dirs]
    source_files = [os.path.basename(f) for f in source_files]
    setup_code = template 
    if debug:
        print("\n")
        print("-" * 70)
        print(setup_code)
        print("-" * 70)
        print("\n")

    now = os.getcwd()
    os.chdir(tempdir)
    with open("setup.py", "w") as fp:
        fp.write(setup_code)

    import sys
    sys.path.insert(0, tempdir)
    if debug:
        print("\n")
        print("-" * 70)
        import pprint
        pprint.pprint(sys.path)
        print("-" * 70)
        print("\n")

    assert subprocess.Popen("%s setup.py build_ext --force --inplace" % sys.executable, shell=True).wait() == 0

    results = []
    for name in names:
        print("BUILT")
        result = __import__(name)
        print("imported")
        if debug:
            print("imported", result)
        results.append(result)

    sys.path = sys.path[1:]
    os.chdir(now)
    print(results)
    return results



def test_full_lib():

    target_mA = os.path.join(test_files, "moduleA.pyx")
    target_mB = os.path.join(test_files, "moduleB.pyx")
    target_mCD = os.path.join(test_files, "moduleCD.pyx")

    mnames = ["moduleA", "moduleB", "moduleCD"]

    PY_NUM_THREADS = 1
    pxd_files = ["A.pxd", "B.pxd", "C.pxd", "D.pxd"]
    full_pxd_files = [ os.path.join(test_files, f) for f in pxd_files]
    decls, instance_map = autowrap.parse(full_pxd_files, ".", num_processes=int(PY_NUM_THREADS))

    # Perform mapping
    pxd_decl_mapping = {}
    for de in decls:
        tmp = pxd_decl_mapping.get(de.cpp_decl.pxd_path, []) 
        tmp.append(de)
        pxd_decl_mapping[ de.cpp_decl.pxd_path] = tmp 

    # assert len(decls) == 10, len(decls)

    allDecl_mapping = {}
    allDecl_mapping[mnames[0]] = {"decls" : pxd_decl_mapping[ full_pxd_files[0] ], "addons" : [], "files" : [ full_pxd_files[0] ]}
    allDecl_mapping[mnames[1]] = {"decls" : pxd_decl_mapping[ full_pxd_files[1] ], "addons" : [], "files" : [ full_pxd_files[1] ]}
    allDecl_mapping[mnames[2]] = {"decls" : pxd_decl_mapping[ full_pxd_files[2] ] + pxd_decl_mapping[ full_pxd_files[3] ], "addons" : [], "files" : [ full_pxd_files[2] ] + [full_pxd_files[3] ]}
    print(allDecl_mapping)

    converters = []
    for modname in mnames:
        m_filename = "%s.pyx" % modname
        cimports, manual_code = autowrap.Main.collect_manual_code(allDecl_mapping[modname]["addons"])
        autowrap.Main.register_converters(converters)
        autowrap_include_dirs = autowrap.generate_code(allDecl_mapping[modname]["decls"], instance_map,
                                                       target=m_filename, debug=False, manual_code=manual_code,
                                                       extra_cimports=cimports,
                                                       include_boost=False, allDecl=allDecl_mapping)
        allDecl_mapping[modname]["inc_dirs"] = autowrap_include_dirs



    for modname in mnames:
        m_filename = "%s.pyx" % modname
        autowrap_include_dirs = allDecl_mapping[modname]["inc_dirs"]
        autowrap.Main.run_cython(inc_dirs=autowrap_include_dirs, extra_opts=None, out=m_filename)


    all_pyx_files = ["%s.pyx" % modname  for modname in mnames]
    all_pxd_files = ["%s.pxd" % modname  for modname in mnames]
    include_dirs = allDecl_mapping[modname]["inc_dirs"]
    print (include_dirs)
    moduleA, moduleB, moduleCD = compile_and_import(mnames, all_pyx_files, include_dirs, extra_files=all_pxd_files)


    print (moduleA)
    print (moduleB)

    Bobj = moduleB.Bklass(5)
    Bsecond = moduleB.B_second(8)
    assert Bsecond.i_ == 8

    Dsecond = moduleCD.D_second(11)
    assert Dsecond.i_ == 11
    Dsecond.runB(Bsecond)
    assert Dsecond.i_ == 8

if __name__ == "__main__":
    test_libcpp()
