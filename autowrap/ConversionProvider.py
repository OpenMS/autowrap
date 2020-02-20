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

from autowrap.Types import CppType  # , printable
from autowrap.Code import Code

import logging as L
import string

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


def mangle(s):
    s = s.replace("(", "_l_")
    s = s.replace(")", "_r_")
    s = s.replace("<", "_lt_")
    s = s.replace(">", "_gt_")
    s = s.replace("[", "_lb_")
    s = s.replace("]", "_rb_")
    s = s.replace(".", "_dot_")
    return s


class ConverterRegistry(object):

    """
    Works with two level lookup: first find converters which support base_type,
    then call .matches on them to find the finally matching converters

    Therefore TypeConverterBase has methods .get_base_types and .matches
    """

    def __init__(self, instance_mapping, names_of_classes_to_wrap,
                 names_of_enums_to_wrap):

        self.lookup = defaultdict(list)

        self.names_of_wrapper_classes = list(instance_mapping.keys())
        self.names_of_wrapper_classes += ["const %s" % k for k in instance_mapping.keys()]
        self.names_of_classes_to_wrap = names_of_classes_to_wrap
        self.names_of_enums_to_wrap = names_of_enums_to_wrap

        self.process_and_set_type_mapping(instance_mapping)

    def process_and_set_type_mapping(self, instance_mapping):
        # as original c++ class decls are decorated with a beginning "_"
        # we have to process  the instance mapping:

        map_ = dict((name, CppType("_" + name)) for name in
                    self.names_of_classes_to_wrap + self.names_of_enums_to_wrap)
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

    def get(self, cpp_type):

        rv = [conv for conv in self.lookup[cpp_type.base_type]
              if conv.matches(cpp_type)]
        if len(rv) < 1:
            raise Exception("no converter for %s" % cpp_type)

        # allways take the latest converter which allows overwriting existing
        # standard converters !
        return rv[-1]

    def __contains__(self, cpp_type):
        try:
            self.get(cpp_type)
            return True
        except:
            return False

    def cython_type(self, type_):
        if isinstance(type_, basestring):
            type_ = CppType(type_)
        return type_.transformed(self.instance_mapping)


class TypeConverterBase(object):

    def set_enums_to_wrap(self, enums_to_wrap):
        self.enums_to_wrap = enums_to_wrap

    def _set_converter_registry(self, r):
        self.converters = r

    def get_base_types(self):
        """
        for first level lookup in registry
        """
        raise NotImplementedError()

    def matches(self, cpp_type):
        """
        for second level lookup in registry
        """
        raise NotImplementedError()

    def call_method(self, res_type, cy_call_str):
        """
        Creates a temporary object which has the type of the current TypeConverter object.

        The object is *always* named "_r" and will be of type "res_type". It
        will be assigned the value of "cy_call_str".

        Note that Cython cannot declare C++ references, therefore 

           cdef int & _r 

        Is illegal to declare and we have to remove any references from the type.
        """
        cy_res_type = self.converters.cython_type(res_type)
        if cy_res_type.is_ref:
            cy_res_type = cy_res_type.base_type
            return "cdef %s _r = %s" % (cy_res_type, cy_call_str)

        return "cdef %s _r = %s" % (cy_res_type, cy_call_str)

    def matching_python_type(self, cpp_type):
        raise NotImplementedError()

    def type_check_expression(self, cpp_type, argument_var):
        raise NotImplementedError()

    def input_conversion(self, cpp_type, argument_var, arg_num):
        """
        Sets up the conversion of input arguments.

        Returns a tuple as follows:
          - code : a code object to be added to the beginning of the function
          - call_as : a piece of code indicating how the argument should be called as going forward
          - cleanup : a piece of cleanup code to be added to the bottom of the function
        """
        raise NotImplementedError()

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        raise NotImplementedError()


    def _codeForInstantiateObjectFromIter(self, cpp_type, it):
        """
        Code for new object instantation from iterator (double deref for iterator-ptr)

        Note that if cpp_type is a pointer and the iterator therefore refers to
        a STL object of std::vector< _FooObject* >, then we need the base type
        to instantate a new object and dereference twice.

        Example output:
            shared_ptr[ _FooObject ] (new _FooObject (*foo_iter)  )
            shared_ptr[ _FooObject ] (new _FooObject (**foo_iter_ptr)  )
        """

        if cpp_type.is_ref:
            cpp_type = cpp_type.base_type

        if cpp_type.is_ptr:
            cpp_type_base = cpp_type.base_type
            return string.Template("shared_ptr[$cpp_type_base](new $cpp_type_base(deref(deref($it))))").substitute(locals())
        else:
            return string.Template("shared_ptr[$cpp_type](new $cpp_type(deref($it)))").substitute(locals())

class VoidConverter(TypeConverterBase):

    def get_base_types(self):
        """
        for first level lookup in registry
        """
        return "void",

    def matches(self, cpp_type):
        """
        for second level lookup in registry
        """
        return not cpp_type.is_ptr

    def call_method(self, res_type, cy_call_str):
        return cy_call_str

    def matching_python_type(self, cpp_type):
        raise NotImplementedError("void has no matching python type")

    def type_check_expression(self, cpp_type, argument_var):
        raise NotImplementedError("void has no matching python type")

    def input_conversion(self, cpp_type, argument_var, arg_num):
        raise NotImplementedError("void has no matching python type")

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return None


