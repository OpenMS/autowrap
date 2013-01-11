from contextlib import contextmanager
import os.path
import sys
import re
from collections import defaultdict

from ConversionProvider import setup_converter_registry
from DeclResolver import ResolvedClass, ResolvedEnum
from Types import CppType

import Code


@contextmanager
def stdout_redirect(stream):
    sys.stdout = stream
    yield
    sys.stdout = sys.__stdout__


def augment_arg_names(method):
    """ replaces missing arg_names with "in_%d" % i, where i is the position
        number of the arg """
    return [(t, n if (n and n != "self") else "in_%d" % i)\
                                  for i, (n, t) in enumerate(method.arguments)]


# TODO:
#   - common path prefix of all pxds
#   - check subdirs for markers
#   - create relative import pathes of all pxds related to common
#     path prefix
#   - set self.pxd_dir to this common prefix


if 0:

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


def fixed_include_dirs():
    import pkg_resources
    boost = pkg_resources.resource_filename("autowrap", "data_files/boost")
    data = pkg_resources.resource_filename("autowrap", "data_files")
    return [boost, data]

class CodeGenerator(object):

    def __init__(self, decls, target_path=None):
        self.decls = sorted(decls, key = lambda decl: decl.name)
        self.target_path = os.path.abspath(target_path)
        self.target_dir  = os.path.dirname(self.target_path)

        self.class_decls = [d for d in decls if isinstance(d, ResolvedClass)]
        self.enum_decls = [d for d in decls if isinstance(d, ResolvedEnum)]
        class_names = [c.name for c in self.class_decls]
        enum_names = [c.name for c in self.enum_decls]

        self.cr = setup_converter_registry(class_names, enum_names)

        self.code = Code.Code()


    def get_include_dirs(self):
        return fixed_include_dirs() + [self.pxd_dir]

    def setup_cimport_paths(self):

        pxd_dirs = set()
        for decl in self.class_decls + self.enum_decls:
            pxd_path = os.path.abspath(decl.cpp_decl.pxd_path)
            pxd_dir = os.path.dirname(pxd_path)
            pxd_dirs.add(pxd_dir)
            pxd_file = os.path.basename(pxd_path)
            decl.pxd_import_path, __ = os.path.splitext(pxd_file)

        assert len(pxd_dirs) == 1, \
                                  "pxd files must be located in same directory"

        self.pxd_dir = pxd_dirs.pop()


    def create_pyx_file(self, debug=False):
        self.setup_cimport_paths()
        self.create_cimports()
        self.create_includes()
        for decl in self.decls:
            if decl.wrap_ignore:
                continue
            if isinstance(decl, ResolvedEnum):
                self.create_wrapper_for_enum(decl)
            elif isinstance(decl, ResolvedClass):
                self.create_wrapper_for_class(decl)
            else:
                raise Exception("can not handle %s" % decl)

        code = self.code.render()
        code += "\n\n"

        if debug:
            print code
        with open(self.target_path, "w") as fp:
            print >> fp, code

    def filterout_iterators(self, methods):
        def parse(anno):
            m = re.match("(\S+)\((\S+)\)", anno)
            assert m is not None, "invalid iter annotation"
            name, type_name = m.groups()
            return name, CppType(type_name)

        begin_iterators = dict()
        end_iterators = dict()
        non_iter_methods = defaultdict(list)
        for name, mi in methods.items():
            for method in mi:
                annotations = method.decl.annotations
                if "wrap-iter-begin" in annotations:
                    py_name, res_type = parse(annotations["wrap-iter-begin"])
                    begin_iterators[py_name] = (method, res_type)
                elif "wrap-iter-end" in annotations:
                    py_name, res_type = parse(annotations["wrap-iter-end"])
                    end_iterators[py_name] = (method, res_type)
                else:
                    non_iter_methods[name].append(method)

        begin_names = set(begin_iterators.keys())
        end_names = set(end_iterators.keys())
        common_names = begin_names & end_names
        if begin_names != end_names:
            # TODO: diesen fall testen
            raise Exception("iter declarations not balanced")

        for py_name in common_names:
            __, res_type_begin = begin_iterators[py_name]
            __, res_type_end = end_iterators[py_name]
            assert res_type_begin == res_type_end, \
                                                "iter value types do not match"

        begin_methods = dict( (n, m) for n, (m, __) in begin_iterators.items())
        end_methods = dict( (n, m) for n, (m, __) in end_iterators.items())
        res_types = dict( (n, t) for n, (__, t) in end_iterators.items())


        iterators = dict()
        for n in common_names:
            iterators[n] = (begin_methods[n], end_methods[n], res_types[n])

        return iterators, non_iter_methods


    def create_wrapper_for_enum(self, decl):
        self.code.add("cdef class $name:", name=decl.name)
        for (name, value) in decl.items:
            self.code.add("    $name = $value", name=name, value=value)


    def create_wrapper_for_class(self, decl):
        name = decl.name
        cy_type = self.cr.cy_decl_str(decl.type_)
        self.code.add("""
               |cdef class $name:
               |    cdef shared_ptr[$cy_type] inst
               |    def __dealloc__(self):
               |         self.inst.reset()
               """, locals())

        cons_created = False

        iterators, non_iter_methods = self.filterout_iterators(decl.methods)

        for (name, methods) in non_iter_methods.items():
            if name == decl.name:
                self.create_wrapper_for_constructor(decl, methods)
                cons_created = True
            else:
                self.create_wrapper_for_method(decl, name, methods)
        assert cons_created, "no constructor for %s created" % name

        self._create_iter_methods(iterators)

    def _create_iter_methods(self, iterators):
        for name, (begin_decl, end_decl, res_type) in iterators.items():
            meth_code = Code.Code()
            begin_name = begin_decl.name
            end_name = end_decl.name

            base_type = res_type.base_type
            meth_code.add("""def $name(self):
                            |    it = self.inst.get().$begin_name()
                            |    cdef $base_type out
                            |    while it != self.inst.get().$end_name():
                            |        out = $base_type.__new__($base_type)
                            |        out.inst =
                            + shared_ptr[_$base_type](new _$base_type(deref(it)))
                            |        yield out
                            |        inc(it)
                            """, locals())

            self.code.add(meth_code)

    def _create_overloaded_method_decl(self, code, cpp_name,
                                      dispatched_m_names, methods, use_return):

        code.add("""def $cpp_name(self, *args):""", locals())

        first_iteration = True
        for (dispatched_m_name, method) in zip(dispatched_m_names, methods):
            args = augment_arg_names(method)
            if not args:
                check_expr = "not args"
            else:
                tns = [ (t, "args[%d]" % i) for i, (t, n) in enumerate(args)]
                checks = ["len(args)==%d" % len(tns)]
                checks += [self.cr.get(t).type_check_expression(t, n)\
                                                            for (t, n) in tns]
                check_expr = " and ".join( "(%s)" % c for c in checks)
            return_ = "return" if use_return else ""
            if_elif = "if" if first_iteration else "elif"
            code.add("""
                    |    $if_elif $check_expr:
                    |        $return_ self.$dispatched_m_name(*args)
                    """, locals())
            first_iteration = False

        code.add("""    else:
                   |        raise Exception('can not handle %s' % (args,))""")

    def create_wrapper_for_method(self, decl, cpp_name, methods):
        if len(methods) == 1:
            self.create_wrapper_for_nonoverloaded_method(decl, cpp_name,
                                                         cpp_name, methods[0],
                                                         )
        else:
            # TODO: what happens if two distinct c++ types as float, double
            # map to the same python type ??
            # -> 1) detection
            # -> 2) force method renaming
            dispatched_m_names = []
            for (i, method) in enumerate(methods):
                dispatched_m_name = "_%s_%d" % (cpp_name, i)
                dispatched_m_names.append(dispatched_m_name)
                self.create_wrapper_for_nonoverloaded_method(decl,
                                                             dispatched_m_name,
                                                             cpp_name,
                                                             method,
                                                             )

            meth_code = Code.Code()
            self._create_overloaded_method_decl(meth_code, cpp_name,
                                                           dispatched_m_names,
                                                           methods,
                                                           True)
            self.code.add(meth_code)

    def _create_meth_decl_and_input_conversion(self, code, py_name, method):
        args = augment_arg_names(method)

        # collect conversion data for input args
        py_signature_parts = []
        input_conversion_codes = []
        cleanups = []
        call_args = []
        checks = []
        in_types = []
        for arg_num, (t, n) in enumerate(args):
            converter = self.cr.get(t)
            py_type = converter.matching_python_type(t)
            conv_code, call_as, cleanup =\
                                      converter.input_conversion(t, n, arg_num)
            py_signature_parts.append("%s %s " % (py_type, n))
            input_conversion_codes.append(conv_code)
            cleanups.append(cleanup)
            call_args.append(call_as)
            in_types.append(t)
            checks.append((n, converter.type_check_expression(t, n)))

        # create method decl statement
        py_signature = ", ".join(["self"] + py_signature_parts)
        code.add("""def $py_name($py_signature):""", locals())

        # create code which convert python input args to c++ args of wrapped
        # method:
        for n, check in checks:
            code.add("    assert %s, 'arg %s invalid'" % (check, n))
        for conv_code in input_conversion_codes:
            code.add(conv_code)

        return call_args, cleanups, in_types

    def create_wrapper_for_nonoverloaded_method(self, decl, py_name, cpp_name,
            method):

        if cpp_name == "operator==":
            self.create_special_eq_method(decl)
            return

        meth_code = Code.Code()

        call_args, cleanups, in_types =\
                         self._create_meth_decl_and_input_conversion(meth_code,
                                                                     py_name,
                                                                     method)

        # call wrapped method and convert result value back to python

        call_args_str = ", ".join(call_args)
        cy_call_str = "self.inst.get().%s(%s)" % (cpp_name, call_args_str)

        res_t = method.result_type
        out_converter = self.cr.get(res_t)
        full_call_stmt = out_converter.call_method(res_t, cy_call_str)

        if isinstance(full_call_stmt, basestring):
            meth_code.add("""
                |    $full_call_stmt
                """, locals())
        else:
            meth_code.add(full_call_stmt)

        for cleanup in cleanups:
            if not cleanup:
                continue
            if isinstance(cleanup, basestring):
                cleanup = "    %s" % cleanup
            meth_code.add(cleanup)

        out_vars = ["py_result"]
        if "ref-arg-out" in method.decl.annotations:
            out_ixs = map(int, method.decl.annotations["ref-arg-out"])
            for i, (type_, call_arg) in enumerate(zip(in_types, call_args)):
                if i in out_ixs:
                    to_py_code = self.cr.get(type_).output_conversion(type_,
                                                                    call_arg,
                                                                    "pyr_%d" %i)
                    out_vars.append("pyr_%d" % i)
                    if isinstance(to_py_code, basestring):
                        to_py_code = "    %s" % to_py_code
                    meth_code.add(to_py_code)

        to_py_code = out_converter.output_conversion(res_t, "_r", "py_result")

        if to_py_code is not None:  # for non void return value

            if isinstance(to_py_code, basestring):
                to_py_code = "    %s" % to_py_code
            meth_code.add(to_py_code)
            meth_code.add("    return %s" % (", ".join(out_vars)))

        self.code.add(meth_code)


    def create_wrapper_for_constructor(self, class_decl, constructors):
        real_constructors = []
        for cons in constructors:
            if len(cons.arguments) == 1:
                (n, t), = cons.arguments
                if t.base_type == class_decl.name and t.is_ref:
                    self.create_special_copy_method(class_decl)
                    continue
            real_constructors.append(cons)

        if len(real_constructors) == 1:
            self.create_wrapper_for_nonoverloaded_constructor(class_decl,
                                              "__init__", real_constructors[0])
        else:
            dispatched_cons_names =[]
            for (i, constructor) in enumerate(real_constructors):
                dispatched_cons_name = "_init_%d" % i
                dispatched_cons_names.append(dispatched_cons_name)
                self.create_wrapper_for_nonoverloaded_constructor(class_decl,
                                             dispatched_cons_name, constructor)
            cons_code = Code.Code()
            self._create_overloaded_method_decl(cons_code,
                                                "__init__",
                                                dispatched_cons_names,
                                                constructors,
                                                False)
            self.code.add(cons_code)


    def create_wrapper_for_nonoverloaded_constructor(self, class_decl, py_name,
                                                           cons_decl):

        """ py_name ist name for constructor, as we dispatch overloaded
            constructors in __init__() the name of the method calling the
            c++ constructor is variable and given by `py_name`.

        """
        cons_code = Code.Code()

        call_args, cleanups, in_types =\
                         self._create_meth_decl_and_input_conversion(cons_code,
                                                                     py_name,
                                                                     cons_decl)

        # create instance of wrapped class
        call_args_str = ", ".join(call_args)
        name = self.cr.cy_decl_str(class_decl.type_)
        cons_code.add("""    self.inst = shared_ptr[$name](new $name($call_args_str))""", locals())

        for cleanup in cleanups:
            if not cleanup:
                continue
            if isinstance(cleanup, basestring):
                cleanup = "    %s" % cleanup
            meth_code.add(cleanup)

        # add cons code to overall code:
        self.code.add(cons_code)

    def create_special_eq_method(self, class_decl):
        meth_code = Code.Code()
        name = class_decl.name
        meth_code.add("""
           |def __richcmp__(self, other, op):
           |   if op != 2:
           |      raise Exception("richcmp for op %d not implmenented" % op)
           |   if not isinstance(other, $name):
           |       return False
           |   cdef $name other_casted = other
           |   cdef $name self_casted = self
           |   return deref(self_casted.inst.get()) == deref(other_casted.inst.get())
           """, locals())
        self.code.add(meth_code)

    def create_special_copy_method(self, class_decl):
        meth_code = Code.Code()
        name = class_decl.name
        meth_code.add("""def __copy__(self):
                        |   cdef $name rv = $name.__new__($name)
                        |   rv.inst = shared_ptr[_$name](new _$name(deref(self.inst.get())))
                        |   return rv
                        """, locals())
        self.code.add(meth_code)

    def create_cimports(self):
        self.create_std_cimports()
        for decl in self.decls:
            if isinstance(decl, ResolvedEnum):
                cpp_decl = decl.cpp_decl
            elif isinstance(decl, ResolvedClass):
                cpp_decl = decl.cpp_decl
            else:
                continue

            rel_pxd_path = os.path.relpath(cpp_decl.pxd_path, self.target_path)
            cython_dir_name = rel_pxd_path.replace(os.sep, ".")
            if os.altsep:
                cython_dir_name = cython_dir_name.replace(os.altsep, ".")
            import_from = decl.pxd_import_path
            self.code.add("from $from_ cimport $name as _$name",
                                       from_=import_from, name = cpp_decl.name)

    def create_std_cimports(self):
        self.code.add("""
           |from  libcpp.string  cimport string as libcpp_string
           |from  libcpp.vector  cimport vector as libcpp_vector
           |from  libcpp.pair    cimport pair as libcpp_pair
           |from smart_ptr cimport shared_ptr
           |from cython.operator cimport dereference as deref,
           + preincrement as inc, address as address""")

    def create_includes(self):
        self.code.add("""
                |cdef extern from "autowrap_tools.hpp":
                |    char * _cast_const_away(char *)
                """)


