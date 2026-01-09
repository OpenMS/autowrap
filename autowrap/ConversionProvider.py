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

from collections import defaultdict
from typing import List, Tuple, Optional, Union, AnyStr

from autowrap.DeclResolver import ResolvedClass
from autowrap.Types import CppType  # , printable
from autowrap.Code import Code

import logging as L
import string


def mangle(s):
    s = s.replace("(", "_l_")
    s = s.replace(")", "_r_")
    s = s.replace("<", "_lt_")
    s = s.replace(">", "_gt_")
    s = s.replace("[", "_lb_")
    s = s.replace("]", "_rb_")
    s = s.replace(".", "_dot_")
    return s


class TypeConverterBase(object):
    def set_enums_to_wrap(self, enums_to_wrap):
        self.enums_to_wrap = enums_to_wrap

    def _set_converter_registry(self, r):
        self.converters = r

    def get_base_types(self) -> List[str]:
        """
        for first level lookup in registry
        """
        raise NotImplementedError()

    def matches(self, cpp_type: CppType) -> bool:
        """
        for second level lookup in registry
        """
        raise NotImplementedError()

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        """
        Creates a temporary object which has the type of the current TypeConverter object.

        The object is *always* named "_r" and will be of type "res_type". It
        will be assigned the value of "cy_call_str".

        Note that Cython cannot declare C++ references, therefore

           cdef int & _r

        is illegal to declare and we have to remove any references from the type.
        Use with_const = False to return the type non-const
        """
        cy_res_type = self.converters.cython_type(res_type)  # type: CppType
        if cy_res_type.is_ref:
            cy_res_type = cy_res_type.base_type
            # TODO what about const refs?
            return "cdef %s _r = %s" % (cy_res_type, cy_call_str)

        return "cdef %s _r = %s" % (cy_res_type.toString(with_const), cy_call_str)

    def matching_python_type(self, cpp_type: CppType) -> str:
        """
        Converts cpp type to general python type, e.g. vector to list
        :param cpp_type: original cpp type
        :return: python equivalent
        """
        raise NotImplementedError()

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        """
        Converts cpp type to general python type, e.g. vector<vector<int>> to list[list[int]]
        :param cpp_type: cpp type
        :return: python equivalent for static typing
        """
        return "Any"
        # If at some point we make it mandatory, we can raise NotImplementedError()

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        """
        For each argument, creates code to check for valid types
        """
        raise NotImplementedError()

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Union[Code, str], Union[Code, str], Union[Code, str]]:
        """
        Sets up the conversion of input arguments.

        Returns a tuple as follows:
          - code : a code object to be added to the beginning of the function
          - call_as : a piece of code indicating how the argument should be called as going forward
          - cleanup : a piece of cleanup code to be added to the bottom of the function
        """
        raise NotImplementedError()

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[Union[Code, str]]:
        raise NotImplementedError()

    @staticmethod
    def _code_for_instantiate_object_from_iter(cpp_type: CppType, it: str) -> str:
        """
        Code for new object instantiation from iterator (double deref for iterator-ptr)

        Note that if cpp_type is a pointer and the iterator therefore refers to
        an STL object of std::vector< _FooObject* >, then we need the base type
        to instantiate a new object and dereference twice.

        Example output:
            shared_ptr[ _FooObject ] (new _FooObject (*foo_iter)  )
            shared_ptr[ _FooObject ] (new _FooObject (**foo_iter_ptr)  )
        """

        if cpp_type.is_ref:
            cpp_type = cpp_type.base_type

        if cpp_type.is_ptr:
            cpp_type_base = cpp_type.base_type
            return string.Template(
                "shared_ptr[$cpp_type_base](new $cpp_type_base(deref(deref($it))))"
            ).substitute(locals())
        else:
            return string.Template("shared_ptr[$cpp_type](new $cpp_type(deref($it)))").substitute(
                locals()
            )


class VoidConverter(TypeConverterBase):
    def get_base_types(self) -> List[str]:
        return ["void"]

    def matches(self, cpp_type: CppType) -> bool:
        return not cpp_type.is_ptr

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        return cy_call_str

    def matching_python_type(self, cpp_type: CppType) -> str:
        raise NotImplementedError("void has no matching python type")

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        return "None"

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        raise NotImplementedError("void has no matching python type")

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[str, str, str]:
        raise NotImplementedError("void has no matching python type")

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[str]:
        return None


class IntegerConverter(TypeConverterBase):
    """
    wraps int.
    """

    def get_base_types(self) -> List[str]:
        return [
            "int",
            "bint",  # C boolean type
            "int32_t",
            "ptrdiff_t",
            "int64_t",
            "uint32_t",
            "uint64_t",
            "size_t",
        ]

    def matches(self, cpp_type: CppType) -> bool:
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "int"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        return "int"

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        return "isinstance(%s, int)" % (argument_var,)

    def input_conversion(self, cpp_type, argument_var, arg_num) -> Tuple[str, str, str]:
        code = ""
        call_as = "(<%s>%s)" % (cpp_type, argument_var)
        cleanup = ""
        return code, call_as, cleanup

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[str]:
        return "%s = <%s>%s" % (output_py_var, cpp_type, input_cpp_var)


class BooleanConverter(TypeConverterBase):
    """
    Wraps a C++ bool. Bools are automatically imported in the beginning of a file with
    'from libcpp import bool'.
    """

    def get_base_types(self) -> List[str]:
        return [
            "bool",
        ]

    def matches(self, cpp_type: CppType) -> bool:
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "bool"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        return "bool"

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        return "isinstance(%s, pybool_t)" % (argument_var,)

    def input_conversion(self, cpp_type, argument_var, arg_num) -> Tuple[str, str, str]:
        code = ""
        call_as = "(<%s>%s)" % (cpp_type, argument_var)
        cleanup = ""
        return code, call_as, cleanup

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[str]:
        return "%s = <%s>%s" % (output_py_var, cpp_type, input_cpp_var)


class UnsignedIntegerConverter(TypeConverterBase):
    """
    wraps unsigned int.
    """

    def get_base_types(self) -> List[str]:
        return [
            "unsigned int",
            "ptrdiff_t",
            "uint32_t",
            "uint64_t",
            "size_t",
        ]

    def matches(self, cpp_type: CppType) -> bool:
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type: CppType) -> str:
        return ""

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        if cpp_type == "bool":
            return "bool"  # use most specific type, we could also inherit
        return "int"

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        return "isinstance(%s, int) and %s >= 0" % (
            argument_var,
            argument_var,
        )

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[str, str, str]:
        code = ""
        call_as = "(<%s>%s)" % (cpp_type, argument_var)
        cleanup = ""
        return code, call_as, cleanup

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[str]:
        return "%s = <%s>%s" % (output_py_var, cpp_type, input_cpp_var)


# TODO: common base class for float, int, str conversion


class DoubleConverter(TypeConverterBase):
    def get_base_types(self) -> List[str]:
        return ["double"]

    def matches(self, cpp_type: CppType) -> bool:
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "double"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        return "float"

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        return "isinstance(%s, float)" % (argument_var,)

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[str, str, str]:
        code = ""
        call_as = "(<%s>%s)" % (cpp_type, argument_var)
        cleanup = ""
        return code, call_as, cleanup

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[str]:
        return "%s = <%s>%s" % (output_py_var, cpp_type, input_cpp_var)


class FloatConverter(TypeConverterBase):
    def get_base_types(self) -> List[str]:
        return ["float"]

    def matches(self, cpp_type: CppType) -> bool:
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "float"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        return "float"

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        return "isinstance(%s, float)" % (argument_var,)

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[str, str, str]:
        code = ""
        call_as = "(<%s>%s)" % (cpp_type, argument_var)
        cleanup = ""
        return code, call_as, cleanup

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[str]:
        return "%s = <%s>%s" % (output_py_var, cpp_type, input_cpp_var)


class EnumConverter(TypeConverterBase):
    def __init__(self, enum):
        self.enum = enum

    def get_base_types(self) -> List[str]:
        return [self.enum.name]

    def matches(self, cpp_type: CppType) -> bool:
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type: CppType) -> str:
        if not self.enum.scoped:
            return "int"
        else:
            return ""

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        if not self.enum.scoped:
            # TODO add some other hint that this must be an
            #  int from the class "__" + self.enum.name
            return "int"
        elif self.enum.cpp_decl.annotations.get("wrap-attach"):
            return "_Py" + self.enum.name
        else:
            return self.enum.name

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        if not self.enum.scoped:
            values = ", ".join(str(v) for (__, v) in self.enum.items)
            return "%s in [%s]" % (argument_var, values)
        else:
            if self.enum.cpp_decl.annotations.get("wrap-attach"):
                if not self.enum.scoped:
                    name = "__" + self.enum.name
                else:
                    name = "_Py" + self.enum.name
            else:
                name = self.enum.name
            # FIX for cross-module scoped enum type checking in multi-module builds
            # (e.g., pyOpenMS with _pyopenms_1.pyx through _pyopenms_8.pyx)
            #
            # Problem: Scoped enums (enum class) are wrapped as Python IntEnum classes
            # (e.g., _PySpectrumType). When module A uses an enum defined in module B,
            # the isinstance check needs access to that Python class.
            #
            # Solution: Use _get_scoped_enum_class() for cross-module lookup. This:
            # - First checks the local module's registry (fast path for same-module enums)
            # - Then searches all loaded pyopenms modules via sys.modules
            # - Falls back to 'int' which works for IntEnum values (IntEnum inherits from int)
            #
            # See also: CodeGenerator.create_default_cimports() where the lookup function
            # and registry are defined.
            return "isinstance(%s, _get_scoped_enum_class('%s'))" % (argument_var, name)

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[str, str, str]:
        code = ""
        if not self.enum.scoped:
            call_as = "(<_%s>%s)" % (cpp_type.base_type, argument_var)
        else:
            # for scoped enums we use the python enum class. There you need to use value
            call_as = "(<_%s>%s.value)" % (cpp_type.base_type, argument_var)
        cleanup = ""
        return code, call_as, cleanup

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[str]:
        if not self.enum.scoped:
            return "%s = <int>%s" % (output_py_var, input_cpp_var)
        else:
            # For scoped enums, wrap the int value in the Python enum class
            # Use _get_scoped_enum_class() for cross-module lookup
            # in multi-module builds (see type_check_expression for details)
            if self.enum.cpp_decl.annotations.get("wrap-attach"):
                name = "_Py" + self.enum.name
            else:
                name = self.enum.name
            return "%s = _get_scoped_enum_class('%s', lambda x: x)(<int>%s)" % (output_py_var, name, input_cpp_var)


class CharConverter(TypeConverterBase):
    def get_base_types(self) -> List[str]:
        return ["char"]

    def matches(self, cpp_type: CppType) -> bool:
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "bytes"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        return "bytes"

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        return "isinstance(%s, bytes) and len(%s) == 1" % (
            argument_var,
            argument_var,
        )

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[str, str, str]:
        code = ""
        call_as = "(<char>((%s)[0]))" % argument_var
        cleanup = ""
        return code, call_as, cleanup

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        return "cdef char  _r = %s" % cy_call_str

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[str]:
        return "%s = chr(<char>(%s))" % (output_py_var, input_cpp_var)


class ConstCharPtrConverter(TypeConverterBase):
    def get_base_types(self) -> List[str]:
        return ["const_char"]

    def matches(self, cpp_type: CppType) -> bool:
        return cpp_type.is_ptr

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "bytes"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        return "bytes"

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        return "isinstance(%s, bytes)" % (argument_var,)

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Code, str, str]:
        code = Code().add(
            "cdef const_char * input_%s = <const_char *> %s" % (argument_var, argument_var)
        )
        call_as = "input_%s" % argument_var
        cleanup = ""
        return code, call_as, cleanup

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        return "cdef const_char  * _r = _cast_const_away(%s)" % cy_call_str

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[str]:
        return "%s = <const_char *>(%s)" % (output_py_var, input_cpp_var)


class CharPtrConverter(TypeConverterBase):
    def get_base_types(self) -> List[str]:
        return ["char"]

    def matches(self, cpp_type: CppType) -> bool:
        return cpp_type.is_ptr

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "bytes"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        return "bytes"

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        return "isinstance(%s, bytes)" % (argument_var,)

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[str, str, str]:
        code = ""
        call_as = "(<char *>%s)" % argument_var
        cleanup = ""
        return code, call_as, cleanup

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        return "cdef char  * _r = _cast_const_away(%s)" % cy_call_str

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[str]:
        return "%s = <char *>(%s)" % (output_py_var, input_cpp_var)


class TypeToWrapConverter(TypeConverterBase):
    def __init__(self, class_: ResolvedClass):
        self.class_: ResolvedClass = class_

    def get_base_types(self) -> List[str]:
        return [self.class_.name]

    def matches(self, cpp_type: CppType) -> bool:
        return True

    def matching_python_type(self, cpp_type: CppType) -> str:
        return cpp_type.base_type

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        # TODO double-check what happens with ptr/ref types and typedefs
        return cpp_type.base_type

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        return "isinstance(%s, %s)" % (argument_var, cpp_type.base_type)

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[str, str, str]:
        code = ""
        if cpp_type.is_ptr:
            call_as = "(%s.inst.get())" % (argument_var,)
        else:
            call_as = "(deref(%s.inst.get()))" % (argument_var,)

        cleanup = ""
        return code, call_as, cleanup

    def call_method(
        self, res_type: CppType, cy_call_str: str, with_const: bool = True
    ) -> Union[Code, str]:
        t = self.converters.cython_type(res_type)

        if t.is_ref:
            # If t is a ref, we would like to call on the base type
            t = t.base_type
        elif t.is_ptr:
            # Special treatment for const raw ptr
            const = ""
            if t.is_const:
                const = "const"

            # If t is a pointer, we would like to call on the base type
            t = t.base_type
            code = Code().add(
                """
                |cdef $const $t * __r = ($cy_call_str)
                |if __r == NULL:
                |    return None
                |cdef $t * _r = new $t(deref(__r))
                """,
                locals(),
            )
            return code

        return "cdef %s * _r = new %s(%s)" % (t, t, cy_call_str)

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[Union[Code, str]]:
        cy_clz = self.converters.cython_type(cpp_type)

        # Need to ensure that type inside the raw ptr is an object and not a ref/ptr
        if cpp_type.is_ptr or cpp_type.is_ref:
            cy_clz = cy_clz.base_type

        t = cpp_type.base_type
        return Code().add(
            """
                      |cdef $t $output_py_var = $t.__new__($t)
                      |$output_py_var.inst = shared_ptr[$cy_clz]($input_cpp_var)
        """,
            locals(),
        )