class IntegerConverter(TypeConverterBase):

    """
    wraps long and int. "long" base_type is converted to "int" by the
    cython parser !
    """

    def get_base_types(self):
        return ("int", "bool", "long", "int32_t", "ptrdiff_t", "int64_t",
                "uint32_t", "uint64_t", "size_t")

    def matches(self, cpp_type):
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type):
        return ""

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, (int, long))" % (argument_var,)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<%s>%s)" % (cpp_type, argument_var)
        cleanup = ""
        return code, call_as, cleanup

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <%s>%s" % (output_py_var, cpp_type, input_cpp_var)


# TODO: common base class for float, int, str conversion

class DoubleConverter(TypeConverterBase):

    def get_base_types(self):
        return "double",

    def matches(self, cpp_type):
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type):
        return "double"

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, float)" % (argument_var,)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<%s>%s)" % (cpp_type, argument_var)
        cleanup = ""
        return code, call_as, cleanup

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <%s>%s" % (output_py_var, cpp_type, input_cpp_var)


class FloatConverter(TypeConverterBase):

    def get_base_types(self):
        return "float",

    def matches(self, cpp_type):
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type):
        return "float"

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, float)" % (argument_var,)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<%s>%s)" % (cpp_type, argument_var)
        cleanup = ""
        return code, call_as, cleanup

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <%s>%s" % (output_py_var, cpp_type, input_cpp_var)


class EnumConverter(TypeConverterBase):

    def __init__(self, enum):
        self.enum = enum

    def get_base_types(self):
        return self.enum.name,

    def matches(self, cpp_type):
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type):
        return "int"

    def type_check_expression(self, cpp_type, argument_var):
        values = ", ".join(str(v) for (__, v) in self.enum.items)
        return "%s in [%s]" % (argument_var, values)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<_%s>%s)" % (cpp_type.base_type, argument_var)
        cleanup = ""
        return code, call_as, cleanup

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <int>%s" % (output_py_var, input_cpp_var)


class CharConverter(TypeConverterBase):

    def get_base_types(self):
        return "char",

    def matches(self, cpp_type):
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type):
        return "bytes"

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, bytes) and len(%s) == 1" % (argument_var, argument_var,)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<char>((%s)[0]))" % argument_var
        cleanup = ""
        return code, call_as, cleanup

    def call_method(self, res_type, cy_call_str):
        return "cdef char  _r = %s" % cy_call_str

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = chr(<char>(%s))" % (output_py_var, input_cpp_var)


class ConstCharPtrConverter(TypeConverterBase):

    def get_base_types(self):
        return "const_char",

    def matches(self, cpp_type):
        return cpp_type.is_ptr

    def matching_python_type(self, cpp_type):
        return "bytes"

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, bytes)" % (argument_var,)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = Code().add("cdef const_char * input_%s = <const_char *> %s" % (argument_var, argument_var))
        call_as = "input_%s" % argument_var
        cleanup = ""
        return code, call_as, cleanup

    def call_method(self, res_type, cy_call_str):
        return "cdef const_char  * _r = _cast_const_away(%s)" % cy_call_str

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <const_char *>(%s)" % (output_py_var, input_cpp_var)


class CharPtrConverter(TypeConverterBase):

    def get_base_types(self):
        return "char",

    def matches(self, cpp_type):
        return cpp_type.is_ptr

    def matching_python_type(self, cpp_type):
        return "bytes"

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, bytes)" % (argument_var,)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<char *>%s)" % argument_var
        cleanup = ""
        return code, call_as, cleanup

    def call_method(self, res_type, cy_call_str):
        return "cdef char  * _r = _cast_const_away(%s)" % cy_call_str

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <char *>(%s)" % (output_py_var, input_cpp_var)


class TypeToWrapConverter(TypeConverterBase):

    def __init__(self, class_):
        self.class_ = class_

    def get_base_types(self):
        return self.class_.name,

    def matches(self, cpp_type):
        return True

    def matching_python_type(self, cpp_type):
        return cpp_type.base_type

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, %s)" % (argument_var, cpp_type.base_type)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""

        cy_type = self.converters.cython_type(cpp_type)
        if cpp_type.is_ptr:
            call_as = "(%s.inst.get())" % (argument_var, )
        else:
            call_as = "(deref(%s.inst.get()))" % (argument_var, )

        cleanup = ""
        return code, call_as, cleanup

    def call_method(self, res_type, cy_call_str):
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
            code = Code().add("""
                |cdef $const $t * __r = ($cy_call_str)
                |if __r == NULL:
                |    return None
                |cdef $t * _r = new $t(deref(__r))
                """, locals())
            return code

        return "cdef %s * _r = new %s(%s)" % (t, t, cy_call_str)

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):

        cy_clz = self.converters.cython_type(cpp_type)

        # Need to ensure that type inside the raw ptr is an object and not a ref/ptr
        if cpp_type.is_ptr or cpp_type.is_ref:
            cy_clz = cy_clz.base_type

        t = cpp_type.base_type
        return Code().add("""
                      |cdef $t $output_py_var = $t.__new__($t)
                      |$output_py_var.inst = shared_ptr[$cy_clz]($input_cpp_var)
        """, locals())


