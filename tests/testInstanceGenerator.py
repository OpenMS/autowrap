import autowrap.InstanceGenerator
import autowrap.PXDParser
import os

#TODO: use parse_str so that the pxd code is next to the testing code

def _parse(*pxdFileNames):
    class_decls = []
    for pxdFileName in pxdFileNames:
        test_file = os.path.join(os.path.dirname(__file__),
                                'test_files',
                                pxdFileName)
        class_decls.extend(autowrap.PXDParser.parse(test_file))
    return class_decls

def test_simple():
    print "testSimple"
    singleDecl, = _parse("minimal.pxd")
    resolved = autowrap.InstanceGenerator.transform([singleDecl])
    assert len(resolved) == 1, len(resolved)

def test_singular():
    print "testSingular"
    singleDecl, = _parse("templates.pxd")
    resolved = autowrap.InstanceGenerator.transform([singleDecl])

    assert len(resolved) == 2, len(resolved)
    res0, res1 = resolved
    assert res0.name == "TemplatesInt", res0.name
    assert res1.name == "TemplatesMixed", res1.name
    res0_restypes = map(lambda m: str(m.result_type), res0.methods)
    assert res0_restypes == ['void', 'int', 'int', 'int', 'int', 'void',
                             'TemplatesInt',
                             'TemplatesMixed', 'Templates[double,float]',
                             'TemplatesInt'], res0_restypes

    res0_names =  map(lambda m: m.name, res0.methods)
    assert res0_names ==  ["Templates", "getA", "getB", "toA",
            "toB", "convert", "r0", "r1", "r2", "r3"], res0_names

    first_arg_names= map(lambda m: None if len(m.arguments) == 0 else
            str(m.arguments[0][0]), res0.methods)
    assert first_arg_names == ["a", None, None, None, None, "arg0", "",
                               "", None, ""], first_arg_names

    second_arg_names= map(lambda m: None if len(m.arguments) < 2 else
            str(m.arguments[1][0]), res0.methods)
    assert second_arg_names == ["b", None, None, None, None, "arg1", None,
                               None, None, ""], second_arg_names

    first_arg_types= map(lambda m: None if len(m.arguments) == 0 else
            str(m.arguments[0][1]), res0.methods)

    assert first_arg_types == ["int", None, None, None, None, "list[int]",
            "TemplatesMixed"  , "TemplatesInt", None , "int"], first_arg_types

    second_arg_types= map(lambda m: None if len(m.arguments) < 2 else
            str(m.arguments[1][1]), res0.methods)
    assert second_arg_types == ["int", None, None, None, None, "list[int]&",
                                    None, None, None , "int"], second_arg_types


    res1_restypes = map(lambda m: str(m.result_type), res1.methods)
    assert res1_restypes == ['void', 'int', 'float', 'int', 'float', 'void',
                             'TemplatesInt',
                             'TemplatesMixed', 'Templates[double,float]',
                             'TemplatesMixed'], res1_restypes

    res1_names =  map(lambda m: m.name, res1.methods)
    assert res1_names ==  ["Templates", "getA", "getB", "toA",
            "toB", "convert", "r0", "r1", "r2", "r3"], res1_names

    first_arg_names= map(lambda m: None if len(m.arguments) == 0 else
            str(m.arguments[0][0]), res1.methods)
    assert first_arg_names == ["a", None, None, None, None, "arg0", "",
                               "", None, ""], first_arg_names

    second_arg_names= map(lambda m: None if len(m.arguments) < 2 else
            str(m.arguments[1][0]), res1.methods)
    assert second_arg_names == ["b", None, None, None, None, "arg1", None,
                               None, None, ""], second_arg_names

    first_arg_types= map(lambda m: None if len(m.arguments) == 0 else
            str(m.arguments[0][1]), res1.methods)

    assert first_arg_types == ["int", None, None, None, None, "list[int]",
            "TemplatesMixed"   , "TemplatesInt", None , "int"], first_arg_types

    second_arg_types= map(lambda m: None if len(m.arguments) < 2 else
            str(m.arguments[1][1]), res1.methods)
    assert second_arg_types == ["float", None, None, None, None,
                                "list[float]&", None, None, None,
                                "float"], second_arg_types