class StdPairConverter(TypeConverterBase):
    # remark: we use list instead of tuple internally, in order to
    # provide call by ref args. Python tuples are immutable.

    def get_base_types(self) -> List[str]:
        return ["libcpp_pair"]

    def matches(self, cpp_type: CppType) -> bool:
        return True

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "list"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        (
            t1,
            t2,
        ) = cpp_type.template_args
        # We use typing.List to be backwards compatible with py <=3.8
        return "List[%s, %s]" % (
            self.converters.get(t1).matching_python_type_full(t1),
            self.converters.get(t2).matching_python_type_full(t2),
        )

    def type_check_expression(self, cpp_type, arg_var):
        (
            t1,
            t2,
        ) = cpp_type.template_args
        inner_conv1 = self.converters.get(t1)
        inner_conv2 = self.converters.get(t2)
        assert inner_conv1 is not None, "arg type %s not supported" % t1
        assert inner_conv2 is not None, "arg type %s not supported" % t2
        inner_check1 = inner_conv1.type_check_expression(t1, "%s[0]" % arg_var)
        inner_check2 = inner_conv2.type_check_expression(t2, "%s[1]" % arg_var)

        return (
            Code()
            .add(
                """
          |isinstance($arg_var, list) and len($arg_var) == 2 and $inner_check1
          + and $inner_check2
          """,
                locals(),
            )
            .render()
        )

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Code, str, Code]:
        (
            t1,
            t2,
        ) = cpp_type.template_args
        temp_var = "v%d" % arg_num
        i1 = self.converters.cython_type(t1)
        i2 = self.converters.cython_type(t2)
        if i1.is_enum:
            assert not t1.is_ptr
            arg0 = "(<%s>%s[0])" % (t1, argument_var)
        elif t1.base_type in self.converters.names_of_wrapper_classes:
            assert not t1.is_ptr
            arg0 = "deref((<%s>%s[0]).inst.get())" % (t1, argument_var)
        else:
            arg0 = "%s[0]" % argument_var
        if i2.is_enum:
            assert not t2.is_ptr
            arg1 = "(<%s>%s[0])" % (t2, argument_var)
        elif t2.base_type in self.converters.names_of_wrapper_classes:
            assert not t2.is_ptr
            arg1 = "deref((<%s>%s[1]).inst.get())" % (t2, argument_var)
        else:
            arg1 = "%s[1]" % argument_var

        code = Code().add(
            """
            |cdef libcpp_pair[$i1, $i2] $temp_var
            |$temp_var.first = $arg0
            |$temp_var.second = $arg1
            """,
            locals(),
        )

        cleanup_code = Code()
        if cpp_type.is_ref and not cpp_type.is_const:
            if not i1.is_enum and t1.base_type in self.converters.names_of_wrapper_classes:
                temp1 = "temp1"
                cleanup_code.add(
                    """
                    |cdef $t1 $temp1 = $t1.__new__($t1)
                    |$temp1.inst = shared_ptr[$i1](new $i1($temp_var.first))
                                   """,
                    locals(),
                )
            else:
                temp1 = "%s.first" % temp_var
            if not i2.is_enum and t2.base_type in self.converters.names_of_wrapper_classes:
                temp2 = "temp2"
                cleanup_code.add(
                    """
                    |cdef $t2 $temp2 = $t2.__new__($t2)
                    |$temp2.inst = shared_ptr[$i2](new $i2($temp_var.second))
                                   """,
                    locals(),
                )
            else:
                temp2 = "%s.second" % temp_var

            cleanup_code.add(
                """
                |$argument_var[:] = [$temp1, $temp2]
                """,
                locals(),
            )
        return code, "%s" % temp_var, cleanup_code

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        return "_r = %s" % (cy_call_str)

    def output_conversion(self, cpp_type: CppType, input_cpp_var: str, output_py_var: str) -> Code:
        assert not cpp_type.is_ptr
        (
            t1,
            t2,
        ) = cpp_type.template_args

        i1 = self.converters.cython_type(t1)
        i2 = self.converters.cython_type(t2)

        code = Code()

        if i1.is_enum:
            out1 = "out1"
            code.add(
                """cdef $i1 out1 = (<$i1> $input_cpp_var.first)
                       """,
                locals(),
            )

        elif t1.base_type in self.converters.names_of_wrapper_classes:
            out1 = "out1"
            code.add(
                """cdef $t1 out1 = $t1.__new__($t1)
                       |out1.inst = shared_ptr[$i1](new $i1($input_cpp_var.first))
                       """,
                locals(),
            )
        else:
            out1 = "%s.first" % input_cpp_var

        if i2.is_enum:
            out2 = "out2"
            code.add(
                """cdef $i2 out2 = (<$i2> $input_cpp_var.second)
                       """,
                locals(),
            )
        elif t2.base_type in self.converters.names_of_wrapper_classes:
            out2 = "out2"
            code.add(
                """cdef $t2 out2 = $t2.__new__($t2)
                       |out2.inst = shared_ptr[$i2](new $i2($input_cpp_var.second))
                       """,
                locals(),
            )
        else:
            out2 = "%s.second" % input_cpp_var

        code.add(
            """cdef list $output_py_var = [$out1, $out2]
            """,
            locals(),
        )
        return code


class StdMapConverter(TypeConverterBase):
    def get_base_types(self) -> List[str]:
        return ["libcpp_map"]

    def matches(self, cpp_type: CppType) -> bool:
        return True

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "dict"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        tt_key, tt_value = cpp_type.template_args
        inner_conv_1 = self.converters.get(tt_key)
        inner_conv_2 = self.converters.get(tt_value)
        # We use typing.Dict to be backwards compatible with py <= 3.8
        return "Dict[%s, %s]" % (
            inner_conv_1.matching_python_type_full(tt_key),
            inner_conv_2.matching_python_type_full(tt_value),
        )

    def type_check_expression(self, cpp_type, arg_var):
        tt_key, tt_value = cpp_type.template_args
        inner_conv_1 = self.converters.get(tt_key)
        inner_conv_2 = self.converters.get(tt_value)
        assert inner_conv_1 is not None, "arg type %s not supported" % tt_key
        assert inner_conv_2 is not None, "arg type %s not supported" % tt_value

        inner_check_1 = inner_conv_1.type_check_expression(tt_key, "k")
        inner_check_2 = inner_conv_2.type_check_expression(tt_value, "v")

        return (
            Code()
            .add(
                """
          |isinstance($arg_var, dict)
          + and all($inner_check_1 for k in $arg_var.keys())
          + and all($inner_check_2 for v in $arg_var.values())
          """,
                locals(),
            )
            .render()
        )

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Code, str, Union[Code, str]]:
        tt_key, tt_value = cpp_type.template_args
        temp_var = "v%d" % arg_num

        code = Code()

        cy_tt_key = self.converters.cython_type(tt_key)
        cy_tt_value = self.converters.cython_type(tt_value)

        py_tt_key = tt_key

        value_conv_code = ""
        value_conv_cleanup = ""
        key_conv_code = ""
        key_conv_cleanup = ""

        # Use mangled variable names to avoid collision with function parameters
        loop_key = mangle("_loop_key_" + argument_var)
        loop_value = mangle("_loop_value_" + argument_var)

        if cy_tt_value.is_enum:
            value_conv = "<%s> %s" % (cy_tt_value, loop_value)
        elif tt_value.base_type in self.converters.names_of_wrapper_classes:
            value_conv = "deref((<%s>%s).inst.get())" % (tt_value.base_type, loop_value)
        elif tt_value.template_args is not None and tt_value.base_type == "libcpp_vector":
            # Special case: the value type is a std::vector< X >, maybe something we can convert?

            # code_top = """
            value_var = loop_value
            (tt,) = tt_value.template_args
            vtemp_var = "svec%s" % arg_num
            inner = self.converters.cython_type(tt)

            # Check whether the inner vector has any classes we need to wrap (we cannot do that)
            contains_classes_to_wrap = (
                tt.template_args is not None
                and len(
                    set(self.converters.names_of_wrapper_classes).intersection(
                        set(tt.all_occuring_base_types())
                    )
                )
                > 0
            )

            if self.converters.cython_type(tt).is_enum:
                # Case 1: We wrap a std::vector<> with an enum base type
                raise Exception("Not Implemented")
            elif tt.base_type in self.converters.names_of_wrapper_classes:
                # Case 2: We wrap a std::vector<> with a base type we need to wrap
                raise Exception("Not Implemented")
            elif (
                tt.template_args is not None
                and tt.base_type == "shared_ptr"
                and len(set(tt.template_args[0].all_occuring_base_types())) == 1
            ):
                # Case 3: We wrap a std::vector< shared_ptr<X> > where X needs to be a type that is easy to wrap
                raise Exception("Not Implemented")
            elif (
                tt.template_args is not None
                and tt.base_type != "libcpp_vector"
                and len(
                    set(self.converters.names_of_wrapper_classes).intersection(
                        set(tt.all_occuring_base_types())
                    )
                )
                > 0
            ):
                # Only if the std::vector contains a class that we need to wrap somewhere,
                # we cannot do it ...
                raise Exception(
                    "Recursion in std::vector<T> is not implemented for other STL methods and wrapped template "
                    "arguments"
                )
            elif (
                tt.template_args is not None
                and tt.base_type == "libcpp_vector"
                and contains_classes_to_wrap
            ):
                # Case 4: We wrap a std::vector<> with a base type that contains
                #         further nested std::vector<> inside
                #         -> deal with recursion
                raise Exception("Not Implemented")
            else:
                # Case 5: We wrap a regular type
                inner = self.converters.cython_type(tt)
                # cython cares for conversion of stl containers with std types,
                # but we need to add the definition to the top
                code = Code().add(
                    """
                    |cdef libcpp_vector[$inner] $vtemp_var
                    """,
                    locals(),
                )

                value_conv_cleanup = Code().add("")
                value_conv_code = Code().add("$vtemp_var = $value_var", locals())
                value_conv = "%s" % vtemp_var
                if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
                    cleanup_code = Code().add(
                        """
                        |$value_var[:] = $vtemp_var
                        """,
                        locals(),
                    )

        elif tt_value in self.converters:
            value_conv_code, value_conv, value_conv_cleanup = self.converters.get(
                tt_value
            ).input_conversion(tt_value, loop_value, 0)
        else:
            value_conv = "<%s> %s" % (cy_tt_value, loop_value)

        if cy_tt_key.is_enum:
            key_conv = "<%s> %s" % (cy_tt_key, loop_key)
        elif tt_key.base_type in self.converters.names_of_wrapper_classes:
            key_conv = "deref(<%s *> (<%s> %s).inst.get())" % (cy_tt_key, py_tt_key, loop_key)
        elif tt_key in self.converters:
            key_conv_code, key_conv, key_conv_cleanup = self.converters.get(
                tt_key
            ).input_conversion(tt_key, loop_key, 0)
        else:
            key_conv = "<%s> %s" % (cy_tt_key, loop_key)

        code.add(
            """
            |cdef libcpp_map[$cy_tt_key, $cy_tt_value] * $temp_var = new
            + libcpp_map[$cy_tt_key, $cy_tt_value]()

            |for $loop_key, $loop_value in $argument_var.items():
            """,
            locals(),
        )

        code.add(key_conv_code)
        code.add(value_conv_code)
        code.add(
            """    deref($temp_var)[ $key_conv ] = $value_conv
            """,
            locals(),
        )
        code.add(key_conv_cleanup)
        code.add(value_conv_cleanup)

        if cpp_type.is_ref and not cpp_type.is_const:
            it = mangle("it_" + argument_var)

            key_conv = "<%s> deref(%s).first" % (cy_tt_key, it)

            # TODO can we refactor such that each if-clause adds a part
            # add code for key that is wrapped
            if (
                tt_key.base_type in self.converters.names_of_wrapper_classes
                and not tt_value.base_type in self.converters.names_of_wrapper_classes
            ):
                value_conv = "<%s> deref(%s).second" % (cy_tt_value, it)
                cy_tt = tt_value.base_type
                item = mangle("item_" + argument_var)
                item_key = mangle("itemk_" + argument_var)
                cleanup_code = Code().add(
                    """
                    |replace = dict()
                    |cdef libcpp_map[$cy_tt_key, $cy_tt_value].iterator $it = $temp_var.begin()
                    |cdef $py_tt_key $item_key
                    |while $it != $temp_var.end():
                    |   $item_key = $py_tt_key.__new__($py_tt_key)
                    |   $item_key.inst = shared_ptr[$cy_tt_key](new $cy_tt_key((deref($it)).first))
                    |   replace[$item_key] = $value_conv
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """,
                    locals(),
                )
            # add code for value that is wrapped
            elif (
                not cy_tt_value.is_enum
                and tt_value.base_type in self.converters.names_of_wrapper_classes
                and not tt_key.base_type in self.converters.names_of_wrapper_classes
            ):
                cy_tt = tt_value.base_type
                item = mangle("item_" + argument_var)
                cleanup_code = Code().add(
                    """
                    |replace = dict()
                    |cdef libcpp_map[$cy_tt_key, $cy_tt_value].iterator $it = $temp_var.begin()
                    |cdef $cy_tt $item
                    |while $it != $temp_var.end():
                    |   $item = $cy_tt.__new__($cy_tt)
                    |   $item.inst = shared_ptr[$cy_tt_value](new $cy_tt_value((deref($it)).second))
                    |   replace[$key_conv] = $item
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """,
                    locals(),
                )
            # add code for value AND key that is wrapped
            elif (
                not cy_tt_value.is_enum
                and tt_value.base_type in self.converters.names_of_wrapper_classes
                and tt_key.base_type in self.converters.names_of_wrapper_classes
            ):
                value_conv = "<%s> deref(%s).second" % (cy_tt_value, it)
                cy_tt = tt_value.base_type
                item_val = mangle("itemv_" + argument_var)
                item_key = mangle("itemk_" + argument_var)
                cleanup_code = Code().add(
                    """
                    |replace = dict()
                    |cdef libcpp_map[$cy_tt_key, $cy_tt_value].iterator $it = $temp_var.begin()
                    |cdef $py_tt_key $item_key
                    |cdef $cy_tt $item_val
                    |while $it != $temp_var.end():
                    |   $item_key = $py_tt_key.__new__($py_tt_key)
                    |   $item_key.inst = shared_ptr[$cy_tt_key](new $cy_tt_key((deref($it)).first))
                    |   $item_val = $cy_tt.__new__($cy_tt)
                    |   $item_val.inst = shared_ptr[$cy_tt_value](new $cy_tt_value((deref($it)).second))
                    |   replace[$item_key] = $item_val
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """,
                    locals(),
                )
            else:
                value_conv = "<%s> deref(%s).second" % (cy_tt_value, it)
                cleanup_code = Code().add(
                    """
                    |replace = dict()
                    |cdef libcpp_map[$cy_tt_key, $cy_tt_value].iterator $it = $temp_var.begin()
                    |while $it != $temp_var.end():
                    |   replace[$key_conv] = $value_conv
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """,
                    locals(),
                )
        else:
            cleanup_code = "del %s" % temp_var

        return code, "deref(%s)" % temp_var, cleanup_code

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        return "_r = %s" % cy_call_str

    def output_conversion(self, cpp_type: CppType, input_cpp_var: str, output_py_var: str) -> Code:
        assert not cpp_type.is_ptr

        tt_key, tt_value = cpp_type.template_args
        cy_tt_key = self.converters.cython_type(tt_key)
        cy_tt_value = self.converters.cython_type(tt_value)
        py_tt_key = tt_key

        it = mangle("it_" + input_cpp_var)

        if (
            not cy_tt_value.is_enum
            and tt_value.base_type in self.converters.names_of_wrapper_classes
        ) and (
            not cy_tt_key.is_enum and tt_key.base_type in self.converters.names_of_wrapper_classes
        ):
            # Both key and value are wrapped classes
            cy_tt_val = tt_value.base_type
            cy_tt_k = tt_key.base_type
            item_key = mangle("itemk_" + output_py_var)
            item_val = mangle("itemv_" + output_py_var)
            code = Code().add(
                """
                |$output_py_var = dict()
                |cdef libcpp_map[$cy_tt_key, $cy_tt_value].iterator $it = $input_cpp_var.begin()
                |cdef $cy_tt_k $item_key
                |cdef $cy_tt_val $item_val
                |while $it != $input_cpp_var.end():
                |   $item_key = $cy_tt_k.__new__($cy_tt_k)
                |   $item_key.inst = shared_ptr[$cy_tt_key](new $cy_tt_key((deref($it)).first))
                |   $item_val = $cy_tt_val.__new__($cy_tt_val)
                |   $item_val.inst = shared_ptr[$cy_tt_value](new $cy_tt_value((deref($it)).second))
                |   $output_py_var[$item_key] = $item_val
                |   inc($it)
                """,
                locals(),
            )
            return code

        elif not cy_tt_key.is_enum and tt_key.base_type in self.converters.names_of_wrapper_classes:
            key_conv = "deref(<%s *> (<%s> key).inst.get())" % (cy_tt_key, py_tt_key)
        else:
            key_conv = "<%s>(deref(%s).first)" % (cy_tt_key, it)

        if (
            not cy_tt_value.is_enum
            and tt_value.base_type in self.converters.names_of_wrapper_classes
        ):
            cy_tt = tt_value.base_type
            item = mangle("item_" + output_py_var)
            code = Code().add(
                """
                |$output_py_var = dict()
                |cdef libcpp_map[$cy_tt_key, $cy_tt_value].iterator $it = $input_cpp_var.begin()
                |cdef $cy_tt $item
                |while $it != $input_cpp_var.end():
                |   $item = $cy_tt.__new__($cy_tt)
                |   $item.inst = shared_ptr[$cy_tt_value](new $cy_tt_value((deref($it)).second))
                |   $output_py_var[$key_conv] = $item
                |   inc($it)
                """,
                locals(),
            )
            return code
        elif not cy_tt_key.is_enum and tt_key.base_type in self.converters.names_of_wrapper_classes:
            value_conv = "<%s>(deref(%s).second)" % (cy_tt_value, it)
            item_key = mangle("itemk_" + output_py_var)
            code = Code().add(
                """
                |$output_py_var = dict()
                |cdef libcpp_map[$cy_tt_key, $cy_tt_value].iterator $it = $input_cpp_var.begin()
                |cdef $py_tt_key $item_key
                |while $it != $input_cpp_var.end():
                |   #$output_py_var[$key_conv] = $value_conv
                |   $item_key = $py_tt_key.__new__($py_tt_key)
                |   $item_key.inst = shared_ptr[$cy_tt_key](new $cy_tt_key((deref($it)).first))
                |   # $output_py_var[$key_conv] = $value_conv
                |   $output_py_var[$item_key] = $value_conv
                |   inc($it)
                """,
                locals(),
            )
            return code
        else:
            value_conv = "<%s>(deref(%s).second)" % (cy_tt_value, it)
            code = Code().add(
                """
                |$output_py_var = dict()
                |cdef libcpp_map[$cy_tt_key, $cy_tt_value].iterator $it = $input_cpp_var.begin()
                |while $it != $input_cpp_var.end():
                |   $output_py_var[$key_conv] = $value_conv
                |   inc($it)
                """,
                locals(),
            )
            return code


