from collections import namedtuple
import re
from DeclResolver import ResolvedClass

from Types import CppType
from Code import Code


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

ConversionInfo = namedtuple("ConversionInfo", [ "py_type", "arg_check_code",
                                                "from_py_code", "to_py_code" ])


def py_type_to_str(t):
    return re.match("<type '(.*)'>", str(t)).group(1)

def check_py_list_code(arg_name, inner_py_type):
    inner_py_type_as_str = py_type_to_str(inner_py_type)
    return Code("""assert type($arg_name) == list
                  + and all(isinstance(it, $inner_py_type_as_str) for it in $arg_name),
                  + "arg $arg_name does not match"
                """).render(**locals())

def py_list_to_vector_X(cp, X_type, var_name):

    conv_fun_name = "py_list_to_vector_%s" % X_type.identifier()
    _, _, py_item_to_X, _ = cp.get(X_type, False, "item")

    cp.ufr.register(conv_fun_name,
          Code("""cdef libcpp_vector[$X_type] $conv_fun_name(list li):
                 |    cdef libcpp_vector[$X_type] res
                 |    for item in li:
                 |        res.push_back($py_item_to_X)
                 |    return res
               """).render(**locals()))

    return "%(conv_fun_name)s(%(var_name)s)" % locals()


def vector_X_to_py_list(cp, X_type, var_name):

    conv_fun_name = "vector_%s_to_py_list" % X_type.identifier()
    _, _, _, X_to_py = cp.get(X_type, False, "v")

    cp.ufr.register(conv_fun_name,
           Code("""cdef $conv_fun_name(libcpp_vector[$X_type] vec):
                  |    return [ $X_to_py for v in vec ]
                """).render(**locals()))

    return "%(conv_fun_name)s(%(var_name)s)" % locals()


def cpp_type_to_wrapped(cp, cpp_type, var_name):

    conv_fun_name = "%s_to_py" % cp.cy_decl_str(cpp_type)

    base_type = cpp_type.base_type

    assert not cpp_type.is_ptr

    cp.ufr.register(conv_fun_name,
        Code().add("""cdef $conv_fun_name(_$base_type & inst):
                    |     cdef $base_type result = $base_type.__new__($base_type)
                    |     result.inst = new _$base_type(inst)
                    |     return result
                    """, **locals())
        )
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
        self.add_data("std::vector", False, self.std_vector_type_info)

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

    def num_type_info(self, cpp_type, arg_name):
        conv = "(<%s>%s)" % (cpp_type.base_type, arg_name)
        # todo: long, uint, integer overflow !
        #
        check = Code()
        check.add("assert isinstance($arg, int), 'int required'",
                  arg=arg_name)
        return ConversionInfo("int", check, conv, conv)

    def char_p_type_info(self, cpp_type, arg_name):
        conv = "(<char *>%s)" % arg_name
        check = Code()
        # todo: unicode ?
        check.add("assert isinstance($arg, str), 'str required'",
                  arg=arg_name)
        return ConversionInfo("bytes", check, conv, conv)

    def std_string_type_info(self, cpp_type, arg_name):
        conv = "(<std_string>%s)" % arg_name
        check = Code()
        # todo: unicode ?
        check.add("assert isinstance($arg, str), 'str required'",
                  arg=arg_name)
        return ConversionInfo("str", check, conv, conv)

    def std_vector_type_info(self, cpp_type, arg_name):
        targs = cpp_type.targs
        assert len(targs) == 1
        targ_cpp_type = targs[0]

        targ_conversion_info = self.get(targ_cpp_type, False, None)
        targ_py_type = targ_conversion_info.py_type

        return ConversionInfo("list",
                              check_py_list_code(arg_name, targ_py_type),\
                              py_list_to_vector_X(self, targ_cpp_type, arg_name),\
                              vector_X_to_py_list(self, targ_cpp_type, arg_name))


    def get(self, cpp_type, arg_name=None):

        fun = self.customized.get((cpp_type.base_type, cpp_type.is_ptr))
        if fun:
            return fun(cpp_type, arg_name)

        if cpp_type.base_type == "_String":
            return ConversionInfo("str",
                                  "",
                                  "_String(<libcpp_string> %s)" % arg_name,
                                  "%s.c_str()" % arg_name)

        # wrapped type
        assert arg_name is not None
        assert cpp_type.base_type in self.wrapped_types
        if not cpp_type.is_ptr:
            return ConversionInfo(cpp_type.base_type,
                    "",
                    "<_%s>(deref(%s.inst))" % (cpp_type, arg_name),
                    cpp_type_to_wrapped(self, cpp_type, arg_name))
        else:
            return ConversionInfo(cpp_type.base_type,
                    "",
                    "<_%s >(%s.inst)" % (cpp_type, arg_name),
                    cpp_ptr_type_to_wrapped(self, cpp_type, arg_name))


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
                               |          return _DataValue(<libcpp_string>obj)
                               |     return None
                              """).render(**locals())
        cp.ufr.register(conv_fun_name, conv_fun_code)
        return Code("$conv_fun_name($arg_name)").render(**locals())


    def _DataValue_to_py(cp, arg_name):
        conv_fun_name = "_DataValue_to_py"
        conv_fun_code = Code("""cdef $conv_fun_name(_DataValue val):
                               |     cdef type = val.valueType()
                               |     if type == _DataType.STRING_VALUE:
                               |         return <libcpp_string> val
                               |     if type == _DataType.INT_VALUE:
                               |         return <int> val
                               |     if type == _DataType.DOUBLE_VALUE:
                               |         return <double> val
                               |     return None
                           """).render(**locals())
        cp.ufr.register(conv_fun_name, conv_fun_code)
        return Code("$conv_fun_name($arg_name)").render(**locals())

    return ConversionInfo("", "", py_to__DataValue(cp, arg_name),
            _DataValue_to_py(cp, arg_name))


if __name__ == "__main__":
    print """
from libcpp.vector cimport vector as libcpp_vector
from libcpp.string cimport string as libcpp_string

from pxd.String cimport String as _String
"""

    cp = ConversionProvider()
    cinfo = cp.get(CppType("std::vector", [CppType("int")]), False, "arg0")
    print cinfo.arg_check_code
    #print
    print cinfo.from_py_code
    #print
    print cinfo.to_py_code


    cinfo = cp.get(CppType("std::vector", [CppType("_String")]), False, "arg1")
    print cinfo.arg_check_code
    #print
    print cinfo.from_py_code
    #print
    print cinfo.to_py_code
    #print

    cp.ufr.print_all_decls()
