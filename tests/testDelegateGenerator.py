import autowrap.DelegateGenerator
import autowrap.PXDParser
import os

def _parse(*pxdFileNames):
    class_decls = []
    for pxdFileName in pxdFileNames:
        test_file = os.path.join(os.path.dirname(__file__),
                                'test_files',
                                pxdFileName)
        class_decls.append(autowrap.PXDParser.parse(test_file))
    return class_decls

def testSimple():
    singleDecl, = _parse("minimal.pxd")
    resolved = autowrap.DelegateGenerator.resolve_templates([singleDecl])
    assert len(resolved) == 1, len(resolved)

def testSingular():
    singleDecl, = _parse("templates.pxd")
    resolved = autowrap.DelegateGenerator.resolve_templates([singleDecl])
    assert len(resolved) == 2, len(resolved)
