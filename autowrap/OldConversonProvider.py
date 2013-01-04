from collections import namedtuple
import re
from DeclResolver import ResolvedClass

from Types import CppType
from Code import Code


class TypeConverterBase(object):

    def __init__(self, types_to_wrap):
        self.types_to_wrap = types_to_wrap

    def getBaseTypes(self):
        raise NotImplementedError()

    def testMatch(self, cpp_type):
        raise NotImplementedError()

    def matchingPythonType(self, cpp_type):
        raise NotImplementedError()

    def inputConversion(self, cpp_type, argument_var, arg_num):
        raise NotImplementedError()

    def outputConversion(self, cpp_type, input_cpp_var, output_py_var):
        raise NotImplementedError()


class NumberConverter(TypeConverterBase):

    def getBaseTypes(self):
        return "int", "long"

    def testMatch(self, cpp_type):
        return not cpp_type.is_ptr

    def matchingPythonType(self, cpp_type):
        return "int"

    def inputConversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<int>%s)" % argument_var
        return code, call_as

    def outputConversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <int>%s" % (output_py_var, input_cpp_var)


class CharPtrConverter(TypeConverterBase):

    def getBaseTypes(self):
        return "char",

    def testMatch(self, cpp_type):
        return cpp_type.is_ptr

    def matchingPythonType(self, cpp_type):
        return "bytes"

    def inputConversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<char *>%s)" % argument_var
        return code, call_as


    def outputConversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <char *>%s" % (output_py_var, input_cpp_var)


class TypeToWrapConverter(TypeConverterBase):

    def getBaseTypes(self):
        return self.types_to_wrap

    def testMatch(self, cpp_type):
        return not cpp_type.is_ptr

    def matchingPythonType(self, cpp_type):
        return cpp_type.base_type

    def inputConversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(deref(%s.inst))" % argument_var
        return code, call_as


    def outputConversion(self, cpp_type, input_cpp_var, output_py_var):
        base_type = cpp_type.base_type
        return Code().add("""
               | $output_py_var = $base_type.__new__($base_type)
               | $output_py_var.inst = adress($input_cpp_var)
        """, locals())


class StdStringConverter(TypeConverterBase):

    def getBaseTypes(self):
        return "std_string",

    def testMatch(self, cpp_type):
        return not cpp_type.is_ptr

    def matchingPythonType(self, cpp_type):
        return "str"

    def inputConversion(self, cpp_type, argument_var, arg_num):
        code = ""
        call_as = "(<std_string>%s)" % argument_var
        return code, call_as


    def outputConversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <std_string>%s" % (output_py_var, input_cpp_var)



