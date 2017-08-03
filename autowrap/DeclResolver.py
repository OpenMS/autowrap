# encoding: utf-8

__license__ = """

Copyright (c) 2012-2014, Uwe Schmitt, all rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

Neither the name of the ETH Zurich nor the names of its contributors may be
used to endorse or promote products derived from this software without specific
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import autowrap.PXDParser as PXDParser
import autowrap.Types as Types
import autowrap.Utils as Utils
import os
from collections import defaultdict
from autowrap.tools import OrderKeepingDictionary



__doc__ = """

    The methods in this module take the class declarations created by
    calling PXDParser.parse and generates a list of resolved class
    declarations.  'resolved' means that all template parameters are
    resolved and inherited methods are resolved from super classes.

    Some preliminaries which you should have in mind to understand the
    code below:

    In pxd files inheritance is declared with 'wrap-inherits'
    annotations.  Python class names are declared with 'wrap-instances'
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

    If you wrap a C++ class without template parameters you can omit
    the 'wrap-instances' annotation. In this case the name of the Python
    class is the same as the name of the C++ class.

    There are a few additional hints you can give to the wrapper, for classes these are:
        - wrap-ignore: will not create a wrapper for this class (e.g. abstract
                       base class that needs to be known to Cython but cannot be wrapped)
        - wrap-manual-memory: will allow the user to provide manual memory
                              management of self.inst, therefore the class will
                              not provide the automated __dealloc__ and inst
                              attribute (but their presence is still expected). 
                              This is useful if you cannot use the shared-ptr
                              approach to store a reference to the C++ class
                              (as with singletons for example).
        - wrap_hash: if the produced class should be hashable, give a hint
                     which method should be used for this. This method will be
                     called on the C++ object and fed into the Python "hash"
                     function. This implies the class also provides a
                     operator== function.
                     Note that the only requirement for a hash function is that
                     equal objects produce equal values

    Thus a class could look like this:

        cdef cppclass B[U,V]:
            # wrap-inherits:
            #    C[U]
            #    D
            #
            # wrap-instances:
            #   B_int_float := B[int, float]
            #   B_pure := B[int, int]
            #
            # wrap-manual-memory
            #
            # wrap-hash:
            #   getStringId().c_str()


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
    """

    def __init__(self, name, methods, attributes, decl, instance_map, local_map):
        self.name = name
        # resolve overloadings
        self.methods = OrderKeepingDictionary()
        for m in methods:
            self.methods.setdefault(m.name, []).append(m)
        self.attributes = attributes

        self.cpp_decl = decl
        # self.items = getattr(decl, "items", [])
        self.wrap_ignore = decl.annotations.get("wrap-ignore", False)
        self.no_pxd_import = decl.annotations.get("no-pxd-import", False)
        self.wrap_manual_memory = decl.annotations.get("wrap-manual-memory", [])
        # fix previous code where we had a bool ... 
        if self.wrap_manual_memory == True:
            self.wrap_manual_memory = ["__old-model"]
        else:
            self.wrap_manual_memory == []
        assert( isinstance(self.wrap_manual_memory, list) )
        self.wrap_hash = decl.annotations.get("wrap-hash", [])
        self.local_map = local_map
        self.instance_map = instance_map

    def get_flattened_methods(self):
        return [m for methods in self.methods.values() for m in methods]

    def __str__(self):
        return "\n   ".join([self.name] + map(str, self.methods))


class ResolvedMethod(object):

    """ contains all info for generating wrapping code of
        resolved class.
        "resolved" means that template parameters are resolved.
    """

    def __init__(self, name, result_type, arguments, decl, instance_map,
                 local_map):
        self.name = name
        self.result_type = result_type
        self.arguments = arguments
        self.cpp_decl = decl
        self.wrap_ignore = decl.annotations.get("wrap-ignore", False)
        self.with_nogil = decl.annotations.get("wrap-with-no-gil", False)
        self.local_map = local_map
        self.instance_amp = instance_map

    def __str__(self):
        args = [("%s %s" % (t, n)).strip() for (n, t) in self.arguments]
        return "%s %s(%s)" % (self.result_type, self.name, ", ".join(args))


class ResolvedFunction(ResolvedMethod):

    pass


def resolve_decls_from_files_single_thread(pathes, root):
    decls = []
    for k, path in enumerate(pathes):
        full_path = os.path.join(root, path)
        if k % 50 == 0: 
            L.log(25, "parsing progress %s out of %s" % (k, len(pathes)))
        decls.extend(PXDParser.parse_pxd_file(full_path))
    return _resolve_decls(decls)

def resolve_decls_from_files(pathes, root, num_processes = 1):
    if num_processes > 1:
        return resolve_decls_from_files_multi_thread(pathes, root, num_processes)
    else:
        return resolve_decls_from_files_single_thread(pathes, root)

def resolve_decls_from_files_multi_thread(pathes, root, num_processes):
    """Perform parsing with multiple threads

    This function distributes the work on `num_processes` processes and each
    process works on 10 files at a time until there are no more files left to
    work on.
    """
    import multiprocessing as mp

    CONCURRENT_FILES_PER_CORE = 10
    pool = mp.Pool(processes=num_processes)
    full_pathes = [os.path.join(root, path) for path in pathes]

    decls = []
    while len(full_pathes) > 0:
        n_work = len(full_pathes)
        remaining = max(0, n_work - num_processes * CONCURRENT_FILES_PER_CORE)
        args = [full_pathes.pop() for k in range(n_work - remaining)]
        L.log(25, "parsing progress %s out of %s with %s processes" % (len(pathes)-remaining, len(pathes), num_processes))

        res = pool.map(PXDParser.parse_pxd_file, args)
        for r in res:
            decls.extend(r)

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

    typedef_decls = filter_out(PXDParser.CTypeDefDecl)
    function_decls = filter_out(PXDParser.CppMethodOrFunctionDecl)
    enum_decls = filter_out(PXDParser.EnumDecl)
    class_decls = filter_out(PXDParser.CppClassDecl)

    class_decls = _resolve_all_inheritances(class_decls)

    typedef_mapping = _build_typedef_mapping(typedef_decls)

    # register enums as type aliases:
    enum_mapping = dict()
    for e in enum_decls:
        enum_mapping[e.name] = Types.CppType(e.name, enum_items=e.items)

    # register class aliases
    instance_mapping = _parse_all_wrap_instances_comments(class_decls)
    # remove local targ mappings:
    instance_mapping = dict((k, v0) for (k, (v0, v1)) in instance_mapping.items())

    # resolve  typedefs in class aliase values
    instance_mapping = dict((k, v.transformed(typedef_mapping)) for (k, v) in
                            instance_mapping.items())

    # add enum mapping to class instances mapping
    intersecting_names = set(instance_mapping) & set(enum_mapping)
    assert not intersecting_names, "enum names and class decls overlap: %s" % intersecting_names

    instance_mapping.update(enum_mapping)

    functions = [_resolve_function(f, instance_mapping, typedef_mapping) for f in function_decls]

    enums = [ResolvedEnum(e) for e in enum_decls]
    typedefs = [ResolvedTypeDef(t) for t in typedef_decls]

    classes = _resolve_class_decls(class_decls, typedef_mapping, instance_mapping)

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
        raise Exception("deriving %s from %s does not match" % (cdcl.name, super_cld.name))

    # map template parameters in super class to the parameters used in current
    # class:
    mapping = dict(zip(super_targs, used_parameters))
    # get copy of methods from super class ans transform template params:
    transformed_methods = super_cld.get_transformed_methods(mapping)
    transformed_methods = dict((k, v) for (k, v) in transformed_methods.items()
                               if k != super_cld.name)  # remove constructors
    for method in transformed_methods:
        L.info("attach to %s: %s" % (cdcl.name, method))
    cdcl.attach_base_methods(transformed_methods)
    # L.info("")


def _build_typedef_mapping(decls):
    _check_typedefs(decls)
    mapping = dict((d.name, d.type_) for d in decls)
    Utils.flatten(mapping)
    return mapping


def _check_typedefs(decls):
    left_sides = [decl.name for decl in decls]
    if len(left_sides) != len(set(left_sides)):
        multiples = [ls for ls in left_sides if left_sides.count(ls) > 1]
        msg = "multiple typedefs for name(s) '%s'" % (", ".join(multiples))
        raise Exception(msg)


def _parse_all_wrap_instances_comments(class_decls):
    """ parses annotations of all classes and registers aliases for
        classes.

        cdef cppclass A[U]:
            #wrap-instances:
            #  AA := A[int]

        generates an entry  'AA' : ( A[int], {'U': 'int'} ) in r
        where "A[int]" is CppType("A", [CppType["int"])

    """
    r = dict()
    for cdcl in class_decls:
        r.update(_parse_wrap_instances_comments(cdcl))
    return r


def _parse_wrap_instances_comments(cdcl):

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
        resolved_classes = _resolve_class_decl(class_decl, typedef_mapping, instance_mapping)
        all_resolved_classes.extend(resolved_classes)
    return all_resolved_classes


def _resolve_class_decl(class_decl, typedef_mapping, i_mapping):
    # one decl can produce multiple classes !

    L.info("resolve class decl %s" % class_decl.name)

    r = _parse_wrap_instances_comments(class_decl)
    resolved_classes = []
    for cinst_name, (type_, t_arg_mapping) in r.items():
        local_mapping = _build_local_typemap(t_arg_mapping, typedef_mapping)

        r_attributes = []
        for adcl in class_decl.attributes:
            r_attributes.append(_resolve_attribute(adcl, i_mapping, local_mapping))

        r_methods = []
        for (mname, mdcls) in class_decl.methods.items():
            for mdcl in mdcls:
                ignore = mdcl.annotations.get("wrap-ignore", False)
                if ignore:
                    continue
                if mdcl.name == class_decl.name:
                    r_method = _resolve_constructor(cinst_name, mdcl, i_mapping, local_mapping)
                else:
                    r_method = _resolve_method(mdcl, i_mapping, local_mapping)
                r_methods.append(r_method)
        r_class = ResolvedClass(cinst_name, r_methods, r_attributes,
                                class_decl, i_mapping, local_mapping)
        resolved_classes.append(r_class)
    return resolved_classes


def _build_local_typemap(t_param_mapping, typedef_mapping):
    # for resolving typedefed types in template instance args:
    local_map = dict((n, t.transformed(typedef_mapping)) for (n, t) in t_param_mapping.items())

    # for resolving 'free' typedefs in method args and result types:
    if set(local_map) & set(typedef_mapping):
        raise Exception("t_param_mapping and typedef_mapping intersects")
    local_map.update(typedef_mapping)
    # resolve indirections induced by update:
    Utils.flatten(local_map)
    return local_map


def _resolve_constructor(cinst_name, method_decl, instance_mapping, local_type_map):
    L.info("resolve method decl: '%s'" % method_decl)
    result = _resolve_method_or_function(method_decl, instance_mapping,
                                         local_type_map, ResolvedMethod)
    result.name = cinst_name
    # L.info("result             : '%s'" % result)
    # L.info("")
    return result


def _resolve_method(method_decl, instance_mapping, local_type_map):
    L.info("resolve method decl: '%s'" % method_decl)
    result = _resolve_method_or_function(method_decl, instance_mapping,
                                         local_type_map, ResolvedMethod)
    # L.info("result             : '%s'" % result)
    # L.info("")
    return result


def _resolve_function(method_decl, instance_mapping, local_type_map):
    L.info("resolve function decl: '%s'" % method_decl)
    result = _resolve_method_or_function(method_decl, instance_mapping,
                                         local_type_map, ResolvedFunction)
    # L.info("result               : '%s'" % result)
    # L.info("")
    return result


def _resolve_method_or_function(method_decl, instance_mapping, local_type_map,
                                clz):
    """
    resolves aliases in return and argument types
    """
    result_type = _resolve_alias(method_decl.result_type, instance_mapping,
                                 local_type_map)
    args = []
    for arg_name, arg_type in method_decl.arguments:
        arg_type = _resolve_alias(arg_type, instance_mapping, local_type_map)
        args.append((arg_name, arg_type))
    name = method_decl.annotations.get("wrap-as", method_decl.name)
    return clz(name, result_type, args, method_decl, instance_mapping, local_type_map)


def _resolve_attribute(adecl, instance_mapping, type_map):
    type_ = _resolve_alias(adecl.type_, instance_mapping, type_map)
    return ResolvedAttribute(adecl.name, type_, adecl)


def _resolve_alias(cpp_type, wrap_inst_decls, type_map):
    cpp_type = cpp_type.transformed(type_map)
    alias = cpp_type.inv_transformed(wrap_inst_decls)
    return alias