class StdPairConverter(TypeConverterBase):

    # remark: we use list instead of tuple internally, in order to
    # provide call by ref args. Python tuples are immutable.

    def get_base_types(self):
        return "libcpp_pair",

    def matches(self, cpp_type):
        return True

    def matching_python_type(self, cpp_type):
        return "list"

    def type_check_expression(self, cpp_type, arg_var):
        t1, t2, = cpp_type.template_args
        inner_conv1 = self.converters.get(t1)
        inner_conv2 = self.converters.get(t2)
        assert inner_conv1 is not None, "arg type %s not supported" % t1
        assert inner_conv2 is not None, "arg type %s not supported" % t2
        inner_check1 = inner_conv1.type_check_expression(t1, "%s[0]" % arg_var)
        inner_check2 = inner_conv2.type_check_expression(t2, "%s[1]" % arg_var)

        return Code().add("""
          |isinstance($arg_var, list) and len($arg_var) == 2 and $inner_check1
          + and $inner_check2
          """, locals()).render()

    def input_conversion(self, cpp_type, argument_var, arg_num):
        t1, t2, = cpp_type.template_args
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

        code = Code().add("""
            |cdef libcpp_pair[$i1, $i2] $temp_var
            |$temp_var.first = $arg0
            |$temp_var.second = $arg1
            """, locals())

        cleanup_code = Code()
        if cpp_type.is_ref and not cpp_type.is_const:
            if not i1.is_enum and t1.base_type in self.converters.names_of_wrapper_classes:
                temp1 = "temp1"
                cleanup_code.add("""
                    |cdef $t1 $temp1 = $t1.__new__($t1)
                    |$temp1.inst = shared_ptr[$i1](new $i1($temp_var.first))
                                   """, locals())
            else:
                temp1 = "%s.first" % temp_var
            if not i2.is_enum and t2.base_type in self.converters.names_of_wrapper_classes:
                temp2 = "temp2"
                cleanup_code.add("""
                    |cdef $t2 $temp2 = $t2.__new__($t2)
                    |$temp2.inst = shared_ptr[$i2](new $i2($temp_var.second))
                                   """, locals())
            else:
                temp2 = "%s.second" % temp_var

            cleanup_code.add("""
                |$argument_var[:] = [$temp1, $temp2]
                """, locals())
        return code, "%s" % temp_var, cleanup_code

    def call_method(self, res_type, cy_call_str):
        return "_r = %s" % (cy_call_str)

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):

        assert not cpp_type.is_ptr
        t1, t2, = cpp_type.template_args

        i1 = self.converters.cython_type(t1)
        i2 = self.converters.cython_type(t2)

        code = Code()

        if i1.is_enum:
            out1 = "out1"
            code.add("""cdef $i1 out1 = (<$i1> $input_cpp_var.first)
                       """, locals())

        elif t1.base_type in self.converters.names_of_wrapper_classes:
            out1 = "out1"
            code.add("""cdef $t1 out1 = $t1.__new__($t1)
                       |out1.inst = shared_ptr[$i1](new $i1($input_cpp_var.first))
                       """, locals())
        else:
            out1 = "%s.first" % input_cpp_var

        if i2.is_enum:
            out2 = "out2"
            code.add("""cdef $i2 out2 = (<$i2> $input_cpp_var.second)
                       """, locals())
        elif t2.base_type in self.converters.names_of_wrapper_classes:
            out2 = "out2"
            code.add("""cdef $t2 out2 = $t2.__new__($t2)
                       |out2.inst = shared_ptr[$i2](new $i2($input_cpp_var.second))
                       """, locals())
        else:
            out2 = "%s.second" % input_cpp_var

        code.add("""cdef list $output_py_var = [$out1, $out2]
            """, locals())
        return code


