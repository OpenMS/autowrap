import autowrap.DeclResolver as DeclResolver
import autowrap.PXDParser
import os
import autowrap.Utils

#TODO: use parse_str so that the pxd code is next to the testing code


def _resolve(*names):
    root = os.path.join(os.path.dirname(__file__), "test_files")
    return autowrap.DeclResolver.resolve_decls_from_files(*names, root=root)

def test_simple():
    dcls = _resolve("minimal.pxd")
    assert len(dcls) == 1, len(dcls)

def test_singular():
    resolved = _resolve("templates.pxd")

    assert len(resolved) == 2, len(resolved)
    res0, res1 = resolved
    assert res0.name == "TemplatesInt", res0.name
    assert res1.name == "TemplatesMixed", res1.name
    res0_restypes = map(str, (m.result_type for m in
        res0.get_flattened_methods()))

    assert res0_restypes == ['void', 'int', 'int', 'int', 'int', 'void',
                             'TemplatesInt',
                             'TemplatesMixed', 'Templates[double,float]',
                             'TemplatesInt'], res0_restypes

    res0_names =  map(lambda m: m.name, res0.get_flattened_methods())
    assert res0_names ==  ["TemplatesInt", "getA", "getB", "toA",
            "toB", "convert", "r0", "r1", "r2", "r3"], res0_names

    first_arg_names= map(lambda m: None if len(m.arguments) == 0 else
            str(m.arguments[0][0]), res0.get_flattened_methods())
    assert first_arg_names == ["a", None, None, None, None, "arg0", "",
                               "", None, ""], first_arg_names

    second_arg_names= map(lambda m: None if len(m.arguments) < 2 else
            str(m.arguments[1][0]), res0.get_flattened_methods())
    assert second_arg_names == ["b", None, None, None, None, "arg1", None,
                               None, None, ""], second_arg_names

    first_arg_types= map(lambda m: None if len(m.arguments) == 0 else
            str(m.arguments[0][1]), res0.get_flattened_methods())

    assert first_arg_types == ["int", None, None, None, None, "list[int]",
            "TemplatesMixed"  , "TemplatesInt", None , "int"], first_arg_types

    second_arg_types= map(lambda m: None if len(m.arguments) < 2 else
            str(m.arguments[1][1]), res0.get_flattened_methods())
    assert second_arg_types == ["int", None, None, None, None, "list[int] &",
                                    None, None, None , "int"], second_arg_types


    res1_restypes = map(lambda m: str(m.result_type),
            res1.get_flattened_methods())
    assert res1_restypes == ['void', 'int', 'float', 'int', 'float', 'void',
                             'TemplatesInt',
                             'TemplatesMixed', 'Templates[double,float]',
                             'TemplatesMixed'], res1_restypes

    res1_names =  map(lambda m: m.name, res1.get_flattened_methods())
    assert res1_names ==  ["TemplatesMixed", "getA", "getB", "toA",
            "toB", "convert", "r0", "r1", "r2", "r3"], res1_names

    first_arg_names= map(lambda m: None if len(m.arguments) == 0 else
            str(m.arguments[0][0]), res1.get_flattened_methods())
    assert first_arg_names == ["a", None, None, None, None, "arg0", "",
                               "", None, ""], first_arg_names

    second_arg_names= map(lambda m: None if len(m.arguments) < 2 else
            str(m.arguments[1][0]), res1.get_flattened_methods())
    assert second_arg_names == ["b", None, None, None, None, "arg1", None,
                               None, None, ""], second_arg_names

    first_arg_types= map(lambda m: None if len(m.arguments) == 0 else
            str(m.arguments[0][1]), res1.get_flattened_methods())

    assert first_arg_types == ["int", None, None, None, None, "list[int]",
            "TemplatesMixed"   , "TemplatesInt", None , "int"], first_arg_types

    second_arg_types= map(lambda m: None if len(m.arguments) < 2 else
            str(m.arguments[1][1]), res1.get_flattened_methods())
    assert second_arg_types == ["float", None, None, None, None,
                                "list[float] &", None, None, None,
                                "float"], second_arg_types

def test_multi_inherit():
    resolved = _resolve("A.pxd", "B.pxd", "C.pxd", "D.pxd")

    data = dict()
    for class_instance in resolved:
        mdata = []
        for m in class_instance.get_flattened_methods():
            li = [ str(m.result_type), m.name ]
            li += [ str(t) for n, t in m.arguments ]
            mdata.append(li)
        data[class_instance.name] = mdata

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
    _resolve("Cycle0.pxd", "Cycle1.pxd", "Cycle2.pxd")

@expect_exception
def test_cycle_detection_in_class_hierarchy1():
    _resolve("Cycle1.pxd", "Cycle2.pxd", "Cycle0.pxd")

@expect_exception
def test_cycle_detection_in_class_hierarchy2():
    _resolve("Cycle2.pxd", "Cycle0.pxd", "Cycle1.pxd")


@expect_exception
def test_template_class_without_wrapas():
    DeclResolver.resolve_decls_from_string("""
cdef extern from "A.h":
    cdef cppclass A[U]:
            A()
                   """)

def test_non_template_class_with_annotation():
    instance, = DeclResolver.resolve_decls_from_string("""
cdef extern from "A.h":
    cdef cppclass A:
        # wrap-instances:
        #  B
        pass
    """)
    assert instance.name == "B"

def test_multi_decls_in_one_file():
    inst1, inst2, enum = DeclResolver.resolve_decls_from_string("""
cdef extern from "A.h":
    cdef cppclass A[B,C] :
        # wrap-instances:
        #   A[int,int]
        pass

    cdef cppclass C[E] :
        # wrap-instances:
        #   C[float]
        pass

    cdef enum F:
            G, H=4, I
    """)
    assert inst1.name == "A"
    T1, T2 =  inst1.cpp_decl.template_parameters
    assert T1 == "B", T1
    assert T2 == "C", T2
    assert len(inst1.methods) == 0

    assert inst2.name == "C"
    T1, =  inst2.cpp_decl.template_parameters
    assert T1 == "E", T1
    assert len(inst2.methods) == 0

    assert enum.name == "F"
    G, H, I = enum.items
    assert G == ("G", 0)
    assert H == ("H", 4)
    assert I == ("I", 5)


def testIntContainer():
    resolved  = _resolve("int_container_class.pxd")
    assert resolved[0].name == "Xint"
    assert [ m.name for m in resolved[0].get_flattened_methods()] == ["Xint", "operator+",
    "getValue"]
    assert resolved[1].name == "XContainerInt"
    assert [ m.name for m in resolved[1].get_flattened_methods()] == ["XContainerInt",
            "push_back", "size",]

def testTypeDefWithFun():
    resolved, = DeclResolver.resolve_decls_from_string("""
cdef extern from "X.h":
    ctypedef int X
    X fun(X x)
            """)
    assert resolved.name == "fun"
    assert str(resolved.result_type) == "int"
    (n, t), = resolved.arguments
    assert n == "x"
    assert str(t) == "int"

def testTypeDefWithClass():
    return
    resolved, = DeclResolver.resolve_decls_from_string("""
cdef extern from "X.h":
    ctypedef int X
    cdef cppclass A[B]:
        # wrap-instances:
        #   A[X]
        X foo(B)
        B bar(X)
            """)
    assert resolved.name == "A"
    assert False

def testWithoutHeader():
    return
    resolved, = DeclResolver.resolve_decls_from_string("""
cdef extern:
    ctypedef int X
    X fun(X x)
            """)
