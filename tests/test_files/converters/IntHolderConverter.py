from autowrap.Code import Code
from autowrap.ConversionProvider import (TypeConverterBase,
                                         mangle,
                                         StdMapConverter)

class IntHolderConverter(TypeConverterBase):

    def get_base_types(self):
        return "IntHolder",

    def matches(self, cpp_type):
        return  not cpp_type.is_ptr

    def matching_python_type(self, cpp_type):
        return "int"

    def type_check_expression(self, cpp_type, argument_var):
        return "isinstance(%s, int)" % (argument_var,)

    def input_conversion(self, cpp_type, argument_var, arg_num):
        # here we inject special behavoir for testing if this converter
        # was called !
        ih_name = "ih_" + argument_var
        code = Code().add("""
                          |cdef _Holder[int] $ih_name
                          |$ih_name.set(<int>$argument_var)
                          """, locals())
        call_as = "(%s)" % ih_name
        cleanup = ""
        return code, call_as, cleanup

    def output_conversion(self, cpp_type, input_cpp_var, output_py_var):
        return "%s = <int>(%s.get())" % (output_py_var, input_cpp_var)
