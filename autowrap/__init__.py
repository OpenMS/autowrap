from version import *

import DeclResolver
import CodeGenerator

import logging as L
L.basicConfig(level=L.INFO)

def parse(files, root):
    return DeclResolver.resolve_decls_from_files(files, root)

def generate_code(decls, instance_map, target, debug, manual_code=None,
        extra_cimports=None):

    gen = CodeGenerator.CodeGenerator(decls,
                                      instance_map,
                                      target,
                                      manual_code,
                                      extra_cimports)
    gen.create_pyx_file(debug)
    includes = gen.get_include_dirs()
    return includes

def parse_and_generate_code(files, root, target, debug, manual_code=None,
        extra_cimports=None):

    decls, instance_map = parse(files, root)
    return generate_code(decls, instance_map, target, debug, manual_code,
            extra_cimports)



