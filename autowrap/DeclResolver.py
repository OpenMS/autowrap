# encoding: utf-8
import PXDParser
import Types
import Utils
import os
from collections import defaultdict

try:
    from collections import OrderedDict
    from collections import Counter
except ImportError:
    print """ Cannot import OrderedDict (only in Python 2.7). 
    If you have a previous version of Python, please download the ordereddict
    package from PyPI (https://pypi.python.org/pypi/ordereddict) to make this
    work.
    Please also download this backport for the Counter and save it in a file
    called "counter_backport" in your PYTHONPATH : http://code.activestate.com/recipes/576611-counter-class/
    """
    from ordereddict import OrderedDict
    from counter_backport import Counter


__doc__ = """

    the methods in this module take the class declarations created by
    calling PXDParser.parse and generates a list of resolved class
    declarations.  'resolved' means that all template parameters are
    resolved and inherited methods are resolved from super classes.

    some preliminaries which you should have in mind to understand the
    code below:

    in pxd files inheritance is declared with 'wrap-inherits'
    annotations.  python class names are declared with 'wrap-instances'
    annotations.

    eg

        cdef cppclass B[U,V]:
            # wrap-inherits:
            #    C[U]
            #    D
            #
            # wrap-instances:
            #   B_int_float := B[int, float]
            #   B_pure := B[int, int]

    So B[U,V] gets additional methods from C[U] and from D.

    In the end we get a Python class B_int_float which wraps B[int,
    float] and a Python class B_pure which wraps B[int,int].

    If you wrap a C++ class without template parameters you can ommit
    the 'wrap-instances' annotation. In this case the name of the Python
    class is the same as the name of the C++ class.

"""

import logging as L

class ResolvedTypeDef(object):

    def __init__(self, decl):
        self.cpp_decl = decl
        self.name = decl.name
        self.type_ = decl.type_
        self.wrap_ignore = decl.annotations.get("wrap-ignore", False)

class ResolvedEnum(object):

    def __init__(self, decl):
        self.name = decl.name
        self.wrap_ignore = decl.annotations.get("wrap-ignore", False)
        self.cpp_decl = decl
        self.items = decl.items
        self.type_ = Types.CppType(self.name, enum_items=self.items)
        L.info("created resolved enum: %s" % (decl.name, ))
        L.info("           with items: %s" % (decl.items))
        L.info("")

class ResolvedAttribute(object):

    def __init__(self, name, type_, decl):
        self.name = name
        self.type_ = type_
        self.cpp_decl = decl
        self.wrap_ignore = decl.annotations.get("wrap-ignore", False)


class ResolvedClass(object):
    """ contains all info for generating wrapping code of
        resolved class.
        "Resolved" means that template parameters and typedefs are resolved.

        classtype contains the type of the baseclass (in case of a templated
        class), while the local_type_mapping contain the mappings of the
        template arguments to their actual types.
    """

    def __init__(self, name, methods, attributes, decl, classtype=None, local_type_mapping={}):
        self.name = name
        # resolve overloadings
        self.methods = OrderedDict()
        for m in methods:
            self.methods.setdefault(m.name, []).append(m)
        self.attributes = attributes

        self.cpp_decl = decl
        if classtype is not None: self.classtype = classtype
        self.local_type_mapping = local_type_mapping
        #self.items = getattr(decl, "items", [])
        self.wrap_ignore = decl.annotations.get("wrap-ignore", False)

    def get_flattened_methods(self):
        return [m for methods in self.methods.values() for m in methods]

    def __str__(self):
        return "\n   ".join([self.name] + map(str, self.methods))

class ResolvedMethod(object):

    """ contains all info for generating wrapping code of
        resolved class.
        "resolved" means that template parameters are resolved.
    """

    def __init__(self, name, result_type, arguments, decl):
        self.name = name
        self.result_type = result_type
        self.arguments = arguments
        self.cpp_decl = decl
        self.wrap_ignore = decl.annotations.get("wrap-ignore", False)

    def __str__(self):
        args = [("%s %s" % (t, n)).strip() for (n, t) in self.arguments]
        return "%s %s(%s)" % (self.result_type, self.name, ", ".join(args))

    def has_special_return_type(self):
        return "wrap-return" in self.cpp_decl.annotations

    def get_special_return_type(self):
        return self.cpp_decl.annotations["wrap-return"]