class StdMapConverter(TypeConverterBase):

    def get_base_types(self):
        return "libcpp_map",

    def matches(self, cpp_type):
        return True

    def matching_python_type(self, cpp_type):
        return "dict"

    def type_check_expression(self, cpp_type, arg_var):
        tt_key, tt_value = cpp_type.template_args
        inner_conv_1 = self.converters.get(tt_key)
        inner_conv_2 = self.converters.get(tt_value)
        assert inner_conv_1 is not None, "arg type %s not supported" % tt_key
        assert inner_conv_2 is not None, "arg type %s not supported" % tt_value

        inner_check_1 = inner_conv_1.type_check_expression(tt_key, "k")
        inner_check_2 = inner_conv_2.type_check_expression(tt_value, "v")

        return Code().add("""
          |isinstance($arg_var, dict)
          + and all($inner_check_1 for k in $arg_var.keys())
          + and all($inner_check_2 for v in $arg_var.values())
          """, locals()).render()

    def input_conversion(self, cpp_type, argument_var, arg_num):
        tt_key, tt_value = cpp_type.template_args
        temp_var = "v%d" % arg_num

        code = Code()

        cy_tt_key = self.converters.cython_type(tt_key)
        cy_tt_value = self.converters.cython_type(tt_value)

        py_tt_key = tt_key

        if (not cy_tt_value.is_enum and tt_value.base_type in self.converters.names_of_wrapper_classes) \
           and (not cy_tt_key.is_enum and tt_key.base_type in self.converters.names_of_wrapper_classes):
            raise Exception("Converter can not handle wrapped classes as keys and values in map")

        value_conv_code = ""
        value_conv_cleanup = ""
        key_conv_code = ""
        key_conv_cleanup = ""

        if cy_tt_value.is_enum:
            value_conv = "<%s> value" % cy_tt_value
        elif tt_value.base_type in self.converters.names_of_wrapper_classes:
            value_conv = "deref((<%s>value).inst.get())" % tt_value.base_type
        elif tt_value.template_args is not None and tt_value.base_type == "libcpp_vector":
            # Special case: the value type is a std::vector< X >, maybe something we can convert?

            # code_top = """
            value_var = "value"
            tt, = tt_value.template_args
            vtemp_var = "svec%s" % arg_num
            inner = self.converters.cython_type(tt)

            # Check whether the inner vector has any classes we need to wrap (we cannot do that)
            contains_classes_to_wrap = tt.template_args is not None and \
                len(set(self.converters.names_of_wrapper_classes).intersection(
                    set(tt.all_occuring_base_types()))) > 0

            if self.converters.cython_type(tt).is_enum:
                # Case 1: We wrap a std::vector<> with an enum base type
                raise Exception("Not Implemented")
            elif tt.base_type in self.converters.names_of_wrapper_classes:
                # Case 2: We wrap a std::vector<> with a base type we need to wrap
                raise Exception("Not Implemented")
            elif tt.template_args is not None and tt.base_type == "shared_ptr" \
                    and len(set(tt.template_args[0].all_occuring_base_types())) == 1:
                # Case 3: We wrap a std::vector< shared_ptr<X> > where X needs to be a type that is easy to wrap
                raise Exception("Not Implemented")
            elif tt.template_args is not None and tt.base_type != "libcpp_vector" and \
                len(set(self.converters.names_of_wrapper_classes).intersection(
                    set(tt.all_occuring_base_types()))) > 0:
                    # Only if the std::vector contains a class that we need to wrap somewhere,
                    # we cannot do it ...
                raise Exception(
                    "Recursion in std::vector<T> is not implemented for other STL methods and wrapped template arguments")
            elif tt.template_args is not None and tt.base_type == "libcpp_vector" and contains_classes_to_wrap:
                # Case 4: We wrap a std::vector<> with a base type that contains
                #         further nested std::vector<> inside
                #         -> deal with recursion
                raise Exception("Not Implemented")
            else:
                # Case 5: We wrap a regular type
                inner = self.converters.cython_type(tt)
                # cython cares for conversion of stl containers with std types,
                # but we need to add the definition to the top
                code = Code().add("""
                    |cdef libcpp_vector[$inner] $vtemp_var
                    """, locals())

                value_conv_cleanup = Code().add("")
                value_conv_code = Code().add("$vtemp_var = $value_var", locals())
                value_conv = "%s" % vtemp_var
                if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
                    cleanup_code = Code().add("""
                        |$value_var[:] = $vtemp_var
                        """, locals())

        elif tt_value in self.converters:
            value_conv_code, value_conv, value_conv_cleanup = \
                self.converters.get(tt_value).input_conversion(tt_value, "value", 0)
        else:
            value_conv = "<%s> value" % cy_tt_value

        if cy_tt_key.is_enum:
            key_conv = "<%s> key" % cy_tt_key
        elif tt_key.base_type in self.converters.names_of_wrapper_classes:
            key_conv = "deref(<%s *> (<%s> key).inst.get())" % (cy_tt_key, py_tt_key)
        elif tt_key in self.converters:
            key_conv_code, key_conv, key_conv_cleanup = \
                self.converters.get(tt_key).input_conversion(tt_key, "key", 0)
        else:
            key_conv = "<%s> key" % cy_tt_key

        code.add("""
            |cdef libcpp_map[$cy_tt_key, $cy_tt_value] * $temp_var = new
            + libcpp_map[$cy_tt_key, $cy_tt_value]()

            |for key, value in $argument_var.items():
            """, locals())

        code.add(key_conv_code)
        code.add(value_conv_code)
        code.add("""    deref($temp_var)[ $key_conv ] = $value_conv
            """, locals())
        code.add(key_conv_cleanup)
        code.add(value_conv_cleanup)

        if cpp_type.is_ref and not cpp_type.is_const:
            it = mangle("it_" + argument_var)

            key_conv = "<%s> deref(%s).first" % (cy_tt_key, it)

            if tt_key.base_type in self.converters.names_of_wrapper_classes \
              and not tt_value.base_type in self.converters.names_of_wrapper_classes:
                value_conv = "<%s> deref(%s).second" % (cy_tt_value, it)
                cy_tt = tt_value.base_type
                item = mangle("item_" + argument_var)
                item_key = mangle("itemk_" + argument_var)
                cleanup_code = Code().add("""
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
                    """, locals())
            elif not cy_tt_value.is_enum and tt_value.base_type in self.converters.names_of_wrapper_classes\
                    and not tt_key.base_type in self.converters.names_of_wrapper_classes:
                cy_tt = tt_value.base_type
                item = mangle("item_" + argument_var)
                cleanup_code = Code().add("""
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
                    """, locals())
            else:
                value_conv = "<%s> deref(%s).second" % (cy_tt_value, it)
                cleanup_code = Code().add("""
                    |replace = dict()
                    |cdef libcpp_map[$cy_tt_key, $cy_tt_value].iterator $it = $temp_var.begin()
                    |while $it != $temp_var.end():
                    |   replace[$key_conv] = $value_conv
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """, locals())
        else:
            cleanup_code = "del %s" % temp_var

        return code, "deref(%s)" % temp_var, cleanup_code

    def call_method(self, res_type, cy_call_str):
        return "_r = %s" % (cy_call_str)

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):

        assert not cpp_type.is_ptr

        tt_key, tt_value = cpp_type.template_args
        cy_tt_key = self.converters.cython_type(tt_key)
        cy_tt_value = self.converters.cython_type(tt_value)
        py_tt_key = tt_key

        it = mangle("it_" + input_cpp_var)

        if (not cy_tt_value.is_enum and tt_value.base_type in self.converters.names_of_wrapper_classes) \
           and (not cy_tt_key.is_enum and tt_key.base_type in self.converters.names_of_wrapper_classes):
            raise Exception("Converter can not handle wrapped classes as keys and values in map")

        elif not cy_tt_key.is_enum and tt_key.base_type in self.converters.names_of_wrapper_classes:
            key_conv = "deref(<%s *> (<%s> key).inst.get())" % (cy_tt_key, py_tt_key)
        else:
            key_conv = "<%s>(deref(%s).first)" % (cy_tt_key, it)

        if not cy_tt_value.is_enum and tt_value.base_type in self.converters.names_of_wrapper_classes:
            cy_tt = tt_value.base_type
            item = mangle("item_" + output_py_var)
            code = Code().add("""
                |$output_py_var = dict()
                |cdef libcpp_map[$cy_tt_key, $cy_tt_value].iterator $it = $input_cpp_var.begin()
                |cdef $cy_tt $item
                |while $it != $input_cpp_var.end():
                |   $item = $cy_tt.__new__($cy_tt)
                |   $item.inst = shared_ptr[$cy_tt_value](new $cy_tt_value((deref($it)).second))
                |   $output_py_var[$key_conv] = $item
                |   inc($it)
                """, locals())
            return code
        elif not cy_tt_key.is_enum and tt_key.base_type in self.converters.names_of_wrapper_classes:
            value_conv = "<%s>(deref(%s).second)" % (cy_tt_value, it)
            item_key = mangle("itemk_" + output_py_var)
            code = Code().add("""
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
                """, locals())
            return code
        else:
            value_conv = "<%s>(deref(%s).second)" % (cy_tt_value, it)
            code = Code().add("""
                |$output_py_var = dict()
                |cdef libcpp_map[$cy_tt_key, $cy_tt_value].iterator $it = $input_cpp_var.begin()
                |while $it != $input_cpp_var.end():
                |   $output_py_var[$key_conv] = $value_conv
                |   inc($it)
                """, locals())
            return code


