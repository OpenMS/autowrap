# encoding: utf-8
import PXDParser
import re
import os
from collections import OrderedDict, defaultdict
import autowrap.Utils


__doc__ = """

    the methods in this module take the class declarations created by
    calling PXDParser.parse and generates a list of resolved class
    declarations.  'resolved' means that all template parameters are
    resolved  and inherited methods are resolved from super classes.

    some preliminaries which you should have in mind to understand the
    code below:

    in pxd files inheritance is declared with 'wrap-inherits'
    annotations.  python class names are declared with 'wrap-instances'
    annotations.

    eg

        cdef cppclass B[U,V]:
            # wrap-inherits: C[U] D
            #
            # wrap-instances: B_int_float[int, float] B_pure[int, int]


    So B[U,V] gets additional methods from C[U] and from D.

    In the end we get a Python class B_int_float which wraps B[int,
    float] and a Python class B_pure which wraps B[int,int].

    If you wrap a C++ class without template parameters you can ommit
    the 'wrap-instances' annotation. In this case the name of the Python
    class is the same as the name of the C++ class.

"""


def _split_targs(decl_str):
    # decl looks like T[X,Y]
    # returns: "T", "[X,Y]", ("X", "Y")
    match = re.match("(\w+)(\[\w+(,\w+)*\])?", decl_str)
    base, t_part, _ = match.groups()
    if t_part is None:
        return base, "", None
    t_parts = tuple(t.strip() for t in t_part[1:-1].split(","))
    return base, t_part, t_parts



class ResolvedClassOrEnum(object):
    """ contains all info for generating wrapping code of
        resolved class.
        "Resolved" means that template parameters are resolved.
    """

    def __init__(self, name, methods, decl=None):
        self.name = name
        # resolve overloadings
        self.methods = OrderedDict()
        for m in methods:
            self.methods.setdefault(m.name, []).append(m)
        self.cpp_decl = decl
        self.items = getattr(decl, "items", [])

    def get_flattened_methods(self):
        return [m for methods in self.methods.values() for m in methods]

    def __str__(self):
        raise Exception("impl not valid any more")
        return "\n   ".join([self.name] + map(str, self.methods))


class ResolvedMethod(object):

    """ contains all info for generating wrapping code of
        resolved class.
        "resolved" means that template parameters are resolved.
    """

    def __init__(self, name, result_type, arguments):
        self.name = name
        self.result_type = result_type
        self.arguments = arguments

    def __str__(self):
        args = [("%s %s" % (t, n)).strip() for (n, t) in self.arguments]
        return "%s %s(%s)" % (self.result_type, self.name, ", ".join(args))

def resolve_decls_from_files(*pathes, **kw):
    root = kw.get("root", ".")
    decls = []
    for path in pathes:
        full_path = os.path.join(root, path)
        decls.extend(PXDParser.parse_pxd_file(full_path))
    return _transform(decls)

def resolve_decls_from_string(pxd_in_a_string):
    return _transform(PXDParser.parse_str(pxd_in_a_string))


def _transform(class_decls):
    """
    input:
        class_decls ist list of instances of PXDParser.BaseDecl.
        (contains annotations
          - about instance names for template parameterized classes
          - about inheritance of methods from other classes in class_decls
        )
    output:
        list of instances of ResolvedClassOrEnum
    """
    assert all(isinstance(d, PXDParser.BaseDecl) for d in class_decls)

    class_decls = _resolve_all_inheritances(class_decls)
    return _resolve_templated_classes(class_decls)


def _resolve_all_inheritances(class_decls):
    """
    enriches each class_decl from class_decls with methods from inherited
    super classes.

    inheritance is declared with 'wrap-inherits' annotations.

    eg

        cdef cppclass B[U,V]:
            # wrap-inherits:
            #    C[U]
            #    D
    """
    name_to_decl = dict((cdcl.name, cdcl) for cdcl in class_decls)

    inheritance_graph = _generate_inheritance_graph(class_decls, name_to_decl)
    _detect_cycles(inheritance_graph)

    # resolve inheritance for each class_decl
    for cdcl in class_decls:
        _resolve_inheritance(cdcl, class_decls, inheritance_graph)

    return class_decls


def _generate_inheritance_graph(class_decls, name_to_decl):
    """
    generates directed graph from class to declareds superclasses,
    each edge has label 'used_parameters'.

    we store graph as dict  node -> [ (succ_node_0, edge_label_0),
                                       ....
                                      (succ_node_n, edge_label_n) ]
    """
    graph = defaultdict(list)
    for cdcl in class_decls:
        for base_decl_str in cdcl.annotations.get("wrap-inherits", []):
            base_class_name, _, used_parameters = _split_targs(base_decl_str)
            base_class = name_to_decl[base_class_name]
            graph[cdcl].append((base_class, used_parameters))
    return graph


