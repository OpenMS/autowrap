import DeclResolver
import CodeGenerator

def parse(*files, **kw):
    return DeclResolver.resolve_decls_from_files(*files, **kw)

def generate_code(decls, target, **kw):
    gen = CodeGenerator.CodeGenerator(decls, target)
    debug = kw.get("debug", False)
    gen.create_pyx_file(debug)
    includes = gen.get_include_dirs()
    return includes

def parse_and_generate_code(*files, **kw):
    return generate_code(parse(*files, **kw), **kw)



