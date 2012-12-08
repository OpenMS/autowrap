import autowrap.DeclResolver
import autowrap.CodeGenerator
import autowrap.PXDParser
import autowrap.Utils

import os

def _resolve(*names):
    root = os.path.join(os.path.dirname(__file__), "test_files")
    return autowrap.DeclResolver.resolve_decls_from_files(*names, root=root)

def testNull():
    from autowrap.CodeGenerator import CodeGenerator
    resolved  = _resolve("int_container_class.pxd")
    here = os.path.dirname(__file__)
    target = os.path.join(here, "test_files", "int_container_class_wrapped.pyx")
    gen = CodeGenerator(resolved, target)
    gen.create_pyx_file(debug=True)
    include_path = os.path.join(here, "test_files")
    wrapped = autowrap.Utils.compile_and_import(target, None, include_path,
            debug=True)
    os.remove(target)
    assert wrapped.__name__ == "int_container_class_wrapped"




