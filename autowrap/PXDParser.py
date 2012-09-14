#encoding: utf-8
from Cython.Compiler.CmdLine import parse_command_line
from Cython.Compiler.Main import create_default_resultobj, CompilationSource
from Cython.Compiler import Pipeline
from Cython.Compiler.Scanning import FileSourceDescriptor
from Cython.Compiler.Nodes import *
from Cython.Compiler.ExprNodes import *

from Types import CppType

import re
import os

from collections import defaultdict, OrderedDict


class IdentityMap(dict):
    """ every get and __getitem__ returns key as value """

    def __getitem__(self, k):
        return k


def parse_class_annotations(node, lines):
    """ parses wrap-instructions inside comments below class def """
    start_at_line = node.pos[1]
    return _parse_multiline_annotations(lines[start_at_line:])


def _parse_multiline_annotations(lines):
    """ does the hard work for parse_class_annotations, and is
        better testable than this.
    """
    it = iter(lines)
    result = defaultdict(list)
    while it:
        try:
            line = it.next().strip()
        except StopIteration:
            break
        if not line:
            continue
        if line.startswith("#"):
            line = line[1:].strip()
            if line.endswith(":"):
                key = line.rstrip(":")
                line = it.next().strip()
                while line.startswith("#  "):
                    value = line[1:].strip()
                    result[key].append(value)
                    line = it.next().strip()
            else:
                key = line
                result[key] = True
        else:
            break
    return result


def parse_line_annotations(node, lines):
    """
       parses comments at end of line, in most cases the lines of
       method declarations
    """

    parts = lines[node.pos[1] - 1].split("#", 1)
    result = dict()
    if len(parts)==2:
        # parse python statements in comments
        fields = [ f.strip() for f in parts[1].split(" ") ]
        for f in fields:
            if ":" in f:
                key, value = f.split(":", 1)
            else:
                key, value = f, 1
        result[key] = value
    return result


class EnumOrClassDecl(object):
        pass


class EnumDecl(EnumOrClassDecl):

    def __init__(self, name, items, annotations):
        self.name = name
        self.items = items
        self.annotations = annotations
        self.wrap_ignore = annotations.get("wrap-ignore", False)
        self.template_parameters = None

    @classmethod
    def fromTree(cls, node, lines):
        name = node.name
        items = []
        annotations = parse_line_annotations(node, lines)
        current_value = 0
        for item in node.items:
            if item.value is not None:
                current_value = item.value.constant_result
            items.append((item.name, current_value))
            current_value += 1

        return cls(name, items, annotations)

    def __str__(self):
        res = "EnumDecl %s : " % self.name
        res += ", ".join("%s: %d" % (i, v) for (i, v) in self.items)
        return res


class CppClassDecl(EnumOrClassDecl):

    def __init__(self, name, template_parameters, methods, annotations):
        self.name = name
        self.template_parameters = template_parameters
        self.methods = methods
        self.annotations = annotations

    @classmethod
    def fromTree(cls, node, lines):

        if hasattr(node, "stats"): # more than just class def
            raise Exception("unhandled case")
            """
            for stat in node.stats:
                if isinstance(stat, CTypeDefNode):
                    alias = stat.base_type.name
                    base_type = stat.declarator.base.name
                    args_node = stat.declarator.dimension.args
                    args = [ CppType(decl.name) for decl in args_node]
                    typedefs[alias] = CppType(base_type, args)
                elif isinstance(stat, CppClassNode):
                    node = stat
                    break
                else:
                    print "ignore node", stat
            """

        name = node.name
        class_annotations = parse_class_annotations(node, lines)

        template_parameters = node.templates
        methods = OrderedDict()
        for att in node.attributes:
            meth = CppMethodDecl.fromTree(att, lines)
            if meth is not None:
                # an OrderedDefaultDict(list) would be nice here:
                methods.setdefault(meth.name,[]).append(meth)

        return cls(name, template_parameters, methods, class_annotations)

    def __str__(self):
        rv = ["cppclass %s: " % (self.name, )]
        for meth_list in self.methods.values():
            rv += ["     " + str(method) for method in meth_list]
        return "\n".join(rv)

    def get_transformed_methods(self, mapping):
        result = dict()
        for mdcl in self.get_method_decls():
            result.setdefault(mdcl.name, []).append(mdcl.transformed(mapping))
        return result

    def get_method_decls(self):
        for name, method_decls in self.methods.items():
            for method_decl in method_decls:
                yield method_decl

    def has_method(self, other_decl):
        with_same_name = self.methods.get(other_decl.name)
        if with_same_name is None:
            return False
        return any(decl.matches(other_decl) for decl in with_same_name)

    def attach_base_methods(self, dd):
        for name, decls in dd.items():
            for decl in decls:
                if not self.has_method(decl):
                    self.methods.setdefault(decl.name,[]).append(decl)


