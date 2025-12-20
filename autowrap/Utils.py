# encoding: utf-8

from __future__ import print_function

__license__ = """

Copyright (c) 2012-2014, Uwe Schmitt, all rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

Neither the name of the ETH Zurich nor the names of its contributors may be
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

import sys

template = """

from distutils.core import setup, Extension

import sys
import pprint

from Cython.Distutils import build_ext

ext = Extension("%(name)s", sources = %(source_files)s, language="c++",
        include_dirs = %(include_dirs)r,
        extra_compile_args = %(compile_args)r,
        extra_link_args = %(link_args)r,
        )

setup(cmdclass = {'build_ext' : build_ext},
      name="%(name)s",
      version="0.0.1",
      ext_modules = [ext],
      package_data = {
            '': ['py.typed', '*.pyi'],
      },
      packages = ['.']
     )

"""


def _compile_array_wrappers_if_needed(tempdir, include_dirs, debug=False):
    """
    Compile ArrayWrappers module if it's needed (i.e., if numpy is being used).
    This makes ArrayWrappers available to the module being compiled.
    """
    import os
    import os.path
    import shutil
    import subprocess
    import sys
    
    # Check if ArrayWrappers source files exist
    autowrap_dir = os.path.dirname(os.path.abspath(__file__))
    array_wrappers_dir = os.path.join(autowrap_dir, "data_files", "autowrap")
    array_wrappers_pyx = os.path.join(array_wrappers_dir, "ArrayWrappers.pyx")
    array_wrappers_pxd = os.path.join(array_wrappers_dir, "ArrayWrappers.pxd")
    
    if not os.path.exists(array_wrappers_pyx):
        # ArrayWrappers not available, skip
        return
    
    if debug:
        print("Compiling ArrayWrappers module...")
    
    # Copy only ArrayWrappers.pyx to tempdir
    # Don't copy .pxd - Cython will auto-generate it from .pyx during compilation
    # The .pxd is only needed by OTHER modules that import ArrayWrappers
    shutil.copy(array_wrappers_pyx, tempdir)
    
    # Create a simple setup.py for ArrayWrappers
    compile_args = []
    link_args = []
    
    if sys.platform == "darwin":
        compile_args += ["-stdlib=libc++", "-std=c++17"]
        link_args += ["-stdlib=libc++"]
    
    if sys.platform == "linux" or sys.platform == "linux2":
        compile_args += ["-std=c++17"]
    
    if sys.platform != "win32":
        compile_args += ["-Wno-unused-but-set-variable"]
    
    # Get numpy include directory if available
    try:
        import numpy
        numpy_include = numpy.get_include()
    except ImportError:
        numpy_include = None
    
    # Filter include_dirs to exclude the autowrap data_files directory
    # to prevent Cython from finding ArrayWrappers.pxd during its own compilation
    filtered_include_dirs = [d for d in include_dirs if array_wrappers_dir not in os.path.abspath(d)]
    if numpy_include and numpy_include not in filtered_include_dirs:
        filtered_include_dirs.append(numpy_include)
    
    include_dirs_abs = [os.path.abspath(d) for d in filtered_include_dirs]
    
    setup_code = """
from distutils.core import setup, Extension
from Cython.Distutils import build_ext

ext = Extension("ArrayWrappers", 
                sources=["ArrayWrappers.pyx"], 
                language="c++",
                include_dirs=%r,
                extra_compile_args=%r,
                extra_link_args=%r)

setup(cmdclass={'build_ext': build_ext},
      name="ArrayWrappers",
      ext_modules=[ext])