class StdSetConverter(TypeConverterBase):
    def get_base_types(self) -> List[str]:
        return ["libcpp_set"]

    def matches(self, cpp_type: CppType) -> bool:
        return True

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "set"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        (tt,) = cpp_type.template_args
        inner_conv = self.converters.get(tt)
        return "Set[%s]" % inner_conv.matching_python_type_full(tt)

    def type_check_expression(self, cpp_type, arg_var):
        (tt,) = cpp_type.template_args
        inner_conv = self.converters.get(tt)
        assert inner_conv is not None, "arg type %s not supported" % tt
        inner_check = inner_conv.type_check_expression(tt, "li")

        return (
            Code()
            .add(
                """
          |isinstance($arg_var, set) and all($inner_check for li in $arg_var)
          """,
                locals(),
            )
            .render()
        )

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Code, str, Union[Code, str]]:
        (tt,) = cpp_type.template_args
        temp_var = "v%d" % arg_num
        inner = self.converters.cython_type(tt)
        it = mangle("it_" + argument_var)
        if inner.is_enum:
            item = "item%d" % arg_num
            code = Code().add(
                """
                |cdef libcpp_set[$inner] * $temp_var = new libcpp_set[$inner]()
                |cdef int $item
                |for $item in $argument_var:
                |   $temp_var.insert(<$inner> $item)
                """,
                locals(),
            )
            if cpp_type.is_ref and not cpp_type.is_const:
                cleanup_code = Code().add(
                    """
                    |replace = set()
                    |cdef libcpp_set[$inner].iterator $it = $temp_var.begin()
                    |while $it != $temp_var.end():
                    |   replace.add(<int> deref($it))
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """,
                    locals(),
                )
            else:
                cleanup_code = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup_code

        elif tt.base_type in self.converters.names_of_wrapper_classes:
            base_type = tt.base_type
            inner = self.converters.cython_type(tt)

            # Only dereference for non-ptr types
            do_deref = "deref"
            if inner.is_ptr:
                do_deref = ""

            cy_tt = tt.base_type
            item = "item%d" % arg_num
            code = Code().add(
                """
                |cdef libcpp_set[$inner] * $temp_var = new libcpp_set[$inner]()
                |cdef $base_type $item
                |for $item in $argument_var:
                |   $temp_var.insert($do_deref($item.inst.get()))
                """,
                locals(),
            )
            if cpp_type.is_ref and not cpp_type.is_const:
                instantiation = self._code_for_instantiate_object_from_iter(inner, it)
                cleanup_code = Code().add(
                    """
                    |replace = set()
                    |cdef libcpp_set[$inner].iterator $it = $temp_var.begin()
                    |while $it != $temp_var.end():
                    |   $item = $cy_tt.__new__($cy_tt)
                    |   $item.inst = $instantiation
                    |   replace.add($item)
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """,
                    locals(),
                )

            else:
                cleanup_code = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup_code
        else:
            inner = self.converters.cython_type(tt)
            # cython cares for conversion of stl containers with std types:
            code = Code().add(
                """
                |cdef libcpp_set[$inner] $temp_var = $argument_var
                """,
                locals(),
            )

            cleanup_code = ""
            if cpp_type.is_ref and not cpp_type.is_const:
                cleanup_code = Code().add(
                    """
                    |$argument_var.clear()
                    |$argument_var.update($temp_var)
                    """,
                    locals(),
                )
            return code, "%s" % temp_var, cleanup_code

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        return "_r = %s" % cy_call_str

    def output_conversion(self, cpp_type: CppType, input_cpp_var: str, output_py_var: str) -> Code:
        assert not cpp_type.is_ptr

        (tt,) = cpp_type.template_args
        inner = self.converters.cython_type(tt)
        if inner.is_enum:
            it = mangle("it_" + input_cpp_var)
            code = Code().add(
                """
                |$output_py_var = set()
                |cdef libcpp_set[$inner].iterator $it = $input_cpp_var.begin()
                |while $it != $input_cpp_var.end():
                |   $output_py_var.add(<int>deref($it))
                |   inc($it)
                """,
                locals(),
            )
            return code

        elif tt.base_type in self.converters.names_of_wrapper_classes:
            cy_tt = tt.base_type
            inner = self.converters.cython_type(tt)
            it = mangle("it_" + input_cpp_var)
            item = mangle("item_" + output_py_var)

            instantiation = self._code_for_instantiate_object_from_iter(inner, it)
            code = Code().add(
                """
                |$output_py_var = set()
                |cdef libcpp_set[$inner].iterator $it = $input_cpp_var.begin()
                |cdef $cy_tt $item
                |while $it != $input_cpp_var.end():
                |   $item = $cy_tt.__new__($cy_tt)
                |   $item.inst = $instantiation
                |   $output_py_var.add($item)
                |   inc($it)
                """,
                locals(),
            )
            return code
        else:
            # cython cares for conversion of stl containers with std types:
            code = Code().add(
                """
                |cdef set $output_py_var = $input_cpp_var
                """,
                locals(),
            )
            return code


