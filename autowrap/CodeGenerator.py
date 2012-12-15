from contextlib import contextmanager
import os.path, sys

@contextmanager
def stdout_redirect(stream):
    sys.stdout = stream
    yield
    sys.stdout = sys.__stdout__


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
        #print current_dir, target_dir, _diff(current_dir, target_dir)
        parts.append(os.path.split(current_dir)[1])
        current_dir, _ = os.path.split(current_dir)

    return ".".join(parts[::-1])



class CodeGenerator(object):

    def __init__(self, decls, target_path=None):
        self.decls = decls
        self.target_path = os.path.abspath(target_path)
        self.target_dir  = os.path.dirname(self.target_path)

    def create_cimport_paths(self):
        for decl in self.decls:
            pxd_path = decl.cpp_decl.pxd_path
            pxd_dir = os.path.dirname(pxd_path)
            test_for_module_markers(pxd_dir, self.target_dir)
            decl.pxd_import_path = cimport_path(pxd_path, self.target_dir)

    def create_pyx_file(self, debug=False):
        self.create_cimport_paths()
        with open(self.target_path, "w") as fp:
            if debug:
                fp = Tee(fp, sys.stdout)
            with stdout_redirect(fp):
                self.create_cimports()
                for decl in self.decls:
                    self.create_wrapper_for(decl)

    def create_wrapper_for(self, decl):
        if decl.items:
            # enum
            pass
        else:
            print "cdef class %s:" % decl.name
            print "   cdef _%s * inst" % (decl.cpp_decl.as_cpp_decl())

            for (name, methods) in decl.methods.items():
                assert len(methods) == 1, "overloading not supported yet"
                method = methods[0]
                if name == decl.name:
                    print "   def __init__(self):"
                    print "       self.inst = new _%s()" % decl.cpp_decl.as_cpp_decl()
                else:
                    all_args = [n for (n, t) in method.arguments]
                    py_args = ["self"] + all_args
                    all_args_str = ", ".join(all_args)
                    py_args_str = ", ".join(py_args)
                    print "   def %s(%s):" % (name, py_args_str)
                    print "       return self.inst.%s(%s)" % (name,
                            all_args_str)



    def create_cimports(self):
        self.create_std_cimports()
        for decl in self.decls:
            cpp_decl = decl.cpp_decl
            rel_pxd_path = os.path.relpath(cpp_decl.pxd_path, self.target_path)
            cython_dir_name = rel_pxd_path.replace(os.sep, ".")
            if os.altsep:
                cython_dir_name = cython_dir_name.replace(os.altsep, ".")
            import_from = decl.pxd_import_path
            print "from %s cimport %s as _%s" % (import_from, cpp_decl.name,
                    cpp_decl.name)

    def create_std_cimports(self):
        print "from libcpp.string cimport string as cpp_string"
        print "from libcpp.vector cimport vector as cpp_vector"



