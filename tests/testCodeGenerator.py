import autowrap.InstanceGenerator
import autowrap.CodeGenerator
import autowrap.PXDParser
import autowrap.Utils

import os

def _parse(*pxdFileNames):
    class_decls = []
    for pxdFileName in pxdFileNames:
        test_file = os.path.join(os.path.dirname(__file__),
                                'test_files',
                                pxdFileName)
        class_decls.extend(autowrap.PXDParser.parse(test_file))
    return class_decls

def testNull():
    from autowrap.CodeGenerator import CodeGenerator
    clds  = _parse("int_container_class.pxd")
    resolved = autowrap.InstanceGenerator.transform(clds)
    here = os.path.join(os.path.dirname("__file__"))
    target = os.path.join(here, "int_container_class_wrapped.pyx")
    gen = CodeGenerator(resolved, target)
    gen.create_pyx_file(debug=True)
    wrapped = autowrap.Utils.compile_and_import(target, None, "test_files")
    print wrapped