class StdVectorConverter(TypeConverterBase):
    def get_base_types(self) -> List[str]:
        return ["libcpp_vector"]

    def matches(self, cpp_type: CppType) -> bool:
        return True

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "list"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        (tt,) = cpp_type.template_args
        try:
            inner_conv = self.converters.get(tt)
            return "List[%s]" % inner_conv.matching_python_type_full(tt)
        except NameError:
            return "List[Any]"

    def type_check_expression(self, cpp_type, arg_var):
        (tt,) = cpp_type.template_args
        inner_conv = self.converters.get(tt)
        assert inner_conv is not None, "arg type %s not supported" % tt
        if arg_var[-4:] == "_rec":
            arg_var_next = "%s_rec" % arg_var
        else:
            # first recursion, set element name
            arg_var_next = "elemt_rec"
        inner_check = inner_conv.type_check_expression(tt, arg_var_next)

        return (
            Code()
            .add(
                """
          |isinstance($arg_var, list) and all($inner_check for $arg_var_next in $arg_var)
          """,
                locals(),
            )
            .render()
        )

    def _prepare_nonrecursive_cleanup(
        self, cpp_type, bottommost_code, it_prev, temp_var, recursion_cnt, *a, **kw
    ):
        # B) Prepare the post-call
        if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
            # If the vector is passed by reference, we need to store the
            # result for Python.
            btm_add = ""
            if recursion_cnt > 0:
                # If we are inside a recursion, we have to dereference the
                # _previous_ iterator.
                a[0]["temp_var_used"] = "deref(%s)" % it_prev
                tp_add = "$it = $temp_var_used.begin()"
            else:
                tp_add = "cdef libcpp_vector[$inner].iterator $it = $temp_var.begin()"
                btm_add = """
                |$argument_var[:] = replace_$recursion_cnt
                |del $temp_var
                """
                a[0]["temp_var_used"] = temp_var

            # Add cleanup code (loop through the temporary vector C++ and
            # add items to the python replace_n list).
            cleanup_code = Code().add(
                tp_add
                + """
                |replace_$recursion_cnt = []
                |while $it != $temp_var_used.end():
                |    $item = $cy_tt.__new__($cy_tt)
                |    $item.inst = $instantiation
                |    replace_$recursion_cnt.append($item)
                |    inc($it)
                """
                + btm_add,
                *a,
                **kw
            )
        else:
            if recursion_cnt == 0:
                if cpp_type.is_ptr:
                    cleanup_code = Code()
                else:
                    cleanup_code = Code().add("del %s" % temp_var)
            else:
                cleanup_code = Code()
                bottommost_code.add("del %s" % temp_var)
        return cleanup_code

    def _prepare_recursive_cleanup(
        self, cpp_type, bottommost_code, it_prev, temp_var, recursion_cnt, *a, **kw
    ):
        # B) Prepare the post-call
        if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
            # If the vector is passed by reference, we need to store the
            # result for Python.
            if recursion_cnt > 0:
                # If we are inside a recursion, we have to dereference the
                # _previous_ iterator.
                a[0]["temp_var_used"] = "deref(%s)" % it_prev
                tp_add = "$it = $temp_var_used.begin()"
            else:
                tp_add = "cdef libcpp_vector[$inner].iterator $it = $temp_var.begin()"
                a[0]["temp_var_used"] = temp_var
            cleanup_code = Code().add(
                tp_add
                + """
                |replace_$recursion_cnt = []
                |while $it != $temp_var_used.end():
                """,
                *a,
                **kw
            )
        else:
            if recursion_cnt == 0:
                cleanup_code = Code().add("del %s" % temp_var)
            else:
                cleanup_code = Code()
                bottommost_code.add("del %s" % temp_var)
        return cleanup_code

    def _prepare_nonrecursive_precall(self, topmost_code, cpp_type, code_top, do_deref, *a, **kw):
        # A) Prepare the pre-call
        if topmost_code is not None:
            if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
                # add cdef statements for the iterators (part of B, post-call but needs to
                # be on top)
                code_top += "|cdef libcpp_vector[$inner].iterator $it"
            topmost_code.add(code_top, *a, **kw)
            code_top = ""
        # Now prepare the loop itself
        code = Code().add(
            code_top
            + """
                |for $item in $argument_var:
                |    $temp_var.push_back($do_deref($item.inst.get()))
                """,
            *a,
            **kw
        )
        return code

    def _perform_recursion(
        self,
        cpp_type,
        tt,
        arg_num,
        item,
        topmost_code,
        bottommost_code,
        code,
        cleanup_code,
        recursion_cnt,
        *a,
        **kw
    ):
        converter = self.cr.get(tt)
        py_type = converter.matching_python_type(tt)
        rec_arg_num = "%s_rec" % arg_num
        # the current item is the argument var of the recursive call
        rec_argument_var = item
        topmost_code_callback = Code()
        bottommost_code_callback = Code()
        #
        # Perform the recursive call
        #
        conv_code, call_as, cleanup = converter.input_conversion(
            tt,
            rec_argument_var,
            rec_arg_num,
            topmost_code_callback,
            bottommost_code_callback,
            recursion_cnt + 1,
        )
        # undo the "deref" if it was added ...
        new_item = call_as
        if call_as.find("deref") != -1:
            new_item = new_item[6:]
            new_item = new_item[:-1]
        a[0]["new_item"] = new_item
        #
        # A) Prepare the pre-call, Step 2
        # add all the "topmost" code from all recursive calls if we are in the topmost recursion
        #
        if topmost_code is None:
            code.content.extend(topmost_code_callback.content)
        else:
            topmost_code.content.extend(topmost_code_callback.content)

        #
        # A) Prepare the pre-call, Step 3
        # add the outer loop
        #
        code.add(
            """
            |for $item in $argument_var:
            """,
            *a,
            **kw
        )
        #
        # A) Prepare the pre-call, Step 4
        # clear the vector since it needs to be empty before we start the inner loop
        #
        code.add(
            Code().add(
                """
            |$new_item.clear()""",
                *a,
                **kw
            )
        )
        #
        # A) Prepare the pre-call, Step 5
        # add the inner loop (may contain more inner loops ... )
        #
        code.add(conv_code)
        #
        # A) Prepare the pre-call, Step 6
        # store the vector from the inner loop in our vector (since
        # it is a std::vector object, there is no "inst" to get).
        #
        code.add(
            """
            |    $temp_var.push_back(deref($new_item))
            """,
            *a,
            **kw
        )

        #
        # B) Prepare the post-call, Step 1
        # add the inner loop (may contain more inner loops ... )
        #
        if hasattr(cleanup, "content"):
            cleanup_code.add(cleanup)
        else:
            cleanup_code.content.append(cleanup)

        #
        # B) Prepare the post-call, Step 2
        # append the result from the inner loop iteration to the current result
        # (only if we actually give back the reference)
        #
        if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
            cleanup_code.add(
                """
                |    replace_$recursion_cnt.append(replace_$recursion_cnt_next)
                |    inc($it)
                             """,
                *a,
                **kw
            )

        #
        # B) Prepare the post-call, Step 3
        # append the "bottommost" code
        #
        if bottommost_code is None:
            # we are the outermost loop
            cleanup_code.content.extend(bottommost_code_callback.content)
            if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
                cleanup_code.add(
                    """
                    |$argument_var[:] = replace_$recursion_cnt
                    |del $temp_var
                                 """,
                    *a,
                    **kw
                )
        else:
            bottommost_code.content.extend(bottommost_code_callback.content)

    def input_conversion(
        self,
        cpp_type: CppType,
        argument_var: str,
        arg_num: int,
        topmost_code: Optional[Code] = None,
        bottommost_code: Optional[Code] = None,
        recursion_cnt: int = 0,
    ) -> Tuple[Code, str, Code]:
        """Do the input conversion for a std::vector<T>

        In this case, the template argument is tt (or "inner").

        It is possible to nest or recurse multiple vectors (like in
        std::vector< std::vector< T > > which is detected since the template
        argument of tt itself is not None).
        """
        # If we are inside a recursion, we expect the top-most and bottom most code to be present...
        if recursion_cnt > 1:
            assert topmost_code is not None
            assert bottommost_code is not None
        (tt,) = cpp_type.template_args
        temp_var = "v%s" % arg_num
        inner = self.converters.cython_type(tt)
        it = mangle("it_" + argument_var)  # + "_%s" % recursion_cnt
        recursion_cnt_next = recursion_cnt + 1
        it_prev = ""
        if recursion_cnt > 0:
            it_prev = mangle("it_" + argument_var[:-4])

        base_type = tt.base_type
        cy_tt = tt.base_type

        # Prepare the code that should be at the very outer level of the
        # function, thus variable declarations (e.g. to prevent a situation
        # where new is called within a loop multiple times and memory loss
        # occurs).
        code_top = """
            |cdef libcpp_vector[$inner] * $temp_var
            + = new libcpp_vector[$inner]()
        """

        # If the inner type is templated and contains a class to wrap by us
        # TODO describe what "to wrap" means. Also typedefs to them etc.?
        inner_contains_classes_to_wrap = (
            tt.template_args is not None
            and len(
                set(self.converters.names_of_wrapper_classes).intersection(
                    set(tt.all_occuring_base_types())
                )
            )
            > 0
        )

        if self.converters.cython_type(tt).is_enum:
            # Case 1: We wrap a std::vector<> with an enum base type
            item = "item%s" % arg_num
            if topmost_code is not None:
                raise Exception("Recursion in std::vector<T> not yet implemented for enum")

            code = Code().add(
                """
                |cdef libcpp_vector[$inner] * $temp_var
                + = new libcpp_vector[$inner]()
                |cdef int $item
                |for $item in $argument_var:
                |    $temp_var.push_back(<$inner> $item)
                """,
                locals(),
            )
            if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
                cleanup_code = Code().add(
                    """
                    |replace = []
                    |cdef libcpp_vector[$inner].iterator $it = $temp_var.begin()
                    |while $it != $temp_var.end():
                    |    replace.append(<int> deref($it))
                    |    inc($it)
                    |$argument_var[:] = replace
                    |del $temp_var
                    """,
                    locals(),
                )
            else:
                cleanup_code = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup_code

        elif tt.base_type in self.converters.names_of_wrapper_classes:
            # Case 2: We wrap a std::vector<> with a base type we need to wrap
            item = "item%s" % arg_num

            # Add cdef of the base type to the toplevel code
            code_top += """
                |cdef $base_type $item
            """

            # Only dereference for non-ptr types
            do_deref = "deref"
            if inner.is_ptr:
                do_deref = ""

            instantiation = self._code_for_instantiate_object_from_iter(inner, it)
            code = self._prepare_nonrecursive_precall(
                topmost_code, cpp_type, code_top, do_deref, locals()
            )
            cleanup_code = self._prepare_nonrecursive_cleanup(
                cpp_type, bottommost_code, it_prev, temp_var, recursion_cnt, locals()
            )

            if cpp_type.is_ptr:
                call_fragment = temp_var
            else:
                call_fragment = "deref(%s)" % temp_var

            return code, call_fragment, cleanup_code

        elif (
            tt.template_args is not None
            and tt.base_type == "shared_ptr"
            and len(set(tt.template_args[0].all_occuring_base_types())) == 1
        ):
            # Case 3: We wrap a std::vector< shared_ptr<X> > where X needs to be a type that is easy to wrap

            (base_type,) = tt.template_args
            (cpp_tt,) = inner.template_args

            item = "%s_rec" % argument_var
            code = Code().add(
                """
                |cdef libcpp_vector[$inner] $temp_var 
                |cdef $base_type $item
                |for $item in $argument_var:
                |    $temp_var.push_back($item.inst)
                |# call
                """,
                locals(),
            )

            cleanup_code = Code().add("")

            if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
                item2 = "%s_rec_b" % argument_var
                instantiation = self._code_for_instantiate_object_from_iter(inner, it)
                cleanup_code = Code().add(
                    """
                    |# gather results
                    |replace = list()
                    |cdef libcpp_vector[$inner].iterator $it = $temp_var.begin()
                    |while $it != $temp_var.end():
                    |   $item = $base_type.__new__($base_type)
                    |   $item.inst = deref($it)
                    |   replace.append($item)
                    |   inc($it)
                    |# replace old vector with new contents
                    |$argument_var[:] = []
                    |for $item2 in replace:
                    |    $argument_var.append($item2)
                    """,
                    locals(),
                )

            return code, "%s" % temp_var, cleanup_code

        elif inner_contains_classes_to_wrap and tt.base_type != "libcpp_vector":
            # Only if the template argument which is neither a class-to-wrap nor a std::vector
            # again is a template of something that anywhere in the template hierarchy contains a
            # class-to-wrap (see CppType.allOccuringBaseTypes), we cannot do it yet.
            # We would probably need to call the input_coversion code generation methods
            # of the according ConversionProviders here.
            # If the inner rest of the template is a pure libcpp_pair<int,int> for example,
            # cython can do it with a simple assignment automatically. See final else-case.
            raise Exception(
                "Recursion in std::vector<T> is not implemented for other STL methods and wrapped template arguments"
            )

        elif inner_contains_classes_to_wrap and tt.base_type == "libcpp_vector":
            # Case 4: We wrap a std::vector<> with a base type that contains
            #         further nested std::vector<> inside
            #         -> deal with recursion
            item = "%s_rec" % argument_var

            # A) Prepare the pre-call
            code = Code()
            if topmost_code is not None:
                if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
                    # add cdef statements for the iterators (part of B, post-call but needs to
                    # be on top)
                    code_top += "|cdef libcpp_vector[$inner].iterator $it"
                topmost_code.add(code_top, locals())
                code_top = ""
            if code_top != "":
                code.add(code_top, locals())

            cleanup_code = self._prepare_recursive_cleanup(
                cpp_type, bottommost_code, it_prev, temp_var, recursion_cnt, locals()
            )

            # Go into recursion (if possible)
            if hasattr(self, "cr"):
                self._perform_recursion(
                    cpp_type,
                    tt,
                    arg_num,
                    item,
                    topmost_code,
                    bottommost_code,
                    code,
                    cleanup_code,
                    recursion_cnt,
                    locals(),
                )
            else:
                raise Exception(
                    "Error: For recursion in std::vector<T> to work, we need a ConverterRegistry instance at self.cr"
                )

            return code, "deref(%s)" % temp_var, cleanup_code

        else:
            # Case 5: We wrap a regular type
            inner = self.converters.cython_type(tt)
            # cython cares for conversion of stl containers with std types:
            code = Code().add(
                """
                |cdef libcpp_vector[$inner] $temp_var = $argument_var
                """,
                locals(),
            )

            cleanup_code = Code().add("")
            if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
                cleanup_code = Code().add(
                    """
                    |$argument_var[:] = $temp_var
                    """,
                    locals(),
                )

            return code, "%s" % temp_var, cleanup_code

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        t = self.converters.cython_type(res_type)
        if t.is_ptr:
            return "_r = deref(%s)" % (cy_call_str)

        return "_r = %s" % (cy_call_str)

    def output_conversion(self, cpp_type: CppType, input_cpp_var: str, output_py_var: str) -> Code:
        (tt,) = cpp_type.template_args
        inner = self.converters.cython_type(tt)

        if inner.is_enum:
            it = mangle("it_" + input_cpp_var)
            code = Code().add(
                """
                |$output_py_var = []
                |cdef libcpp_vector[$inner].iterator $it = $input_cpp_var.begin()
                |while $it != $input_cpp_var.end():
                |   $output_py_var.append(<int>deref($it))
                |   inc($it)
                """,
                locals(),
            )
            return code

        # TODO recursion missing for outputting list[list[list..[WrappedClass]]..]
        elif tt.base_type in self.converters.names_of_wrapper_classes:
            cy_tt = tt.base_type
            inner = self.converters.cython_type(tt)
            it = mangle("it_" + input_cpp_var)
            item = mangle("item_" + output_py_var)

            instantiation = self._code_for_instantiate_object_from_iter(inner, it)
            code = Code().add(
                """
                |$output_py_var = []
                |cdef libcpp_vector[$inner].iterator $it = $input_cpp_var.begin()
                |cdef $cy_tt $item
                |while $it != $input_cpp_var.end():
                |   $item = $cy_tt.__new__($cy_tt)
                |   $item.inst = $instantiation
                |   $output_py_var.append($item)
                |   inc($it)
                """,
                locals(),
            )
            return code

        elif (
            tt.base_type == "shared_ptr"
            and len(set(tt.template_args[0].all_occuring_base_types())) == 1
        ):
            inner = self.converters.cython_type(tt)
            it = mangle("it_" + input_cpp_var)
            item = mangle("item_" + output_py_var)

            (base_type,) = tt.template_args
            (cpp_tt,) = inner.template_args

            code = Code().add(
                """
                |$output_py_var = []
                |cdef libcpp_vector[$inner].iterator $it = $input_cpp_var.begin()
                |cdef $base_type $item
                |while $it != $input_cpp_var.end():
                |   $item = $base_type.__new__($base_type)
                |   $item.inst = deref($it)
                |   $output_py_var.append($item)
                |   inc($it)
                """,
                locals(),
            )
            return code

        else:
            # cython cares for conversion of stl containers with std types:
            code = Code().add(
                """
                |cdef list $output_py_var = $input_cpp_var
                """,
                locals(),
            )
            return code