class ResolvedFunction(ResolvedMethod):

    pass


# Main Entry points: from files or from string
def resolve_decls_from_files(pathes, root):
    """This is the main entry point: resolve .pxd declarations from files

    """
    decls = []
    for path in pathes:
        full_path = os.path.join(root, path)
        L.info("parse %s" % full_path)
        decls.extend(PXDParser.parse_pxd_file(full_path))
    return _resolve_decls(decls)


def resolve_decls_from_string(pxd_in_a_string):
    return _resolve_decls(PXDParser.parse_str(pxd_in_a_string))


def _resolve_decls(decls):
    """
    input:
        class_decls ist list of instances of PXDParser.BaseDecl.
        (contains annotations
          - about instance names for template parameterized classes
          - about inheritance of methods from other classes in class_decls
        )
    output:
        list of instances of ResolvedClass
    """

    L.info("start resolving decls")
    assert all(isinstance(d, PXDParser.BaseDecl) for d in decls)

    def filter_out(tt):
        return [d for d in decls if isinstance(d, tt) and d.name is not None]

    typedef_decls  = filter_out(PXDParser.CTypeDefDecl)
    function_decls = filter_out(PXDParser.CppMethodOrFunctionDecl)
    enum_decls     = filter_out(PXDParser.EnumDecl)
    class_decls    = filter_out(PXDParser.CppClassDecl)

    class_decls = _resolve_all_inheritances(class_decls)

    typedef_mapping = _build_typedef_mapping(typedef_decls)

    # register enums as type aliases:
    enum_mapping = dict()
    for e in enum_decls:
        enum_mapping[e.name] = Types.CppType(e.name, enum_items=e.items)

    # register class aliases -> we want to add parent classes to the dictionary
    # in order to be able to correctly map the templated classes to their C++
    # equivalents
    instance_mapping = _parse_all_wrap_instances_comments(class_decls, True)
    # remove local targ mappings:
    instance_mapping = dict( (k, v0) for (k, (v0,v1)) in
                                                      instance_mapping.items())

    # resolve  typedefs in class aliase values
    instance_mapping = dict((k, v.transformed(typedef_mapping)) for (k, v) in
                                                      instance_mapping.items())

    # add enum mapping to class instances mapping
    intersecting_names = set(instance_mapping) & set(enum_mapping)
    assert not intersecting_names, "enum names and class decls overlap: %s"\
                                   % intersecting_names

    instance_mapping.update(enum_mapping)

    functions = [_resolve_function(f, instance_mapping, typedef_mapping)
                                                       for f in function_decls]

    enums = [ResolvedEnum(e) for e in enum_decls]
    typedefs = [ResolvedTypeDef(t) for t in typedef_decls]

    classes = _resolve_class_decls(class_decls,
                                   typedef_mapping,
                                   instance_mapping)

    return classes + enums + functions + typedefs, instance_mapping


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
            base = Types.CppType.from_string(base_decl_str)
            base_class = name_to_decl[base.base_type]
            L.info("%s inherits %s" % (cdcl.name, base))
            graph[cdcl].append((base_class, base.template_args))
    return graph


def _detect_cycles(inheritance_graph):
    graph = Utils.remove_labels(inheritance_graph)
    cycle = Utils.find_cycle(graph)
    if cycle is not None:
        info = " -> ".join(map(str, cycle))
        raise Exception("inheritance hierarchy contains cycle: " + info)


def _resolve_inheritance(cdcl, class_decls, inheritance_graph):
    """
    enciches class_decl with methods from all inherited super classes,
    that is: methods from super_classes and their super_classes.
    """

    L.info("resolve_inheritance for %s" % cdcl.name)

    # first we recurses to all super classes:
    for super_cld, _ in inheritance_graph[cdcl]:
        _resolve_inheritance(super_cld, class_decls, inheritance_graph)

    # now all super classes are already "resolved" by recursion, we just have
    # to get  the methods from the immediate super_classes:
    for super_cld, used_parameters in inheritance_graph[cdcl]:
        _add_inherited_methods(cdcl, super_cld, used_parameters)


def _add_inherited_methods(cdcl, super_cld, used_parameters):

    L.info("add_inherited_methods for %s" % cdcl.name)

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
    transformed_methods = dict((k,v) for (k,v) in transformed_methods.items()
                                if k != super_cld.name) # remove constructors
    for method in transformed_methods:
        L.info("attach to %s: %s" % (cdcl.name, method))
    cdcl.attach_base_methods(transformed_methods)
    L.info("")