class StdSetConverter(TypeConverterBase):

    def get_base_types(self):
        return "libcpp_set",

    def matches(self, cpp_type):
        return True

    def matching_python_type(self, cpp_type):
        return "set"

    def type_check_expression(self, cpp_type, arg_var):
        tt, = cpp_type.template_args
        inner_conv = self.converters.get(tt)
        assert inner_conv is not None, "arg type %s not supported" % tt
        inner_check = inner_conv.type_check_expression(tt, "li")

        return Code().add("""
          |isinstance($arg_var, set) and all($inner_check for li in $arg_var)
          """, locals()).render()

    def input_conversion(self, cpp_type, argument_var, arg_num):
        tt, = cpp_type.template_args
        temp_var = "v%d" % arg_num
        inner = self.converters.cython_type(tt)
        it = mangle("it_" + argument_var)
        if inner.is_enum:
            item = "item%d" % arg_num
            code = Code().add("""
                |cdef libcpp_set[$inner] * $temp_var = new libcpp_set[$inner]()
                |cdef int $item
                |for $item in $argument_var:
                |   $temp_var.insert(<$inner> $item)
                """, locals())
            if cpp_type.is_ref and not cpp_type.is_const:
                cleanup_code = Code().add("""
                    |replace = set()
                    |cdef libcpp_set[$inner].iterator $it = $temp_var.begin()
                    |while $it != $temp_var.end():
                    |   replace.add(<int> deref($it))
                    |   inc($it)
                    |$argument_var.clear()
                    |$argument_var.update(replace)
                    |del $temp_var
                    """, locals())
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
            code = Code().add("""
                |cdef libcpp_set[$inner] * $temp_var = new libcpp_set[$inner]()
                |cdef $base_type $item
                |for $item in $argument_var:
                |   $temp_var.insert($do_deref($item.inst.get()))
                """, locals())
            if cpp_type.is_ref and not cpp_type.is_const:

                instantiation = self._codeForInstantiateObjectFromIter(inner, it)
                cleanup_code = Code().add("""
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
                    """, locals())

            else:
                cleanup_code = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup_code
        else:
            inner = self.converters.cython_type(tt)
            # cython cares for conversion of stl containers with std types:
            code = Code().add("""
                |cdef libcpp_set[$inner] $temp_var = $argument_var
                """, locals())

            cleanup_code = ""
            if cpp_type.is_ref and not cpp_type.is_const:
                cleanup_code = Code().add("""
                    |$argument_var.clear()
                    |$argument_var.update($temp_var)
                    """, locals())
            return code, "%s" % temp_var, cleanup_code

    def call_method(self, res_type, cy_call_str):
        return "_r = %s" % (cy_call_str)

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):

        assert not cpp_type.is_ptr

        tt, = cpp_type.template_args
        inner = self.converters.cython_type(tt)
        if inner.is_enum:
            it = mangle("it_" + input_cpp_var)
            code = Code().add("""
                |$output_py_var = set()
                |cdef libcpp_set[$inner].iterator $it = $input_cpp_var.begin()
                |while $it != $input_cpp_var.end():
                |   $output_py_var.add(<int>deref($it))
                |   inc($it)
                """, locals())
            return code

        elif tt.base_type in self.converters.names_of_wrapper_classes:
            cy_tt = tt.base_type
            inner = self.converters.cython_type(tt)
            it = mangle("it_" + input_cpp_var)
            item = mangle("item_" + output_py_var)

            instantiation = self._codeForInstantiateObjectFromIter(inner, it)
            code = Code().add("""
                |$output_py_var = set()
                |cdef libcpp_set[$inner].iterator $it = $input_cpp_var.begin()
                |cdef $cy_tt $item
                |while $it != $input_cpp_var.end():
                |   $item = $cy_tt.__new__($cy_tt)
                |   $item.inst = $instantiation
                |   $output_py_var.add($item)
                |   inc($it)
                """, locals())
            return code
        else:
            # cython cares for conversion of stl containers with std types:
            code = Code().add("""
                |cdef set $output_py_var = $input_cpp_var
                """, locals())
            return code