class StdVectorAsNumpyConverter(TypeConverterBase):
    """
    Converter for libcpp_vector_as_np - wraps std::vector<T> as numpy arrays.
    
    This converter uses a special type name 'libcpp_vector_as_np' in PXD files
    to distinguish from the standard list-based vector conversion.
    
    Key features:
    - For references (&): Returns numpy VIEW using Cython memory views (no copy)
      - For const refs: Sets readonly flag with setflags(write=False)
      - For non-const refs: Returns writable view
      - Memory view automatically keeps owner alive
    - For value returns: Uses ArrayWrapper with buffer protocol (single copy via swap)
    - For inputs: Accepts numpy arrays, creates temporary C++ vector
    - Supports nested vectors for 2D arrays
    - Uses fast memcpy for efficient data transfer
    
    Usage in PXD:
        from libcpp.vector cimport vector as libcpp_vector_as_np
        
        cdef extern from "mylib.hpp":
            cdef cppclass MyClass:
                libcpp_vector_as_np[double] getData()  # Returns numpy array
                void processData(libcpp_vector_as_np[double] data)  # Accepts numpy array
    """
    
    # Mapping of C++ types to numpy dtype strings
    NUMPY_DTYPE_MAP = {
        "float": "float32",
        "double": "float64", 
        "int8_t": "int8",
        "int16_t": "int16",
        "int": "int32",
        "int32_t": "int32",
        "int64_t": "int64",
        "long": "int64",
        "uint8_t": "uint8",
        "uint16_t": "uint16",
        "uint32_t": "uint32",
        "unsigned int": "uint32",
        "uint64_t": "uint64",
        "unsigned long": "uint64",
        "size_t": "uint64",
        "bool": "bool_",
    }
    
    # Map numpy dtypes to C types for memcpy
    CTYPE_MAP = {
        "float32": "float",
        "float64": "double",
        "int8": "int8_t",
        "int16": "int16_t",
        "int32": "int",
        "int64": "long",
        "uint8": "uint8_t",
        "uint16": "uint16_t",
        "uint32": "unsigned int",
        "uint64": "unsigned long",
        "bool_": "bool",
    }
    
    def get_base_types(self) -> List[str]:
        return ["libcpp_vector_as_np"]
    
    def matches(self, cpp_type: CppType) -> bool:
        """Match vectors of numeric types and nested vectors."""
        if not cpp_type.template_args:
            return False
        (tt,) = cpp_type.template_args
        
        # Check if inner type is a numeric type that numpy supports
        if tt.base_type in self.NUMPY_DTYPE_MAP:
            return True
        
        # Check if it's a nested vector
        if tt.base_type == "libcpp_vector_as_np" and tt.template_args:
            # Recursively check nested vector
            return self.matches(tt)
        
        return False
    
    def _get_numpy_dtype(self, cpp_type: CppType) -> str:
        """Get numpy dtype string for a C++ type."""
        return self.NUMPY_DTYPE_MAP.get(cpp_type.base_type, "float64")
    
    def _is_nested_vector(self, cpp_type: CppType) -> bool:
        """Check if this is a nested vector."""
        if not cpp_type.template_args:
            return False
        (tt,) = cpp_type.template_args
        return tt.base_type == "libcpp_vector_as_np"
    
    def matching_python_type(self, cpp_type: CppType) -> str:
        """Return Cython type for function signature.
        
        Use proper numpy.ndarray type annotations that Cython understands.
        This ensures only numpy arrays are accepted, not lists.
        """
        (tt,) = cpp_type.template_args
        
        if self._is_nested_vector(cpp_type):
            # For 2D arrays
            (inner_tt,) = tt.template_args
            dtype = self._get_numpy_dtype(inner_tt)
            return f"numpy.ndarray[numpy.{dtype}_t, ndim=2]"
        else:
            # For 1D arrays
            dtype = self._get_numpy_dtype(tt)
            return f"numpy.ndarray[numpy.{dtype}_t, ndim=1]"
    
    def matching_python_type_full(self, cpp_type: CppType) -> str:
        """Return type hint for type checkers (for docstrings).
        
        This provides proper numpy type hints for documentation and type checking tools.
        """
        (tt,) = cpp_type.template_args
        
        if self._is_nested_vector(cpp_type):
            # For 2D arrays, use proper NDArray type hint syntax
            (inner_tt,) = tt.template_args
            dtype = self._get_numpy_dtype(inner_tt)
            return f"numpy.ndarray[numpy.{dtype}_t, ndim=2]"
        else:
            # For 1D arrays, use proper NDArray type hint syntax
            dtype = self._get_numpy_dtype(tt)
            return f"numpy.ndarray[numpy.{dtype}_t, ndim=1]"
    
    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        """Check if argument is a numpy array (strict - no lists)."""
        # Only accept numpy arrays, not lists or other array-like objects
        return f"isinstance({argument_var}, numpy.ndarray)"
    
    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Code, str, Union[Code, str]]:
        """Convert numpy array to C++ vector for input parameters.
        
        The argument is already guaranteed to be a numpy array with the correct type
        thanks to Cython's type annotation, so we don't need to call asarray().
        """
        (tt,) = cpp_type.template_args
        temp_var = "v%d" % arg_num
        
        if self._is_nested_vector(cpp_type):
            # Handle nested vectors (2D arrays)
            (inner_tt,) = tt.template_args
            inner_type = self.converters.cython_type(inner_tt)
            outer_inner_type = self.converters.cython_type(tt)
            dtype = self._get_numpy_dtype(inner_tt)
            
            code = Code().add(
                """
                |# Convert 2D numpy array to nested C++ vector
                |cdef libcpp_vector[$outer_inner_type] * $temp_var = new libcpp_vector[$outer_inner_type]()
                |cdef size_t i_$arg_num, j_$arg_num
                |cdef libcpp_vector[$inner_type] row_$arg_num
                |for i_$arg_num in range($argument_var.shape[0]):
                |    row_$arg_num = libcpp_vector[$inner_type]()
                |    for j_$arg_num in range($argument_var.shape[1]):
                |        row_$arg_num.push_back(<$inner_type>$argument_var[i_$arg_num, j_$arg_num])
                |    $temp_var.push_back(row_$arg_num)
                """,
                dict(
                    argument_var=argument_var,
                    temp_var=temp_var,
                    inner_type=inner_type,
                    outer_inner_type=outer_inner_type,
                    dtype=dtype,
                    arg_num=arg_num,
                ),
            )
            cleanup = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup
        else:
            # Handle simple vectors (1D arrays)
            # No need for asarray() - Cython already ensures correct type
            inner_type = self.converters.cython_type(tt)
            dtype = self._get_numpy_dtype(tt)
            ctype = self.CTYPE_MAP.get(dtype, "double")
            
            code = Code().add(
                """
                |# Convert 1D numpy array to C++ vector (fast memcpy)
                |cdef libcpp_vector[$inner_type] * $temp_var = new libcpp_vector[$inner_type]()
                |cdef size_t n_$arg_num = $argument_var.shape[0]
                |$temp_var.resize(n_$arg_num)
                |if n_$arg_num > 0:
                |    memcpy($temp_var.data(), <void*>numpy.PyArray_DATA($argument_var), n_$arg_num * sizeof($ctype))
                """,
                dict(
                    argument_var=argument_var,
                    temp_var=temp_var,
                    inner_type=inner_type,
                    dtype=dtype,
                    arg_num=arg_num,
                    ctype=ctype,
                ),
            )
            
            cleanup = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup
    
    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        # For reference returns, use address() to get a pointer and avoid copying
        cy_res_type = self.converters.cython_type(res_type)  # type: CppType
        if cy_res_type.is_ref:
            # Create a copy of the type without the reference flag
            cy_ptr_type = cy_res_type.copy()
            cy_ptr_type.is_ref = False
            base_type_str = cy_ptr_type.toString(with_const)
            return "cdef %s * _r = address(%s)" % (base_type_str, cy_call_str)
        return "_r = %s" % cy_call_str
    
    def _get_wrapper_class_name(self, cpp_type: CppType) -> str:
        """Get the appropriate ArrayWrapper class name suffix for a type."""
        type_map = {
            "float": "Float",
            "double": "Double",
            "int8_t": "Int8",
            "int16_t": "Int16",
            "int32_t": "Int32",
            "int": "Int32",
            "int64_t": "Int64",
            "long": "Int64",
            "uint8_t": "UInt8",
            "uint16_t": "UInt16",
            "uint32_t": "UInt32",
            "unsigned int": "UInt32",
            "uint64_t": "UInt64",
            "unsigned long": "UInt64",
        }
        return type_map.get(cpp_type.base_type, "Double")
    
    def _get_numpy_type_enum(self, cpp_type: CppType) -> str:
        """Get the numpy type enum for PyArray_SimpleNewFromData."""
        type_map = {
            "float": "NPY_FLOAT32",
            "double": "NPY_FLOAT64",
            "int8_t": "NPY_INT8",
            "int16_t": "NPY_INT16",
            "int32_t": "NPY_INT32",
            "int": "NPY_INT32",
            "int64_t": "NPY_INT64",
            "long": "NPY_INT64",
            "uint8_t": "NPY_UINT8",
            "uint16_t": "NPY_UINT16",
            "uint32_t": "NPY_UINT32",
            "unsigned int": "NPY_UINT32",
            "uint64_t": "NPY_UINT64",
            "unsigned long": "NPY_UINT64",
            "bool": "NPY_BOOL",
        }
        return type_map.get(cpp_type.base_type, "NPY_FLOAT64")
    
    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[Code]:
        """Convert C++ vector to numpy array.
        
        Uses Cython memory views for references and ArrayWrapper for value returns:
        - For references: Create zero-copy view using Cython memory view syntax
        - For const references: Set readonly flag after creating view
        - For value returns: Use owning wrapper (data is already a copy)
        - Always set .base attribute to prevent garbage collection
        """
        (tt,) = cpp_type.template_args
        
        if self._is_nested_vector(cpp_type):
            # Handle nested vectors (2D arrays) - always copy for now
            (inner_tt,) = tt.template_args
            inner_type = self.converters.cython_type(inner_tt)
            dtype = self._get_numpy_dtype(inner_tt)
            ctype = self.CTYPE_MAP.get(dtype, "double")
            
            code = Code().add(
                """
                |# Convert nested C++ vector to 2D numpy array (copy)
                |cdef size_t n_rows = $input_cpp_var.size()
                |cdef size_t n_cols = $input_cpp_var[0].size() if n_rows > 0 else 0
                |cdef object $output_py_var = numpy.empty((n_rows, n_cols), dtype=numpy.$dtype)
                |cdef size_t i, j
                |cdef $ctype* row_ptr
                |for i in range(n_rows):
                |    row_ptr = <$ctype*>$input_cpp_var[i].data()
                |    for j in range(n_cols):
                |        $output_py_var[i, j] = row_ptr[j]
                """,
                dict(
                    input_cpp_var=input_cpp_var,
                    output_py_var=output_py_var,
                    inner_type=inner_type,
                    dtype=dtype,
                    ctype=ctype,
                ),
            )
            return code
        else:
            # Handle simple vectors (1D arrays)
            inner_type = self.converters.cython_type(tt)
            dtype = self._get_numpy_dtype(tt)
            ctype = self.CTYPE_MAP.get(dtype, "double")
            wrapper_suffix = self._get_wrapper_class_name(tt)
            
            # Check if this is a reference return (view opportunity)
            if cpp_type.is_ref:
                # Reference return: Use Cython memory view for zero-copy access
                # For const references: set readonly flag
                # Explicitly set .base to self to keep the owner alive (not the memory view)
                # Note: input_cpp_var is a pointer (from address() in call_method), so dereference it
                if cpp_type.is_const:
                    code = Code().add(
                        """
                        |# Convert C++ const vector reference to numpy array VIEW (zero-copy, readonly)
                        |cdef size_t _size_$output_py_var = deref($input_cpp_var).size()
                        |cdef numpy.npy_intp[1] _shape_$output_py_var
                        |_shape_$output_py_var[0] = <numpy.npy_intp>_size_$output_py_var
                        |cdef object $output_py_var = numpy.PyArray_SimpleNewFromData(1, _shape_$output_py_var, numpy.$npy_type, <void*>deref($input_cpp_var).data())
                        |$output_py_var.setflags(write=False)
                        |# Set base to self to keep owner alive
                        |Py_INCREF(self)
                        |numpy.PyArray_SetBaseObject(<numpy.ndarray>$output_py_var, <object>self)
                        """,
                        dict(
                            input_cpp_var=input_cpp_var,
                            output_py_var=output_py_var,
                            ctype=ctype,
                            npy_type=self._get_numpy_type_enum(tt),
                        ),
                    )
                else:
                    code = Code().add(
                        """
                        |# Convert C++ vector reference to numpy array VIEW (zero-copy, writable)
                        |cdef size_t _size_$output_py_var = deref($input_cpp_var).size()
                        |cdef numpy.npy_intp[1] _shape_$output_py_var
                        |_shape_$output_py_var[0] = <numpy.npy_intp>_size_$output_py_var
                        |cdef object $output_py_var = numpy.PyArray_SimpleNewFromData(1, _shape_$output_py_var, numpy.$npy_type, <void*>deref($input_cpp_var).data())
                        |# Set base to self to keep owner alive
                        |Py_INCREF(self)
                        |numpy.PyArray_SetBaseObject(<numpy.ndarray>$output_py_var, <object>self)
                        """,
                        dict(
                            input_cpp_var=input_cpp_var,
                            output_py_var=output_py_var,
                            ctype=ctype,
                            npy_type=self._get_numpy_type_enum(tt),
                        ),
                    )
                return code
            else:
                # Value return - use owning wrapper (data is already a copy via move/swap)
                code = Code().add(
                    """
                    |# Convert C++ vector to numpy array using owning wrapper (data already copied)
                    |cdef ArrayWrapper$wrapper_suffix _wrapper_$output_py_var = ArrayWrapper$wrapper_suffix()
                    |_wrapper_$output_py_var.set_data($input_cpp_var)
                    |cdef object $output_py_var = numpy.asarray(_wrapper_$output_py_var)
                    """,
                    dict(
                        input_cpp_var=input_cpp_var,
                        output_py_var=output_py_var,
                        wrapper_suffix=wrapper_suffix,
                    ),
                )
                return code


