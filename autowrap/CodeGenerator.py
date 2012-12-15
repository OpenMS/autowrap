from contextlib import contextmanager
import os.path, sys

import ToCppConverters

import Code

@contextmanager
def stdout_redirect(stream):
    sys.stdout = stream
    yield
    sys.stdout = sys.__stdout__


def input_arg_names(method):
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
        self.conv_provider = ToCppConverters.ConversionInfoProvider()
        self.code = Code.Code()

    def create_cimport_paths(self):
        for decl in self.decls:
            pxd_path = decl.cpp_decl.pxd_path
            pxd_dir = os.path.dirname(pxd_path)
            test_for_module_markers(pxd_dir, self.target_dir)
            decl.pxd_import_path = cimport_path(pxd_path, self.target_dir)

    def create_pyx_file(self, debug=False):
        self.create_cimport_paths()
        self.create_cimports()
        for decl in self.decls:
            if decl.items:
                self.create_wrapper_for_enumd(decl)
            else:
                self.create_wrapper_for_class(decl)

        code = self.code.render()
        if debug:
            print code
        with open(self.target_path, "w") as fp:
            print >> fp, code


    def create_wrapper_for_enum(self, decl):
        raise Exception("enums not implemented yet")

    def create_wrapper_for_class(self, decl):
        self.code.add("cdef class $name:", name=decl.name)
        self.code.add("    cdef _$cy_type * inst",
                                 cy_type= decl.cpp_decl.as_cython_decl())

        for (name, methods) in decl.methods.items():
            if name == decl.name:
                self.create_wrapper_for_constructor(decl, methods)
            else:
                self.create_wrapper_for_method(decl, name, methods)

    def create_wrapper_for_method(self, decl, name, methods):
        if len(methods) == 1:
            method = methods[0]
            meth_code = Code.Code()

            all_args = input_arg_names(method)
            py_args = ["self"] + all_args
            py_args_str = ", ".join(py_args)
            cinfos = []
            for (__, t), n in zip(method.arguments, all_args):
                cinfo = self.conv_provider.get(t, n)
                cinfos.append(cinfo)

            meth_code.add("def $name($py_args_str):", name=method.name,
                                                     py_args_str=py_args_str)

            # generate input conversion
            for cinfo in cinfos:
                meth_code.add(cinfo.arg_check_code)

            # call c++ method with converted args
            input_args = ", ".join(info.from_py_code for info in cinfos)
            meth_code.add("    result = self.inst.$meth_name($args)",
                                   meth_name = name, args =input_args)

            # generate output conversion
            meth_code.add("    return result")

            self.code.add(meth_code)
        else:
            raise Exception("overloading not supported yet")

    def create_wrapper_for_constructor(self, decl, methods):
        if len(methods) == 1:
            meth_code = Code.Code()
            meth_code.add("def __init__(self):")
            meth_code.add("    self.inst = new _$name()",
                         name=decl.cpp_decl.as_cython_decl())
            self.code.add(meth_code)
        else:
            raise Exception("overloading not supported yet")

    def create_cimports(self):
        self.create_std_cimports()
        for decl in self.decls:
            cpp_decl = decl.cpp_decl
            rel_pxd_path = os.path.relpath(cpp_decl.pxd_path, self.target_path)
            cython_dir_name = rel_pxd_path.replace(os.sep, ".")
            if os.altsep:
                cython_dir_name = cython_dir_name.replace(os.altsep, ".")
            import_from = decl.pxd_import_path
            self.code.add("from $from_ cimport $name as _$name",
                          from_=import_from, name = cpp_decl.name)

    def create_std_cimports(self):
        self.code.add("""from libcpp.string cimport string as cpp_string
                        |from libcpp.vector cimport vector as cpp_vector
                        +""")