class StdVectorConverter(TypeConverterBase):

    def get_base_types(self):
        return "libcpp_vector",

    def matches(self, cpp_type):
        return True

    def matching_python_type(self, cpp_type):
        return "list"

    def type_check_expression(self, cpp_type, arg_var):
        tt, = cpp_type.template_args
        inner_conv = self.converters.get(tt)
        assert inner_conv is not None, "arg type %s not supported" % tt
        if arg_var[-4:] == "_rec":
            arg_var_next = "%s_rec" % arg_var
        else:
            # first recursion, set element name
            arg_var_next = "elemt_rec"
        inner_check = inner_conv.type_check_expression(tt, arg_var_next)

        return Code().add("""
          |isinstance($arg_var, list) and all($inner_check for $arg_var_next in $arg_var)
          """, locals()).render()

    def _prepare_nonrecursive_cleanup(self, cpp_type, bottommost_code, it_prev, temp_var, recursion_cnt, *a, **kw):
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
            cleanup_code = Code().add(tp_add + """
                |replace_$recursion_cnt = []
                |while $it != $temp_var_used.end():
                |    $item = $cy_tt.__new__($cy_tt)
                |    $item.inst = $instantiation
                |    replace_$recursion_cnt.append($item)
                |    inc($it)
                """ + btm_add, *a, **kw)
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

    def _prepare_recursive_cleanup(self, cpp_type, bottommost_code, it_prev, temp_var, recursion_cnt, *a, **kw):
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
            cleanup_code = Code().add(tp_add + """
                |replace_$recursion_cnt = []
                |while $it != $temp_var_used.end():
                """, *a, **kw)
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
        code = Code().add(code_top + """
                |for $item in $argument_var:
                |    $temp_var.push_back($do_deref($item.inst.get()))
                """, *a, **kw)
        return code

    def _perform_recursion(self, cpp_type, tt, arg_num, item, topmost_code,
                           bottommost_code, code, cleanup_code, recursion_cnt,
                           *a, **kw):

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
        conv_code, call_as, cleanup =\
            converter.input_conversion(tt, rec_argument_var, rec_arg_num,
                                       topmost_code_callback, bottommost_code_callback, recursion_cnt + 1)
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
        code.add("""
            |for $item in $argument_var:
            """, *a, **kw)
        #
        # A) Prepare the pre-call, Step 4
        # clear the vector since it needs to be empty before we start the inner loop
        #
        code.add(Code().add("""
            |$new_item.clear()""", *a, **kw))
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
        code.add("""
            |    $temp_var.push_back(deref($new_item))
            """, *a, **kw)

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
            cleanup_code.add("""
                |    replace_$recursion_cnt.append(replace_$recursion_cnt_next)
                |    inc($it)
                             """, *a, **kw)

        #
        # B) Prepare the post-call, Step 3
        # append the "bottommost" code
        #
        if bottommost_code is None:
            # we are the outermost loop
            cleanup_code.content.extend(bottommost_code_callback.content)
            if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
                cleanup_code.add("""
                    |$argument_var[:] = replace_$recursion_cnt
                    |del $temp_var
                                 """, *a, **kw)
        else:
            bottommost_code.content.extend(bottommost_code_callback.content)

    def input_conversion(self, cpp_type, argument_var, arg_num, topmost_code=None, bottommost_code=None, recursion_cnt=0):
        """Do the input conversion for a std::vector<T>

        In this case, the template argument is tt (or "inner").

        It is possible to nest or recurse multiple vectors (like in
        std::vector< std::vector< T > > which is detected since the template
        argument of tt itself is not None).
        """
        # If we are inside a recursion, we expect the toplmost and bottom most code to be present...
        if recursion_cnt > 1:
            assert topmost_code is not None
            assert bottommost_code is not None
        tt, = cpp_type.template_args
        temp_var = "v%s" % arg_num
        inner = self.converters.cython_type(tt)
        it = mangle("it_" + argument_var)  # + "_%s" % recursion_cnt
        recursion_cnt_next = recursion_cnt + 1
        it_prev = ""
        if recursion_cnt > 0:
            it_prev = mangle("it_" + argument_var[:-4])

        base_type = tt.base_type
        inner = self.converters.cython_type(tt)
        cy_tt = tt.base_type

        # Prepare the code that should be at the very outer level of the
        # function, thus variable declarations (e.g. to prevent a situation
        # where new is called within a loop multiple times and memory loss
        # occurs).
        code_top = """
            |cdef libcpp_vector[$inner] * $temp_var
            + = new libcpp_vector[$inner]()
        """

        contains_classes_to_wrap = tt.template_args is not None and \
            len(set(self.converters.names_of_wrapper_classes).intersection(
                set(tt.all_occuring_base_types()))) > 0

        if self.converters.cython_type(tt).is_enum:
            # Case 1: We wrap a std::vector<> with an enum base type
            item = "item%s" % arg_num
            if topmost_code is not None:
                raise Exception("Recursion in std::vector<T> not yet implemented for enum")
                code_top = ""
            code = Code().add("""
                |cdef libcpp_vector[$inner] * $temp_var
                + = new libcpp_vector[$inner]()
                |cdef int $item
                |for $item in $argument_var:
                |    $temp_var.push_back(<$inner> $item)
                """, locals())
            if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
                cleanup_code = Code().add("""
                    |replace = []
                    |cdef libcpp_vector[$inner].iterator $it = $temp_var.begin()
                    |while $it != $temp_var.end():
                    |    replace.append(<int> deref($it))
                    |    inc($it)
                    |$argument_var[:] = replace
                    |del $temp_var
                    """, locals())
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

            instantiation = self._codeForInstantiateObjectFromIter(inner, it)
            code = self._prepare_nonrecursive_precall(topmost_code, cpp_type, code_top, do_deref, locals())
            cleanup_code = self._prepare_nonrecursive_cleanup(
                cpp_type, bottommost_code, it_prev, temp_var, recursion_cnt, locals())

            if cpp_type.is_ptr:
                call_fragment = temp_var
            else:
                call_fragment = "deref(%s)" % temp_var

            return code, call_fragment, cleanup_code

        elif tt.template_args is not None and tt.base_type == "shared_ptr" \
                and len(set(tt.template_args[0].all_occuring_base_types())) == 1:
            # Case 3: We wrap a std::vector< shared_ptr<X> > where X needs to be a type that is easy to wrap

            base_type, = tt.template_args
            cpp_tt, = inner.template_args

            item = "%s_rec" % argument_var
            code = Code().add("""
                |cdef libcpp_vector[$inner] $temp_var 
                |cdef $base_type $item
                |for $item in $argument_var:
                |    $temp_var.push_back($item.inst)
                |# call
                """, locals())

            cleanup_code = Code().add("")

            if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
                item2 = "%s_rec_b" % argument_var
                instantiation = self._codeForInstantiateObjectFromIter(inner, it)
                cleanup_code = Code().add("""
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
                    """, locals())

            return code, "%s" % temp_var, cleanup_code

        elif tt.template_args is not None and tt.base_type != "libcpp_vector" and \
            len(set(self.converters.names_of_wrapper_classes).intersection(
                set(tt.all_occuring_base_types()))) > 0:
                # Only if the std::vector contains a class that we need to wrap somewhere,
                # we cannot do it ...
            raise Exception(
                "Recursion in std::vector<T> is not implemented for other STL methods and wrapped template arguments")

        elif tt.template_args is not None and tt.base_type == "libcpp_vector" and contains_classes_to_wrap:
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
                cpp_type, bottommost_code, it_prev, temp_var, recursion_cnt, locals())

            # Go into recursion (if possible)
            if hasattr(self, "cr"):
                self._perform_recursion(
                    cpp_type, tt, arg_num, item, topmost_code, bottommost_code, code, cleanup_code, recursion_cnt, locals())
            else:
                raise Exception(
                    "Error: For recursion in std::vector<T> to work, we need a ConverterRegistry instance at self.cr")

            return code, "deref(%s)" % temp_var, cleanup_code

        else:
            # Case 5: We wrap a regular type
            inner = self.converters.cython_type(tt)
            # cython cares for conversion of stl containers with std types:
            code = Code().add("""
                |cdef libcpp_vector[$inner] $temp_var = $argument_var
                """, locals())

            cleanup_code = Code().add("")
            if cpp_type.topmost_is_ref and not cpp_type.topmost_is_const:
                cleanup_code = Code().add("""
                    |$argument_var[:] = $temp_var
                    """, locals())

            return code, "%s" % temp_var, cleanup_code

    def call_method(self, res_type, cy_call_str):

        t = self.converters.cython_type(res_type)
        if t.is_ptr:
            return "_r = deref(%s)" % (cy_call_str)

        return "_r = %s" % (cy_call_str)

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):

        tt, = cpp_type.template_args
        inner = self.converters.cython_type(tt)

        if inner.is_enum:
            it = mangle("it_" + input_cpp_var)
            code = Code().add("""
                |$output_py_var = []
                |cdef libcpp_vector[$inner].iterator $it = $input_cpp_var.begin()
                |while $it != $input_cpp_var.end():
                |   $output_py_var.append(<int>deref($it))
                |   inc($it)
                """, locals())
            return code

        elif tt.base_type in self.converters.names_of_wrapper_classes:
            cy_tt = tt.base_type
            inner = self.converters.cython_type(tt)
            it = mangle("it_" + input_cpp_var)
            item = mangle("item_" + output_py_var)

            instantiation = self._codeForInstantiateObjectFromIter(inner, it)
            code = Code().add("""
                |$output_py_var = []
                |cdef libcpp_vector[$inner].iterator $it = $input_cpp_var.begin()
                |cdef $cy_tt $item
                |while $it != $input_cpp_var.end():
                |   $item = $cy_tt.__new__($cy_tt)
                |   $item.inst = $instantiation
                |   $output_py_var.append($item)
                |   inc($it)
                """, locals())
            return code

        elif tt.base_type == "shared_ptr" \
                and len(set(tt.template_args[0].all_occuring_base_types())) == 1:

            inner = self.converters.cython_type(tt)
            it = mangle("it_" + input_cpp_var)
            item = mangle("item_" + output_py_var)

            base_type, = tt.template_args
            cpp_tt, = inner.template_args

            code = Code().add("""
                |$output_py_var = []
                |cdef libcpp_vector[$inner].iterator $it = $input_cpp_var.begin()
                |cdef $base_type $item
                |while $it != $input_cpp_var.end():
                |   $item = $base_type.__new__($base_type)
                |   $item.inst = deref($it)
                |   $output_py_var.append($item)
                |   inc($it)
                """, locals())
            return code

        else:
            # cython cares for conversion of stl containers with std types:
            code = Code().add("""
                |cdef list $output_py_var = $input_cpp_var
                """, locals())
            return code


