# encoding: utf-8
from PXDParser import EnumOrClassDecl
import re
from collections import OrderedDict, defaultdict


__doc__ = """

    the methods in this module take the class declarations created by calling
    PXDParser.parse and generates a list of instantiated class declarations.
    'instanciated' means that all template parameters are resolved  and
    inherited methods are resolved from super classes.


    some preliminaries which you should have in mind to understand the code
    below:

    in pxd files inheritance is declared with 'wrap-inherits' annotations.
    python class names are declared with 'wrap-instances' annotations.

    eg

        cdef cppclass B[U,V]:
            # wrap-inherits:
            #    C[U]
            #    D
            #
            # wrap-instances:
            #    B_int_float[int, float]
            #    B_pure[int, int]


    So B[U,V] gets additional methods from C[U] and from D.

    In the end we get a Python class B_int_float which wraps B[int, float]
    and a Python class B_pure which wraps B[int,int].

    If you wrap a C++ class without template parameters you can ommit the
    'wrap-instances' annotation. In this case the name of the Python class is the
    same as the name of the C++ class.

"""


def split_targs(decl_str):
    # decl looks like T[X,Y]
    # returns: "T", "[X,Y]", ("X", "Y")
    match = re.match("(\w+)(\[\w+(,\w+)*\])?", decl_str)
    base, t_part, _ = match.groups()
    if t_part is None:
        return base, "", None
    t_parts = tuple(t.strip() for t in t_part[1:-1].split(","))
    return base, t_part, t_parts


def find_cycle(graph_as_dict):
    """ modified version of
    http://neopythonic.blogspot.de/2009/01/detecting-cycles-in-directed-graph.html
    """

    nodes = graph_as_dict.keys()
    for n in graph_as_dict.values():
        nodes.extend(n)
    todo = list(set(nodes))
    while todo:
        node = todo.pop()
        stack = [node]
        while stack:
            top = stack[-1]
            for node in graph_as_dict.get(top, []):
                if node in stack:
                    return stack[stack.index(node):]
                if node in todo:
                    stack.append(node)
                    todo.remove(node)
                    break
            else:
                node = stack.pop()
    return None


class NullMapping(dict):

    def __getitem__(self, k):
        return None


class ClassInstance(object):
    """ contains all info for generating wrapping code of
        instanciated class.
        "Instance" means that template parameters are resolved.
    """

    def __init__(self, name, methods, decl=None):
        self.name = name
        self.methods = methods
        self.decl = decl

    def __str__(self):
        return "\n   ".join([self.name] + map(str, self.methods))


class MethodInstance(object):

    """ contains all info for generating wrapping code of
        instanciated class.
        "Instance" means that template parameters are resolved.
    """

    def __init__(self, name, result_type, arguments):
        self.name = name
        self.result_type = result_type
        self.arguments = arguments

    def __str__(self):
        args = [("%s %s" % (t, n)).strip() for (n, t) in self.arguments]
        return "%s %s(%s)" % (self.result_type, self.name, ", ".join(args))


def transform(class_decls):
    """
    input:
        class_decls ist list of innstances of PXDParser.EnumOrClassDecl.
        (contains annotations
            - about instance names for template parameterized classes
            - about inheritance of methods from other classes in class_decls
        )
    output:
        list of instances of ClassInstance
    """
    assert all(isinstance(d, EnumOrClassDecl) for d in class_decls)

    class_decls = resolve_all_inheritances(class_decls)
    instances = create_class_instances(class_decls)
    return instances


def resolve_all_inheritances(class_decls):
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

    inheritance_graph = generate_inheritance_graph(class_decls, name_to_decl)
    check_for_and_handle_cycles(inheritance_graph)

    # resolve inheritance for each class_decl
    for cdcl in class_decls:
        resolve_inheritance(cdcl, class_decls, inheritance_graph)

    return class_decls


def generate_inheritance_graph(class_decls, name_to_decl):
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
            base_class_name, _, used_parameters = split_targs(base_decl_str)
            base_class = name_to_decl[base_class_name]
            graph[cdcl].append((base_class, used_parameters))
    return graph


def check_for_and_handle_cycles(graph):
    rm_edge_labels = lambda succ_list: [succ for succ, label in succ_list]
    pure_graph = dict((n0, rm_edge_labels(ni)) for n0, ni in graph.items())
    cycle = find_cycle(pure_graph)
    if cycle is not None:
        info = " -> ".join(map(str, cycle))
        raise Exception("inheritance hierarchy contains cycle: " + info)


def resolve_inheritance(cdcl, class_decls, inheritance_graph):
    """
    encriches class_decl with methods from all inherited super classes,
    that is: methods from super_classes and their super_classes.
    """

    # first we recurses to all super classes:
    for super_cld, _ in inheritance_graph[cdcl]:
        resolve_inheritance(super_cld, class_decls, inheritance_graph)

    # now all super classes are already "resolved" by recursion, we just have
    # to get  the methods from the immediate super_classes:
    for super_cld, used_parameters in inheritance_graph[cdcl]:
        add_methods_from_super_class(cdcl, super_cld, used_parameters)


def add_methods_from_super_class(cdcl, super_cld, used_parameters):

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


def create_class_instances(class_decls):
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

    registry = create_alias_registry(class_decls)
    resolved_classes = []
    for alias, class_decl, t_param_mapping in registry.values():
        methods = []
        for mdcl in class_decl.get_method_decls():
            if mdcl.annotations.get("wrap-ignore"):
                continue
            inst = create_method_instance(mdcl, registry, t_param_mapping)
            if inst.name == class_decl.name:
                inst.name = alias
            methods.append(inst)
        resolved_classes.append(ClassInstance(alias, methods, class_decl))
    return resolved_classes


def create_method_instance(method_decl, registry, t_param_mapping):
    """
    resolves aliases in return and argument types
    """
    result_type = resolve_alias(method_decl.result_type, registry,
                                t_param_mapping)
    args = []
    for arg_name, arg_type in method_decl.args:
        arg_type = resolve_alias(arg_type, registry, t_param_mapping)
        args.append((arg_name, arg_type))
    new_name = method_decl.annotations.get("wrap-as")
    return MethodInstance(new_name or method_decl.name, result_type, args)


def resolve_alias(cpp_type, registry, t_param_mapping):
    cpp_type = cpp_type.transform(t_param_mapping)
    key = str(cpp_type)
    if key.endswith("&"):
        key = key[:-1]
    alias = registry.get(key)
    if alias is None:
        return cpp_type
    return alias[0]


def create_alias_registry(class_decls):
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
            register_alias(cdcl, instance_decl_str, r)
        elif inst_annotations:
            for instance_decl_str in inst_annotations:
                register_alias(cdcl, instance_decl_str, r)
        else:
            raise Exception("templated class has no 'wrap-instances' "
                            "annotations. declare instances or supress "
                            "wrapping with 'wrap-ignore' annotation")
    return r


def register_alias(cdcl, instance_decl_str, r):
    """
    instance_decl_str looks like  "Tint[int]" inside declared c++ class T[X]
    """

    alias, t_part, t_instances = split_targs(instance_decl_str)
    if t_instances is not None:
        t_params = cdcl.template_parameters
        t_param_mapping = dict(zip(t_params, t_instances))
    else:
        t_param_mapping = NullMapping()
    # maps 'T[int]' -> ('Tint', cdcl, { 'X': 'int' })
    r[cdcl.name + t_part] = (alias, cdcl, t_param_mapping)
