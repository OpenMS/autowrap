import DeclResolver
import CodeGenerator
import PXDParser

def parse(files, root):
    return DeclResolver.resolve_decls_from_files(files, root)

def generate_code(decls, instance_map, target, debug):
    gen = CodeGenerator.CodeGenerator(decls, instance_map, target)
    gen.create_pyx_file(debug)
    includes = gen.get_include_dirs()
    return includes

def parse_and_generate_code(files, root, target, debug):

    decls, instance_map = parse(files, root)
    return generate_code(decls, instance_map, target, debug)
