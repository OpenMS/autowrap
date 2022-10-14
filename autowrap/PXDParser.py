# encoding: utf-8
from __future__ import print_function, absolute_import, annotations

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

from typing import Dict, Union, List, Collection, Sequence, AnyStr, TYPE_CHECKING

if TYPE_CHECKING:
    from autowrap.DeclResolver import ResolvedMethod

import Cython.Compiler.Nodes
from Cython.Compiler.CmdLine import parse_command_line
from Cython.Compiler.Main import create_default_resultobj, CompilationSource, Context
from Cython.Compiler import Pipeline, FusedNode
from Cython.Compiler.Scanning import FileSourceDescriptor
from Cython.Compiler.Nodes import *
from Cython.Compiler.ExprNodes import *
import Cython.Compiler.Errors

from autowrap.Types import CppType

import os

from autowrap import logger
from autowrap.Code import Code as Code

from collections import defaultdict
from .tools import OrderKeepingDictionary

AnnotDict = Dict[str, Union[bool, List[str]]]

"""
Methods in this module use Cythons Parser to build an Cython syntax tree
from the annotated .pxd files and creates a representation of the
included classes and methods.
"""


def _check_type_constness(ctype: Nodes.CBaseTypeNode) -> bool:
    """Regardless of Cython version, checks whether the passed Cython type is const"""
    try:
        return isinstance(ctype, Nodes.CConstTypeNode)
    except AttributeError:
        return isinstance(ctype, Nodes.CConstOrVolatileTypeNode) and ctype.is_const


def parse_class_annotations(node, lines: Collection[str]) -> AnnotDict:
    """parses wrap-instructions inside comments below class def.
    Either returns a list of strings for annotations/directives with a ':' and following strings
    or True/False for boolean directives without ':'
    """
    start_at_line = node.pos[1]
    return _parse_multiline_annotations(lines[start_at_line:])


def _parse_multiline_annotations(lines: Collection[str]) -> AnnotDict:
    """does the hard work for parse_class_annotations, and is
    better testable than this.
    """
    it = iter(lines)
    result = defaultdict(list)
    while it:
        try:
            line = next(it).strip()
        except StopIteration:
            break
        if not line:
            continue
        if line.startswith("#"):
            line = line[1:].strip()
            if line.endswith(":"):
                key = line.rstrip(":")
                line = next(it).strip()
                while line.startswith("#  "):
                    if key == "wrap-doc":
                        value = line[3:].rstrip()  # rstrip to keep indentation in docs
                    else:
                        value = line[1:].strip()

                    if (
                        key == "wrap-doc" or value
                    ):  # don't add empty non wrap-doc values
                        result[key].append(value)

                    try:
                        line = next(it).lstrip()  # lstrip to keep empty lines in docs
                    except StopIteration:
                        break
            else:
                key = line
                result[key] = True
        else:
            break

    # make sure wrap-doc is always a Code object
    if "wrap-doc" in result.keys():
        doc = result.get("wrap-doc", [])
        if isinstance(doc, basestring):
            doc = [doc]

        c = Code()
        c.addRawList(doc)
        result["wrap-doc"] = c
    return result