class StdStringConverter(TypeConverterBase):
    """
    This converter deals with functions that expect/return a C++ std::string.
    It expects and returns bytes on the python side.
    Note that this provider will NOT be picked up if it is located inside
    a container (e.g. std::vector aka libcpp_vector). However, it can and
    should be used to indicate the correct typing for the automatic
    conversion by Cython, which is set to bytes in autowrap.
    """

    def get_base_types(self) -> List[str]:
        return ["libcpp_string"]

    def matches(self, cpp_type: CppType) -> bool:
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "bytes"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        return "bytes"

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[str, str, str]:
        code = ""
        call_as = "(<libcpp_string>%s)" % argument_var
        cleanup = ""
        return code, call_as, cleanup

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        return "isinstance(%s, bytes)" % argument_var

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[str]:
        return "%s = <libcpp_string>%s" % (output_py_var, input_cpp_var)


# TODO I think we have to be more clear about the use case of this ConvProv
#  Currently it can be used if you don't know if the incoming
#  py type is bytes or unicode. We currently have no provider that allows
#  for specifically unicode only.
class StdStringUnicodeConverter(StdStringConverter):
    """
    This converter deals with functions that expect a C++ std::string.
    Note that this provider will NOT be picked up if it is located inside
    a container (e.g. std::vector aka libcpp_vector). Please use the usual
    StdStringConverter to at least get the typing right.
    It can only be used in function parameters (i.e. input).
    It can handle both bytes and unicode strings and converts to bytes internally.
    """

    def get_base_types(self) -> List[str]:
        return ["libcpp_utf8_string"]

    def matching_python_type(self, cpp_type: CppType) -> str:
        return ""  # TODO can we use "basestring"?

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        return "Union[bytes, str]"

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Code, str, str]:
        code = Code()
        # although python3 does not have "unicode" as a built-in type anymore,
        # Cython understands it and uses the Py_IsUnicodeCheck
        code.add(
            """
            |if isinstance($argument_var, str):
            |    $argument_var = $argument_var.encode('utf-8')
            """,
            locals(),
        )
        call_as = "(<libcpp_string>%s)" % argument_var
        cleanup = ""
        return code, call_as, cleanup

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        return "isinstance(%s, (bytes, str))" % argument_var


class StdStringUnicodeOutputConverter(StdStringUnicodeConverter):
    """
    This converter deals with functions that return a C++ std::string.
    Note that this provider will NOT be picked up if it is located inside
    a container (e.g. std::vector aka libcpp_vector). Please use the usual
    StdStringConverter to at least get the typing right.
    It should only be used in function returns (i.e. output).
    It returns unicode strings to python and therefore expects the C++
    function to return something that is decodable from utf8 (including ascii)
    """

    def get_base_types(self) -> List[str]:
        return ["libcpp_utf8_output_string"]

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        return "str"  # python3

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[str]:
        return "%s = %s.decode('utf-8')" % (output_py_var, input_cpp_var)


class SharedPtrConverter(TypeConverterBase):
    """
    This converter deals with functions that expect a shared_ptr[BaseClass] as
    an argument. For this to work, BaseClass needs to have a Python type and
    thus the expected pointer already exists at BaseClass.inst => all we need
    to do is to pass this inst shared_ptr to the function.
    """

    def get_base_types(self) -> List[str]:
        return ["shared_ptr"]

    def matches(self, cpp_type: CppType) -> bool:
        (tt,) = cpp_type.template_args
        return tt in self.converters.names_of_wrapper_classes

    def matching_python_type(self, cpp_type: CppType) -> str:
        (tt,) = cpp_type.template_args
        return str(tt)

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        (tt,) = cpp_type.template_args
        inner = self.converters.get(tt)
        return inner.matching_python_type_full(tt)

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Code, str, Union[Code, str]]:
        (tt,) = cpp_type.template_args
        inner = self.converters.cython_type(tt)
        # Cython expects us to get a C++ type (we cannot just stick var.inst into the function)
        code = Code().add(
            """
            |cdef shared_ptr[$inner] input_$argument_var = $argument_var.inst
            """,
            locals(),
        )
        call_as = "input_" + argument_var
        cleanup = ""
        # Put the pointer back if we pass by reference
        if cpp_type.is_ref and not cpp_type.is_const:
            cleanup = Code().add(
                """
                |$argument_var.inst = input_$argument_var
                """,
                locals(),
            )
        return code, call_as, cleanup

    def type_check_expression(self, cpp_type: CppType, argument_var: str) -> str:
        # We can just use the Python type of the template argument
        (tt,) = cpp_type.template_args
        return "isinstance(%s, %s)" % (argument_var, tt)

    def output_conversion(self, cpp_type: CppType, input_cpp_var: str, output_py_var: str) -> Code:
        # L.info("Output conversion for %s" % (cpp_type))
        (tt,) = cpp_type.template_args
        code = Code()
        if tt.is_const:
            # If the template argument is constant, we need to have non-const base-types for our code
            inner = self.converters.cython_type(tt).toString(False)
            tt = tt.toString(withConst=False)
            code.add(
                """
                     |# Const shared_ptr detected, we need to produce a non-const copy to stick into Python object
                     |cdef $inner * raw_$input_cpp_var = new $inner((deref(<$inner * const>$input_cpp_var.get())))
                     |cdef $tt py_result
                     |$output_py_var = $tt.__new__($tt)
                     |$output_py_var.inst = shared_ptr[$inner](raw_$input_cpp_var) """,
                locals(),
            )
        else:
            code.add(
                """
                |cdef $tt py_result
                |$output_py_var = $tt.__new__($tt)
                |$output_py_var.inst = $input_cpp_var""",
                locals(),
            )
        return code


# =============================================================================
# New STL Container Converters (C++11/14/17/20)
# =============================================================================


class StdUnorderedMapConverter(TypeConverterBase):
    """
    Converter for std::unordered_map<K, V> - hash-based map with O(1) average lookup.
    Maps to Python dict.

    Input conversion: Python dict -> std::unordered_map (iterates and inserts)
    Output conversion: std::unordered_map -> Python dict (iterates and copies)

    Supports reference parameters - modifications to the map in C++ are
    reflected back to the Python dict after the call.

    Example PXD declaration:
        libcpp_unordered_map[libcpp_string, int] getData()
        void processData(libcpp_unordered_map[libcpp_string, int]& data)

    Example Python usage:
        data = obj.getData()           # Returns dict
        obj.processData({b"key": 42})  # Pass dict
    """

    def get_base_types(self) -> List[str]:
        return ["libcpp_unordered_map"]

    def matches(self, cpp_type: CppType) -> bool:
        return True

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "dict"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        tt_key, tt_value = cpp_type.template_args
        inner_conv_1 = self.converters.get(tt_key)
        inner_conv_2 = self.converters.get(tt_value)
        return "Dict[%s, %s]" % (
            inner_conv_1.matching_python_type_full(tt_key),
            inner_conv_2.matching_python_type_full(tt_value),
        )

    def type_check_expression(self, cpp_type, arg_var):
        tt_key, tt_value = cpp_type.template_args
        inner_conv_1 = self.converters.get(tt_key)
        inner_conv_2 = self.converters.get(tt_value)
        assert inner_conv_1 is not None, "arg type %s not supported" % tt_key
        assert inner_conv_2 is not None, "arg type %s not supported" % tt_value

        inner_check_1 = inner_conv_1.type_check_expression(tt_key, "k")
        inner_check_2 = inner_conv_2.type_check_expression(tt_value, "v")

        return (
            Code()
            .add(
                """
          |isinstance($arg_var, dict)
          + and all($inner_check_1 for k in $arg_var.keys())
          + and all($inner_check_2 for v in $arg_var.values())
          """,
                locals(),
            )
            .render()
        )

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Code, str, Union[Code, str]]:
        tt_key, tt_value = cpp_type.template_args
        temp_var = "v%d" % arg_num

        code = Code()

        cy_tt_key = self.converters.cython_type(tt_key)
        cy_tt_value = self.converters.cython_type(tt_value)

        # Use mangled variable names to avoid collision with function parameters
        loop_key = mangle("_loop_key_" + argument_var)
        loop_value = mangle("_loop_value_" + argument_var)

        if cy_tt_value.is_enum:
            value_conv = "<%s> %s" % (cy_tt_value, loop_value)
        elif tt_value.base_type in self.converters.names_of_wrapper_classes:
            value_conv = "deref((<%s>%s).inst.get())" % (tt_value.base_type, loop_value)
        else:
            value_conv = "<%s> %s" % (cy_tt_value, loop_value)

        if cy_tt_key.is_enum:
            key_conv = "<%s> %s" % (cy_tt_key, loop_key)
        elif tt_key.base_type in self.converters.names_of_wrapper_classes:
            key_conv = "deref(<%s *> (<%s> %s).inst.get())" % (cy_tt_key, tt_key, loop_key)
        else:
            key_conv = "<%s> %s" % (cy_tt_key, loop_key)

        code.add(
            """
            |cdef libcpp_unordered_map[$cy_tt_key, $cy_tt_value] * $temp_var = new
            + libcpp_unordered_map[$cy_tt_key, $cy_tt_value]()

            |for $loop_key, $loop_value in $argument_var.items():
            |    deref($temp_var)[ $key_conv ] = $value_conv
            """,
            locals(),
        )

        if cpp_type.is_ref and not cpp_type.is_const:
            it = mangle("it_" + argument_var)
            py_tt_key = tt_key

            key_conv_out = "<%s> deref(%s).first" % (cy_tt_key, it)

            # Handle key that is wrapped
            if (
                tt_key.base_type in self.converters.names_of_wrapper_classes
                and not tt_value.base_type in self.converters.names_of_wrapper_classes
            ):
                value_conv_out = "<%s> deref(%s).second" % (cy_tt_value, it)
                item_key = mangle("itemk_" + argument_var)
                cleanup_code = Code().add(
                    """
                    |replace = dict()
                    |cdef libcpp_unordered_map[$cy_tt_key, $cy_tt_value].iterator $it = $temp_var.begin()
                    |cdef $py_tt_key $item_key
                    |while $it != $temp_var.end():
                    |   $item_key = $py_tt_key.__new__($py_tt_key)
                    |   $item_key.inst = shared_ptr[$cy_tt_key](new $cy_tt_key((deref($it)).first))
                    |   replace[$item_key] = $value_conv_out
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """,
                    locals(),
                )
            # Handle value that is wrapped
            elif (
                not cy_tt_value.is_enum
                and tt_value.base_type in self.converters.names_of_wrapper_classes
                and not tt_key.base_type in self.converters.names_of_wrapper_classes
            ):
                cy_tt = tt_value.base_type
                item = mangle("item_" + argument_var)
                cleanup_code = Code().add(
                    """
                    |replace = dict()
                    |cdef libcpp_unordered_map[$cy_tt_key, $cy_tt_value].iterator $it = $temp_var.begin()
                    |cdef $cy_tt $item
                    |while $it != $temp_var.end():
                    |   $item = $cy_tt.__new__($cy_tt)
                    |   $item.inst = shared_ptr[$cy_tt_value](new $cy_tt_value((deref($it)).second))
                    |   replace[$key_conv_out] = $item
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """,
                    locals(),
                )
            # Handle both key AND value that are wrapped
            elif (
                not cy_tt_value.is_enum
                and tt_value.base_type in self.converters.names_of_wrapper_classes
                and tt_key.base_type in self.converters.names_of_wrapper_classes
            ):
                cy_tt = tt_value.base_type
                item_val = mangle("itemv_" + argument_var)
                item_key = mangle("itemk_" + argument_var)
                cleanup_code = Code().add(
                    """
                    |replace = dict()
                    |cdef libcpp_unordered_map[$cy_tt_key, $cy_tt_value].iterator $it = $temp_var.begin()
                    |cdef $py_tt_key $item_key
                    |cdef $cy_tt $item_val
                    |while $it != $temp_var.end():
                    |   $item_key = $py_tt_key.__new__($py_tt_key)
                    |   $item_key.inst = shared_ptr[$cy_tt_key](new $cy_tt_key((deref($it)).first))
                    |   $item_val = $cy_tt.__new__($cy_tt)
                    |   $item_val.inst = shared_ptr[$cy_tt_value](new $cy_tt_value((deref($it)).second))
                    |   replace[$item_key] = $item_val
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """,
                    locals(),
                )
            else:
                value_conv_out = "<%s> deref(%s).second" % (cy_tt_value, it)
                cleanup_code = Code().add(
                    """
                    |replace = dict()
                    |cdef libcpp_unordered_map[$cy_tt_key, $cy_tt_value].iterator $it = $temp_var.begin()
                    |while $it != $temp_var.end():
                    |   replace[$key_conv_out] = $value_conv_out
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """,
                    locals(),
                )
        else:
            cleanup_code = "del %s" % temp_var

        return code, "deref(%s)" % temp_var, cleanup_code

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        return "_r = %s" % cy_call_str

    def output_conversion(self, cpp_type: CppType, input_cpp_var: str, output_py_var: str) -> Code:
        assert not cpp_type.is_ptr

        tt_key, tt_value = cpp_type.template_args
        cy_tt_key = self.converters.cython_type(tt_key)
        cy_tt_value = self.converters.cython_type(tt_value)
        py_tt_key = tt_key

        it = mangle("it_" + input_cpp_var)

        # Both key and value are wrapped classes
        if (
            not cy_tt_value.is_enum
            and tt_value.base_type in self.converters.names_of_wrapper_classes
        ) and (
            not cy_tt_key.is_enum and tt_key.base_type in self.converters.names_of_wrapper_classes
        ):
            cy_tt_val = tt_value.base_type
            cy_tt_k = tt_key.base_type
            item_key = mangle("itemk_" + output_py_var)
            item_val = mangle("itemv_" + output_py_var)
            code = Code().add(
                """
                |$output_py_var = dict()
                |cdef libcpp_unordered_map[$cy_tt_key, $cy_tt_value].iterator $it = $input_cpp_var.begin()
                |cdef $cy_tt_k $item_key
                |cdef $cy_tt_val $item_val
                |while $it != $input_cpp_var.end():
                |   $item_key = $cy_tt_k.__new__($cy_tt_k)
                |   $item_key.inst = shared_ptr[$cy_tt_key](new $cy_tt_key((deref($it)).first))
                |   $item_val = $cy_tt_val.__new__($cy_tt_val)
                |   $item_val.inst = shared_ptr[$cy_tt_value](new $cy_tt_value((deref($it)).second))
                |   $output_py_var[$item_key] = $item_val
                |   inc($it)
                """,
                locals(),
            )
            return code

        # Only key is wrapped
        elif not cy_tt_key.is_enum and tt_key.base_type in self.converters.names_of_wrapper_classes:
            value_conv = "<%s>(deref(%s).second)" % (cy_tt_value, it)
            item_key = mangle("itemk_" + output_py_var)
            code = Code().add(
                """
                |$output_py_var = dict()
                |cdef libcpp_unordered_map[$cy_tt_key, $cy_tt_value].iterator $it = $input_cpp_var.begin()
                |cdef $py_tt_key $item_key
                |while $it != $input_cpp_var.end():
                |   $item_key = $py_tt_key.__new__($py_tt_key)
                |   $item_key.inst = shared_ptr[$cy_tt_key](new $cy_tt_key((deref($it)).first))
                |   $output_py_var[$item_key] = $value_conv
                |   inc($it)
                """,
                locals(),
            )
            return code

        # Only value is wrapped
        elif (
            not cy_tt_value.is_enum
            and tt_value.base_type in self.converters.names_of_wrapper_classes
        ):
            cy_tt = tt_value.base_type
            key_conv = "<%s>(deref(%s).first)" % (cy_tt_key, it)
            item = mangle("item_" + output_py_var)
            code = Code().add(
                """
                |$output_py_var = dict()
                |cdef libcpp_unordered_map[$cy_tt_key, $cy_tt_value].iterator $it = $input_cpp_var.begin()
                |cdef $cy_tt $item
                |while $it != $input_cpp_var.end():
                |   $item = $cy_tt.__new__($cy_tt)
                |   $item.inst = shared_ptr[$cy_tt_value](new $cy_tt_value((deref($it)).second))
                |   $output_py_var[$key_conv] = $item
                |   inc($it)
                """,
                locals(),
            )
            return code

        # Neither key nor value is wrapped
        else:
            key_conv = "<%s>(deref(%s).first)" % (cy_tt_key, it)
            value_conv = "<%s>(deref(%s).second)" % (cy_tt_value, it)
            code = Code().add(
                """
                |$output_py_var = dict()
                |cdef libcpp_unordered_map[$cy_tt_key, $cy_tt_value].iterator $it = $input_cpp_var.begin()
                |while $it != $input_cpp_var.end():
                |   $output_py_var[$key_conv] = $value_conv
                |   inc($it)
                """,
                locals(),
            )
            return code


