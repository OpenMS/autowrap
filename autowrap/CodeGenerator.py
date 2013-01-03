from contextlib import contextmanager
import os.path, sys

from ConversionProvider import ConversionProvider
from DeclResolver import ResolvedClass

import Code

@contextmanager
def stdout_redirect(stream):
    sys.stdout = stream
    yield
    sys.stdout = sys.__stdout__


def argument_names(method):
    return [n if (n and n != "self") else "in_%d" % i\
            for i, (n, t) in enumerate(method.arguments)]


class Tee(object):

    def __init__(self, *fps):
        self.fps = fps

    def write(self, *a):
        for fp in self.fps:
            fp.write(*a)

    def writelines(self, *a):
        for fp in self.fps:
            fp.writelines(*a)

    def flush(self, *a):
        for fp in self.fps:
            fp.flush(*a)


def _normalize(path):
    path = os.path.abspath(path)
    if path.endswith("/"):
        path = path[:-1]
    return path


def _diff(a_path, b_path):
    """ a_path minus b_path prefix """
    a_path = _normalize(a_path)
    b_path = _normalize(b_path)
    assert os.path.commonprefix([a_path, b_path]) == b_path,\
           "%s is not a prefix of %s" % (b_path, a_path)

    return a_path[len(b_path)+1:]


def _has_module_marker(dir_):
    return os.path.isfile(os.path.join(dir_, "__init__.py")) or \
           os.path.isfile(os.path.join(dir_, "__init__.pyx"))


def test_for_module_markers(start_at_dir, up_to_dir):
    start_at_dir = _normalize(start_at_dir)
    up_to_dir = _normalize(up_to_dir)

    assert os.path.commonprefix([start_at_dir, up_to_dir]) == up_to_dir,\
           "%s is not a prefix of %s" % (up_to_dir, start_at_dir)

    current_dir = start_at_dir
    while current_dir != up_to_dir:
        # test for __init__.pyx or __init__.py in current_dir
        if not _has_module_marker(current_dir):
               raise Exception("__init__.py[x] missing in %s" % current_dir)
        current_dir, _ = os.path.split(current_dir)


def cimport_path(pxd_path, target_dir):
    pxd_path = _normalize(pxd_path)
    pxd_dir  = _normalize(os.path.dirname(pxd_path))
    target_dir = _normalize(target_dir)

    base_pxd, _  = os.path.splitext(os.path.basename(pxd_path))
    parts = [base_pxd]
    current_dir = pxd_dir
    while _has_module_marker(current_dir):
        parts.append(os.path.split(current_dir)[1])
        current_dir, _ = os.path.split(current_dir)

    return ".".join(parts[::-1])