def parse_line_annotations(
    node: Cython.Compiler.Nodes.Node, lines: Sequence[str]
) -> AnnotDict:
    """
    parses comments at end of line, in most cases the lines of
    method declarations.
    handles method declarations over multiple lines
    """

    result = dict()
    # pos starts counting with 1 and limits are inclusive
    start = node.pos[1] - 1
    end = node.end_pos()[1]

    while end < len(lines):
        if lines[end].strip() == "":
            end += 1
            continue
        if lines[end].strip().startswith(")"):
            end += 1
        break

    for line in lines[start:end]:
        try:
            __, __, comment = line.partition("#")
            if comment:
                key = None
                for f_ in comment.split(" "):
                    f = f_.strip()
                    if not f:
                        continue
                    if ":" in f:
                        key, value = f.split(":", 1)
                        assert value.strip(), (
                            "empty value (or excess space?) for key '%s' in line '%s'"
                            % (key, line.rstrip())
                        )
                        result[key] = value
                    elif f.find("wrap-") != -1:
                        key, value = f, True
                        result[key] = value
                    elif key is not None:
                        # they belong to the previous key
                        value = " " + f_
                        result[key] += value
        except Exception as e:
            raise ValueError("Cannot parse '{}'".format(line)) from e
    # check for multi line annotations after method declaration
    additional_annotations = _parse_multiline_annotations(lines[end:])
    # add multi line doc string to result (overwrites single line wrap-doc, if exists)
    if "wrap-doc" in additional_annotations.keys():
        result["wrap-doc"] = additional_annotations["wrap-doc"]
    else:
        # make sure wrap-doc is always a Code object
        if "wrap-doc" in result.keys():
            doc = result.get("wrap-doc", [])
            if isinstance(doc, basestring):
                doc = [doc]

            c = Code()
            c.addRawList(doc)
            result["wrap-doc"] = c
    return result


def _extract_template_args(node: Cython.Compiler.Nodes.Node) -> CppType:
    if isinstance(node, NameNode):
        return CppType(node.name, None)

    name = node.base.name
    if isinstance(node.index, TupleNode):
        args = [_extract_template_args(n) for n in node.index.args]
    elif isinstance(node.index, IndexNode):
        args = [_extract_template_args(node.index)]
    elif isinstance(node.index, NameNode):
        args = [CppType(node.index.name)]
    else:
        raise Exception(
            "Can not handle node %s in template argument declaration" % node.index
        )
    return CppType(name, args)


def _extract_type(
    base_type: Cython.Compiler.Nodes.CBaseTypeNode,
    decl: Cython.Compiler.Nodes.CDeclaratorNode,
) -> CppType:
    """extracts type information from node in parse_pxd_file tree"""

    type_is_const = _check_type_constness(base_type)

    # Complex const values, e.g. "const Int *" need to be reduced to base type
    # to get the correct name. Note: we will have to deal with const-ness first
    # and then with templated arguments that are nested.
    if type_is_const:
        base_type = base_type.base_type

    template_parameters = None
    if isinstance(base_type, TemplatedTypeNode):
        template_parameters = []
        for arg_node in base_type.positional_args:
            if isinstance(arg_node, CComplexBaseTypeNode):
                arg_decl = arg_node.declarator
                is_ptr = isinstance(arg_decl, CPtrDeclaratorNode)
                is_ref = isinstance(arg_decl, CReferenceDeclaratorNode)
                is_unsigned = (
                    hasattr(arg_node.base_type, "signed")
                    and not arg_node.base_type.signed
                )
                is_long = (
                    hasattr(arg_node.base_type, "longness")
                    and arg_node.base_type.longness
                )

                # Handle const template arguments which do not have a name
                # themselves, only their base types have name attribute (see
                # for example: shared_ptr<const Int>)
                arg_is_const = _check_type_constness(arg_node.base_type)
                if arg_is_const:
                    name = arg_node.base_type.base_type.name
                else:
                    name = arg_node.base_type.name

                args = None
                template_args = getattr(arg_node.base_type, "positional_args", None)
                if template_args:
                    args = [
                        _extract_type(t.base_type, t.declarator) for t in template_args
                    ]
                    name = arg_node.base_type.base_type_node.name
                ttype = CppType(
                    name,
                    args,
                    is_ptr,
                    is_ref,
                    is_unsigned,
                    is_long,
                    is_const=arg_is_const,
                )
                template_parameters.append(ttype)
            elif isinstance(arg_node, NameNode):
                name = arg_node.name
                template_parameters.append(CppType(name))
            elif isinstance(arg_node, IndexNode):  # nested template !
                tt = _extract_template_args(arg_node)
                template_parameters.append(tt)
            else:
                raise Exception(
                    "Can not handle template argument node (arg_node) %r"
                    % arg_node.pos[0].file_path
                    + " line: %r" % arg_node.pos[1]
                    + " col: %r" % arg_node.pos[2]
                )

        base_type = base_type.base_type_node

    is_ptr = isinstance(decl, CPtrDeclaratorNode)
    is_ref = isinstance(decl, CReferenceDeclaratorNode)
    is_unsigned = hasattr(base_type, "signed") and not base_type.signed
    is_long = hasattr(base_type, "longness") and base_type.longness

    return CppType(
        base_type.name,
        template_parameters,
        is_ptr,
        is_ref,
        is_unsigned,
        is_long,
        is_const=type_is_const,
    )


