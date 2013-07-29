from version import *


import logging as L
L.basicConfig(level=L.INFO)

"""
The autowrap process consists of two steps:
    i) parsing of files (done by DeclResolver, which in turn uses the PXDParser
        to parse files)
    ii) generating the code (CodeGenerator)
"""

def parse(files, root):
    import DeclResolver
    return DeclResolver.resolve_decls_from_files(files, root)

def generate_code(decls, instance_map, target, debug, manual_code=None,
        extra_cimports=None):

    import CodeGenerator
    gen = CodeGenerator.CodeGenerator(decls,
                                      instance_map,
                                      target,
                                      manual_code,
                                      extra_cimports)
    gen.create_pyx_file(debug)
    includes = gen.get_include_dirs()
    print "Autwrap has wrapped %s classes, %s methods and %s enums" % (
        gen.wrapped_classes_cnt,
        gen.wrapped_methods_cnt,
        gen.wrapped_enums_cnt)
    return includes

def parse_and_generate_code(files, root, target, debug, manual_code=None,
        extra_cimports=None):

    print "Autowrap will start to parse and generate code. "\
              "Will parse %s files" % len(files)
    decls, instance_map = parse(files, root)
    print "Done parsing the files, will generate the code..."
    return generate_code(decls, instance_map, target, debug, manual_code,
            extra_cimports)



