from collections import namedtuple
import re
from collections import defaultdict
from DeclResolver import ResolvedClass

from Types import CppType
from Code import Code


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

    Therefore TypeConverterBase has method .get_base_types and .matches
    """

    def __init__(self, instance_mapping):
        self.lookup = defaultdict(list)
        self.names_to_wrap = instance_mapping.keys()
        self.process_and_set_instance_mapping(instance_mapping)

    def process_and_set_instance_mapping(self, instance_mapping):
        # as original c++ class decls are decorated with a beginning "_"
        # we have to process  the instance mapping:
        map_ = dict((name, CppType("_"+name)) for name in self.names_to_wrap)
        self.instance_mapping = dict()
        for alias, type_ in instance_mapping.items():
            self.instance_mapping[alias] = type_.transformed(map_)

    def register(self, converter):

        assert isinstance(converter, TypeConverterBase)
        converter._set_converter_registry(self)

        # we take a defaultdict(list) for lookup as base_type is only some kind
        # of "hash value" to speedup lookup. what finally counts is the matches
        # method of the converters, see get() below:

        for base_type in converter.get_base_types():
            self.lookup[base_type].append(converter)

    def get(self, cpp_type):

        rv = [conv for conv in self.lookup[cpp_type.base_type]\
                   if conv.matches(cpp_type)]
        if len(rv)<1:
            raise Exception("no converter for %s" % cpp_type)

        # allways take the latest converter which allows overwriting existing
        # standard converters !
        return rv[-1]


    def cy_decl_str(self, type_):

        if isinstance(type_, basestring):
            type_ = CppType(type_)

        return self._cy_decl_str(type_)

    def _cy_decl_str(self, type_):
        return type_.transformed(self.instance_mapping)


class TypeConverterBase(object):

    def __init__(self):
        self._of_classes_to_wrap = None

    def set_classes_to_wrap(self, classes_to_wrap):
        self._of_classes_to_wrap = classes_to_wrap

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
        cy_res_type = self.converters.cy_decl_str(res_type)
        return "cdef %s _r = %s" % (cy_res_type, cy_call_str)

    def matching_python_type(self, cpp_type):
        raise NotImplementedError()

    def type_check_expression(self, cpp_type, argument_var):
        raise NotImplementedError()

    def input_conversion(self, cpp_type, argument_var, arg_num):
        raise NotImplementedError()

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        raise NotImplementedError()


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
        return "int"

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, int)" % (argument_var,)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<%s>%s)" % (cpp_type.base_type, argument_var)
        cleanup = ""
        return code, call_as, cleanup

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <%s>%s" % (output_py_var, cpp_type.base_type, input_cpp_var)

# TODO: common base class for float, int, str conversion

class FloatConverter(TypeConverterBase):

    """
    wraps long and int. "long" base_type is converted to "int" by the
    cython parser !
    """
    def get_base_types(self):
        return "float", "double",

    def matches(self, cpp_type):
        return not cpp_type.is_ptr

    def matching_python_type(self, cpp_type):
        return "float"

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, float)" % (argument_var,)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<float>%s)" % argument_var
        cleanup = ""
        return code, call_as, cleanup

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <float>%s" % (output_py_var, input_cpp_var)


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

        cy_type = self.converters.cy_decl_str(cpp_type)
        if cpp_type.is_ptr:
            call_as = "<%s>(%s.inst.get())" % (cy_type, argument_var)
        else:
            call_as = "<%s>deref(%s.inst.get())" % (cy_type, argument_var)
        cleanup = ""
        return code, call_as, cleanup

    def call_method(self, res_type, cy_call_str):
        #t = res_type.base_type
        t = self.converters.cy_decl_str(res_type)

        return "cdef %s * _r = new %s(%s)" % (t, t, cy_call_str)


    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):

        assert not cpp_type.is_ptr

        cy_clz = self.converters.cy_decl_str(cpp_type)
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
        i1 = self.converters.cy_decl_str(t1)
        i2 = self.converters.cy_decl_str(t2)
        if t1.base_type in self.converters.names_to_wrap:
            assert not t1.is_ptr
            arg0 = "deref((<%s>%s[0]).inst.get())" % (t1, argument_var)
        else:
            arg0 = "%s[0]" % argument_var
        if t2.base_type in self.converters.names_to_wrap:
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
        if cpp_type.is_ref:
            if t1.base_type in self.converters.names_to_wrap:
                temp1 = "temp1"
                cleanup_code.add("""
                    |cdef $t1 $temp1 = $t1.__new__($t1)
                    |$temp1.inst = shared_ptr[$i1](new $i1($temp_var.first))
                                   """, locals())
            else:
                temp1 = "%s.first" % temp_var
            if t2.base_type in self.converters.names_to_wrap:
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

        i1 = self.converters.cy_decl_str(t1)
        i2 = self.converters.cy_decl_str(t2)

        code = Code()

        if t1.base_type in self.converters.names_to_wrap:
            out1 = "out1"
            code.add("""cdef $t1 out1 = $t1.__new__($t1)
                       |out1.inst = shared_ptr[$i1](new $i1($input_cpp_var.first))
                       """, locals())
        else:
            out1 = "%s.first" % input_cpp_var
        if t2.base_type in self.converters.names_to_wrap:
            out2 = "out2"
            code.add("""cdef $t2 out2 = $t2.__new__($t2)
                       |out2.inst = shared_ptr[$i2](new $i2($input_cpp_var.second))
                       """, locals())
        else:
            out2 = "%s.second" % input_cpp_var

        code.add("""cdef list $output_py_var = [$out1, $out2]
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
        inner_check = inner_conv.type_check_expression(tt, "li")

        return Code().add("""
          |isinstance($arg_var, list) and all($inner_check for li in $arg_var)
          """, locals()).render()

    def input_conversion(self, cpp_type, argument_var, arg_num):
        tt, = cpp_type.template_args
        temp_var = "v%d" % arg_num
        if tt.base_type in self.converters.names_to_wrap:
            base_type = tt.base_type
            inner = self.converters.cy_decl_str(tt)
            cy_tt = tt.base_type
            item = "item%d" % arg_num
            code = Code().add("""
                |cdef libcpp_vector[$inner] * $temp_var
                + = new libcpp_vector[$inner]()
                |cdef $base_type $item
                |for $item in $argument_var:
                |   $temp_var.push_back(deref($item.inst.get()))
                """, locals())
            if cpp_type.is_ref:
                cleanup_code = Code().add("""
                    |cdef replace = []
                    |cdef libcpp_vector[$inner].iterator it = $temp_var.begin()
                    |while it != $temp_var.end():
                    |   $item = $cy_tt.__new__($cy_tt)
                    |   $item.inst = shared_ptr[$inner](new $inner(deref(it)))
                    |   replace.append($item)
                    |   inc(it)
                    |$argument_var[:] = replace
                    |del $temp_var
                    """, locals())
            else:
                cleanup_code = "del %s" % temp_var
            return code, "deref(%s)" % temp_var, cleanup_code
        else:
            inner = self.converters.cy_decl_str(tt)
            # cython cares for conversion of stl containers with std types:
            code = Code().add("""
                |cdef libcpp_vector[$inner] $temp_var = $argument_var
                """, locals())

            cleanup_code = ""
            if cpp_type.is_ref:
                cleanup_code = Code().add("""
                    |$argument_var[:] = $temp_var
                    """, locals())
            return code, "%s" % temp_var, cleanup_code

    def call_method(self, res_type, cy_call_str):
        return "_r = %s" % (cy_call_str)


    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):

        assert not cpp_type.is_ptr

        tt, = cpp_type.template_args
        if tt.base_type in self.converters.names_to_wrap:
            cy_tt = tt.base_type
            inner = self.converters.cy_decl_str(tt)
            it = mangle("it_" + input_cpp_var)
            item = mangle("item_" + output_py_var)
            code = Code().add("""
                |$output_py_var = []
                |cdef libcpp_vector[$inner].iterator $it = $input_cpp_var.begin()
                |cdef $cy_tt $item
                |while $it != $input_cpp_var.end():
                |   $item = $cy_tt.__new__($cy_tt)
                |   $item.inst = shared_ptr[$inner](new $inner(deref($it)))
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
        return "str"

    def input_conversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<libcpp_string>%s)" % argument_var
        cleanup = ""
        return code, call_as, cleanup

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, str)" % argument_var

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <libcpp_string>%s" % (output_py_var, input_cpp_var)


special_converters = []


def setup_converter_registry(classes_to_wrap, enums_to_wrap, instance_map):

    converters = ConverterRegistry(instance_map)
    converters.register(IntegerConverter())
    converters.register(FloatConverter())
    converters.register(CharPtrConverter())
    converters.register(StdStringConverter())
    converters.register(StdVectorConverter())
    converters.register(StdPairConverter())
    converters.register(VoidConverter())

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