class BaseDecl(object):
    def __init__(
        self, name: str, annotations: Dict[str, Union[bool, List[str]]], pxd_path: str
    ):
        self.name: str = name
        self.annotations: AnnotDict = annotations
        self.pxd_path: str = pxd_path


class CTypeDefDecl(BaseDecl):
    def __init__(self, new_name: str, type_, annotations: AnnotDict, pxd_path):
        super(CTypeDefDecl, self).__init__(new_name, annotations, pxd_path)
        self.type_ = type_

    @classmethod
    def parseTree(cls, node, lines, pxd_path):
        decl = node.declarator
        if isinstance(decl, CPtrDeclaratorNode):
            new_name = decl.base.name
        else:
            new_name = decl.name
        type_ = _extract_type(node.base_type, node.declarator)
        annotations = parse_line_annotations(node, lines)
        return cls(new_name, type_, annotations, pxd_path)


class EnumDecl(BaseDecl):
    def __init__(self, name, scoped, items, annotations, pxd_path):
        super(EnumDecl, self).__init__(name, annotations, pxd_path)
        self.scoped = scoped
        self.items = items
        self.template_parameters = None

    @classmethod
    def parseTree(cls, node: CEnumDefNode, lines, pxd_path):
        name = node.name
        items = []
        try:
            scoped = node.scoped
        except AttributeError:
            scoped = False
        annotations = parse_class_annotations(node, lines)
        current_value = 0
        for item in node.items:
            if item.value is not None:
                current_value = item.value.constant_result
            items.append((item.name, current_value))
            current_value += 1

        return cls(name, scoped, items, annotations, pxd_path)

    def __str__(self):
        res = "EnumDecl %s : " % self.name
        res += "scoped" if self.scoped else ""
        res += ", ".join("%s: %d" % (i, v) for (i, v) in self.items)
        return res

    def get_method_decls(self):
        return []


