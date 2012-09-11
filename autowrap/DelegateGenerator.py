from PXDParser import EnumOrClassDecl
import re


class FrozenDict(dict):

    def __init__(self, dd):
        dict.__init__(self, dd)

    def __setitem__(self, k, v):
        raise Exception("dict is frozen, setitem not allowed")

    def __hash__(self):
        return hash(tuple(sorted(self.items())))

class TemplateParameterMapping(FrozenDict):
    pass


class ClassRegistry(object):

    def __init__(self):
        self.dd = dict()

    def register(self, alias, basename, template_mapping):
        assert template_mapping is None or \
               isinstance(template_mapping, TemplateParameterMapping)
        self.dd[basename, template_mapping] = alias

    def get_alias(self, basename, template_mapping):
        assert template_mapping is None or \
               isinstance(template_mapping, TemplateParameterMapping)
        return self.dd[basename, template_mapping]

    def keys(self):
        return self.dd.keys()


class ClassInstance(object):

    def __init__(self, name, template_instances, methods):
        self.name = name
        self.template_instances = template_instances
        self.methods = methods


class MethodInstance(object):

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


def resolve_templates(class_decls):
    assert all(isinstance(d, EnumOrClassDecl) for d
                          in class_decls)

    registry = register_all_instances(class_decls)
    instances = generate_and_resolve_all_instances(class_decls, registry)
    return instances


def register_all_instances(class_decls):
    """ parses annotations of all classes and registers aliases for
        parameterized classes """
    r = ClassRegistry()
    for decl in class_decls:
        instances = decl.annotations.get("wrap-instances")
        if decl.template_parameters is None and instances is None:
            # default: instance name of python class equals cpp class name
            # in case of missing template parameters
            r.register(decl.name, decl.name, None)
        elif decl.template_parameters is not None and instances is None\
            and not decl.wrap_ignore:
            raise Exception("templated class has no 'wrap-instances' "
                            "annotations. declare instances or supress "
                            "wrapping with 'wrap-ignore' annotation")
        else:
            for instance in instances:
                match = re.match("(\w+)(\[\w+(,\w+)*\])?", instance)
                alias, t_instances, _ = match.groups()
                t_instances = t_instances[1:-1] # remove wrapping []
                t_instances = [ t.strip() for t in t_instances.split(",") ]
                t_params = decl.template_parameters
                mapping = TemplateParameterMapping(zip(t_params, t_instances))
                r.register(alias, decl.name, mapping)
    return r


def generate_and_resolve_all_instances(class_decls, registry):

    resolved_classes = []
    class_decls = dict((c.name, c) for c in class_decls)
    for instance in registry.keys():
        resolved_classes.append(instance)

    return resolved_classes