class StdStringConverter(TypeConverterBase):

    def get_base_types(self):
        return "libcpp_string",

    def matches(self, cpp_type):
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type):
        return "bytes"

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<libcpp_string>%s)" % argument_var
        cleanup = ""
        return code, call_as, cleanup

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, bytes)" % argument_var

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <libcpp_string>%s" % (output_py_var, input_cpp_var)


class StdStringUnicodeConverter(StdStringConverter):
    def get_base_types(self):
        return "libcpp_utf8_string",

    def matching_python_type(self, cpp_type):
        return ""

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = Code()
        code.add("""
            |if isinstance($argument_var, unicode):
            |    $argument_var = $argument_var.encode('utf-8')
            """, locals())
        call_as = "(<libcpp_string>%s)" % argument_var
        cleanup = ""
        return code, call_as, cleanup

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, (bytes, unicode))" % argument_var


class StdStringUnicodeOutputConverter(StdStringUnicodeConverter):

    def get_base_types(self):
        return "libcpp_utf8_output_string",

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = %s.decode('utf-8')" % (output_py_var, input_cpp_var)


class SharedPtrConverter(TypeConverterBase):

    """
    This converter deals with functions that expect a shared_ptr[BaseClass] as
    an argument. For this to work, BaseClass needs to have a Python type and
    thus the expected pointer already exists at BaseClass.inst => all we need
    to do is to pass this inst shared_ptr to the function.
    """

    def get_base_types(self):
        return "shared_ptr",

    def matches(self, cpp_type):
        tt, = cpp_type.template_args
        return tt in self.converters.names_of_wrapper_classes

    def matching_python_type(self, cpp_type):
        tt, = cpp_type.template_args
        return str(tt)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        tt, = cpp_type.template_args
        inner = self.converters.cython_type(tt)
        # Cython expects us to get a C++ type (we cannot just stick var.inst into the function)
        code = Code().add("""
            |cdef shared_ptr[$inner] input_$argument_var = $argument_var.inst
            """, locals())
        call_as = "input_" + argument_var
        cleanup = ""
        # Put the pointer back if we pass by reference
        if cpp_type.is_ref and not cpp_type.is_const:
            cleanup = Code().add("""
                |$argument_var.inst = input_$argument_var
                """, locals())
        return code, call_as, cleanup

    def type_check_expression(self, cpp_type, argument_var):
        # We can just use the Python type of the template argument
        tt, = cpp_type.template_args
        return "isinstance(%s, %s)" % (argument_var, tt)

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        # L.info("Output conversion for %s" % (cpp_type))
        tt, = cpp_type.template_args
        code = Code()
        if tt.is_const:
            # If the template argument is constant, we need to have non-const base-types for our code
            inner = self.converters.cython_type(tt).toString(False)
            tt = tt.toString(withConst=False)
            code.add("""
                     |# Const shared_ptr detected, we need to produce a non-const copy to stick into Python object
                     |cdef $inner * raw_$input_cpp_var = new $inner((deref(<$inner * const>$input_cpp_var.get())))
                     |cdef $tt py_result
                     |$output_py_var = $tt.__new__($tt)
                     |$output_py_var.inst = shared_ptr[$inner](raw_$input_cpp_var) """, locals())
        else:
            code.add("""
                |cdef $tt py_result
                |$output_py_var = $tt.__new__($tt)
                |$output_py_var.inst = $input_cpp_var""", locals())
        return code

special_converters = []


def setup_converter_registry(classes_to_wrap, enums_to_wrap, instance_map):

    names_of_classes_to_wrap = list(set(c.cpp_decl.name for c in
                                        classes_to_wrap))
    names_of_enums_to_wrap = list(set(c.cpp_decl.name for c in enums_to_wrap))

    converters = ConverterRegistry(instance_map,
                                   names_of_classes_to_wrap,
                                   names_of_enums_to_wrap)

    converters.register(IntegerConverter())
    converters.register(FloatConverter())
    converters.register(DoubleConverter())
    converters.register(ConstCharPtrConverter())
    converters.register(CharPtrConverter())
    converters.register(CharConverter())
    converters.register(StdStringConverter())
    converters.register(StdStringUnicodeConverter())
    converters.register(StdStringUnicodeOutputConverter())
    converters.register(StdVectorConverter())
    converters.register(StdSetConverter())
    converters.register(StdMapConverter())
    converters.register(StdPairConverter())
    converters.register(VoidConverter())
    converters.register(SharedPtrConverter())

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