def _build_typedef_mapping(decls):
    _check_typedefs(decls)
    mapping = dict((d.name, d.type_) for d in decls)
    Utils.flatten(mapping)
    return mapping


def _check_typedefs(decls):
    left_sides = [decl.name for decl in decls]
    if len(left_sides) != len(set(left_sides)):
        c = Counter(left_sides)
        multiples = [k for (k,v) in c.items() if c>1]
        msg = "multiple typedefs for name(s) '%s'" % (", ".join(multiples))
        raise Exception(msg)


def _parse_all_wrap_instances_comments(class_decls, addParentClasses=False):
    """ Parses from a set of CppClassDecl the corresponding types including the wrap-instances comments.

    For a regular, non-templated class it will return a dictionary { 'A' : (CppTypeA, {}) } 
    For a templated class, for example

        cdef cppclass A[U]:
            #wrap-instances:
            #  A_int := A[int]

    it will return a dictionary { 'A_int' : (CppTypeA, {'U': CppTypeInt} ) } 

    Note that if addParentClasses is True, an additional entry for 'A' will be
    added _even_ if no declaration A := ... is given! This is important so that
    the type of base class 'A' can also be mapped correctly.
    """
    r = dict()
    for cdcl in class_decls:
        r.update(_parse_wrap_instances_comments(cdcl, addParentClasses))
    return r



def _parse_wrap_instances_comments(cdcl, addParentClasses=False):
    """ Parses from a CppClassDecl the corresponding types including the wrap-instances comments.

    See _parse_all_wrap_instances_comments for more detailed documentation.
    """

    inst_annotations = cdcl.annotations.get("wrap-instances")
    r = dict()
    if cdcl.template_parameters is None and not inst_annotations:
        # missing "wrap-instances" annotation works for non-template class:
        # instance name of python class equals c++ class name
        r[cdcl.name] = Types.CppType(cdcl.name), dict()
    elif inst_annotations:
        for instance_decl_str in inst_annotations:
            name, type_, tinst_map = parse_alias(cdcl, instance_decl_str)
            r[name] = type_, tinst_map
        if not r.has_key(cdcl.name) and addParentClasses:
            # If the parent does not have an entry (e.g. only A_int exists but
            # A does not exist) we have slight problem. We still need to
            # translate instances of A to their C++ types. Thus we add them
            # here to the dictionary.
            # Make sure to copy the type and mark the copy as dummy entry
            # (important for the inv_transformed fxn in Types).
            newtype_ = type_.copy()
            newtype_.is_dummy = True
            r[cdcl.name] = newtype_, tinst_map
    #for name, (t, m) in r.items():
        #m_str = Types.printable(m)
        #L.info("parse_wrap_instances_comments %s -> (%s, %s)" %(name, t, m_str))
    return r


def parse_alias(cdcl, instance_decl_str):
    """
    instance_decl_str looks like "Tint := T[int]"
    """

    name, type_ = parse_inst_decl(instance_decl_str)
    t_args = type_.template_args
    if t_args is not None:
        t_params = cdcl.template_parameters
        t_param_mapping = dict(zip(t_params, t_args))
    else:
        t_param_mapping = dict()

    return name, type_, t_param_mapping


def parse_inst_decl(str_):
    """
    instance_decl_str looks like "Tint := T[int]"
    returns "Tint", CppType.from_string("T[int]")
    """
    try:
        left, __, right = str_.partition(":=")
        name, decl_str = left.strip(), right.strip()
        return name, Types.CppType.from_string(decl_str)
    except:
        raise Exception("could not parse instance delcaration '%s'" % str_)




def _resolve_class_decls(class_decls, typedef_mapping, instance_mapping):
    """
    """
    all_resolved_classes = []
    for class_decl in class_decls:
        resolved_classes = _resolve_class_decl(class_decl,
                                               typedef_mapping,
                                               instance_mapping)
        all_resolved_classes.extend(resolved_classes)
    return all_resolved_classes