class StdUnorderedSetConverter(TypeConverterBase):
    """
    Converter for std::unordered_set<T> - hash-based set with O(1) average lookup.
    Maps to Python set.

    Input conversion: Python set -> std::unordered_set (iterates and inserts)
    Output conversion: std::unordered_set -> Python set (iterates and copies)

    Supports reference parameters - modifications to the set in C++ are
    reflected back to the Python set after the call.

    Example PXD declaration:
        libcpp_unordered_set[int] getValues()
        int countUnique(libcpp_unordered_set[int]& values)

    Example Python usage:
        values = obj.getValues()       # Returns set
        count = obj.countUnique({1, 2, 3})  # Pass set
    """

    def get_base_types(self) -> List[str]:
        return ["libcpp_unordered_set"]

    def matches(self, cpp_type: CppType) -> bool:
        return True

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "set"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        (tt,) = cpp_type.template_args
        inner_conv = self.converters.get(tt)
        return "Set[%s]" % inner_conv.matching_python_type_full(tt)

    def type_check_expression(self, cpp_type, arg_var):
        (tt,) = cpp_type.template_args
        inner_conv = self.converters.get(tt)
        assert inner_conv is not None, "arg type %s not supported" % tt
        inner_check = inner_conv.type_check_expression(tt, "li")

        return (
            Code()
            .add(
                """
          |isinstance($arg_var, set) and all($inner_check for li in $arg_var)
          """,
                locals(),
            )
            .render()
        )

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Code, str, Union[Code, str]]:
        (tt,) = cpp_type.template_args
        temp_var = "v%d" % arg_num
        inner = self.converters.cython_type(tt)
        it = mangle("it_" + argument_var)

        if inner.is_enum:
            item = "item%d" % arg_num
            code = Code().add(
                """
                |cdef libcpp_unordered_set[$inner] * $temp_var = new libcpp_unordered_set[$inner]()
                |cdef int $item
                |for $item in $argument_var:
                |   $temp_var.insert(<$inner> $item)
                """,
                locals(),
            )
            if cpp_type.is_ref and not cpp_type.is_const:
                cleanup_code = Code().add(
                    """
                    |replace = set()
                    |cdef libcpp_unordered_set[$inner].iterator $it = $temp_var.begin()
                    |while $it != $temp_var.end():
                    |   replace.add(<int> deref($it))
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """,
                    locals(),
                )
            else:
                cleanup_code = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup_code

        elif tt.base_type in self.converters.names_of_wrapper_classes:
            base_type = tt.base_type
            do_deref = "deref" if not inner.is_ptr else ""
            cy_tt = tt.base_type
            item = "item%d" % arg_num
            code = Code().add(
                """
                |cdef libcpp_unordered_set[$inner] * $temp_var = new libcpp_unordered_set[$inner]()
                |cdef $base_type $item
                |for $item in $argument_var:
                |   $temp_var.insert($do_deref($item.inst.get()))
                """,
                locals(),
            )
            if cpp_type.is_ref and not cpp_type.is_const:
                item_out = mangle("item_" + argument_var)
                cleanup_code = Code().add(
                    """
                    |replace = set()
                    |cdef libcpp_unordered_set[$inner].iterator $it = $temp_var.begin()
                    |cdef $cy_tt $item_out
                    |while $it != $temp_var.end():
                    |   $item_out = $cy_tt.__new__($cy_tt)
                    |   $item_out.inst = shared_ptr[$inner](new $inner(deref($it)))
                    |   replace.add($item_out)
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """,
                    locals(),
                )
            else:
                cleanup_code = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup_code
        else:
            # Primitive types - need explicit iteration
            item = "item%d" % arg_num
            code = Code().add(
                """
                |cdef libcpp_unordered_set[$inner] * $temp_var = new libcpp_unordered_set[$inner]()
                |for $item in $argument_var:
                |   $temp_var.insert(<$inner> $item)
                """,
                locals(),
            )
            if cpp_type.is_ref and not cpp_type.is_const:
                cleanup_code = Code().add(
                    """
                    |replace = set()
                    |cdef libcpp_unordered_set[$inner].iterator $it = $temp_var.begin()
                    |while $it != $temp_var.end():
                    |   replace.add(<$inner> deref($it))
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """,
                    locals(),
                )
            else:
                cleanup_code = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup_code

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        return "_r = %s" % cy_call_str

    def output_conversion(self, cpp_type: CppType, input_cpp_var: str, output_py_var: str) -> Code:
        assert not cpp_type.is_ptr

        (tt,) = cpp_type.template_args
        inner = self.converters.cython_type(tt)
        it = mangle("it_" + input_cpp_var)

        if inner.is_enum:
            code = Code().add(
                """
                |$output_py_var = set()
                |cdef libcpp_unordered_set[$inner].iterator $it = $input_cpp_var.begin()
                |while $it != $input_cpp_var.end():
                |   $output_py_var.add(<int>deref($it))
                |   inc($it)
                """,
                locals(),
            )
            return code
        elif tt.base_type in self.converters.names_of_wrapper_classes:
            cy_tt = tt.base_type
            item = mangle("item_" + output_py_var)
            code = Code().add(
                """
                |$output_py_var = set()
                |cdef libcpp_unordered_set[$inner].iterator $it = $input_cpp_var.begin()
                |cdef $cy_tt $item
                |while $it != $input_cpp_var.end():
                |   $item = $cy_tt.__new__($cy_tt)
                |   $item.inst = shared_ptr[$inner](new $inner(deref($it)))
                |   $output_py_var.add($item)
                |   inc($it)
                """,
                locals(),
            )
            return code
        else:
            # Primitive types - need explicit iteration
            code = Code().add(
                """
                |$output_py_var = set()
                |cdef libcpp_unordered_set[$inner].iterator $it = $input_cpp_var.begin()
                |while $it != $input_cpp_var.end():
                |   $output_py_var.add(<$inner>deref($it))
                |   inc($it)
                """,
                locals(),
            )
            return code


class StdDequeConverter(TypeConverterBase):
    """
    Converter for std::deque<T> - double-ended queue with O(1) access at both ends.
    Maps to Python list.

    Input conversion: Python list -> std::deque (iterates and push_back)
    Output conversion: std::deque -> Python list (uses at() for indexed access)

    Supports reference parameters - modifications to the deque in C++ are
    reflected back to the Python list after the call.

    Note: While Python has collections.deque, we use list for simplicity and
    compatibility with existing autowrap patterns.

    Example PXD declaration:
        libcpp_deque[int] getItems()
        int processQueue(libcpp_deque[int]& items)

    Example Python usage:
        items = obj.getItems()         # Returns list
        obj.processQueue([1, 2, 3])    # Pass list
    """

    def get_base_types(self) -> List[str]:
        return ["libcpp_deque"]

    def matches(self, cpp_type: CppType) -> bool:
        return True

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "list"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        (tt,) = cpp_type.template_args
        inner_conv = self.converters.get(tt)
        return "List[%s]" % inner_conv.matching_python_type_full(tt)

    def type_check_expression(self, cpp_type, arg_var):
        (tt,) = cpp_type.template_args
        inner_conv = self.converters.get(tt)
        assert inner_conv is not None, "arg type %s not supported" % tt
        inner_check = inner_conv.type_check_expression(tt, "li")
        return (
            Code()
            .add(
                """
          |isinstance($arg_var, list) and all($inner_check for li in $arg_var)
          """,
                locals(),
            )
            .render()
        )

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Code, str, Union[Code, str]]:
        (tt,) = cpp_type.template_args
        temp_var = "v%d" % arg_num
        inner = self.converters.cython_type(tt)
        it = mangle("it_" + argument_var)

        if inner.is_enum:
            item = "item%d" % arg_num
            code = Code().add(
                """
                |cdef libcpp_deque[$inner] * $temp_var = new libcpp_deque[$inner]()
                |cdef int $item
                |for $item in $argument_var:
                |   $temp_var.push_back(<$inner> $item)
                """,
                locals(),
            )
            if cpp_type.is_ref and not cpp_type.is_const:
                cleanup_code = Code().add(
                    """
                    |$argument_var[:] = [<int>$temp_var.at(i) for i in range($temp_var.size())]
                    |del $temp_var
                    """,
                    locals(),
                )
            else:
                cleanup_code = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup_code

        elif tt.base_type in self.converters.names_of_wrapper_classes:
            base_type = tt.base_type
            do_deref = "deref" if not inner.is_ptr else ""
            cy_tt = tt.base_type
            item = "item%d" % arg_num
            code = Code().add(
                """
                |cdef libcpp_deque[$inner] * $temp_var = new libcpp_deque[$inner]()
                |cdef $base_type $item
                |for $item in $argument_var:
                |   $temp_var.push_back($do_deref($item.inst.get()))
                """,
                locals(),
            )
            cleanup_code = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup_code
        else:
            # Primitive types - need explicit iteration
            item = "item%d" % arg_num
            code = Code().add(
                """
                |cdef libcpp_deque[$inner] $temp_var
                |for $item in $argument_var:
                |   $temp_var.push_back(<$inner> $item)
                """,
                locals(),
            )
            cleanup_code = ""
            if cpp_type.is_ref and not cpp_type.is_const:
                cleanup_code = Code().add(
                    """
                    |$argument_var[:] = [<$inner>$temp_var.at(i) for i in range($temp_var.size())]
                    """,
                    locals(),
                )
            return code, "%s" % temp_var, cleanup_code

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        return "_r = %s" % cy_call_str

    def output_conversion(self, cpp_type: CppType, input_cpp_var: str, output_py_var: str) -> Code:
        assert not cpp_type.is_ptr

        (tt,) = cpp_type.template_args
        inner = self.converters.cython_type(tt)

        if inner.is_enum:
            code = Code().add(
                """
                |$output_py_var = [<int>$input_cpp_var.at(i) for i in range($input_cpp_var.size())]
                """,
                locals(),
            )
            return code
        elif tt.base_type in self.converters.names_of_wrapper_classes:
            cy_tt = tt.base_type
            item = mangle("item_" + output_py_var)
            code = Code().add(
                """
                |$output_py_var = []
                |cdef $cy_tt $item
                |for i in range($input_cpp_var.size()):
                |   $item = $cy_tt.__new__($cy_tt)
                |   $item.inst = shared_ptr[$inner](new $inner($input_cpp_var.at(i)))
                |   $output_py_var.append($item)
                """,
                locals(),
            )
            return code
        else:
            # Primitive types - need explicit at() access
            code = Code().add(
                """
                |$output_py_var = [<$inner>$input_cpp_var.at(i) for i in range($input_cpp_var.size())]
                """,
                locals(),
            )
            return code


