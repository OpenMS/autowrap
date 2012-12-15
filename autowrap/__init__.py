import DeclResolver
import CodeGenerator

def parse(*files, **kw):
    return DeclResolver.resolve_decls_from_files(*files, **kw)

def generate_code(decls, target):
    gen = CodeGenerator.CodeGenerator(decls, target)
    gen.create_pyx_file(debug=True)

def parse_and_generate_code(*files, **kw):
    target = kw["target"]
    generate_code(parse(*files, **kw), target)



