#encoding: utf-8
import copy
import re

class CppType(object):

    CTYPES = ["int", "long", "double", "float", "char", "void"]
    LIBCPPTYPES = ["vector", "string", "list", "pair"]

    def __init__(self, base_type, template_args = None, is_ptr=False,
                 is_ref=False, is_unsigned = False, is_enum=False):
        self.base_type =  "void" if base_type is None else base_type
        self.is_ptr = is_ptr
        self.is_ref = is_ref
        self.is_unsigned = is_unsigned
        self.is_enum = is_enum
        self.template_args = template_args and tuple(template_args)

    def transform(self, typemap):
        base_type = typemap.get(self.base_type, self.base_type)
        if self.template_args:
            template_args = [t.transform(typemap) for t in self.template_args]
        else:
            template_args = self.template_args

        return CppType(base_type, template_args, self.is_ptr, self.is_ref,
                       self.is_unsigned, self.is_enum)

    def __hash__(self):

        # this one is recursive if we have template_args !
        return hash((self.base_type, self.is_ptr, self.is_ref,
                    self.is_unsigned, self.is_enum, hash(self.template_args)))

    def __eq__(self, other):
        """ for using Types as dict keys """
        # this one is recursive if we have template_args !
        return  (self.base_type, self.is_ptr, self.is_ref, self.is_unsigned,
                     self.is_enum, self.template_args ) == \
                (other.base_type, other.is_ptr, other.is_ref, other.is_unsigned,
                     other.is_enum, other.template_args)

    def without_ref(self):
        rv = copy.copy(self)
        rv.is_ref = False
        return rv

    def __str__(self):
        unsigned = "unsigned" if self.is_unsigned else ""
        ptr  = "*" if self.is_ptr else ""
        ref  = "&" if self.is_ref else ""
        if ptr and ref:
            raise NotImplementedError("can not handel ref and ptr together")
        if self.template_args is not None:
            inner = "[%s]" % (",".join(str(t) for t in self.template_args))
        else:
            inner = ""
        result = "%s %s%s%s" % (unsigned, self.base_type, inner, ptr or ref)
        return result.lstrip() # if unsigned is "" -> lstrip


    def matches(self, base_type, **kw):

        is_ptr = kw.get("is_ptr")
        is_ref = kw.get("is_ref")
        is_unsigned = kw.get("is_runsigned")
        template_args = kw.get("template_args")
        is_enum = kw.get("is_enum")

        if self.base_type != base_type:
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

    @staticmethod
    def parseDeclaration(as_string):
        base_type, t_str = re.match("(\w+)(\[.*\])?", as_string).groups()
        if t_str is None:
            return CppType(base_type)
        t_args = t_str[1:-1].split(",")
        t_types = [ CppType.parseDeclaration(t.strip()) for t in t_args ]
        return CppType(base_type, t_types)


def __cy_repr(type_):
    """ returns cython type representation """

    if type_.is_enum:
        rv = "enum "
    else:
        rv = ""
    if type_.base_type in CppType.CTYPES or \
        type_.base_type in CppType.LIBCPPTYPES:
        if type_.is_unsigned:
           rv += "unsigned "
        rv += type_.base_type
    else:
        rv += "_" + type_.base_type
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
    rv += type_.base_type
    if type_.template_args is not None:
        rv += "<%s>" % ",".join(cpp_repr(t) for t in type_.template_args)

    if type_.is_ptr:
        rv += " * "
    elif type_.is_ref:
        rv += " & "
    return rv


def __py_name(type_):
    """ returns Python representation, that is the name the module
        will expose to its users """
    return type_.base_type

def __py_type_for_cpp_type(type_):

    if type_.matches("char", is_ptr=True):
            return CppType("str")

    if type_.is_ptr:
        return None

    if type_.is_enum:
            return CppType("int")

    if type_.matches("long"):
            type_.base_type = "int" # preserve unsignedt...
            return type_

    if type_.matches("int"):
            return type_

    if type_.matches("bool"):
            return CppType("int")

    if type_.matches("float"):
            return type_

    if type_.matches("double"):
            return CppType("float")

    if type_.matches("string"):
            return CppType("str")

    if type_.matches("vector") or type_.matches("list"):
        return CppType("list")

    if type_.matches("pair"):
        return CppType("tuple")

    return type_

def __cy_decl(type_):

    type_ = py_type_for_cpp_type(type_)
    if type_ is None: return
    if type_.matches(None):
       return ""

    return ("unsigned " if type_.is_unsigned else "")  + type_.base_type + ("*" if type_.is_ptr  else "")


def __pysig_for_cpp_type(type_):

    pybase = py_type_for_cpp_type(type_).base_type
    if type_.template_args is None:
        return pybase

    else:
        pyargs = [pysig_for_cpp_type(t) for t in type_.template_args]