def _detect_cycles(graph):
    rm_edge_labels = lambda succ_list: [succ for succ, label in succ_list]
    pure_graph = dict((n0, rm_edge_labels(ni)) for n0, ni in graph.items())
    cycle = autowrap.Utils.find_cycle(pure_graph)
    if cycle is not None:
        info = " -> ".join(map(str, cycle))
        raise Exception("inheritance hierarchy contains cycle: " + info)


def _resolve_inheritance(cdcl, class_decls, inheritance_graph):
    """
    encriches class_decl with methods from all inherited super classes,
    that is: methods from super_classes and their super_classes.
    """

    # first we recurses to all super classes:
    for super_cld, _ in inheritance_graph[cdcl]:
        _resolve_inheritance(super_cld, class_decls, inheritance_graph)

    # now all super classes are already "resolved" by recursion, we just have
    # to get  the methods from the immediate super_classes:
    for super_cld, used_parameters in inheritance_graph[cdcl]:
        _add_inherited_methods(cdcl, super_cld, used_parameters)


def _add_inherited_methods(cdcl, super_cld, used_parameters):

    super_targs = super_cld.template_parameters
    # template paremeer None behaves like []
    used_parameters = used_parameters or []
    super_targs = super_targs or []

    # check if parmetirization signature matches:
    if len(used_parameters) != len(super_targs):
        raise Exception("deriving %s from %s does not match"
                        % (cdcl.name, super_cld.name))

    # map template parameters in super class to the parameters used in current
    # class:
    mapping = dict(zip(super_targs, used_parameters))
    # get copy of methods from super class ans transform template params:
    transformed_methods = super_cld.get_transformed_methods(mapping)
    cdcl.attach_base_methods(transformed_methods)


def _resolve_templated_classes(class_decls):
    """
    generates concrete names of python classes.

    names are declared with 'wrap-instances' annotations.

    eg

        cdef cppclass B[U,V]:
            # wrap-instances:
            #    B_int_float[int, float]
            #    B_pure[int, int]

    this least to two python classes B_int_float and B_pure,
    the first wraps C++ class B[int, float], the second wraps B[int,int]

    """

    registry = _create_alias_registry(class_decls)
    resolved_classes = []
    for alias, decl, t_param_mapping in registry.values():
        methods = []
        for mdcl in decl.get_method_decls():
            if mdcl.annotations.get("wrap-ignore"):
                continue
            inst = _resolve_method(mdcl, registry, t_param_mapping)
            if inst.name == decl.name:
                inst.name = alias
            methods.append(inst)
        resolved_classes.append(ResolvedClassOrEnum(alias, methods, decl))
    return resolved_classes


def _resolve_method(method_decl, registry, t_param_mapping):
    """
    resolves aliases in return and argument types
    """
    result_type = _resolve_alias(method_decl.result_type, registry,
                                t_param_mapping)
    args = []
    for arg_name, arg_type in method_decl.arguments:
        arg_type = _resolve_alias(arg_type, registry, t_param_mapping)
        args.append((arg_name, arg_type))
    new_name = method_decl.annotations.get("wrap-as")
    return ResolvedMethod(new_name or method_decl.name, result_type, args)


def _resolve_alias(cpp_type, registry, t_param_mapping):
    cpp_type = cpp_type.transform(t_param_mapping)
    key = str(cpp_type)
    if key.endswith("&"):
        key = key[:-1]
    alias = registry.get(key)
    if alias is None:
        return cpp_type
    return alias[0]


def _create_alias_registry(class_decls):
    """ parses annotations of all classes and registers aliases for
        classes.

        cdef cppclass A[U]:
            #wrap-instances:
            #  AA[int]

        generates an entry  'A[int]' : ( 'AA', cldA, {'U': 'int'} )
        where cldA is the class_decl of A.

    """
    r = OrderedDict()
    for cdcl in class_decls:
        if cdcl.annotations.get("wrap-ignore", False):
            continue

        inst_annotations = cdcl.annotations.get("wrap-instances")

        if cdcl.template_parameters is None and not inst_annotations:
            # missing "wrap-instances" annotation works for non-template class:
            # instance name of python class equals c++ class name
            instance_decl_str = cdcl.name
            _register_alias(cdcl, instance_decl_str, r)
        elif inst_annotations:
            for instance_decl_str in inst_annotations:
                _register_alias(cdcl, instance_decl_str, r)
        else:
            raise Exception("templated class %s in %s has no 'wrap-instances'"
                            "annotations. declare instances or supress "
                            "wrapping with 'wrap-ignore' annotation" % (
                                cdcl.name, cdcl.pxd_path))
    return r


def _register_alias(cdcl, instance_decl_str, r):
    """
    instance_decl_str looks like  "Tint[int]" inside declared c++ class T[X]
    """

    alias, t_part, t_instances = _split_targs(instance_decl_str)
    if t_instances is not None:
        t_params = cdcl.template_parameters
        t_param_mapping = dict(zip(t_params, t_instances))
    else:
        t_param_mapping = dict()
    # maps 'T[int]' -> ('Tint', cdcl, { 'X': 'int' })
    r[cdcl.name + t_part] = (alias, cdcl, t_param_mapping)
