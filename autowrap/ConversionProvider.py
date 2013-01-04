from collections import namedtuple
import re
from collections import defaultdict
from DeclResolver import ResolvedClass

from Types import CppType
from Code import Code

class ConverterRegistry(object):
    """
    Works with two level lookup: first find converters which support base_type,
    then call .matches on them to find the finally matching converters

    Therefore TypeConverterBase has method .get_base_types and .matches
    """

    def __init__(self):
        self.lookup = defaultdict(list)

    def register(self, converter):
        assert isinstance(converter, TypeConverterBase)
        converter._set_converter_registry(self)
        for base_type in converter.get_base_types():
            self.lookup[base_type].append(converter)

    def get(self, cpp_type):
        rv = [conv for conv in self.lookup[cpp_type.base_type]\
                   if conv.matches(cpp_type)]
        if len(rv)>1:
            raise Exception("multiple converters for %s" % cpp_type)
        if len(rv)<1:
            raise Exception("no converter for %s" % cpp_type)
        return rv[0]

    def set_names_of_classes_to_wrap(self, names_of_classes_to_wrap):
        for converters in self.lookup.values():
            for converter in converters:
                converter.set_names_of_classes_to_wrap(names_of_classes_to_wrap)
        self.names_of_classes_to_wrap = names_of_classes_to_wrap

    def cy_decl_str(self, type_):
        if type_.template_args is not None:
            targs = [self.cy_decl_str(t) for t in type_.template_args]
            targs = "[%s]" % (", ".join(targs))
        else:
            targs = ""

        if type_.base_type in self.names_of_classes_to_wrap:
            base = "_%s" % type_.base_type
        else:
            base = type_.base_type

        if type_.is_ptr:
            base += " * "
        return "%s%s" % (base, targs)




class TypeConverterBase(object):

    def __init__(self):
        self.names_of_classes_to_wrap = None

    def set_names_of_classes_to_wrap(self, names_of_classes_to_wrap):
        self.names_of_classes_to_wrap = names_of_classes_to_wrap

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

    def matching_python_type(self, cpp_type):
        raise NotImplementedError()

    def type_check_expression(self, cpp_type, argument_var):
        raise NotImplementedError()

    def input_conversion(self, cpp_type, argument_var, arg_num):
        raise NotImplementedError()

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        raise NotImplementedError()


class NumberConverter(TypeConverterBase):

    def get_base_types(self):
        return "int", "long"

    def matches(self, cpp_type):
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type):
        return "int"

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, int)" % (argument_var,)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<int>%s)" % argument_var
        return code, call_as

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <int>%s" % (output_py_var, input_cpp_var)


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
        return code, call_as


    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <char *>%s" % (output_py_var, input_cpp_var)


class TypeToWrapConverter(TypeConverterBase):

    def __init__(self, name_of_class_to_wrap):
        self.name_of_class_to_wrap = name_of_class_to_wrap

    def get_base_types(self):
        return self.name_of_class_to_wrap,

    def matches(self, cpp_type):
        return True

    def matching_python_type(self, cpp_type):
        return cpp_type.base_type

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, %s)" % (argument_var, cpp_type.base_type)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""
        bt = cpp_type.base_type
        if cpp_type.is_ptr:
            call_as = "<_%s *>(%s.inst)" % (bt, argument_var)
        else:
            call_as = "<_%s>deref(%s.inst)" % (bt, argument_var)
        return code, call_as


    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):

        assert not cpp_type.is_ptr

        cy_clz = cpp_type.base_type
        return Code().add("""
                      |cdef $cy_clz $output_py_var = $cy_clz.__new__($cy_clz)
                      |$output_py_var.inst = new _$cy_clz($input_cpp_var)
        """, locals())

class StdVectorConverter(TypeConverterBase):

    def get_base_types(self):
        return "std_vector",

    def matches(self, cpp_type):
        return True

    def matching_python_type(self, cpp_type):
        return "list"

    def type_check_expression(self, cpp_type, arg_var):
        t_t, = cpp_type.template_args
        inner_conv = self.converters.get(t_t)
        assert inner_conv is not None, "arg type %s not supported" % t_t
        inner_check = inner_conv.type_check_expression(t_t, "li")

        return Code().add("""
          |isinstance($arg_var, list) and all($inner_check for li in $arg_var)
          """, locals()).render()

    def input_conversion(self, cpp_type, argument_var, arg_num):
        t_t, = cpp_type.template_args
        if t_t.base_type in self.names_of_classes_to_wrap:
            temp_var = "v%d" % arg_num
            code = Code().add("""
                    |cdef std_vector[_$t_t] * $temp_var = new std_vector[_$t_t]()
                    |cdef $t_t item
                    |for item in $argument_var:
                    |   $temp_var.push_back(deref(item.inst))
                    """, locals())
            return code, "deref(%s)" % temp_var

        else:
            temp_var = "v%d" % arg_num
            code = Code().add("""
                    |cdef std_vector[$t_t] * $temp_var = new std_vector[$t_t]()
                    |cdef $t_t item
                    |for item in $argument_var:
                    |   $temp_var.push_back(item)
                    """, locals())
            return code, "deref(%s)" % temp_var


    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return None

        assert not cpp_type.is_ptr

        cy_clz = cpp_type.base_type
        return Code().add("""
                      |cdef $cy_clz $output_py_var = $cy_clz.__new__($cy_clz)
                      |$output_py_var.inst = new _$cy_clz($input_cpp_var)
        """, locals())


class StdStringConverter(TypeConverterBase):

    def get_base_types(self):
        return "std_string",

    def matches(self, cpp_type):
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type):
        return "str"

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<std_string>%s)" % argument_var
        return code, call_as

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, str)" % argument_var

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <std_string>%s" % (output_py_var, input_cpp_var)


def setup_converter_registry(names_of_classes_to_wrap):

    converter = ConverterRegistry()
    converter.register(NumberConverter())
    converter.register(CharPtrConverter())
    converter.register(StdStringConverter())
    converter.register(StdVectorConverter())
    for name in names_of_classes_to_wrap:
        converter.register(TypeToWrapConverter(name))

    converter.set_names_of_classes_to_wrap(names_of_classes_to_wrap)

    return converter

