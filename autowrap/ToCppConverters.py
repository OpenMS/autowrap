from collections import namedtuple, OrderedDict
import re
from string import Template

from CppType import CppType
from Code    import Code

        
class Context(object):
    registry = dict()

    @staticmethod
    def register(name, code):
        Context.registry[name] = code

    @staticmethod
    def print_all_decls():
        for code in Context.registry.values():
            print code.replace("       |", "")
            print

ConversionInfo = namedtuple("ConversionInfo", [ "py_type", "arg_check_code", "from_py_code", "to_py_code" ])


def py_type_to_str(t):
    return re.match("<type '(.*)'>", str(t)).group(1)

def check_py_list_code(arg_name, inner_py_type):
    inner_py_type_as_str = py_type_to_str(inner_py_type)
    return Code("""assert type($arg_name) == list 
                  + and all(isinstance(it, $inner_py_type_as_str) for it in $arg_name),
                  + "arg $arg_name does not match" 
                """).render(**locals())

def py_list_to_vector_X(c, X_type, var_name):
    
    conv_fun_name = "py_list_to_vector_%s" % X_type.identifier()
    _, _, py_item_to_X, _ = c.get(X_type, "item")

    Context.register(conv_fun_name,
          Code("""cdef libcpp_vector[$X_type] $conv_fun_name(list li):
                 |    cdef libcpp_vector[$X_type] res
                 |    for item in li:
                 |        res.push_back($py_item_to_X)
                 |    return res
               """).render(**locals()))

    return "%(conv_fun_name)s(%(var_name)s)" % locals()
    

def vector_X_to_py_list(c, X_type, var_name):

    conv_fun_name = "vector_%s_to_py_list" % X_type.identifier()
    _, _, _, X_to_py = c.get(X_type, "v")

    Context.register(conv_fun_name,
           Code("""cdef $conv_fun_name(libcpp_vector[$X_type] vec):
                  |    return [ $X_to_py for v in vec ]
                """).render(**locals()))

    return "%(conv_fun_name)s(%(var_name)s)" % locals()

class ConversionInfoProvider(object):

    def __init__(self):
        self.customized = dict()
        self.add_data("int", self.num_type_info)
        self.add_data("long", self.num_type_info)
        self.add_data("bool", self.num_type_info)

        self.add_data("std::string", self.std_string_type_info)
        self.add_data("std::vector", self.std_vector_type_info)

    def add_data(self, name, fun):
        self.customized[name] = fun
    
    def num_type_info(self, cpp_type, arg_name):
        conv = "(<%s>%s)" % (cpp_type.base, arg_name)
        return ConversionInfo(int, "", conv, conv)


    def std_string_type_info(self, cpp_type, arg_name):
        conv = "(<libcpp_string>%s)" % arg_name
        return ConversionInfo(str, "", conv, conv)

    def std_vector_type_info(self, cpp_type, arg_name):
        targs = cpp_type.targs
        assert len(targs) == 1
        targ_cpp_type = targs[0]

        targ_conversion_info = self.get(targ_cpp_type, None)
        targ_py_type = targ_conversion_info.py_type

        return ConversionInfo(list, 
                              check_py_list_code(arg_name, targ_py_type),\
                              py_list_to_vector_X(self, targ_cpp_type, arg_name),\
                              vector_X_to_py_list(self, targ_cpp_type, arg_name))


    def get(self, cpp_type, arg_name="<unused>"):

        fun = self.customized.get(cpp_type.base)
        if fun:
            return fun(cpp_type, arg_name)

        if cpp_type.base == "_String":
            return ConversionInfo(str, 
                                  "", 
                                  "_String(<libcpp_string> %s)" % arg_name,
                                  "%s.c_str()" % arg_name)


def conversion_info_DataValue(c, cpp_type, arg_name):
    
    def py_to__DataValue(c, arg_name):
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
        Context.register(conv_fun_name, conv_fun_code)
        return Code("$conv_fun_name($arg_name)").render(**locals())


    def _DataValue_to_py(c, arg_name):
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
        Context.register(conv_fun_name, conv_fun_code)
        return Code("$conv_fun_name($arg_name)").render(**locals())

    return ConversionInfo("", "", py_to__DataValue(c, arg_name), _DataValue_to_py(c, arg_name))

    
if __name__ == "__main__":
    print """
from libcpp.vector cimport vector as libcpp_vector
from libcpp.string cimport string as libcpp_string

from pxd.String cimport String as _String
"""
    
    c = ConversionInfoProvider()
    cinfo = c.get(CppType("std::vector", [CppType("int")]), "arg0")
    print cinfo.arg_check_code
    #print
    print cinfo.from_py_code
    #print
    print cinfo.to_py_code


    cinfo = c.get(CppType("std::vector", [CppType("_String")]), "arg1")
    print cinfo.arg_check_code
    #print
    print cinfo.from_py_code
    #print
    print cinfo.to_py_code
    #print

    Context.print_all_decls()