"""

class UtilFunctionRegistry(object):

    def __init__(self):
        self.registry = dict()

    def register(self, name, code):
        self.registry[name] = code

    def get_all_decls(self):
        return self.registry.values()

    def print_all_decls(self):
        for code in self.registry.values():
            print code.replace("       |", "")
            print

ConversionInfo = namedtuple("ConversionInfo", [ "py_type",
                                                "arg_check_code",
                                                "from_py_code",
                                                "from_py_cleanup_code",
                                                "call_as",
                                                "to_py_code",
                                                "to_py_cleanup_code"])


def check_py_list_code(arg_name, inner_py_type_as_str):
    return Code().add("""assert type($arg_name) == list
          + and all(isinstance(it, $inner_py_type_as_str) for it in $arg_name),
          + "arg $arg_name does not match"
                """, locals())


def py_list_to_vector_X(cp, X_type, var_in, var_out):

    X_type_str = cp.cy_type_str(X_type)
    X_base_type = X_type.base_type

    conv_fun_name = "py_list_to_vector_%s" % X_type_str
    __, __, py_item_to_X, cleanup, call_as, __, __ = cp.get(X_type, "item")


    cp.ufr.register(conv_fun_name,
            Code().add("""
        |cdef std_vector[$X_type_str] * $conv_fun_name(list li):
        |    cdef std_vector[$X_type_str] * res = new std_vector[$X_type_str]()
        |    cdef $X_base_type item
        |    cdef $X_type_str _item
        |    for item in li:
        |        _item = $py_item_to_X
        |        res.push_back(_item)
        |        $cleanup
        |    return res
                    """, locals()))

    return "%(conv_fun_name)s(%(var_in)s)" % locals(), "del %s" % var_out, "(deref(%s))" % var_out



def vector_X_to_py_list(cp, X_type, var_name):

    X_type_str = cp.cy_type_str(X_type)
    conv_fun_name = "vector_%s_to_py_list" % X_type_str # TODO: mangling !
    __, __, __, __, __, X_to_py, cleanup = cp.get(X_type, "v")

    assert cleanup == "", "do not know how to handle cleaup %r" % cleanup

    cp.ufr.register(conv_fun_name,
       Code().add("""
            |cdef $conv_fun_name(std_vector[$X_type_str] vec):
            |    return [ $X_to_py for v in vec ]
            """, locals()))

    return "%(conv_fun_name)s(%(var_name)s)" % locals(), ""


def cpp_type_to_wrapped(cp, cpp_type, var_name):

    conv_fun_name = "%s_to_py" % cp.cy_decl_str(cpp_type)

    base_type = cpp_type.base_type

    assert not cpp_type.is_ptr

    code = Code().add("""
         |cdef $conv_fun_name(_$base_type & inst):
         |     cdef $base_type result = $base_type.__new__($base_type)
         |     result.inst = new _$base_type(inst)
         |     return result
         """, locals())

    cp.ufr.register(conv_fun_name, code)
    return "%(conv_fun_name)s(%(var_name)s)" % locals()

def cpp_ptr_type_to_wrapped(cp, cpp_type, var_name):
    pass




class ConversionProvider(object):

    def __init__(self, decls):

        self.wrapped_types = [d.name for d in decls if isinstance(d,
                                                          ResolvedClass)]
        self.ufr = UtilFunctionRegistry()

        self.customized = dict()
        self.add_data("int", False, self.num_type_info)
        self.add_data("char", False, self.num_type_info)
        self.add_data("char", True, self.char_p_type_info)
        self.add_data("long", False, self.num_type_info)
        self.add_data("bool", False, self.num_type_info)

        self.add_data("std_string", False, self.std_string_type_info)
        self.add_data("std_vector", False, self.std_vector_type_info)

    def render_utils(self):
        return "\n\n".join(c.render() for c in self.ufr.registry.values())

    def cy_decl_str(self, what):
        if isinstance(what, CppType):
            return self._cy_decl_str_for_type(what)
        elif isinstance(what, ResolvedClass):
            return self._cy_decl_str_for_decl(what)
        raise Exception("cy_decl for %s not implemented" % what)

    def _cy_decl_str_for_decl(self, decl):
        if not decl.tinstances:
            return "_%s" % decl.name
        return "_%s[%s]" % (self.decl, ", ".join(decl.tinstances))


    def _cy_decl_str_for_type(self, type_):
        if type_.template_args is not None:
            targs = [self.cy_decl_str(t) for t in type_.template_args]
            targs = "[%s]" % (", ".join(targs))
        else:
            targs = ""

        if type_.base_type in self.wrapped_types:
            base = "_%s" % type_.base_type
        else:
            base = type_.base_type

        if type_.is_ptr:
            base += "__ptr_"

        return "%s%s" % (base, targs)


    def add_data(self, name, is_ptr, fun):
        self.customized[name, is_ptr] = fun

    def num_type_info(self, cpp_type, arg_in, arg_out):
        conv = "(<%s>%s)" % (cpp_type.base_type, arg_in)
        # todo: long, uint, integer overflow !
        #
        check = Code()
        check.add("assert isinstance($arg, int), 'int required'",
                  arg=arg_in)
        return ConversionInfo("int", check, conv, "", arg_out, conv, "")

    def char_p_type_info(self, cpp_type, arg_in, arg_out):
        conv = "(<char *>%s)" % arg_in
        check = Code()
        # todo: unicode ?
        check.add("assert isinstance($arg, str), 'str required'",
                  arg=arg_in)
        return ConversionInfo("bytes", check, conv, "", arg_out, conv, "")

    def std_string_type_info(self, cpp_type, arg_in, arg_out):
        conv = "(<std_string>%s)" % arg_in
        check = Code()
        # todo: unicode ?
        check.add("assert isinstance($arg, str), 'str required'",
                  arg=arg_in)
        return ConversionInfo("str", check, conv, "", arg_out, conv, "")

    def cy_type_str(self, cpp_type):
        prefix = "_" if cpp_type.base_type in self.wrapped_types else ""
        if cpp_type.template_args is not None:
            cy_types = [self.cy_type_str(t) for t in cpp_type.template_args]
            postfix = "[%s]" % ", ".join(cy_types)
        else:
            postfix = ""

        if cpp_type.is_ptr:
            postfix += "*"

        return "%s%s%s" % (prefix, cpp_type.base_type, postfix)

    def std_vector_type_info(self, cpp_type, arg_in, arg_out):
        targ_cpp_type, = cpp_type.template_args

        targ_conversion_info = self.get(targ_cpp_type, "")
        targ_py_type = targ_conversion_info.py_type
        from_py, from_py_cleanup, call_as = py_list_to_vector_X(self, targ_cpp_type,
                arg_in, arg_out)
        to_py, to_py_cleanup = vector_X_to_py_list(self, targ_cpp_type, arg_out)

        return ConversionInfo("list",
                              check_py_list_code(arg_in, targ_py_type),\
                              from_py,
                              from_py_cleanup,
                              call_as,
                              to_py,
                              to_py_cleanup)


    def get(self, cpp_type, arg_in=None, arg_out=None):

        fun = self.customized.get((cpp_type.base_type, cpp_type.is_ptr))
        if fun:
            return fun(cpp_type, arg_in, arg_out)

        if cpp_type.base_type == "_String":
            return ConversionInfo("str",
                                  "",
                                  "_String(<std_string> %s)" % arg_in,
                                  "",
                                  "%s.c_str()" % arg_in,
                                  "")

        # wrapped type
        assert arg_in is not None
        assert cpp_type.base_type in self.wrapped_types
        if not cpp_type.is_ptr:
            return ConversionInfo(cpp_type.base_type,
                    "",
                    "<_%s>(deref(%s.inst))" % (cpp_type, arg_in),
                    "",
                    arg_out,
                    cpp_type_to_wrapped(self, cpp_type, arg_in),
                    "")
        else:
            return ConversionInfo(cpp_type.base_type,
                    "",
                    "<_%s >(%s.inst)" % (cpp_type, arg_in),
                    "",
                    arg_out,
                    cpp_ptr_type_to_wrapped(self, cpp_type, arg_in),
                    "")


        raise Exception("no conversion info for %s" % cpp_type)



def conversion_info_DataValue(cp, cpp_type, arg_name):

    def py_to__DataValue(cp, arg_name):
        conv_fun_name = "py_to__DataValue"
        conv_fun_code = Code("""cdef $conv_fun_name(obj):
                               |     if isinstance(obj, int):
                               |          return _DataValue(<int>obj)
                               |     if isinstance(obj, float):
                               |          return _DataValue(<double>obj)
                               |     if isinstance(obj, str):
                               |          return _DataValue(<std_string>obj)
                               |     return None
                              """).render(locals())
        cp.ufr.register(conv_fun_name, conv_fun_code)
        return Code("$conv_fun_name($arg_name)").render(locals())


    def _DataValue_to_py(cp, arg_name):
        conv_fun_name = "_DataValue_to_py"
        conv_fun_code = Code("""cdef $conv_fun_name(_DataValue val):
                               |     cdef type = val.valueType()
                               |     if type == _DataType.STRING_VALUE:
                               |         return <std_string> val
                               |     if type == _DataType.INT_VALUE:
                               |         return <int> val
                               |     if type == _DataType.DOUBLE_VALUE:
                               |         return <double> val
                               |     return None
                           """).render(locals())
        cp.ufr.register(conv_fun_name, conv_fun_code)
        return Code("$conv_fun_name($arg_name)").render(locals())

    return ConversionInfo("", "", py_to__DataValue(cp, arg_name),
            _DataValue_to_py(cp, arg_name))
    """