def test_multi_inherit():
    decls = _parse("A.pxd", "B.pxd", "C.pxd", "D.pxd")
    resolved = autowrap.InstanceGenerator.transform(decls)
    data = dict()
    for class_instance in resolved:
        mdata = []
        for m in class_instance.methods:
            li = [ str(m.result_type), m.name ]
            li += [ str(t) for n, t in m.arguments ]
            mdata.append(li)
        data[class_instance.name] = mdata

    #import pprint
    #print pprint.pprint(data)

    assert data == {'D1': [['void', u'Afun', 'int', 'int'],
                            ['void', u'Afun', 'float', 'int'],
                            ['int', u'BIdentity', 'int'],
                            ['void', u'Cint', 'int', 'float']],
                    'D2': [['void', u'Afun', 'float', 'int'],
                            ['void', u'Afun', 'int', 'int'],
                            ['float', u'BIdentity', 'float'],
                            ['void', u'Cint', 'int', 'int']]}


def expect_exception(fun):
    def wrapper(*a, **kw):
        try:
            fun(*a, **kw)
        except Exception:
            if 0:
                print "info: expected excption. here some more info:"
                import traceback
                traceback.print_exc()
                print
            pass
        else:
            assert False, "%s did not raise exception" % fun
    # set name, so that test frame work recognizes wrapped function
    wrapper.__name__ = fun.__name__+"__exception_wrapped"
    return wrapper

@expect_exception
def test_cycle_detection_in_class_hierarchy0():
    decls = _parse("Cycle0.pxd", "Cycle1.pxd", "Cycle2.pxd")
    autowrap.InstanceGenerator.transform(decls)

@expect_exception
def test_cycle_detection_in_class_hierarchy1():
    decls = _parse("Cycle1.pxd", "Cycle2.pxd", "Cycle0.pxd")
    autowrap.InstanceGenerator.transform(decls)

@expect_exception
def test_cycle_detection_in_class_hierarchy2():
    decls = _parse("Cycle2.pxd", "Cycle0.pxd", "Cycle1.pxd")
    autowrap.InstanceGenerator.transform(decls)

def test_hierarchy_detector0():
    from  autowrap.InstanceGenerator import find_cycle

    dd = dict()
    dd[1] = [2]
    dd[2] = [1]
    assert find_cycle(dd) == [2,1]

    dd = dict()
    dd[1] = [2]
    assert find_cycle(dd) is None


def test_hierarchy_detector1():
    from  autowrap.InstanceGenerator import find_cycle

    dd = dict()
    dd[1] = [2, 3]
    dd[2] = [3]
    assert find_cycle(dd) is None

def test_hierarchy_detector2():
    from  autowrap.InstanceGenerator import find_cycle

    dd = dict()
    dd[1] = [2, 3]
    dd[2] = [3]
    dd[3] = [4]
    dd[4] = [2]
    assert find_cycle(dd) == [4, 2, 3]


def test_hierarchy_detector3():
    from  autowrap.InstanceGenerator import find_cycle

    dd = dict()
    dd[1] = [2]
    dd[2] = [3,4]
    dd[3] = [5]
    assert find_cycle(dd) is None



def test_template_class_without_wrapas():
    from autowrap.PXDParser import parse_str
    from autowrap.InstanceGenerator import transform
    decl = parse_str("""
cdef extern from "A.h":
    cdef cppclass A[U]:
            A()
    """)
    try:
        transform([decl])
    except:
        pass
    else:
        assert False, "expected exception"

def test_non_template_class_with_annotation():
    from autowrap.PXDParser import parse_str
    from autowrap.InstanceGenerator import transform
    decl, = parse_str("""
cdef extern from "A.h":
    cdef cppclass A:
        # wrap-instances:
        #  B
        pass
    """)
    instance, = transform([decl])
    assert instance.name == "B"