""" % (include_dirs_abs, compile_args, link_args)
    
    # Write and build ArrayWrappers
    setup_file = os.path.join(tempdir, "setup_arraywrappers.py")
    with open(setup_file, "w") as fp:
        fp.write(setup_code)
    
    # Build ArrayWrappers in the tempdir
    result = subprocess.Popen(
        "%s %s build_ext --inplace" % (sys.executable, setup_file),
        shell=True,
        cwd=tempdir
    ).wait()
    
    if result != 0:
        print("Warning: Failed to compile ArrayWrappers module")
    elif debug:
        print("ArrayWrappers compiled successfully")
    
    # After building successfully, copy the .pxd file so other modules can cimport from it
    # We do this AFTER compilation to avoid conflicts during ArrayWrappers own compilation
    if result == 0 and os.path.exists(array_wrappers_pxd):
        shutil.copy(array_wrappers_pxd, tempdir)
        if debug:
            print("Copied ArrayWrappers.pxd to tempdir")


def compile_and_import(name, source_files, include_dirs=None, **kws):
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
    
    # Note: ArrayWrappers classes are now inlined into generated modules,
    # so we don't need to compile them separately anymore
    
    for source_file in source_files:
        if source_file[-4:] != ".pyx" and source_file[-4:] != ".cpp":
            raise NameError("Expected pyx and/or cpp files as source files for compilation.")
        shutil.copy(source_file, tempdir)
        stub = source_file[:-4] + ".pyi"
        if os.path.exists(stub):
            shutil.copy(stub, os.path.join(tempdir, name + ".pyi"))

    compile_args = []
    link_args = []

    if sys.platform == "darwin":
        compile_args += ["-stdlib=libc++", "-std=c++17"]
        link_args += ["-stdlib=libc++"]

    if sys.platform == "linux" or sys.platform == "linux2":
        compile_args += ["-std=c++17"]

    if sys.platform != "win32":
        compile_args += ["-Wno-unused-but-set-variable"]

    include_dirs = [os.path.abspath(d) for d in include_dirs]
    source_files = [os.path.basename(f) for f in source_files]
    setup_code = template % locals()
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

    # module folder needs to have a py.typed file to recognize type stubs
    open("py.typed", "a").close()

    import sys

    sys.path.insert(0, tempdir)
    if debug:
        print("\n")
        print("-" * 70)
        import pprint

        pprint.pprint(sys.path)
        print("-" * 70)
        print("\n")

    assert (
        subprocess.Popen(
            "%s setup.py build_ext --force --inplace" % sys.executable, shell=True
        ).wait()
        == 0
    )
    print("BUILT")
    result = __import__(name)
    print("imported")
    if debug:
        print("imported", result)

    sys.path = sys.path[1:]
    os.chdir(now)
    print(result)
    return result


def remove_labels(graph):
    _remove_labels = lambda succ_list: [s for s, label in succ_list]
    pure_graph = dict((n0, _remove_labels(ni)) for n0, ni in graph.items())
    return pure_graph


def find_cycle(graph_as_dict):
    """modified version of
    http://neopythonic.blogspot.de/2009/01/detecting-cycles-in-directed-graph.html
    """

    nodes = list(graph_as_dict.keys())
    for n in graph_as_dict.values():
        nodes.extend(n)
    todo = list(set(nodes))
    while todo:
        node = todo.pop()
        stack = [node]
        while stack:
            top = stack[-1]
            for node in graph_as_dict.get(top, []):
                if node in stack:
                    return stack[stack.index(node) :]
                if node in todo:
                    stack.append(node)
                    todo.remove(node)
                    break
            else:
                node = stack.pop()
    return None


def _check_for_cycles_in_mapping(mapping):
    # detect cylces in typedefs
    graph = dict()
    for alias, type_ in mapping.items():
        successors = type_.all_occuring_base_types()
        graph[alias] = successors

    cycle = find_cycle(graph)
    if cycle is not None:
        info = " -> ".join(map(str, cycle))
        raise Exception("mapping contains cycle: " + info)


def print_map(mapping):
    for k, v in mapping.items():
        print("%8s -> %s" % (k, v))


def flatten(mapping):
    """resolves nested mappings, eg:
        A -> B
        B -> C[X,D]
        C -> Z
        D -> Y
    is resolved to:
        A -> Z[X,Y]
        B -> Z[X,Y]
        C -> Z
        D -> Y
    """
    _check_for_cycles_in_mapping(mapping)
    # this loop only terminates for cylce free mappings:
    while True:
        for name, type_ in mapping.items():
            transformed = type_.transformed(mapping)
            if transformed != type_:
                mapping[name] = transformed
                break
        else:
            break
