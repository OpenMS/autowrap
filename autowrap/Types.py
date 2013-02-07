#encoding: utf-8
import copy
import re

class CppType(object):

    CTYPES = ["int", "long", "double", "float", "char", "void"]
    LIBCPPTYPES = ["vector", "string", "list", "pair"]

    def __init__(self, base_type, template_args = None, is_ptr=False,
                 is_ref=False, is_unsigned = False, enum_items=None):
        self.base_type =  "void" if base_type is None else base_type
        self.is_ptr = is_ptr
        self.is_ref = is_ref
        self.is_unsigned = is_unsigned
        self.is_enum = enum_items is not None
        self.enum_items = enum_items
        self.template_args = template_args and tuple(template_args)

    def transformed(self, typemap):
        copied = self.copy()
        copied._transform(typemap, 0)
        copied.check_for_recursion()
        return copied

    def _transform(self, typemap, indent):

        aliased_t = typemap.get(self.base_type)
        if aliased_t is not None:
            if self.template_args is not None:
                if aliased_t.template_args is not None:
                    raise Exception("invalid transform")
                self._overwrite_base_type(aliased_t)
            else:
                self._overwrite_base_type(aliased_t)
                self.template_args = aliased_t.template_args
        for t in self.template_args or []:
            t._transform(typemap, indent+1)

    def _rm_flags(self):
        rv = self.copy()
        rv.is_ptr = rv.is_ref = False
        return rv

    def inv_transformed(self, typemap):
        inv_typemap = dict((v, CppType(k)) for (k,v) in typemap.items())
        return self._inv_transform(inv_typemap)

    def _inv_transform(self, inv_typemap):
        pure = self._rm_flags()
        if pure in inv_typemap:
            res = inv_typemap.get(pure)
            if self.is_ptr:
                res.is_ptr = True
            elif self.is_ref:
                res.is_ref = True
            return res
        if self.template_args is not None:
            trans_targs = [t._inv_transform(inv_typemap) for t in
                    self.template_args]
            self.template_args = trans_targs
        return self

    def _overwrite_base_type(self, other):
        if self.is_ptr and other.is_ptr:
            raise Exception("double ptr alias not supported")
        if self.is_ref and other.is_ref:
            raise Exception("double ref alias not supported")
        if self.is_ptr and other.is_ref:
            raise Exception("mixing ptr and ref not supported")
        self.base_type = other.base_type
        self.is_ptr = self.is_ptr or other.is_ptr
        self.is_ref = self.is_ref or other.is_ref
        self.is_unsigned = self.is_unsigned or other.is_unsigned

    def __hash__(self):
        """ for using Types as dict keys """
        return hash(str(self))

    def __eq__(self, other):
        """ for using Types as dict keys """
        return str(self) == str(other)

    def __ne__(self, other):
        """ for using Types as dict keys """
        return str(self) != str(other)

    def copy(self):
        return copy.deepcopy(self)

    def __str__(self):
        if self.is_unsigned and self.base_type != "size_t":
            unsigned = "unsigned"
        else:
            unsigned = ""

        ptr  = "*" if self.is_ptr else ""
        ref  = "&" if self.is_ref else ""
        if ptr and ref:
            raise NotImplementedError("can not handel ref and ptr together")
        if self.template_args is not None:
            inner = "[%s]" % (",".join(str(t) for t in self.template_args))
        else:
            inner = ""
        result = "%s %s%s %s" % (unsigned, self.base_type, inner, ptr or ref)
        return result.strip() # if unsigned is "" or ptr is "" and ref is ""

    def check_for_recursion(self):
        try:
            self._check_for_recursion(set())
        except Exception, e:
            if str(e) != "recursion check failed":
                raise e
            raise Exception("re check for '%s' failed" % self)

    def _check_for_recursion(self, seen_base_types):
        if self.base_type in seen_base_types:
            raise Exception("recursion check failed")
        seen_base_types.add(self.base_type)
        for t in self.template_args or []:
            # copy is needed, else B[X,X] would fail
            t._check_for_recursion(seen_base_types.copy())

    def all_occuring_base_types(self):
        base_types = set()
        self._collect_base_types(base_types)
        return base_types

    def _collect_base_types(self, base_types):
        base_types.add(self.base_type)
        for t in self.template_args or []:
            t._collect_base_types(base_types)

    @staticmethod
    def from_string(str_):
        try:
            return CppType._from_string(str_)
        except Exception, e:
            raise
            #raise Exception("could not parse '%s'" % str_)

    @staticmethod
    def _from_string(str_):
        matched = re.match("([a-zA-Z0-9][ a-zA-Z0-9]*)(\[.*\])? *[&\*]?", str_.strip())
        if matched is None:
            raise Exception("can not parse '%s'" % str_)
        base_type, t_str = matched.groups()
        if t_str is None:
            orig_for_error_message = base_type
            base_type = base_type.strip()
            is_unsigned, ptr, ref = False, False, False
            if base_type.startswith("unsigned"):
                is_unsigned = True
                base_type = base_type[8:].strip()
            if base_type.startswith("unsigned"):
                raise Exception("can not parse %s" % orig_for_error_message)
            if " " in base_type:
                raise Exception("can not parse %s" % orig_for_error_message)
            is_ref =  str_.endswith("&")
            is_ptr =  str_.endswith("*")
            return CppType(base_type,
                           is_unsigned=is_unsigned,
                           is_ptr=is_ptr,
                           is_ref=is_ref)

        t_args = t_str[1:-1].split(",")
        if t_args == [""]:
            t_types= []
        else:
            t_types = [ CppType.from_string(t.strip()) for t in t_args ]
        is_ref =  str_.endswith("&")
        is_ptr =  str_.endswith("*")

        return CppType(base_type, t_types, is_ref=is_ref, is_ptr=is_ptr)

def printable(type_map, join_str=", "):
    if not type_map:
        return "None"
    m_str = join_str.join("%s -> %s" %(k, v) for (k,v) in type_map.items())
    return m_str