class CppClassDecl(BaseDecl):
    methods: Dict[AnyStr, List[CppMethodOrFunctionDecl]]
    attributes: List[CppAttributeDecl]
    template_parameters: List[AnyStr]

    def __init__(
        self, name, template_parameters, methods, attributes, annotations, pxd_path
    ):
        super(CppClassDecl, self).__init__(name, annotations, pxd_path)
        self.methods = methods
        self.attributes = attributes
        self.template_parameters = template_parameters

    @classmethod
    def parseTree(
        cls, node: Cython.Compiler.Nodes.CppClassNode, lines: Collection[str], pxd_path
    ):
        name = node.name
        template_parameters = node.templates
        if (
            template_parameters
            and isinstance(template_parameters, list)
            and isinstance(template_parameters[0], tuple)
        ):
            # Cython 0.24 uses [(string, bool)] to indicate name and whether
            # template argument is required or optional.
            # For now, convert to pre-0.24 format
            template_parameters = [t[0] for t in template_parameters]

        class_annotations = parse_class_annotations(node, lines)
        methods = OrderKeepingDictionary()
        attributes = []
        for att in node.attributes:
            decl = None
            if isinstance(att, CVarDefNode):  # attribute or member function
                decl = MethodOrAttributeDecl.parseTree(att, lines, pxd_path)
            elif isinstance(att, CEnumDefNode):
                logger.warning(
                    "Nested enums currently not supported by autowrap. Skipping its wrap."
                    " Please add them under a new cdef extern section with class namespace. E.g.: \n"
                    "cdef extern from 'foo.hpp' namespace 'Foo': \n"
                    "    cpdef enum class MyEnum 'Foo::MyEnum': \n"
                    "      # wrap-attach: Foo \n"
                    "      A,B,C"
                )
                # TODO we might be able to support it with the following
                # decl = EnumDecl.parseTree(att, lines, pxd_path)
            elif isinstance(att, CClassDefNode):
                logger.warning(
                    "Nested classes are currently not supported by autowrap. Skipping its wrap."
                    " Try to add them under a new cdef extern section with class namespace. E.g.: \n"
                    "cdef extern from 'foo.hpp' namespace 'Foo': \n"
                    "    cpdef cppclass MyClass 'Foo::MyClass': \n"
                    "      ..."
                )
            if decl is not None:
                if isinstance(decl, CppMethodOrFunctionDecl):
                    methods.setdefault(decl.name, []).append(decl)
                elif isinstance(decl, CppAttributeDecl):
                    attributes.append(decl)
                elif isinstance(decl, EnumDecl):
                    # Should not happen since we currently forbid it in the logic above
                    # attributes.append(decl)
                    pass

        return cls(
            name, template_parameters, methods, attributes, class_annotations, pxd_path
        )

    def __str__(self):
        rv = ["cppclass %s: " % (self.name,)]
        for meth_list in self.methods.values():
            rv += ["     " + str(method) for method in meth_list]
        return "\n".join(rv)

    def get_transformed_methods(self, mapping):
        result = defaultdict(list)
        for mdcl in self.get_method_decls():
            result[mdcl.name].append(mdcl.transformed(mapping))
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
                    self.methods.setdefault(decl.name, []).append(decl)


class CppAttributeDecl(BaseDecl):
    def __init__(self, name, type_: CppType, annotations, pxd_path):
        super(CppAttributeDecl, self).__init__(name, annotations, pxd_path)
        self.type_ = type_


class CppMethodOrFunctionDecl(BaseDecl):
    def __init__(self, result_type, name, arguments, is_static, annotations, pxd_path):
        super(CppMethodOrFunctionDecl, self).__init__(name, annotations, pxd_path)
        self.result_type = result_type
        self.arguments = arguments
        self.is_static = is_static

    def transformed(self, typemap):
        result_type = self.result_type.transformed(typemap)
        args = [(n, t.transformed(typemap)) for n, t in self.arguments]
        return CppMethodOrFunctionDecl(
            result_type,
            self.name,
            args,
            self.is_static,
            self.annotations,
            self.pxd_path,
        )

    def matches(self, other):
        """only checks method name signature,
        does not consider argument names"""
        if self.name != other.name:
            return False
        self_key = [self.result_type] + [t for (__, t) in self.arguments]
        other_key = [other.result_type] + [t for (__, t) in other.arguments]
        return self_key == other_key

    def __str__(self):
        return "CppMethodOrFunctionDecl: %s %s (%s)" % (
            self.result_type,
            self.name,
            ["%s %s" % (str(t), n) for n, t in self.arguments],
        )