class StdListConverter(TypeConverterBase):
    """
    Converter for std::list<T> - doubly linked list with O(1) insertion/deletion.
    Maps to Python list.

    Input conversion: Python list -> std::list (iterates and push_back)
    Output conversion: std::list -> Python list (iterates using iterators)

    Supports reference parameters - modifications to the list in C++ are
    reflected back to the Python list after the call.

    Note: std::list provides O(1) insertion/deletion but O(n) random access.
    The Python list interface doesn't expose these characteristics.

    Example PXD declaration:
        libcpp_list[double] getValues()
        double sumValues(libcpp_list[double]& values)

    Example Python usage:
        values = obj.getValues()           # Returns list
        total = obj.sumValues([1.0, 2.0])  # Pass list
    """

    def get_base_types(self) -> List[str]:
        return ["libcpp_list"]

    def matches(self, cpp_type: CppType) -> bool:
        return True

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "list"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        (tt,) = cpp_type.template_args
        inner_conv = self.converters.get(tt)
        return "List[%s]" % inner_conv.matching_python_type_full(tt)

    def type_check_expression(self, cpp_type, arg_var):
        (tt,) = cpp_type.template_args
        inner_conv = self.converters.get(tt)
        assert inner_conv is not None, "arg type %s not supported" % tt
        inner_check = inner_conv.type_check_expression(tt, "li")
        return (
            Code()
            .add(
                """
          |isinstance($arg_var, list) and all($inner_check for li in $arg_var)
          """,
                locals(),
            )
            .render()
        )

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Code, str, Union[Code, str]]:
        (tt,) = cpp_type.template_args
        temp_var = "v%d" % arg_num
        inner = self.converters.cython_type(tt)
        it = mangle("it_" + argument_var)

        if inner.is_enum:
            item = "item%d" % arg_num
            code = Code().add(
                """
                |cdef libcpp_list[$inner] * $temp_var = new libcpp_list[$inner]()
                |cdef int $item
                |for $item in $argument_var:
                |   $temp_var.push_back(<$inner> $item)
                """,
                locals(),
            )
            if cpp_type.is_ref and not cpp_type.is_const:
                cleanup_code = Code().add(
                    """
                    |$argument_var[:] = []
                    |cdef libcpp_list[$inner].iterator $it = $temp_var.begin()
                    |while $it != $temp_var.end():
                    |   $argument_var.append(<int>deref($it))
                    |   inc($it)
                    |del $temp_var
                    """,
                    locals(),
                )
            else:
                cleanup_code = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup_code

        elif tt.base_type in self.converters.names_of_wrapper_classes:
            base_type = tt.base_type
            do_deref = "deref" if not inner.is_ptr else ""
            cy_tt = tt.base_type
            item = "item%d" % arg_num
            code = Code().add(
                """
                |cdef libcpp_list[$inner] * $temp_var = new libcpp_list[$inner]()
                |cdef $base_type $item
                |for $item in $argument_var:
                |   $temp_var.push_back($do_deref($item.inst.get()))
                """,
                locals(),
            )
            cleanup_code = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup_code
        else:
            code = Code().add(
                """
                |cdef libcpp_list[$inner] $temp_var
                |for item in $argument_var:
                |   $temp_var.push_back(item)
                """,
                locals(),
            )
            cleanup_code = ""
            if cpp_type.is_ref and not cpp_type.is_const:
                cleanup_code = Code().add(
                    """
                    |$argument_var[:] = []
                    |cdef libcpp_list[$inner].iterator $it = $temp_var.begin()
                    |while $it != $temp_var.end():
                    |   $argument_var.append(deref($it))
                    |   inc($it)
                    """,
                    locals(),
                )
            return code, "%s" % temp_var, cleanup_code

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        return "_r = %s" % cy_call_str

    def output_conversion(self, cpp_type: CppType, input_cpp_var: str, output_py_var: str) -> Code:
        assert not cpp_type.is_ptr

        (tt,) = cpp_type.template_args
        inner = self.converters.cython_type(tt)
        it = mangle("it_" + input_cpp_var)

        if inner.is_enum:
            code = Code().add(
                """
                |$output_py_var = []
                |cdef libcpp_list[$inner].iterator $it = $input_cpp_var.begin()
                |while $it != $input_cpp_var.end():
                |   $output_py_var.append(<int>deref($it))
                |   inc($it)
                """,
                locals(),
            )
            return code
        elif tt.base_type in self.converters.names_of_wrapper_classes:
            cy_tt = tt.base_type
            item = mangle("item_" + output_py_var)
            code = Code().add(
                """
                |$output_py_var = []
                |cdef libcpp_list[$inner].iterator $it = $input_cpp_var.begin()
                |cdef $cy_tt $item
                |while $it != $input_cpp_var.end():
                |   $item = $cy_tt.__new__($cy_tt)
                |   $item.inst = shared_ptr[$inner](new $inner(deref($it)))
                |   $output_py_var.append($item)
                |   inc($it)
                """,
                locals(),
            )
            return code
        else:
            code = Code().add(
                """
                |$output_py_var = []
                |cdef libcpp_list[$inner].iterator $it = $input_cpp_var.begin()
                |while $it != $input_cpp_var.end():
                |   $output_py_var.append(deref($it))
                |   inc($it)
                """,
                locals(),
            )
            return code


class StdOptionalConverter(TypeConverterBase):
    """
    Converter for std::optional<T> (C++17) - represents an optional value.
    Maps to T | None in Python.

    Input conversion:
        - Python None -> empty std::optional (std::nullopt)
        - Python value of type T -> std::optional containing the value

    Output conversion:
        - Empty std::optional (has_value() == false) -> Python None
        - std::optional with value -> the contained value

    Note: The function signature uses 'object' type to allow None to be passed.
    Type validation is performed at runtime via the type_check_expression.
    The docstring correctly shows Optional[T] for documentation purposes.

    Example PXD declaration:
        libcpp_optional[int] getValue(bool hasValue)
        int processValue(libcpp_optional[int] opt)

    Example Python usage:
        result = obj.getValue(True)   # Returns int or None
        obj.processValue(42)          # Pass a value
        obj.processValue(None)        # Pass empty optional
    """

    def get_base_types(self) -> List[str]:
        return ["libcpp_optional"]

    def matches(self, cpp_type: CppType) -> bool:
        return True

    def matching_python_type(self, cpp_type: CppType) -> str:
        # Return 'object' to allow None to be passed as a parameter.
        # The type_check_expression validates the actual type at runtime.
        return "object"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        (tt,) = cpp_type.template_args
        inner_conv = self.converters.get(tt)
        return "Optional[%s]" % inner_conv.matching_python_type_full(tt)

    def type_check_expression(self, cpp_type, arg_var):
        (tt,) = cpp_type.template_args
        inner_conv = self.converters.get(tt)
        assert inner_conv is not None, "arg type %s not supported" % tt
        inner_check = inner_conv.type_check_expression(tt, arg_var)
        return "(%s is None or %s)" % (arg_var, inner_check)

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Code, str, Union[Code, str]]:
        (tt,) = cpp_type.template_args
        temp_var = "v%d" % arg_num
        inner = self.converters.cython_type(tt)

        if tt.base_type in self.converters.names_of_wrapper_classes:
            cy_tt = tt.base_type
            code = Code().add(
                """
                |cdef libcpp_optional[$inner] $temp_var
                |if $argument_var is not None:
                |   $temp_var = libcpp_optional[$inner](deref((<$cy_tt>$argument_var).inst.get()))
                """,
                locals(),
            )
        else:
            code = Code().add(
                """
                |cdef libcpp_optional[$inner] $temp_var
                |if $argument_var is not None:
                |   $temp_var = libcpp_optional[$inner](<$inner>$argument_var)
                """,
                locals(),
            )
        return code, temp_var, ""

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        return "_r = %s" % cy_call_str

    def output_conversion(self, cpp_type: CppType, input_cpp_var: str, output_py_var: str) -> Code:
        (tt,) = cpp_type.template_args
        inner = self.converters.cython_type(tt)

        if tt.base_type in self.converters.names_of_wrapper_classes:
            cy_tt = tt.base_type
            code = Code().add(
                """
                |if $input_cpp_var.has_value():
                |   $output_py_var = $cy_tt.__new__($cy_tt)
                |   $output_py_var.inst = shared_ptr[$inner](new $inner($input_cpp_var.value()))
                |else:
                |   $output_py_var = None
                """,
                locals(),
            )
        else:
            code = Code().add(
                """
                |if $input_cpp_var.has_value():
                |   $output_py_var = $input_cpp_var.value()
                |else:
                |   $output_py_var = None
                """,
                locals(),
            )
        return code


class StdStringViewConverter(TypeConverterBase):
    """
    Converter for std::string_view (C++17) - non-owning reference to a string.

    Input conversion:
        - Python bytes -> std::string_view (direct)
        - Python str -> encoded to UTF-8 bytes -> std::string_view

    Output conversion:
        - std::string_view is not typically returned (it's a view, not owning)
        - If returned, converts to Python bytes

    Note: std::string_view does not own its data, so it's primarily useful
    for input parameters where the Python bytes object remains valid during
    the C++ function call.

    Example PXD declaration:
        size_t getLength(libcpp_string_view sv)
        void processText(libcpp_string_view text)

    Example Python usage:
        length = obj.getLength(b"hello")      # Pass bytes
        length = obj.getLength("hello")       # Pass str (auto-encoded to UTF-8)
    """

    def get_base_types(self) -> List[str]:
        return ["libcpp_string_view"]

    def matches(self, cpp_type: CppType) -> bool:
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type: CppType) -> str:
        return "bytes"

    def matching_python_type_full(self, cpp_type: CppType) -> str:
        return "bytes"

    def type_check_expression(self, cpp_type: CppType, arg_var: str) -> str:
        return "isinstance(%s, (bytes, str))" % arg_var

    def input_conversion(
        self, cpp_type: CppType, argument_var: str, arg_num: int
    ) -> Tuple[Code, str, Union[Code, str]]:
        temp_var = "v%d" % arg_num
        code = Code().add(
            """
            |cdef bytes $temp_var
            |if isinstance($argument_var, str):
            |   $temp_var = $argument_var.encode('utf-8')
            |else:
            |   $temp_var = $argument_var
            """,
            locals(),
        )
        # string_view can be implicitly constructed from const char*
        return code, "(<libcpp_string_view>%s)" % temp_var, ""

    def call_method(self, res_type: CppType, cy_call_str: str, with_const: bool = True) -> str:
        return "_r = %s" % cy_call_str

    def output_conversion(
        self, cpp_type: CppType, input_cpp_var: str, output_py_var: str
    ) -> Optional[str]:
        # Convert string_view to Python bytes
        return "%s = <bytes>%s.data()[:%s.size()]" % (output_py_var, input_cpp_var, input_cpp_var)


class ConverterRegistry(object):
    """
    Works with two level lookup: first find converters which support base_type,
    then call .matches on them to find the finally matching converters

    Therefore TypeConverterBase has methods .get_base_types and .matches
    """

    def __init__(self, instance_mapping, names_of_classes_to_wrap, names_of_enums_to_wrap):
        self.lookup = defaultdict(list)

        self.names_of_wrapper_classes = list(instance_mapping.keys())
        # add everything with a const prefix again
        # TODO super hack. We need to support const completely/better without hacks
        self.names_of_wrapper_classes += ["const %s" % k for k in instance_mapping.keys()]
        self.names_of_classes_to_wrap = names_of_classes_to_wrap
        self.names_of_enums_to_wrap = names_of_enums_to_wrap

        self.process_and_set_type_mapping(instance_mapping)

    def process_and_set_type_mapping(self, instance_mapping):
        # as original c++ class decls are decorated with a beginning "_"
        # we have to process the instance mapping:

        map_ = dict(
            (name, CppType("_" + name))
            for name in self.names_of_classes_to_wrap + self.names_of_enums_to_wrap
        )
        self.instance_mapping = dict()
        for alias, type_ in instance_mapping.items():
            self.instance_mapping[alias] = type_.transformed(map_)

    def register(self, converter):
        assert isinstance(converter, TypeConverterBase)
        L.info("register %s" % converter)
        converter._set_converter_registry(self)

        # we take a defaultdict(list) for lookup as base_type is only some kind
        # of "hash value" to speedup lookup. what finally counts is the matches
        # method of the converters, see get() below:

        for base_type in converter.get_base_types():
            self.lookup[base_type].append(converter)

    def get(self, cpp_type: CppType) -> TypeConverterBase:
        """
        Gets a conversion provider that inherits from TypeConverterBase and matches both cpp_type.base_type
        and the matches function from the successfully looked-up TypeConverter

        :param cpp_type: CppType
        :return: TypeConverterBase
        :except: NameError
        """
        rv = [conv for conv in self.lookup[cpp_type.base_type] if conv.matches(cpp_type)]
        if len(rv) < 1:
            raise NameError("no converter for %s in: %s" % (cpp_type, str(self.lookup)))

        # always take the latest converter which allows overwriting existing
        # standard converters (externally)!
        return rv[-1]

    def __contains__(self, cpp_type):
        try:
            self.get(cpp_type)
            return True
        except NameError:
            return False

    def cython_type(self, type_: Union[CppType, AnyStr]) -> CppType:
        if isinstance(type_, (str, bytes)):
            type_ = CppType(type_)
        return type_.transformed(self.instance_mapping)


special_converters = []


def setup_converter_registry(classes_to_wrap, enums_to_wrap, instance_map):
    names_of_classes_to_wrap = list(set(c.cpp_decl.name for c in classes_to_wrap))
    names_of_enums_to_wrap = list(set(c.cpp_decl.name for c in enums_to_wrap))

    converters = ConverterRegistry(instance_map, names_of_classes_to_wrap, names_of_enums_to_wrap)

    converters.register(IntegerConverter())
    converters.register(BooleanConverter())
    converters.register(UnsignedIntegerConverter())
    converters.register(FloatConverter())
    converters.register(DoubleConverter())
    converters.register(ConstCharPtrConverter())
    converters.register(CharPtrConverter())
    converters.register(CharConverter())
    converters.register(StdStringConverter())
    converters.register(StdStringUnicodeConverter())
    converters.register(StdStringUnicodeOutputConverter())
    converters.register(StdVectorAsNumpyConverter())
    converters.register(StdVectorConverter())
    converters.register(StdSetConverter())
    converters.register(StdMapConverter())
    converters.register(StdPairConverter())
    converters.register(VoidConverter())
    converters.register(SharedPtrConverter())
    # New STL converters (C++11/14/17/20)
    converters.register(StdUnorderedMapConverter())
    converters.register(StdUnorderedSetConverter())
    converters.register(StdDequeConverter())
    converters.register(StdListConverter())
    converters.register(StdOptionalConverter())
    converters.register(StdStringViewConverter())

    for clz in classes_to_wrap:
        converters.register(TypeToWrapConverter(clz))

    for enum in enums_to_wrap:
        converters.register(EnumConverter(enum))

    # now special converters which may overlap / overwrite the already
    # registered  converters of types to wrap:
    for converter in special_converters:
        converters.register(converter)

    return converters


# now one can externally register own converters:
#
# from autowrap.ConversionProvider import TypeConverterBase, special_converters
#
# class MyConverter(TypeConverterBase):
#     ...
#
# special_converters.append(MyConverter())
#