class CodeGenerator(object):

    def __init__(self, decls, target_path=None):
        self.decls = decls
        self.target_path = os.path.abspath(target_path)
        self.target_dir  = os.path.dirname(self.target_path)
        self.cp = ConversionProvider(decls)
        self.code = Code.Code()

    def setup_cimport_paths(self):
        for decl in self.decls:
            if isinstance(decl, ResolvedClass):
                pxd_path = decl.cpp_decl.pxd_path
                pxd_dir = os.path.dirname(pxd_path)
                test_for_module_markers(pxd_dir, self.target_dir)
                decl.pxd_import_path = cimport_path(pxd_path, self.target_dir)

    def create_pyx_file(self, debug=False):
        self.setup_cimport_paths()
        self.create_cimports()
        for decl in self.decls:
            if decl.items:
                self.create_wrapper_for_enum(decl)
            else:
                self.create_wrapper_for_class(decl)

        code = self.code.render()
        code += "\n\n"
        code += self.cp.render_utils()

        if debug:
            print code
        with open(self.target_path, "w") as fp:
            print >> fp, code

    def create_wrapper_for_enum(self, decl):
        self.code.add("cdef class $name:", name=decl.name)
        for (name, value) in decl.items:
            self.code.add("    $name = $value", name=name, value=value)


    def create_wrapper_for_class(self, decl):
        name = decl.name
        cy_type = self.cp.cy_decl_str(decl)
        self.code.add("""
               |cdef class $name:
               |    cdef $cy_type * inst
               |    def __dealloc__(self):
               |        if self.inst:
               |            del self.inst """, locals())

        for (name, methods) in decl.methods.items():
            if name == decl.name:
                self.create_wrapper_for_constructor(decl, methods)
            else:
                self.create_wrapper_for_method(decl, name, methods)

    def create_wrapper_for_method(self, decl, cpp_name, methods):
        if len(methods) == 1:
            self.create_wrapper_for_nonoverloaded_method(decl, cpp_name,
                                                         cpp_name, methods[0])
        else:
            for (i, method) in enumerate(methods):
                local_name = "_%s_%d" % (cpp_name, i)
                self.create_wrapper_for_nonoverloaded_method(decl, local_name,
                        cpp_name, method)

            meth_code = Code.Code()
            meth_code.add("""
                   |def $cpp_name(self, *args):
                   |    sign = tuple(map(type, args))
                   """, locals())
            for (i, method) in enumerate(methods):
                local_name = "_%s_%d" % (cpp_name, i)
                py_types = []
                arg_types =  [t for (n,t) in method.arguments]
                for arg_type in arg_types:
                    cinfo = self.cp.get(arg_type, "")
                    py_types.append(cinfo.py_type)
                py_sign = ", ".join(py_types)
                if py_sign != "":
                    py_sign += ","
                meth_code.add("""
                       |    if sign == ($py_sign):
                       |        return self.$local_name(*args)
                       """, locals())

            meth_code.add("    raise Exception('can not handle %s' % (sign,))")
            self.code.add(meth_code)

    def create_wrapper_for_nonoverloaded_method(self, decl, py_name, cpp_name,
                                                method):

        meth_code = Code.Code()

        meth_arg_names = argument_names(method)
        cinfos = []

        # collect info for converting input-args to args for cpp method:
        for i, (__, arg_t), arg_name in zip(xrange(9999), method.arguments,
                                            meth_arg_names):
            cpp_meth_arg = "arg%d" % i
            cinfo = self.cp.get(arg_t, arg_name, cpp_meth_arg)
            cinfos.append(cinfo)


        # create signature of python method
        py_args = ["self"]
        for (cinfo, arg_name) in zip(cinfos, meth_arg_names):
            py_args.append("%s %s" % (cinfo.py_type, arg_name))
        py_signature = ", ".join(py_args)

        meth_code.add("def $py_name($py_signature):", locals())

        # generate input check
        for cinfo in cinfos:
            meth_code.add(cinfo.arg_check_code)

        # create variable for calling cpp method
        cpp_meth_args = []
        for i, cinfo in enumerate(cinfos):
            cpp_meth_arg = "arg%d" % i
            py_to_cpp_conv = cinfo.from_py_code
            meth_code.add("    $cpp_meth_arg = $py_to_cpp_conv", locals())
            cpp_meth_args.append(cinfo.call_as)

        # call c++ method with converted args and generate output conversion
        args_str = ", ".join(cpp_meth_args)
        cy_result_type = self.cp.cy_decl_str(method.result_type)

        cinfo = self.cp.get(method.result_type, "_r")
        to_py_code = cinfo.to_py_code

        meth_code.add("""
                |    cdef $cy_result_type _r = self.inst.$cpp_name($args_str)
                |    cdef py_result = $to_py_code
                |    return py_result """, locals())

        self.code.add(meth_code)

    def create_wrapper_for_constructor(self, class_decl, methods):
        if len(methods) == 1:
            self.create_wrapper_for_nonoverloaded_constructor(class_decl,
                                                              "__init__",
                                                              methods[0])
        else:
            init_code = Code.Code()
            init_code.add("""def __init__(self, *args):
                            |    sign = tuple(map(type, args))""")

            for i, method in enumerate(methods):
                special_init_name = "_init_%d" % i

                py_types = []
                arg_types =  [t for (n,t) in method.arguments]
                for arg_type in arg_types:
                    cinfo = self.cp.get(arg_type, "")
                    py_types.append(cinfo.py_type)
                py_sign = ", ".join(py_types)
                if py_sign != "":
                    py_sign += ","
                init_code.add("""    if sign == ($py_sign):
                                |        self.$special_init_name(*args)
                                |        return""", locals())

                self.create_wrapper_for_nonoverloaded_constructor(class_decl,
                                                     special_init_name, method)

            init_code.add("    raise Exception('can not handle %s' % (sign,))")
            self.code.add(init_code)


    def create_wrapper_for_nonoverloaded_constructor(self, class_decl, py_name,
                                                           cons_decl):

        """ py_name ist name for constructor, as we dispatch overloaded
            constructors in __init__() the name of the method calling the
            c++ constructor is variable and given by `py_name`.

        """
        # TODO: examples !!!

        init_code = Code.Code()

        cons_arg_names = argument_names(cons_decl)
        cinfos = []

        # collect info for converting input-args to args for cpp constructor:
        for i, (__, arg_t), arg_name in zip(xrange(9999), cons_decl.arguments,
                                            cons_arg_names):
            cpp_cons_arg = "arg%d" % i
            cinfo = self.cp.get(arg_t, arg_name, cpp_cons_arg)
            cinfos.append(cinfo)

        # create signature of python method:
        py_args = ["self"]
        for cinfo, arg_name in zip(cinfos, cons_arg_names):
            py_args.append("%s %s" % (cinfo.py_type, arg_name))
        py_signature = ", ".join(py_args)

        init_code.add("def $py_name($py_signature):", locals())

        # generate input check
        for cinfo in cinfos:
            init_code.add(cinfo.arg_check_code)

        # create variables for calling cpp constructor:
        cpp_cons_args = []
        for i, cinfo in enumerate(cinfos):
            cpp_cons_arg = "arg%d" % i
            py_to_cpp_conv = cinfo.from_py_code
            init_code.add("    $cpp_cons_arg = $py_to_cpp_conv", locals())
            cpp_cons_args.append(cinfo.call_as)

        # call c++ method with converted args
        args = ", ".join(cpp_cons_args)
        init_code.add("    self.inst = new $name($args)",
                         name=self.cp.cy_decl_str(class_decl), args=args)

        # add cons code to overall code:
        self.code.add(init_code)


    def create_cimports(self):
        self.create_std_cimports()
        for decl in self.decls:
            if isinstance(decl, ResolvedClass):
                cpp_decl = decl.cpp_decl
                rel_pxd_path = os.path.relpath(cpp_decl.pxd_path,
                                               self.target_path)
                cython_dir_name = rel_pxd_path.replace(os.sep, ".")
                if os.altsep:
                    cython_dir_name = cython_dir_name.replace(os.altsep, ".")
                import_from = decl.pxd_import_path
                self.code.add("from $from_ cimport $name as _$name",
                                       from_=import_from, name = cpp_decl.name)

    def create_std_cimports(self):
        self.code.add("""
           |from libcpp.string cimport string as std_string
           |from libcpp.vector cimport vector as std_vector
           |from cython.operator cimport dereference as deref,
           + preincrement as inc, address as address""")