class MethodOrAttributeDecl(object):
    @classmethod
    def parseTree(cls, node: CVarDefNode, lines, pxd_path):
        if isinstance(node, CEnumDefNode):
            return EnumDecl.parseTree(node, lines, pxd_path)

        annotations = parse_line_annotations(node, lines)
        if isinstance(node, CppClassNode):
            return None  # nested classes only can be declared in pxd

        is_static = False

        (decl,) = node.declarators
        result_type = _extract_type(node.base_type, decl)

        if isinstance(decl, CNameDeclaratorNode):
            # Handle regular declarations
            return CppAttributeDecl(decl.name, result_type, annotations, pxd_path)

        if isinstance(decl, CPtrDeclaratorNode) and not isinstance(
            decl.base, CFuncDeclaratorNode
        ):
            # Handle raw pointer declarations (call with base name)
            return CppAttributeDecl(decl.base.name, result_type, annotations, pxd_path)

        # if the variable name declaration is part of a function declaration
        if isinstance(decl.base, CFuncDeclaratorNode):
            # go up the base type
            decl = decl.base

        if node.decorators is not None:
            for dec in node.decorators:
                if dec.decorator.name == "staticmethod":
                    is_static = True

        name = decl.base.name
        args = []
        for arg in decl.args:
            argdecl = arg.declarator
            if isinstance(argdecl, CReferenceDeclaratorNode):
                argname = argdecl.base.name
            elif isinstance(argdecl, CPtrDeclaratorNode):
                base = argdecl.base
                if isinstance(base, CPtrDeclaratorNode):
                    raise Exception("multi ptr not supported for method " + name)
                argname = base.name
            else:
                # TODO document in which case the following if-case occurs and why two times .base
                if not hasattr(argdecl, "name"):
                    argname = argdecl.base.base.name
                else:
                    argname = argdecl.name
            tt = _extract_type(arg.base_type, argdecl)
            args.append((argname, tt))

        return CppMethodOrFunctionDecl(
            result_type, name, args, is_static, annotations, pxd_path
        )


def parse_str(what):
    import tempfile

    # delete=False keeps file after closing it !
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.write(what.encode("utf-8"))
        fp.flush()
        fp.close()  # needed for reading it on win
        result = parse_pxd_file(fp.name)
        return result


def parse_pxd_file(path, warn_level=1):
    Cython.Compiler.Errors.LEVEL = warn_level

    options, sources = parse_command_line(["--cplus", path])

    import pkg_resources

    # TODO sync with CodeGenerator.py function fixed_include_dirs
    data = pkg_resources.resource_filename("autowrap", "data_files/autowrap")
    options.include_path = [data]
    options.language_level = sys.version_info.major

    path = os.path.abspath(path)
    basename = os.path.basename(path)
    name, ext = os.path.splitext(basename)

    source_desc = FileSourceDescriptor(path, basename)
    source = CompilationSource(source_desc, name, os.getcwd())
    result = create_default_resultobj(source, options)

    try:  # Cython 0.X
        context = options.create_context()
    except:  # Cython 3.X
        context = Context.from_options(options)
    pipeline = Pipeline.create_pyx_pipeline(context, options, result)
    context.setup_errors(options, result)
    root = pipeline[0](source)  # only parser

    def iter_bodies(tree):
        try:
            for n in tree.body.stats[0].stats:
                # cimports at head of file
                yield n
        except:
            pass
        if hasattr(tree.body, "stats"):
            for s in tree.body.stats:
                if isinstance(s, CDefExternNode):
                    body = s.body
                    if hasattr(body, "stats"):
                        for node in body.stats:
                            yield node
                    else:
                        yield body
        elif hasattr(tree.body, "body"):
            body = tree.body.body
            yield body
        else:
            raise Exception("parse_pxd_file failed: no valid .pxd file !")

    lines = open(path).readlines()

    def cimport(b, _, __):
        print("cimport", b.module_name, "as", b.as_name)

    handlers = {
        CEnumDefNode: EnumDecl.parseTree,
        CppClassNode: CppClassDecl.parseTree,
        CTypeDefNode: CTypeDefDecl.parseTree,
        CVarDefNode: MethodOrAttributeDecl.parseTree,
        CImportStatNode: cimport,
    }

    result = []
    for body in iter_bodies(root):
        handler = handlers.get(type(body))
        if handler is not None:
            # with open('log.txt', 'a') as f:
            #    f.write("parsed %s, handler=%s \n" % (body.__class__, handler.__self__))
            result.append(handler(body, lines, path))
        else:
            for node in getattr(body, "stats", []):
                handler = handlers.get(type(node))
                if handler is not None:
                    result.append(handler(node, lines, path))
    return result


if __name__ == "__main__":

    import sys

    if len(sys.argv) == 3:
        print(parse_pxd_file(sys.argv[1], sys.argv[2]))
    else:
        print(parse_pxd_file(sys.argv[1]))
