# encoding: utf-8

from __future__ import print_function
import pdb

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

from contextlib import contextmanager
import os.path
import sys
import re
from collections import defaultdict
from typing import (
    TypeVar,
    Callable,
    Union,
    Tuple,
    Type,
    Dict,
    Collection,
    AnyStr,
    List,
    Optional,
)

import Cython.Compiler.Version

from autowrap.ConversionProvider import setup_converter_registry, ConverterRegistry
from autowrap.DeclResolver import (
    ResolvedClass,
    ResolvedEnum,
    ResolvedTypeDef,
    ResolvedFunction,
    ResolvedMethod,
)

ResolvedDecl = TypeVar(
    "ResolvedDecl",
    ResolvedEnum,
    ResolvedFunction,
    ResolvedClass,
    ResolvedMethod,
    ResolvedTypeDef,
)
from autowrap.Types import CppType  # , printable
from autowrap.version import version as autowrap_version
from autowrap.Code import Code

CodeDict = Dict[AnyStr, Code]

import logging as L

special_class_doc = ""


def namespace_handler(ns):
    return ns


try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


def augment_arg_names(method):
    """replaces missing arg_names with "in_%d" % i, where i is the position
    number of the arg"""
    return [
        (t, n if (n and n != "self") else "in_%d" % i)
        for i, (n, t) in enumerate(method.arguments)
    ]


def fixed_include_dirs(include_boost: bool) -> List[AnyStr]:
    import pkg_resources

    boost = pkg_resources.resource_filename("autowrap", "data_files/boost")
    data = pkg_resources.resource_filename("autowrap", "data_files")
    autowrap_internal = pkg_resources.resource_filename(
        "autowrap", "data_files/autowrap"
    )

    if not include_boost:
        return [autowrap_internal]
    else:
        return [boost, data, autowrap_internal]


