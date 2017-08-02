# encoding: utf-8

from __future__ import print_function
from __future__ import absolute_import

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

from .version import *

import logging as L
L.basicConfig(level=L.INFO)

"""
The autowrap process consists of two steps:
    i) parsing of files (done by DeclResolver, which in turn uses the PXDParser
        to parse files)
    ii) generating the code (CodeGenerator)
"""


def parse(files, root, num_processes=1):
    import autowrap.DeclResolver
    return DeclResolver.resolve_decls_from_files(files, root, num_processes)


def generate_code(decls, instance_map, target, debug=False, manual_code=None,
                  extra_cimports=None, include_boost=True, include_numpy=False, allDecl=[]):

    import autowrap.CodeGenerator
    gen = CodeGenerator.CodeGenerator(decls,
                                      instance_map,
                                      pyx_target_path=target,
                                      manual_code=manual_code,
                                      extra_cimports=extra_cimports, 
                                      allDecl=allDecl)
    gen.include_numpy=include_numpy
    gen.create_pyx_file(debug)
    includes = gen.get_include_dirs(include_boost)
    print("Autwrap has wrapped %s classes, %s methods and %s enums" % (
        gen.wrapped_classes_cnt,
        gen.wrapped_methods_cnt,
        gen.wrapped_enums_cnt))
    return includes


def parse_and_generate_code(files, root, target, debug, manual_code=None,
                            extra_cimports=None, include_boost=True):

    print("Autowrap will start to parse and generate code. "
          "Will parse %s files" % len(files))
    decls, instance_map = parse(files, root)
    print("Done parsing the files, will generate the code...")
    return generate_code(decls, instance_map, target, debug, manual_code,
                         extra_cimports, include_boost)