def _resolve_class_decl(class_decl, typedef_mapping, i_mapping):
    # one decl can produce multiple classes !

    L.info("resolve class decl %s" % class_decl.name)

    r = _parse_wrap_instances_comments(class_decl)
    resolved_classes = []
    for name, (type_, t_arg_mapping) in r.items():
        local_mapping = _build_local_typemap(t_arg_mapping, typedef_mapping)

        r_attributes = []
        for adcl in class_decl.attributes:
            r_attributes.append(_resolve_attribute(adcl, i_mapping,
                                                                local_mapping))

        r_methods = []
        for (mname, mdcls) in class_decl.methods.items():
            for mdcl in mdcls:
                ignore = mdcl.annotations.get("wrap-ignore", False)
                if ignore:
                    continue
                r_method = _resolve_method(mdcl, i_mapping, local_mapping, name)
                r_methods.append(r_method)
        # also store the original classtype (type_) and the mapping of the local template arguments for the cimport statement
        r_class = ResolvedClass(name, r_methods, r_attributes, class_decl, type_, local_mapping) 
        resolved_classes.append(r_class)
    return resolved_classes


def _build_local_typemap(t_param_mapping, typedef_mapping):
    # for resolving typedefed types in template instance args:
    local_map = dict((n, t.transformed(typedef_mapping)) for (n, t) in \
            t_param_mapping.items())

    # for resolving 'free' typedefs in method args and result types:
    if set(local_map) & set(typedef_mapping):
        raise Exception("t_param_mapping and typedef_mapping intersects")
    local_map.update(typedef_mapping)
    # resolve indirections induced by update:
    Utils.flatten(local_map)
    return local_map


def _resolve_method(method_decl, instance_mapping, type_map, classname=None):
    L.info("resolve method decl: '%s'" % method_decl)
    #L.info("\n   im= %s" % Types.printable(instance_mapping, "\n       "))
    #L.info("\n   tm= %s" % Types.printable(type_map, "\n       "))
    result = _resolve_method_or_function(method_decl, instance_mapping,
                                         type_map, ResolvedMethod, classname)
    L.info("result             : '%s'" % result)
    L.info("")
    return result


def _resolve_function(method_decl, instance_mapping, type_map):
    L.info("resolve function decl: '%s'" % method_decl)
    #L.info("\n   im= %s" % Types.printable(instance_mapping, "\n       "))
    #L.info("\n   tm= %s" % Types.printable(type_map, "\n       "))
    result = _resolve_method_or_function(method_decl, instance_mapping,
                                         type_map, ResolvedFunction)
    L.info("result               : '%s'" % result)
    L.info("")
    return result


def _resolve_method_or_function(method_decl, instance_mapping, type_map, clz, classname=None):
    """
    resolves aliases in return and argument types
    """
    result_type = _resolve_alias(method_decl.result_type, instance_mapping,
                                type_map)
    args = []
    for arg_name, arg_type in method_decl.arguments:
        arg_type = _resolve_alias(arg_type, instance_mapping, type_map)
        args.append((arg_name, arg_type))
    name = method_decl.annotations.get("wrap-as", method_decl.name)
    name = _resolve_constructor(name, instance_mapping, classname)
    return clz(name, result_type, args, method_decl)

def _resolve_attribute(adecl, instance_mapping, type_map):
    type_ = _resolve_alias(adecl.type_, instance_mapping, type_map)
    return ResolvedAttribute(adecl.name, type_, adecl)

def _resolve_constructor(name, instance_mapping, classname):
    """ Will resolve the constructor from the class name of the template, the
    mappings and the "Python classname" for this instance.
    """
    # Construct a map that contains for each basetype the mapping to the
    # correct classes. For templated classes, the base type will map to a list
    # of instances
    map_ = {}
    for n, t in instance_mapping.items():
        li = map_.get(t.base_type, [])
        li.append(n)
        map_[t.base_type] = li

    if map_.has_key(name):
        li = map_[name]
        # If there is only one entry, we return it (no templates)
        if len(li) == 1: return li[0]
        # If the classname is in the list, we return the correct classname
        if classname in li: return classname
        else:
            # This should never happen
            raise Exception("_resolve_constructor did not have classname in map %s" % map_)
    else:
        return name


def _resolve_alias(cpp_type, wrap_inst_decls, type_map):
    cpp_type = cpp_type.transformed(type_map)
    #cpp_type = cpp_type.transformed(wrap_inst_decls)
    alias = cpp_type.inv_transformed(wrap_inst_decls)
    return alias