class CodeGenerator(object):
    """
    This is the main Code Generator.

    Its main entry function is "create_pyx_file" which generates the pyx file
    from the input (given in the initialization).

    The actual conversion of input/output arguments is done in the
    ConversionProviders for each argument type.
    """

    pxd_dir: Optional[AnyStr]
    manual_code: Dict[str, Code]
    extra_cimports: Collection[str]
    include_shared_ptr: str
    include_refholder: bool
    include_numpy: bool
    add_relative: bool

    target_path: AnyStr
    target_pxd_path: AnyStr
    target_pyi_path: AnyStr
    target_dir: AnyStr

    write_pxd: bool
    resolved: List[ResolvedDecl]

    all_decl: Dict[AnyStr, Dict[AnyStr, ResolvedDecl]]
    all_typedefs: List[ResolvedTypeDef]
    all_enums: List[ResolvedEnum]
    all_functions: List[ResolvedFunction]
    all_classes: List[ResolvedClass]
    all_resolved: List[ResolvedDecl]

    cr: ConverterRegistry

    top_level_code: List[Code]
    top_level_pyx_code: List[Code]
    enum_codes: Dict[AnyStr, Code]
    class_codes: Dict[AnyStr, Code]
    class_codes_extra: Dict[AnyStr, List[Code]]
    class_pxd_codes: Dict[AnyStr, Code]
    top_level_typestub_code: List[Code]
    typestub_codes: Dict[AnyStr, Code]
    wrapped_enums_cnt: int
    wrapped_classes_cnt: int
    wrapped_methods_cnt: int

    def __init__(
        self,
        resolved,
        instance_mapping,
        pyx_target_path=None,
        manual_code=None,
        extra_cimports=None,
        all_decl=None,
        add_relative=False,
        shared_ptr="boost",
    ):

        self.pxd_dir = None
        if all_decl is None:
            all_decl = dict()
        if manual_code is None:
            manual_code = dict()

        self.manual_code: Dict[str, Code] = manual_code
        self.extra_cimports: Collection[str] = extra_cimports
        self.include_shared_ptr: str = shared_ptr
        self.include_refholder: bool = True
        self.include_numpy: bool = False
        self.add_relative: bool = add_relative

        self.target_path: AnyStr = os.path.abspath(pyx_target_path)
        self.target_pxd_path: AnyStr = self.target_path.split(".pyx")[0] + ".pxd"
        self.target_pyi_path: AnyStr = self.target_path.split(".pyx")[0] + ".pyi"
        self.target_dir: AnyStr = os.path.dirname(self.target_path)

        # If true, we will write separate pxd and pyx files (need to ensure the
        # right code goes to header if we use pxd headers). Alternatively, we
        # will simply write a single pyx file.
        self.write_pxd: bool = len(all_decl) > 0

        # Step 1: get all declarations of current module and split by type
        classes = [d for d in resolved if isinstance(d, ResolvedClass)]
        enums = [d for d in resolved if isinstance(d, ResolvedEnum)]
        functions = [d for d in resolved if isinstance(d, ResolvedFunction)]
        typedefs = [d for d in resolved if isinstance(d, ResolvedTypeDef)]

        # Add them sorted by type, then by name
        self.resolved: List[ResolvedDecl] = []
        self.resolved.extend(sorted(typedefs, key=lambda d: d.name))
        self.resolved.extend(sorted(enums, key=lambda d: d.name))
        self.resolved.extend(sorted(functions, key=lambda d: d.name))
        self.resolved.extend(sorted(classes, key=lambda d: d.name))

        self.instance_mapping = instance_mapping
        for td in typedefs:
            self.instance_mapping[td.name] = td.type_

        # Step 2: get classes of complete project (includes other modules)
        self.all_decl = all_decl
        # If other external decls were passed:
        if len(all_decl) > 0:

            self.all_typedefs = []
            self.all_enums = []
            self.all_functions = []
            self.all_classes = []
            for modname, v in all_decl.items():
                self.all_classes.extend(
                    [d for d in v["decls"] if isinstance(d, ResolvedClass)]
                )
                self.all_enums.extend(
                    [d for d in v["decls"] if isinstance(d, ResolvedEnum)]
                )
                self.all_functions.extend(
                    [d for d in v["decls"] if isinstance(d, ResolvedFunction)]
                )
                self.all_typedefs.extend(
                    [d for d in v["decls"] if isinstance(d, ResolvedTypeDef)]
                )

            self.all_resolved = []
            self.all_resolved.extend(sorted(self.all_typedefs, key=lambda d: d.name))
            self.all_resolved.extend(sorted(self.all_enums, key=lambda d: d.name))
            self.all_resolved.extend(sorted(self.all_functions, key=lambda d: d.name))
            self.all_resolved.extend(sorted(self.all_classes, key=lambda d: d.name))
        else:
            self.all_typedefs = typedefs
            self.all_enums = enums
            self.all_functions = functions
            self.all_classes = classes
            self.all_resolved = self.resolved

        # Register using all classes so that we know about the complete project
        self.cr: ConverterRegistry = setup_converter_registry(
            self.all_classes, self.all_enums, instance_mapping
        )

        self.top_level_code: List[Code] = []
        self.top_level_pyx_code: List[Code] = []
        self.enum_codes: Dict[AnyStr, Code] = defaultdict(lambda: Code())
        self.class_codes: Dict[AnyStr, Code] = defaultdict(lambda: Code())
        self.class_codes_extra: Dict[AnyStr, List[Code]] = defaultdict(list)
        self.class_pxd_codes: Dict[AnyStr, Code] = defaultdict(lambda: Code())
        self.top_level_typestub_code: List[Code] = []
        self.typestub_codes: Dict[AnyStr, Code] = defaultdict(lambda: Code())
        self.wrapped_enums_cnt: int = 0
        self.wrapped_classes_cnt: int = 0
        self.wrapped_methods_cnt: int = 0

    def get_include_dirs(self, include_boost: bool) -> List[AnyStr]:
        if self.pxd_dir is not None:
            return fixed_include_dirs(include_boost) + [self.pxd_dir]
        else:
            return fixed_include_dirs(include_boost)

    def setup_cimport_paths(self) -> None:
        """
        Adds the pxd_import_path attribute to all resolved decls and set self.pxd_dir
        """

        pxd_dirs = set()
        for resolved_decl in self.all_resolved:
            pxd_path = os.path.abspath(resolved_decl.cpp_decl.pxd_path)
            pxd_dir = os.path.dirname(pxd_path)
            pxd_dirs.add(pxd_dir)
            pxd_file = os.path.basename(pxd_path)
            resolved_decl.pxd_import_path, __ = os.path.splitext(pxd_file)

        # TODO allow different dirs relative to a root maybe
        assert len(pxd_dirs) <= 1, "pxd files must be located in same directory"

        self.pxd_dir = pxd_dirs.pop() if pxd_dirs else None

    def create_pyx_file(self, debug: bool = False) -> None:
        """This creates the actual Cython code

        It calls create_wrapper_for_class, create_wrapper_for_enum and
        create_wrapper_for_free_function respectively to create the code for
        all classes, enums and free functions.
        """
        self.setup_cimport_paths()
        self.create_cimports()
        self.create_foreign_cimports()
        self.create_includes()

        def create_for(
            clazz: Type[ResolvedDecl],
            method: Callable[
                [ResolvedDecl, Union[CodeDict, Tuple[CodeDict, CodeDict]]], None
            ],
            codez: Union[CodeDict, Tuple[CodeDict, CodeDict]],
        ):
            for resolved in self.resolved:
                if resolved.wrap_ignore:
                    continue
                if isinstance(resolved, clazz):
                    method(resolved, codez)

        # first wrap classes, so that self.class_codes[..] is initialized
        # for attaching enums or static functions
        create_for(ResolvedClass, self.create_wrapper_for_class, self.class_codes)
        create_for(
            ResolvedEnum,
            self.create_wrapper_for_enum,
            (self.enum_codes, self.typestub_codes),
        )
        create_for(
            ResolvedFunction, self.create_wrapper_for_free_function, self.class_codes
        )

        # resolve extra
        for clz, codes in self.class_codes_extra.items():
            if clz not in self.class_codes:
                raise Exception(
                    "Cannot attach to class",
                    clz,
                    "make sure all wrap-attach are in the same file as parent class",
                )
            for c in codes:
                self.class_codes[clz].add(c)

        # Create code for the pyx file
        if self.write_pxd:
            pyx_code = self.create_default_cimports().render()
            pyx_code += "\n".join(ci.render() for ci in self.top_level_pyx_code)
        else:
            pyx_code = "\n".join(ci.render() for ci in self.top_level_code)
            pyx_code += "\n".join(ci.render() for ci in self.top_level_pyx_code)

        pyx_code += " \n"
        names = set()
        # Write enum codes first, since for scoped enums, this contains python classes
        # that need to be present before usage.
        for n, c in self.enum_codes.items():
            pyx_code += c.render()
            pyx_code += " \n"
            names.add(n)
        for n, c in self.class_codes.items():
            pyx_code += c.render()
            pyx_code += " \n"
            names.add(n)

        # manual code which does not extend wrapped classes:
        for name, c in self.manual_code.items():
            if name not in names:
                pyx_code += c.render()
            pyx_code += " \n"

        # Create code for the pxd file
        pxd_code = "\n".join(ci.render() for ci in self.top_level_code)
        pxd_code += " \n"
        for n, c in self.class_pxd_codes.items():
            pxd_code += c.render()
            pxd_code += " \n"

        pyi_code = "from typing import overload, Any, List, Dict, Tuple, Set, Sequence, Union \n\n"
        pyi_code += "from enum import Enum as _PyEnum\n\n"
        pyi_code += "\n".join(ci.render() for ci in self.top_level_typestub_code)
        pyi_code += "\n\n"
        for n, c in self.typestub_codes.items():
            pyi_code += c.render()
            pyi_code += " \n\n"

        with open(self.target_pyi_path, "w") as fp:
            fp.write(pyi_code)

        if debug:
            if self.write_pxd:
                print("PXD:")
            else:
                print("PXD (will not be written):")
            print(pxd_code)
            print("PYX:")
            print(pyx_code)
        with open(self.target_path, "w") as fp:
            fp.write(pyx_code)

        if self.write_pxd:
            with open(self.target_pxd_path, "w") as fp:
                fp.write(pxd_code)

    def filterout_iterators(self, methods):
        def parse(anno):
            m = re.match(r"(\S+)\((\S+)\)", anno)
            assert m is not None, "invalid iter annotation"
            newname, type_str = m.groups()
            return newname, CppType.from_string(type_str)

        begin_iterators = dict()
        end_iterators = dict()
        non_iter_methods = defaultdict(list)
        for name, mi in methods.items():
            for method in mi:
                annotations = method.cpp_decl.annotations
                if "wrap-iter-begin" in annotations:
                    py_name, res_type = parse(annotations["wrap-iter-begin"])
                    begin_iterators[py_name] = (method, res_type)
                elif "wrap-iter-end" in annotations:
                    py_name, res_type = parse(annotations["wrap-iter-end"])
                    end_iterators[py_name] = (method, res_type)
                else:
                    non_iter_methods[name].append(method)

        begin_names = set(begin_iterators.keys())
        end_names = set(end_iterators.keys())
        common_names = begin_names & end_names
        if begin_names != end_names:
            # TODO: test this case
            raise Exception("iter declarations not balanced")

        for py_name in common_names:
            __, res_type_begin = begin_iterators[py_name]
            __, res_type_end = end_iterators[py_name]
            assert res_type_begin == res_type_end, "iter value types do not match"

        begin_methods = dict((n, m) for n, (m, __) in begin_iterators.items())
        end_methods = dict((n, m) for n, (m, __) in end_iterators.items())
        res_types = dict((n, t) for n, (__, t) in end_iterators.items())

        iterators = dict()
        for n in common_names:
            iterators[n] = (begin_methods[n], end_methods[n], res_types[n])

        return iterators, non_iter_methods

    def create_wrapper_for_enum(
        self, decl: ResolvedEnum, out_codes_and_stub_codes: Tuple[CodeDict, CodeDict]
    ) -> None:
        """Create the wrapped code and stubs for an enum
        :param decl: The enum to be wrapped
        :param out_codes_and_stub_codes: The running pyx code and pyi stub code dicts to be filled
        :return: None
        """
        out_codes, out_stub_codes = out_codes_and_stub_codes
        self.wrapped_enums_cnt += 1
        if decl.cpp_decl.annotations.get("wrap-attach"):
            if not decl.scoped:
                name = "__" + decl.name
            else:
                name = "_Py" + decl.name  # __ prefix in python are private members
        else:
            name = decl.name

        doc = decl.cpp_decl.annotations.get("wrap-doc", None)
        if doc is not None:
            doc = '"""\n    ' + doc.render(indent=4) + '\n    """'

        L.info("create wrapper for enum %s" % name)
        code = Code()
        stub_code = Code()
        enum_pxd_code = Code()

        enum_pxd_code.add(
            """
                   |
                   |cdef class $name:
                   |  pass
                 """,
            name=name,
        )

        if not decl.scoped:
            code.add(
                """
                       |
                       |cdef class $name:
                       |    $doc
                     """,
                name=name,
                doc=doc,
            )
            stub_code.add(
                """
                       |
                       |class $name:
                       |    $doc
                     """,
                name=name,
                doc=doc,
            )
        else:  # for scoped enums we use the python enum class
            # TODO check if we somehow can use an extension class (cdef or cpdef). Should be faster.
            #  see https://groups.google.com/g/cython-users/c/PpwhyIzqGyA
            #  and https://github.com/cython/cython/pull/3221
            code.add(
                """
                       |
                       |class $name(_PyEnum):
                       |    $doc
                     """,
                name=name,
                doc=doc,
            )

            stub_code.add(
                """
                       |
                       |class $name(_PyEnum):
                       |    $doc
                     """,
                name=name,
                doc=doc,
            )

        for (optname, value) in decl.items:
            code.add("    $name = $value", name=optname, value=value)
            stub_code.add("    $name : int", name=optname, value=value)

        # Add mapping of int (enum) to the value of the enum (as string)
        if not decl.scoped:
            code.add(
                """
                    |
                    |    def getMapping(self):
                    |        return dict([ (v, k) for k, v in self.__class__.__dict__.items()
                    + if isinstance(v, int) ])"""
            )
            stub_code.add(
                """
                        |
                        |    def getMapping(self) -> Dict[int, str]:
                        |       ...
                        """
            )

        # TODO check if we need to add an import or custom type to type stubs for enums
        out_codes[decl.name] = code
        out_stub_codes[decl.name] = stub_code
        self.class_pxd_codes[decl.name] = enum_pxd_code

        # Add an extra member to previously declared class code snippets
        for class_name in decl.cpp_decl.annotations.get("wrap-attach", []):
            code = Code()
            stub_code = Code()
            display_name = decl.cpp_decl.annotations.get("wrap-as", [decl.name])[0]
            code.add("%s = %s" % (display_name, name))
            stub_code.add("%s : %s" % (display_name, name))
            self.typestub_codes[class_name].add(stub_code)
            self.class_codes[class_name].add(code)

    def create_wrapper_for_class(
        self, r_class: ResolvedClass, out_codes: CodeDict
    ) -> None:
        """Create Cython code for a single class

        Note that the cdef class definition and the member variables go into
        the .pxd file while the Python-level implementation goes into the .pyx
        file. This allows us to cimport these classes later across modules.

        """
        self.wrapped_classes_cnt += 1
        self.wrapped_methods_cnt += len(r_class.methods)
        cname = r_class.name
        if r_class.cpp_decl.annotations.get("wrap-attach"):
            pyname = "__" + r_class.name
        else:
            pyname = cname

        L.info("create wrapper for class %s" % cname)
        cy_type = self.cr.cython_type(cname)

        # Attempt to derive sane class name and namespace
        cpp_name = str(cy_type)
        namespace = namespace_handler(r_class.ns)
        if cpp_name.startswith("_"):
            cpp_name = cpp_name[1:]

        class_pxd_code = Code()
        class_code = Code()
        typestub_code = Code()

        # Class documentation (multi-line)
        docstring = "Cython implementation of %s\n" % cy_type
        docstring += special_class_doc % locals()
        if r_class.cpp_decl.annotations.get("wrap-inherits", "") != "":
            docstring += (
                "      -- Inherits from %s\n"
                % r_class.cpp_decl.annotations.get("wrap-inherits", "")
            )

        extra_doc = r_class.cpp_decl.annotations.get("wrap-doc", None)
        if extra_doc is not None:
            docstring += "\n"
            docstring += extra_doc.render(indent=4)

        self.typestub_codes[cname] = typestub_code
        typestub_code.add(
            """
                        |
                        |class $pyname:
                        |    \"\"\"
                        |    $docstring
                        |    \"\"\"
                        """,
            locals(),
        )

        if r_class.methods:
            shared_ptr_inst = "cdef shared_ptr[%s] inst" % cy_type

            if (
                len(r_class.wrap_manual_memory) != 0
                and r_class.wrap_manual_memory[0] != "__old-model"
            ):
                shared_ptr_inst = r_class.wrap_manual_memory[0]
            if self.write_pxd:
                class_pxd_code.add(
                    """
                                |
                                |cdef class $pyname:
                                |    \"\"\"
                                |    $docstring
                                |    \"\"\"
                                |    $shared_ptr_inst
                                |
                                """,
                    locals(),
                )

                # do not implement in pyx file, only in pxd file
                shared_ptr_inst = "# see .pxd file for cdef of inst ptr"

            if len(r_class.wrap_manual_memory) != 0:
                class_code.add(
                    """
                                |
                                |cdef class $pyname:
                                |    \"\"\"
                                |    $docstring
                                |    \"\"\"
                                |
                                """,
                    locals(),
                )
            else:
                class_code.add(
                    """
                                |
                                |cdef class $pyname:
                                |    \"\"\"
                                |    $docstring
                                |    \"\"\"
                                |
                                |    $shared_ptr_inst
                                |
                                |    def __dealloc__(self):
                                |         self.inst.reset()
                                |
                                """,
                    locals(),
                )
        else:
            # Deal with pure structs (no methods)
            class_pxd_code.add(
                """
                            |
                            |cdef class $pyname:
                            |    \"\"\"
                            |    $docstring
                            |    \"\"\"
                            |
                            |    pass
                            |
                            """,
                locals(),
            )
            class_code.add(
                """
                            |
                            |cdef class $pyname:
                            |    \"\"\"
                            |    $docstring
                            |    \"\"\"
                            |
                            """,
                locals(),
            )

        if len(r_class.wrap_hash) != 0:
            class_code.add(
                """
                            |
                            |    def __hash__(self):
                            |      # The only required property is that objects which compare equal have
                            |      # the same hash value:
                            |      return hash(deref(self.inst.get()).%s )
                            |
                            """
                % r_class.wrap_hash[0],
                locals(),
            )

        if "wrap-buffer-protocol" in r_class.cpp_decl.annotations:
            buffer_parts = r_class.cpp_decl.annotations["wrap-buffer-protocol"][
                0
            ].split(",")
            buffer_sourcer = buffer_parts[0]
            buffer_type = buffer_parts[1]
            buffer_sizer = buffer_parts[2]
            buffer_code = {
                "char": "c",
                "signed char": "b",
                "unsigned char": "B",
                "bool": "?",
                "short": "h",
                "unsigned short": "H",
                "int": "i",
                "unsigned int": "I",
                "long": "l",
                "unsigned long": "L",
                "long long": "q",
                "unsigned long long": "Q",
                "ssize_t": "n",
                "size_t": "N",
                "float": "f",
                "double": "d",
                "char[]": "s",
                "char[]": "p",
                "void*": "P",
            }[buffer_type]
            class_code.add(
                """
                                |
                                |    cdef Py_ssize_t _buffer_protocol_shape[1]
                                |    cdef Py_ssize_t _buffer_protocol_stride[1]
                                |
                                |    def __getbuffer__(self, Py_buffer *buffer, int flags):
                                |        cdef size_t size = self.inst.get().{buffer_sizer}
                                |        # Prepare flat buffer for exporting
                                |        self._buffer_protocol_shape[0] = size
                                |        self._buffer_protocol_stride[0] = <Py_ssize_t>sizeof({buffer_type})
                                |
                                |        buffer.buf = <char *>(self.inst.get().{buffer_sourcer})
                                |        buffer.format = '{buffer_code}'
                                |        buffer.internal = NULL
                                |        buffer.itemsize = sizeof({buffer_type})
                                |        buffer.len = size
                                |        buffer.ndim = 1
                                |        buffer.obj = self
                                |        buffer.readonly = False
                                |        buffer.shape = self._buffer_protocol_shape
                                |        buffer.strides = self._buffer_protocol_stride
                                |        buffer.suboffsets = NULL
                                |
                                |    def __releasebuffer__(self, Py_buffer *buffer):
                                |        pass
                                |
                                """.format(
                    **locals()
                )
            )

        self.class_pxd_codes[cname] = class_pxd_code
        out_codes[cname] = class_code

        cons_created = False

        for attribute in r_class.attributes:
            if not attribute.wrap_ignore:
                try:
                    pyx_code, stub_code = self._create_wrapper_for_attribute(attribute)
                    class_code.add(pyx_code)
                    typestub_code.add(stub_code)
                except Exception:
                    raise Exception(
                        "Failed to create wrapper for attribute "
                        + attribute.cpp_decl.name
                        + " in: "
                        + attribute.cpp_decl.pxd_path
                    )

        iterators, non_iter_methods = self.filterout_iterators(r_class.methods)

        for (name, methods) in non_iter_methods.items():
            if name == r_class.name:
                codes, stub_code = self.create_wrapper_for_constructor(r_class, methods)
                cons_created = True
            else:
                codes, stub_code = self.create_wrapper_for_method(
                    r_class, name, methods
                )
            typestub_code.add(stub_code)
            for ci in codes:
                class_code.add(ci)

        has_ops = dict()
        for ops in ["==", "!=", "<", "<=", ">", ">="]:
            has_op = ("operator%s" % ops) in non_iter_methods
            has_ops[ops] = has_op

        if any(v for v in has_ops.values()):
            code, stubs = self.create_special_cmp_method(r_class, has_ops)
            class_code.add(code)
            typestub_code.add(stubs)

        codes, stub_codes = self._create_iter_methods(
            iterators, r_class.instance_map, r_class.local_map
        )
        for ci, si in zip(codes, stub_codes):
            class_code.add(ci)
            typestub_code.add(si)

        extra_methods_code = self.manual_code.get(cname)
        if extra_methods_code:
            class_code.add(extra_methods_code)

        for class_name in r_class.cpp_decl.annotations.get("wrap-attach", []):
            code = Code()
            display_name = r_class.cpp_decl.annotations.get("wrap-as", [r_class.name])[
                0
            ]
            code.add("%s = %s" % (display_name, "__" + r_class.name))
            tmp = self.class_codes_extra.get(class_name, [])
            tmp.append(code)
            self.class_codes_extra[class_name] = tmp

    def _create_iter_methods(self, iterators, instance_mapping, local_mapping):
        """
        Create Iterator methods using the Python yield keyword
        TODO: parse doc string. Difficult, since annotation of an iterator function is divided into
          two directives: wrap-iter-begin and wrap-iter-end
        TODO: allow iterators that decrease? Not urgent since it usually can be modelled by reverse_iterators, see test
        """
        codes = []
        stub_codes = []
        for name, (begin_decl, end_decl, res_type) in iterators.items():
            L.info("   create wrapper for iter %s" % name)
            meth_code = Code()
            stub_code = Code()
            begin_name = begin_decl.name
            end_name = end_decl.name

            # TODO: this step is duplicated from DeclResolver.py
            # can we combine both maps to one single map ?
            res_type = res_type.transformed(local_mapping)
            res_type = res_type.inv_transformed(instance_mapping)

            cy_type = self.cr.cython_type(res_type)
            base_type = res_type.base_type

            meth_code.add(
                """
                            |
                            |def $name(self):
                            |    it = self.inst.get().$begin_name()
                            |    cdef $base_type out
                            |    while it != self.inst.get().$end_name():
                            |        out = $base_type.__new__($base_type)
                            |        out.inst =
                            + shared_ptr[$cy_type](new $cy_type(deref(it)))
                            |        yield out
                            |        inc(it)
                            """,
                locals(),
            )
            stub_code.add(
                """
                            |
                            |def $name(self) -> $base_type:
                            |   ...
                            """,
                locals(),
            )
            codes.append(meth_code)
            stub_codes.append(stub_code)
        return codes, stub_codes

    def _create_overloaded_method_decl(
        self, py_name, dispatched_m_names, methods, use_return, use_kwargs=False
    ):

        L.info("   create wrapper decl for overloaded method %s" % py_name)

        method_code = Code()
        typestub_code = Code()
        kwargs = ""
        if use_kwargs:
            kwargs = ", **kwargs"

        docstrings = Code()
        signatures = []
        for method in methods:
            ## TODO refactor this part as something like getTypingSignature or getTypingSignatureParts
            ##  or maybe save them for the after-the-next for-loop that generates them again
            args = augment_arg_names(method)
            py_typing_signature_parts = []
            for arg_num, (t, n) in enumerate(args):
                converter = self.cr.get(t)
                py_typing_type = converter.matching_python_type_full(t)
                py_typing_signature_parts.append("%s: %s " % (n, py_typing_type))
            args_typestub_str = ", ".join(py_typing_signature_parts)
            return_type = self.cr.get(method.result_type).matching_python_type_full(
                method.result_type
            )

            if return_type:
                return_type = "-> " + return_type
            else:
                return_type = ""

            # Add autodoc docstring signatures first: https://github.com/sphinx-doc/sphinx/pull/7748
            sig = f"{py_name}(self, {args_typestub_str}) {return_type}"
            signatures.append(sig)
            #docstrings.add(sig)

        #docstrings.add("")

        for method, sig in zip(methods, signatures):
            docstrings.add(".. rubric:: Overload:")
            docstrings.add(".. py:function:: %s" % sig)
            docstrings.add("  :noindex:")
            docstrings.add("")
            # Now add Cython signatures with additional description for each overload (if available)
            extra_doc = method.cpp_decl.annotations.get("wrap-doc", None)
            if extra_doc is not None:
                docstrings.extend(extra_doc)
                docstrings.add("")

        docstring_as_str = docstrings.render(indent=8)
        method_code.add(
            """
                          |
                          |def $py_name(self, *args $kwargs):
                          |    \"\"\"\n$docstring_as_str
                          |    
                          |    \"\"\"
                        """,
            locals(),
        )

        first_iteration = True

        for (dispatched_m_name, method, sig) in zip(
            dispatched_m_names, methods, signatures
        ):
            args = augment_arg_names(method)
            return_type = self.cr.get(method.result_type).matching_python_type_full(
                method.result_type
            )

            if return_type:
                return_type = "-> " + return_type + ":"
            else:
                return_type = ":"

            # Prepare docstring for typestubs
            docstring = "Cython signature: %s" % method
            extra_doc = method.cpp_decl.annotations.get("wrap-doc", None)
            if extra_doc is not None:
                docstring += "\n" + extra_doc.render(indent=8)

            typestub_code.add(
                """
                          |
                          |@overload
                          |def $sig:
                          |    \"\"\"
                          |    $docstring
                          |    \"\"\"
                          |    ...
                        """,
                locals(),
            )

            if not args:
                check_expr = "not args"

                # Special case for empty constructors with a pass
                if method.cpp_decl.annotations.get("wrap-pass-constructor", False):
                    assert use_kwargs, (
                        "Cannot use wrap-pass-constructor without setting kwargs (e.g. outside a "
                        "constructor) "
                    )
                    check_expr = 'kwargs.get("__createUnsafeObject__") is True'

            else:
                tns = [(t, "args[%d]" % i) for i, (t, n) in enumerate(args)]
                checks = ["len(args)==%d" % len(tns)]
                checks += [self.cr.get(t).type_check_expression(t, n) for (t, n) in tns]
                check_expr = " and ".join("(%s)" % c for c in checks)
            return_ = "return" if use_return else ""
            if_elif = "if" if first_iteration else "elif"
            method_code.add(
                """
                            |    $if_elif $check_expr:
                            |        $return_ self.$dispatched_m_name(*args)
                            """,
                locals(),
            )
            first_iteration = False

        method_code.add(
            """    else:
                        |           raise
                        + Exception('can not handle type of %s' % (args,))"""
        )
        return method_code, typestub_code

    def create_wrapper_for_method(self, cdcl, py_name, methods):

        if py_name.startswith("operator"):
            __, __, op = py_name.partition("operator")
            if op in ["!=", "==", "<", "<=", ">", ">="]:
                # handled in create_wrapper_for_class, as one has to collect
                # these
                return [], Code()
            elif op == "()":
                codes = self.create_cast_methods(methods)
                return codes, Code()
            elif op == "[]":
                assert len(methods) == 1, "overloaded operator[] not supported"
                code_get, typestub_get = self.create_special_getitem_method(methods[0])
                code_set, typestub_set = self.create_special_setitem_method(methods[0])
                typestub_get.extend(typestub_set)
                return [code_get, code_set], typestub_get
            elif op == "+":
                assert len(methods) == 1, "overloaded operator+ not supported"
                code, stubs = self.create_special_op_method(
                    "add", "+", cdcl, methods[0]
                )
                return [code], stubs
            elif op == "-":
                assert len(methods) == 1, "overloaded operator- not supported"
                code, stubs = self.create_special_op_method(
                    "sub", "-", cdcl, methods[0]
                )
                return [code], stubs
            elif op == "*":
                assert len(methods) == 1, "overloaded operator* not supported"
                code, stubs = self.create_special_op_method(
                    "mul", "*", cdcl, methods[0]
                )
                return [code], stubs
            elif op == "/":
                assert len(methods) == 1, "overloaded operator/ not supported"
                code, stubs = self.create_special_op_method(
                    "truediv", "/", cdcl, methods[0]
                )
                return [code], stubs
            elif op == "<<":
                assert len(methods) == 1, "overloaded operator<< not supported"
                code, stubs = self.create_special_op_method(
                    "lshift", "<<", cdcl, methods[0]
                )
                return [code], stubs
            elif op == ">>":
                assert len(methods) == 1, "overloaded operator>> not supported"
                code, stubs = self.create_special_op_method(
                    "rshift", ">>", cdcl, methods[0]
                )
                return [code], stubs
            elif op == "%":
                assert len(methods) == 1, "overloaded operator% no supported"
                code, stubs = self.create_special_op_method(
                    "mod", "%", cdcl, methods[0]
                )
                return [code], stubs
            elif op == "+=":
                assert len(methods) == 1, "overloaded operator+= not supported"
                code, stubs = self.create_special_iop_method(
                    "iadd", "+=", cdcl, methods[0]
                )
                return [code], stubs
            elif op == "-=":
                assert len(methods) == 1, "overloaded operator-= not supported"
                code, stubs = self.create_special_iop_method(
                    "isub", "-=", cdcl, methods[0]
                )
                return [code], stubs
            elif op == "*=":
                assert len(methods) == 1, "overloaded operator*= not supported"
                code, stubs = self.create_special_iop_method(
                    "imul", "*=", cdcl, methods[0]
                )
                return [code], stubs
            elif op == "/=":
                assert len(methods) == 1, "overloaded operator/= not supported"
                code, stubs = self.create_special_iop_method(
                    "itruediv", "/=", cdcl, methods[0]
                )
                return [code], stubs
            elif op == "%=":
                assert len(methods) == 1, "overloaded operator%= not supported"
                code, stubs = self.create_special_iop_method(
                    "imod", "%=", cdcl, methods[0]
                )
                return [code], stubs
            elif op == "<<=":
                assert len(methods) == 1, "overloaded operator<<= not supported"
                code, stubs = self.create_special_iop_method(
                    "ilshift", "<<=", cdcl, methods[0]
                )
                return [code], stubs
            elif op == ">>=":
                assert len(methods) == 1, "overloaded operator>>= not supported"
                code, stubs = self.create_special_iop_method(
                    "irshift", ">>=", cdcl, methods[0]
                )
                return [code], stubs

        if len(methods) == 1:
            code, typestubs = self.create_wrapper_for_nonoverloaded_method(
                cdcl, py_name, methods[0]
            )
            return [code], typestubs
        else:
            # TODO: what happens if two distinct c++ types as float, double
            #   map to the same python type ??
            #    -> 1) detection
            #    -> 2) force method renaming
            codes = []
            dispatched_m_names = []
            for (i, method) in enumerate(methods):
                dispatched_m_name = "_%s_%d" % (py_name, i)
                dispatched_m_names.append(dispatched_m_name)
                # We should not need typestubs for the dispatched parent method
                code, _ = self.create_wrapper_for_nonoverloaded_method(
                    cdcl, dispatched_m_name, method
                )
                codes.append(code)

            code, typestubs = self._create_overloaded_method_decl(
                py_name, dispatched_m_names, methods, True
            )
            codes.append(code)
            return codes, typestubs

    def _create_fun_decl_and_input_conversion(
        self, code, py_name, method, is_free_fun=False
    ):
        """Creates the function declarations and the input conversion to C++
        and the output conversion back to Python.

        The input conversion is directly added to the "code" object while the
        conversion back to Python is returned as "cleanups".
        """
        args = augment_arg_names(method)

        # Step 0: collect conversion data for input args and call
        # input_conversion for more sophisticated conversion code (e.g. std::vector<Obj>)
        py_signature_parts = []
        py_typing_signature_parts = []
        input_conversion_codes = []
        cleanups = []
        call_args = []
        checks = []
        in_types = []
        for arg_num, (t, n) in enumerate(args):
            # get new ConversionProvider using the converter registry
            converter = self.cr.get(t)
            converter.cr = self.cr
            py_type = converter.matching_python_type(t)
            py_typing_type = converter.matching_python_type_full(t)
            conv_code, call_as, cleanup = converter.input_conversion(t, n, arg_num)
            py_signature_parts.append("%s %s " % (py_type, n))
            py_typing_signature_parts.append("%s: %s " % (n, py_typing_type))
            input_conversion_codes.append(conv_code)
            cleanups.append(cleanup)
            call_args.append(call_as)
            in_types.append(t)
            checks.append((n, converter.type_check_expression(t, n)))

        # Step 1: create method decl statement
        if not is_free_fun and not method.is_static:
            py_signature_parts.insert(0, "self")
            py_typing_signature_parts.insert(0, "self")

        py_signature = ", ".join(py_signature_parts)
        py_typing_signature = ", ".join(py_typing_signature_parts)
        return_type = self.cr.get(method.result_type).matching_python_type_full(
            method.result_type
        )
        if return_type:
            return_type = "-> " + return_type
        else:
            return_type = ""

        # Prepare docstring
        docstring = f"{py_name}({py_typing_signature}) {return_type}"
        stubdocstring = "Cython signature: %s" % method

        extra_doc = method.cpp_decl.annotations.get("wrap-doc", None)
        if extra_doc is not None:
            docstring += "\n" + extra_doc.render(indent=8)
            stubdocstring += "\n" + extra_doc.render(indent=8)

        if method.is_static:
            code.add(
                """
                       |
                       |@staticmethod
                       |def $py_name($py_signature):
                       |    \"\"\"
                       |    $docstring
                       |    \"\"\"
                       """,
                locals(),
            )
        else:
            code.add(
                """
                       |
                       |def $py_name($py_signature):
                       |    \"\"\"
                       |    $docstring
                       |    \"\"\"
                       """,
                locals(),
            )

        stub = Code()

        if method.is_static:
            stub.add(
                """
                       |
                       |@staticmethod
                       |def $py_name($py_typing_signature) $return_type:
                       |    \"\"\"
                       |    $stubdocstring
                       |    \"\"\"
                       |    ...
                       """,
                locals(),
            )
        else:
            stub.add(
                """
                       |
                       |def $py_name($py_typing_signature) $return_type:
                       |    \"\"\"
                       |    $stubdocstring
                       |    \"\"\"
                       |    ...
                       """,
                locals(),
            )

        # Step 2a: create code which converts python input args to c++ args of
        # wrapped method
        for n, check in checks:
            code.add("    assert %s, 'arg %s wrong type'" % (check, n))
        # Step 2b: add any more sophisticated conversion code that was created
        # above:
        for conv_code in input_conversion_codes:
            code.add(conv_code)

        return call_args, cleanups, in_types, stub

    def _create_wrapper_for_attribute(self, attribute):
        code = Code()
        stubs = Code()
        name = attribute.name
        wrap_as = attribute.cpp_decl.annotations.get("wrap-as", name)
        if attribute.type_.is_const:
            wrap_constant = True
        else:
            wrap_constant = attribute.cpp_decl.annotations.get("wrap-constant", False)

        t = attribute.type_

        converter = self.cr.get(t)
        py_type = converter.matching_python_type(t)
        py_typing_type = converter.matching_python_type_full(t)
        conv_code, call_as, cleanup = converter.input_conversion(t, name, 0)

        code.add(
            """
            |
            |property $wrap_as:
            """,
            locals(),
        )

        stubs.add(
            """
                |
                |$name: $py_typing_type
                """,
            locals(),
        )

        if wrap_constant:
            code.add(
                """
                |    def __set__(self, $py_type $name):
                |       raise AttributeError("Cannot set constant")
                """,
                locals(),
            )

        else:
            code.add(
                """
                |    def __set__(self, $py_type $name):
                """,
                locals(),
            )

            # TODO: implement an add with indent level
            indented = Code()
            indented.add(conv_code)
            code.add(indented)

            code.add(
                """
                |        self.inst.get().$name = $call_as
                """,
                locals(),
            )
            indented = Code()

            if isinstance(cleanup, basestring):
                cleanup = "    %s" % cleanup

            indented.add(cleanup)
            code.add(indented)

        # For pointers and refs this should create code that creates a copy so returning is safe
        to_py_code = converter.output_conversion(t, "_r", "py_result")
        access_stmt = converter.call_method(t, "self.inst.get().%s" % name, False)

        cy_type = self.cr.cython_type(t)

        if isinstance(to_py_code, basestring):
            to_py_code = "    %s" % to_py_code

        if isinstance(access_stmt, basestring):
            access_stmt = "    %s" % access_stmt

        if t.is_ptr:
            # For pointer types, we need to guard against unsafe access
            code.add(
                """
                |
                |    def __get__(self):
                |        if self.inst.get().%s is NULL:
                |             raise Exception("Cannot access pointer that is NULL")
                """
                % name,
                locals(),
            )
        else:
            code.add(
                """
                |
                |    def __get__(self):
                """,
                locals(),
            )

        # increase indent:
        indented = Code()
        indented.add(access_stmt)
        indented.add(to_py_code)
        code.add(indented)
        code.add("        return py_result")
        return code, stubs

    def create_wrapper_for_nonoverloaded_method(self, cdcl, py_name, method):

        L.info("   create wrapper for %s ('%s')" % (py_name, method))
        meth_code = Code()

        (
            call_args,
            cleanups,
            in_types,
            stubs,
        ) = self._create_fun_decl_and_input_conversion(meth_code, py_name, method)

        # call wrapped method and convert result value back to python
        cpp_name = method.cpp_decl.name
        call_args_str = ", ".join(call_args)
        if method.is_static:
            cy_call_str = "%s.%s(%s)" % (
                str(self.cr.cython_type(cdcl.name)),
                cpp_name,
                call_args_str,
            )
        else:
            cy_call_str = "self.inst.get().%s(%s)" % (cpp_name, call_args_str)

        res_t = method.result_type
        out_converter = self.cr.get(res_t)
        full_call_stmt = out_converter.call_method(res_t, cy_call_str)

        if method.with_nogil:
            meth_code.add(
                """
              |    with nogil:
              """
            )
            indented = Code()
        else:
            indented = meth_code

        if isinstance(full_call_stmt, basestring):
            indented.add(
                """
                |    $full_call_stmt
                """,
                locals(),
            )
        else:
            indented.add(full_call_stmt)

        for cleanup in reversed(cleanups):
            if not cleanup:
                continue
            if isinstance(cleanup, basestring):
                cleanup = "    %s" % cleanup
            indented.add(cleanup)

        to_py_code = out_converter.output_conversion(res_t, "_r", "py_result")

        if to_py_code is not None:  # for non void return value

            if isinstance(to_py_code, basestring):
                to_py_code = "    %s" % to_py_code
            indented.add(to_py_code)
            indented.add("    return py_result")

        if method.with_nogil:
            meth_code.add(indented)

        return meth_code, stubs

    def create_wrapper_for_free_function(
        self, decl: ResolvedFunction, out_codes: CodeDict
    ) -> None:
        """
        Creates wrapping code for a free function
        :param decl: The ResolvedFunction decl to be wrapped
        :param out_codes: The running pyx code dict to be filled with the outcome
        :return: None
        """
        L.info("create wrapper for free function %s" % decl.name)
        self.wrapped_methods_cnt += 1
        static_clz = decl.cpp_decl.annotations.get("wrap-attach")
        if static_clz is None:
            code, typestub = self._create_wrapper_for_free_function(decl)
        else:
            code = Code()
            stub = Code()
            static_name = "__static_%s_%s" % (
                static_clz,
                decl.name,
            )  # name used to attach to class
            code.add("%s = %s" % (decl.name, static_name))
            stub.add(
                """
                    |
                    |%s: %s
                     """
                % (decl.name, static_name)
            )
            out_codes[static_clz].add(code)
            self.typestub_codes[static_clz].add(stub)
            orig_cpp_name = decl.cpp_decl.name  # original cpp name (not displayname)
            code, typestub = self._create_wrapper_for_free_function(
                decl, static_name, orig_cpp_name
            )

        self.top_level_pyx_code.append(code)
        self.top_level_typestub_code.append(typestub)

    def _create_wrapper_for_free_function(
        self, decl: ResolvedFunction, name=None, orig_cpp_name=None
    ):
        if name is None:
            name = decl.name

        # Need to the original cpp name and not the display name (which is for
        # Python only and C++ knows nothing about)
        if orig_cpp_name is None:
            orig_cpp_name = decl.name

        fun_code = Code()

        (
            call_args,
            cleanups,
            in_types,
            stubs,
        ) = self._create_fun_decl_and_input_conversion(
            fun_code, name, decl, is_free_fun=True
        )

        call_args_str = ", ".join(call_args)
        mangled_name = "_" + orig_cpp_name + "_" + decl.pxd_import_path
        cy_call_str = "%s(%s)" % (mangled_name, call_args_str)

        res_t = decl.result_type
        out_converter = self.cr.get(res_t)
        full_call_stmt = out_converter.call_method(res_t, cy_call_str)

        if isinstance(full_call_stmt, basestring):
            fun_code.add(
                """
                |    $full_call_stmt
                """,
                locals(),
            )
        else:
            fun_code.add(full_call_stmt)

        for cleanup in reversed(cleanups):
            if not cleanup:
                continue
            if isinstance(cleanup, basestring):
                cleanup = "    %s" % cleanup
            fun_code.add(cleanup)

        to_py_code = out_converter.output_conversion(res_t, "_r", "py_result")

        out_vars = ["py_result"]
        if to_py_code is not None:  # for non void return value

            if isinstance(to_py_code, basestring):
                to_py_code = "    %s" % to_py_code
            fun_code.add(to_py_code)
            fun_code.add("    return %s" % (", ".join(out_vars)))

        return fun_code, stubs

    def create_wrapper_for_constructor(self, class_decl, constructors):
        real_constructors = []
        codes = []
        typestub_code = Code()
        for cons in constructors:
            if len(cons.arguments) == 1:
                ((n, t),) = cons.arguments
                if t.base_type == class_decl.name and t.is_ref:
                    code = self.create_special_copy_method(class_decl)
                    codes.append(code)
            real_constructors.append(cons)

        if len(real_constructors) == 1:

            if real_constructors[0].cpp_decl.annotations.get(
                "wrap-pass-constructor", False
            ):
                # We have a single constructor that cannot be called (except
                # with the magic keyword), simply check the magic word
                cons_code = Code()
                cons_code.add(
                    """
                   |
                   |def __init__(self, *args, **kwargs):
                   |    if not kwargs.get("__createUnsafeObject__") is True:
                   |        raise Exception("Cannot call this constructor")
                    """,
                    locals(),
                )
                codes.append(cons_code)
                return codes, Code()

            code, typestub = self.create_wrapper_for_nonoverloaded_constructor(
                class_decl, "__init__", real_constructors[0]
            )
            codes.append(code)
            typestub_code.extend(typestub)

        else:
            dispatched_cons_names = []
            for (i, constructor) in enumerate(real_constructors):
                dispatched_cons_name = "_init_%d" % i
                dispatched_cons_names.append(dispatched_cons_name)
                # we don't need to generate the individual stubs here since
                # _create_overloaded_method_decl will do it with the correct name __init__
                # outside of the for loop
                code, _ = self.create_wrapper_for_nonoverloaded_constructor(
                    class_decl, dispatched_cons_name, constructor
                )
                codes.append(code)
            code, typestub = self._create_overloaded_method_decl(
                "__init__", dispatched_cons_names, constructors, False, True
            )
            codes.append(code)
            typestub_code.extend(typestub)
        return codes, typestub_code

    def create_wrapper_for_nonoverloaded_constructor(
        self, class_decl, py_name, cons_decl
    ):
        """py_name is the name for constructor, as we dispatch overloaded
        constructors in __init__() the name of the method calling the
        C++ constructor is variable and given by `py_name`.

        """
        L.info("   create wrapper for non overloaded constructor %s" % py_name)
        cons_code = Code()
        stub_code = Code()

        (
            call_args,
            cleanups,
            in_types,
            stubs,
        ) = self._create_fun_decl_and_input_conversion(cons_code, py_name, cons_decl)

        stub_code.extend(stubs)
        wrap_pass = cons_decl.cpp_decl.annotations.get("wrap-pass-constructor", False)
        if wrap_pass:
            cons_code.add("    pass")
            # TODO check if we should create stubs for a "passed" ctor
            return cons_code, Code()

        # create instance of wrapped class
        call_args_str = ", ".join(call_args)
        name = class_decl.name
        cy_type = self.cr.cython_type(name)
        cons_code.add(
            """    self.inst = shared_ptr[$cy_type](new $cy_type($call_args_str))""",
            locals(),
        )

        for cleanup in reversed(cleanups):
            if not cleanup:
                continue
            if isinstance(cleanup, basestring):
                cleanup = "    %s" % cleanup
            cons_code.add(cleanup)

        return cons_code, stub_code

    def create_special_op_method(
        self, pyname, symbol, cdcl: ResolvedClass, mdcl: ResolvedMethod
    ):
        L.info(f"   create wrapper for operator{symbol}")
        assert len(mdcl.arguments) == 1, f"operator{symbol} has wrong signature"
        ((__, t),) = mdcl.arguments
        name = cdcl.name
        assert (
            t.base_type == name
        ), f"can only apply operator{symbol} to object of same type"
        assert (
            mdcl.result_type.base_type == name
        ), f"can only return same type for operator{symbol}"
        cy_t = self.cr.cython_type(t)
        code = Code()
        # TODO use make_shared instead of new if C++11 available
        code.add(
            f"""
        |
        |def __{pyname}__({name} self, {name} other not None):
        |    cdef {cy_t} * this = self.inst.get()
        |    cdef {cy_t} * that = other.inst.get()
        |    cdef {cy_t} applied = deref(this) {symbol} deref(that)
        |    cdef {name} result = {name}.__new__({name})
        |    result.inst = shared_ptr[{cy_t}](new {cy_t}(applied))
        |    return result
        """
        )
        stubs = Code()
        stubs.add(
            f"""
        |
        |def __{pyname}__(self: {name}, other: {name}) -> {name}:
        |    ...
        """
        )

        return code, stubs

    def create_special_iop_method(self, pyname, symbol, cdcl, mdcl):
        L.info(f"   create wrapper for operator{symbol}")
        assert len(mdcl.arguments) == 1, f"operator{symbol} has wrong signature"
        ((__, t),) = mdcl.arguments
        name = cdcl.name
        assert (
            t.base_type == name
        ), f"can only apply operator{symbol} to object of same type"
        assert (
            mdcl.result_type.base_type == name
        ), f"can only return same type for operator{symbol}"
        cy_t = self.cr.cython_type(t)
        code = Code()
        code.add(
            f"""
        |
        |def __{pyname}__({name} self, {name} other not None):
        |    cdef {cy_t} * this = self.inst.get()
        |    cdef {cy_t} * that = other.inst.get()
        |    _{pyname}(this, that)
        |    return self
        """
        )

        stubs = Code()
        stubs.add(
            f"""
        |
        |def __{pyname}__(self: {name}, other: {name}) -> {name}:
        |    ...
        """
        )

        tl = Code()
        tl.add(
            f"""
                |cdef extern from "autowrap_tools.hpp":
                |    void _{pyname}({cy_t} *, {cy_t} *)
                """
        )

        self.top_level_code.append(tl)

        return code, stubs

    # TODO allow getitem for any key. Not just size_t and similar.
    def create_special_getitem_method(self, mdcl):
        L.info("   create get wrapper for operator[]")
        meth_code = Code()

        (
            (call_arg,),
            cleanups,
            (in_type,),
            stubs,
        ) = self._create_fun_decl_and_input_conversion(meth_code, "__getitem__", mdcl)

        meth_code.add(
            """
                     |    cdef long _idx = $call_arg
                     """,
            locals(),
        )

        if in_type.is_unsigned:
            meth_code.add(
                """
                        |    if _idx < 0:
                        |        raise IndexError("invalid index %d" % _idx)
                        """,
                locals(),
            )

        size_guard = mdcl.cpp_decl.annotations.get("wrap-upper-limit")
        if size_guard:
            meth_code.add(
                """
                     |    if _idx >= self.inst.get().$size_guard:
                     |        raise IndexError("invalid index %d" % _idx)
                     """,
                locals(),
            )

        # call wrapped method and convert result value back to python

        cy_call_str = "deref(self.inst.get())[%s]" % call_arg

        res_t = mdcl.result_type
        out_converter = self.cr.get(res_t)
        full_call_stmt = out_converter.call_method(res_t, cy_call_str)

        if isinstance(full_call_stmt, basestring):
            meth_code.add(
                """
                |    $full_call_stmt
                """,
                locals(),
            )
        else:
            meth_code.add(full_call_stmt)

        for cleanup in reversed(cleanups):
            if not cleanup:
                continue
            if isinstance(cleanup, basestring):
                cleanup = Code().add(cleanup)
            meth_code.add(cleanup)

        out_var = "py_result"
        to_py_code = out_converter.output_conversion(res_t, "_r", out_var)
        if to_py_code is not None:  # for non void return value

            if isinstance(to_py_code, basestring):
                to_py_code = "    %s" % to_py_code
            meth_code.add(to_py_code)
            meth_code.add("    return $out_var", locals())

        return meth_code, stubs

    # TODO allow setitem for any key. Not just size_t and similar.
    def create_special_setitem_method(self, mdcl):
        # Note: setting will only work with a ref signature
        #   Object operator[](size_t k)  -> only get is implemented
        #   Object& operator[](size_t k) -> get and set is implemented
        res_t = mdcl.result_type
        if not res_t.is_ref:
            L.info(
                "   skip set wrapper for operator[] since return value is not a reference"
            )
            return Code(), Code()

        res_t_base = res_t.base_type

        L.info("   create set wrapper for operator[]")
        out_converter = self.cr.get(res_t)
        res_t_typing = out_converter.matching_python_type_full(res_t)

        meth_code = Code()
        stub_code = Code()

        # Prepare docstring
        docstring = "Cython signature: %s" % mdcl
        extra_doc = mdcl.cpp_decl.annotations.get("wrap-doc", None)
        if extra_doc is not None:
            docstring += "\n" + extra_doc.render(indent=8)

        stub_code.add(
            """
                     |def __setitem__(self, key: int, value: $res_t_typing ) -> None:
                     |    \"\"\"$docstring\"\"\"
                     |    ...
                     """,
            locals(),
        )

        call_arg = "key"
        value_arg = "value"

        meth_code.add(
            """
                     |def __setitem__(self, key, $res_t_base value):
                     |    \"\"\"$docstring\"\"\"
                     |    assert isinstance(key, int), 'arg index wrong type'
                     |
                     |    cdef long _idx = $call_arg
                     |    if _idx < 0:
                     |        raise IndexError("invalid index %d" % _idx)
                     """,
            locals(),
        )

        size_guard = mdcl.cpp_decl.annotations.get("wrap-upper-limit")
        if size_guard:
            meth_code.add(
                """
                     |    if _idx >= self.inst.get().$size_guard:
                     |        raise IndexError("invalid index %d" % _idx)
                     """,
                locals(),
            )

        # Store the input argument as
        #  CppObject[ idx ] = value
        #
        cy_call_str = "deref(self.inst.get())[%s]" % call_arg
        code, call_as, cleanup = out_converter.input_conversion(res_t, value_arg, 0)
        meth_code.add(
            """
                 |    $cy_call_str = $call_as
                 """,
            locals(),
        )

        return meth_code, stub_code

    # TODO return generated stubs as well. Figure out if we can return a list of stubs
    def create_cast_methods(self, mdecls):
        py_names = []
        for mdcl in mdecls:
            name = mdcl.cpp_decl.annotations.get("wrap-cast")
            if name is None:
                raise Exception("need wrap-cast annotation for %s" % mdcl)
            if name in py_names:
                raise Exception("wrap-cast annotation not unique for %s" % mdcl)
            py_names.append(name)
        codes = []
        for (py_name, mdecl) in zip(py_names, mdecls):
            code = Code()
            res_t = mdecl.result_type
            cy_t = self.cr.cython_type(res_t)
            out_converter = self.cr.get(res_t)

            code.add(
                """
                     |
                     |def $py_name(self):""",
                locals(),
            )

            call_stmt = "<%s>(deref(self.inst.get()))" % cy_t
            full_call_stmt = out_converter.call_method(res_t, call_stmt)

            if isinstance(full_call_stmt, basestring):
                code.add(
                    """
                    |    $full_call_stmt
                    """,
                    locals(),
                )
            else:
                code.add(full_call_stmt)

            to_py_code = out_converter.output_conversion(res_t, "_r", "py_res")
            if isinstance(to_py_code, basestring):
                to_py_code = "    %s" % to_py_code
            code.add(to_py_code)
            code.add("""    return py_res""")
            codes.append(code)
        return codes

    def create_special_cmp_method(self, cdcl, ops):
        L.info("   create wrapper __richcmp__")
        meth_code = Code()
        stub_code = Code()

        name = cdcl.name
        op_code_map = {
            "<": 0,
            "==": 2,
            ">": 4,
            "<=": 1,
            "!=": 3,
            ">=": 5,
        }
        inv_op_code_map = dict((v, k) for (k, v) in op_code_map.items())

        implemented_op_codes = tuple(op_code_map[k] for (k, v) in ops.items() if v)
        meth_code.add(
            """
           |
           |def __richcmp__(self, other, op):
           |    if op not in $implemented_op_codes:
           |       op_str = $inv_op_code_map[op]
           |       raise NotImplementedError("Comparison operator %s not implemented" % op_str)
           |    if not isinstance(other, $name):
           |       raise NotImplementedError("Comparison currently only allowed with objects of the same type.
           + Use isinstance and define yourself.")
           |    cdef $name other_casted = other
           |    cdef $name self_casted = self
           """,
            locals(),
        )
        stub_code.add(
            """
           |
           |def __richcmp__(self, other: $name, op: int) -> Any:
           |    ...
           """,
            locals(),
        )

        for op in implemented_op_codes:
            op_sign = inv_op_code_map[op]
            meth_code.add(
                """    if op==$op:
                            |        return deref(self_casted.inst.get())
                            + $op_sign deref(other_casted.inst.get())""",
                locals(),
            )
        return meth_code, stub_code

    def create_special_copy_method(self, class_decl):
        L.info("   create wrapper __copy__")
        meth_code = Code()
        name = class_decl.name
        cy_type = self.cr.cython_type(name)
        meth_code.add(
            """
                        |
                        |def __copy__(self):
                        |   cdef $name rv = $name.__new__($name)
                        |   rv.inst = shared_ptr[$cy_type](new $cy_type(deref(self.inst.get())))
                        |   return rv
                        """,
            locals(),
        )
        meth_code.add(
            """
                        |
                        |def __deepcopy__(self, memo):
                        |   cdef $name rv = $name.__new__($name)
                        |   rv.inst = shared_ptr[$cy_type](new $cy_type(deref(self.inst.get())))
                        |   return rv
                        """,
            locals(),
        )
        return meth_code

    def create_foreign_cimports(self):
        """Iterate over foreign modules and import all relevant classes from them

        It is necessary to let Cython know about other autowrap-created classes
        that may reside in other modules, basically any "cdef" definitions that
        we may be using in this compilation unit. Since we are passing objects
        as arguments quite frequently, we need to know about all other wrapped
        classes and we need to cimport them.

        E.g. if we have module1 containing classA, classB and want to access it
        through the pxd header, then we need to add:

            from .module1 import classA, classB

        """
        code = Code()
        L.info("Create foreign imports for module %s" % self.target_path)
        for module in self.all_decl:
            # We skip our own module

            mname = module
            if sys.version_info >= (3, 0) and self.add_relative:
                mname = "." + module

            if os.path.basename(self.target_path).split(".pyx")[0] != module:

                for resolved in self.all_decl[module]["decls"]:

                    # We need to import classes and enums that could be used in
                    # the Cython code in the current module

                    # use Cython name, which correctly imports template classes (instead of C name)
                    name = resolved.name

                    if resolved.__class__ in (ResolvedEnum,):
                        if resolved.cpp_decl.annotations.get("wrap-attach"):
                            # No need to import attached classes as they are
                            # usually in the same pxd file and should not be
                            # globally exported.
                            pass
                        else:
                            code.add("from $mname cimport $name", locals())
                    if resolved.__class__ in (ResolvedClass,):

                        # Skip classes that explicitely should not have a pxd
                        # import statement (abstract base classes and the like)
                        if not resolved.no_pxd_import:
                            if resolved.cpp_decl.annotations.get("wrap-attach"):
                                code.add("from $mname cimport __$name", locals())
                            else:
                                code.add("from $mname cimport $name", locals())

            else:
                L.info("Skip imports from self (own module %s)" % module)

        self.top_level_code.append(code)

    def create_cimports(self):
        self.create_std_cimports()
        code = Code()
        for resolved in self.all_resolved:
            import_from = resolved.pxd_import_path
            name = resolved.name
            if resolved.__class__ in (ResolvedEnum,):
                code.add("from $import_from cimport $name as _$name", locals())
            elif resolved.__class__ in (ResolvedClass,):
                name = resolved.cpp_decl.name
                code.add("from $import_from cimport $name as _$name", locals())
            elif resolved.__class__ in (ResolvedFunction,):
                # Ensure the name the original C++ name (and not the Python display name)
                name = resolved.cpp_decl.name
                mangled_name = "_" + name + "_" + import_from
                code.add("from $import_from cimport $name as $mangled_name", locals())
            elif resolved.__class__ in (ResolvedTypeDef,):
                code.add("from $import_from cimport $name", locals())

        self.top_level_code.append(code)

    def create_default_cimports(self):
        code = Code()
        # Using embedsignature here does not help much as it is only the Python
        # signature which does not really specify the argument types. We have
        # to use a docstring for each method.
        code.add(
            """
                   |#Generated with autowrap %s and Cython (Parser) %s
                   |#cython: c_string_encoding=ascii
                   |#cython: embedsignature=False
                   |from  enum             import Enum as _PyEnum
                   |from cpython cimport Py_buffer
                   |from  libcpp.string   cimport string as libcpp_string
                   |from  libcpp.string   cimport string as libcpp_utf8_string
                   |from  libcpp.string   cimport string as libcpp_utf8_output_string
                   |from  libcpp.set      cimport set as libcpp_set
                   |from  libcpp.vector   cimport vector as libcpp_vector
                   |from  libcpp.pair     cimport pair as libcpp_pair
                   |from  libcpp.map      cimport map  as libcpp_map
                   |from  libcpp          cimport bool
                   |from  libc.string     cimport const_char
                   |from  cython.operator cimport dereference as deref,
                   + preincrement as inc, address as address
                   """
            % ("%s.%s.%s" % autowrap_version, Cython.Compiler.Version.watermark)
        )
        if self.include_refholder:
            code.add(
                """
                   |from  AutowrapRefHolder      cimport AutowrapRefHolder
                   |from  AutowrapPtrHolder      cimport AutowrapPtrHolder
                   |from  AutowrapConstPtrHolder cimport AutowrapConstPtrHolder
                   """
            )
        if self.include_shared_ptr == "boost":
            code.add(
                """
                   |from  smart_ptr       cimport shared_ptr
                   """
            )
        elif self.include_shared_ptr == "std":
            code.add(
                """
                   |from  libcpp.memory   cimport shared_ptr
                   """
            )
        if self.include_numpy:
            code.add(
                """
                   |cimport numpy as np
                   |import numpy as np
                   |cimport numpy as numpy
                   |import numpy as numpy
                   """
            )

        return code

    def create_std_cimports(self):
        code = self.create_default_cimports()
        if self.extra_cimports is not None:
            for stmt in self.extra_cimports:
                code.add(stmt)

        self.top_level_code.append(code)
        return code

    def create_includes(self):
        code = Code()
        code.add(
            """
                |cdef extern from "autowrap_tools.hpp":
                |    char * _cast_const_away(char *)
                """
        )

        self.top_level_code.append(code)