def extract_type(base_type, decl):
    """ extracts type information from node in parse tree """
    template_parameters = None
    if isinstance(base_type, TemplatedTypeNode):
        template_parameters = []
        for arg in base_type.positional_args:
            if isinstance(arg, CComplexBaseTypeNode):
                decl = arg.declarator
                is_ptr = isinstance(decl, CPtrDeclaratorNode)
                is_ref = isinstance(decl, CReferenceDeclaratorNode)
                name = arg.base_type.name
                ttype = CppType(name, None, is_ptr, is_ref)
                template_parameters.append(ttype)
            elif isinstance(arg, NameNode):
                name = arg.name
                template_parameters.append(CppType(name))
            elif isinstance(arg, IndexNode): # nested template !
                # only handles one nesting level !
                name = arg.base.name
                if hasattr(arg.index, "args"):
                    args = [ CppType(a.name) for a in arg.index.args ]
                else:
                    args = [ CppType(arg.index.name) ]
                tt = CppType(name, args)
                template_parameters.append(tt)
            else:
                raise Exception("can not handle template arg %r" % arg)

        base_type = base_type.base_type_node

    is_ptr = isinstance(decl, CPtrDeclaratorNode)
    is_ref = isinstance(decl, CReferenceDeclaratorNode)
    is_unsigned = hasattr(base_type, "signed") and not base_type.signed
    return CppType(base_type.name, template_parameters, is_ptr, is_ref,
                   is_unsigned)


class CppMethodDecl(object):

    def __init__(self, result_type,  name, args, annotations):

        self.result_type = result_type
        self.name = name
        self.args = args
        self.annotations = annotations
        self.wrap = not self.annotations.get("ignore", False)

    def transformed(self, typemap):
        result_type = self.result_type.transform(typemap)
        args = [ (n, t.transform(typemap)) for n, t in self.args ]
        return CppMethodDecl(result_type, self.name, args, self.annotations)


    def matches(self, other):
        """ only checks method name signature,
            does not consider argument names"""
        if self.name != other.name:
            return False
        self_key = [ self.result_type ] + [ t for (a,t) in self.args ]
        other_key = [ other.result_type ] + [ t for (a,t) in other.args ]
        return self_key == other_key


    @classmethod
    def fromTree(cls, node, lines):

        annotations = parse_line_annotations(node, lines)
        #import pdb; pdb.set_trace()

        if isinstance(node, CppClassNode):
            return None # nested classes only can be delcared in pxd

        decl = node.declarators[0]
        result_type = extract_type(node.base_type, decl)

        if isinstance(decl, CNameDeclaratorNode):
            if re.match("^operator\W*\(\)$", decl.name):
                name = decl.name[:-2]
                args = []
                return cls(result_type, name, args, annotations)
            raise Exception("can not handle %s" % decl.name)

        if isinstance(decl.base, CFuncDeclaratorNode):
            decl = decl.base

        name = decl.base.name
        args = []
        for arg in decl.args:
            argdecl = arg.declarator
            if isinstance(argdecl, CReferenceDeclaratorNode) or \
               isinstance(argdecl, CPtrDeclaratorNode):
                argname = argdecl.base.name
            else:
                argname = argdecl.name
            tt = extract_type(arg.base_type, argdecl)
            args.append((argname,tt))

        return cls(result_type, name, args, annotations)

    def __str__(self):
        rv = str(self.result_type)
        rv += " " + self.name
        argl = [str(type_) + " " + str(name) for name, type_ in self.args]
        return rv + "(" + ", ".join(argl) + ")"


def parse_str(what):
    import tempfile

    with tempfile.NamedTemporaryFile() as fp:
        fp.write(what)
        fp.flush()
        return parse(fp.name)

def parse(path):

    """ reads pxd file and extracts *SINGLE* class """
    #TODO: multiple classes in one files, makes testing easier !

    options, sources = parse_command_line(["--cplus", path])

    path = os.path.abspath(path)
    basename = os.path.basename(path)
    name, ext = os.path.splitext(basename)

    source_desc = FileSourceDescriptor(path, basename)
    source = CompilationSource(source_desc, name, os.getcwd())
    result = create_default_resultobj(source, options)

    context = options.create_context()
    pipeline = Pipeline.create_pyx_pipeline(context, options, result)
    tree = pipeline[0](source)  # only parser

    if hasattr(tree.body, "stats"):
        for s in tree.body.stats:
            if isinstance(s, CDefExternNode):
                body = s.body
                break
    elif hasattr(tree.body, "body"):
        body = tree.body.body
    else:
        raise Exception("parse failed: no valied .pxd file !")

    lines = open(path).readlines()

    if isinstance(body, CEnumDefNode):
            return EnumDecl.fromTree(body, lines)

    return CppClassDecl.fromTree(body, lines)

if __name__ == "__main__":

    import sys
    print parse(sys.argv[1])
