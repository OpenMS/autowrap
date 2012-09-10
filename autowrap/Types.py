#encoding: utf-8
import copy

class CppType(object):

    CTYPES = ["int", "long", "double", "float", "char", "void"]
    LIBCPPTYPES = ["vector", "string", "list", "pair"]

    def __init__(self, basetype, is_ptr=False, is_ref=False,
                       is_unsigned = False,
                       template_args=None, is_enum=False):
        self.basetype =  "void" if basetype is None else basetype
        self.is_ptr = is_ptr
        self.is_ref = is_ref
        self.is_unsigned = is_unsigned
        self.is_enum = is_enum
        self.template_args = template_args and tuple(template_args)

    def __hash__(self):

        # this one is recursive if we have template_args !
        return hash( (self.basetype, self.is_ptr, self.is_ref, 
                     self.is_unsigned, self.is_enum, hash(self.template_args) ) )
    def __eq__(self, other):
        """ for using Types as dict keys """
        # this one is recursive if we have template_args !
        return  (self.basetype, self.is_ptr, self.is_ref, self.is_unsigned,
                     self.is_enum, self.template_args ) == \
                (other.basetype, other.is_ptr, other.is_ref, other.is_unsigned,
                     other.is_enum, other.template_args) 

    def without_ref(self):
        rv = copy.copy(self)
        rv.is_ref = False
        return rv

    def matches(self, basetype, **kw):

        is_ptr = kw.get("is_ptr")
        is_ref = kw.get("is_ref")
        is_unsigned = kw.get("is_runsigned")
        template_args = kw.get("template_args")
        is_enum = kw.get("is_enum")

        if self.basetype != basetype:
            return False

        if (is_ptr is not None and is_ptr != self.is_ptr):
            return False

        if (is_ref is not None and is_ref != self.is_ref):
            return False

        if (is_unsigned is not None and is_unsigned != self.is_unsigned):
            return False

        if (is_enum is not None and is_enum != self.is_enum):
            return False

        if (template_args is not None and template_args != self.template_args):
            return False

        return True

       

def cy_repr(type_):
    """ returns cython type representation """

    if type_.is_enum:
        rv = "enum "
    else:
        rv = ""
    if type_.basetype in Type.CTYPES or type_.basetype in Type.LIBCPPTYPES:
        if type_.is_unsigned:
           rv += "unsigned "
        rv += type_.basetype
    else:
        rv += "_" + type_.basetype
    if type_.template_args is not None:
        rv += "[%s]" % ",".join(cy_repr(t) for t in type_.template_args)

    if type_.is_ptr:
        rv += " * "
    elif type_.is_ref:
        rv += " & "
    return rv


def __cpp_repr(type_):
    """ returns C++ type representation """

    if type_.is_enum:
        rv = "enum "
    else:
        rv = ""

    if type_.is_unsigned:
        rv += "unsigned "
    rv += type_.basetype
    if type_.template_args is not None:
        rv += "<%s>" % ",".join(cpp_repr(t) for t in type_.template_args)

    if type_.is_ptr:
        rv += " * "
    elif type_.is_ref:
        rv += " & "
    return rv


def py_name(type_):
    """ returns Python representation, that is the name the module
        will expose to its users """
    return type_.basetype

def py_type_for_cpp_type(type_):

    if type_.matches("char", is_ptr=True):
            return Type("str")

    if type_.is_ptr:
        return None

    if type_.is_enum:
            return Type("int")

    if type_.matches("long"):
            type_.basetype = "int" # preserve unsignedt...
            return type_

    if type_.matches("int"):
            return type_

    if type_.matches("bool"):
            return Type("int")

    if type_.matches("float"):
            return type_

    if type_.matches("double"):
            return Type("float")

    if type_.matches("string"):
            return Type("str")

    if type_.matches("vector") or type_.matches("list"):
        return Type("list")

    if type_.matches("pair"):
        return Type("tuple")

    return type_

def cy_decl(type_):

    type_ = py_type_for_cpp_type(type_)
    if type_ is None: return
    if type_.matches(None):
       return ""

    return ("unsigned " if type_.is_unsigned else "")  + type_.basetype + ("*" if type_.is_ptr  else "")


def pysig_for_cpp_type(type_):

    pybase = py_type_for_cpp_type(type_).basetype
    if type_.template_args is None:
        return pybase

    else:
        pyargs = [pysig_for_cpp_type(t) for t in type_.template_args]
        return "%s[%s]" % (pybase, ", ".join(pyargs))


 
        
