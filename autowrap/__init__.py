import DeclResolver

def parse(files):
    return DeclResolver.resolve_decls_from_files(*files)

