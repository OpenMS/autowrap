import pdb
from contextlib import contextmanager
import os.path
import sys
import re
from collections import defaultdict

from ConversionProvider import setup_converter_registry
from DeclResolver import (ResolvedClass, ResolvedEnum,
                          ResolvedMethod, ResolvedFunction)
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



def fixed_include_dirs():
    import pkg_resources
    boost = pkg_resources.resource_filename("autowrap", "data_files/boost")
    data = pkg_resources.resource_filename("autowrap", "data_files")
    return [boost, data]

class CodeGenerator(object):

    def __init__(self, instances, instance_mapping, target_path=None,
            extra_methods=None):

        if extra_methods is None:
            extra_methods = dict()

        self.extra_methods = extra_methods

        self.instances = sorted(instances, key = lambda decl: decl.name)
        self.target_path = os.path.abspath(target_path)
        self.target_dir  = os.path.dirname(self.target_path)

        self.classes = [d for d in instances if isinstance(d, ResolvedClass)]
        self.enums = [d for d in instances if isinstance(d, ResolvedEnum)]
        self.functions = [d for d in instances if isinstance(d,
                                                    ResolvedFunction)]

        self.instance_mapping = instance_mapping

        class_names = [c.name for c in self.classes]
        enum_names = [c.name for c in self.enums]

        self.cr = setup_converter_registry(self.classes,
                                           self.enums,
                                           instance_mapping)

        self.top_level_code = []

    def get_include_dirs(self):
        return fixed_include_dirs() + [self.pxd_dir]

    def setup_cimport_paths(self):

        pxd_dirs = set()
        for inst in self.classes + self.enums + self.functions:
            pxd_path = os.path.abspath(inst.cpp_decl.pxd_path)
            pxd_dir = os.path.dirname(pxd_path)
            pxd_dirs.add(pxd_dir)
            pxd_file = os.path.basename(pxd_path)
            inst.pxd_import_path, __ = os.path.splitext(pxd_file)

        assert len(pxd_dirs) == 1, \
                                  "pxd files must be located in same directory"

        self.pxd_dir = pxd_dirs.pop()


    def create_pyx_file(self, debug=False):
        self.setup_cimport_paths()
        self.create_cimports()
        self.create_includes()
        for inst in self.instances:
            if inst.wrap_ignore:
                continue
            if isinstance(inst, ResolvedEnum):
                self.create_wrapper_for_enum(inst)
            elif isinstance(inst, ResolvedClass):
                self.create_wrapper_for_class(inst)
            elif isinstance(inst, ResolvedFunction):
                self.create_wrapper_for_free_function(inst)
            else:
                raise Exception("can not create wrapper for %s "\
                                "(%s)" % (inst.__class__, inst))

        code = "\n\n".join(tl.render() for tl in self.top_level_code)

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
                annotations = method.cpp_decl.annotations
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
        code = Code.Code()
        code.add("cdef class $name:", name=decl.name)
        for (name, value) in decl.items:
            code.add("    $name = $value", name=name, value=value)


        self.top_level_code.append(code)

    def create_wrapper_for_class(self, cdcl):
        cname = cdcl.name
        cy_type = self.cr.cy_decl_str(cname)
        class_code = Code.Code()
        class_code.add("""
                         |cdef class $cname:
                         |    cdef shared_ptr[$cy_type] inst
                         |    def __dealloc__(self):
                         |         self.inst.reset()
                         """, locals())

        cons_created = False

        iterators, non_iter_methods = self.filterout_iterators(cdcl.methods)

        for (name, methods) in non_iter_methods.items():
            if name == cdcl.name:
                self.create_wrapper_for_constructor(cdcl, methods, class_code)
                cons_created = True
            else:
                self.create_wrapper_for_method(cdcl, name, methods, class_code)
        assert cons_created, "no constructor for %s created" % cname

        self._create_iter_methods(class_code, iterators)

        extra_methods_code = self.extra_methods.get(cname)
        if extra_methods_code:
            for extra_code in extra_methods_code:
                class_code.add(extra_code)

        self.top_level_code.append(class_code)

    def _create_iter_methods(self, class_code, iterators):
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

            class_code.add(meth_code)

    def _create_overloaded_method_decl(self, class_code, py_name,
                                      dispatched_m_names, methods, use_return):

        method_code = Code.Code()
        method_code.add("""def $py_name(self, *args):""", locals())

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
            method_code.add("""
                            |    $if_elif $check_expr:
                            |        $return_ self.$dispatched_m_name(*args)
                            """, locals())
            first_iteration = False

        method_code.add("""    else:
                        |           raise
                        + Exception('can not handle %s' % (args,))""")
        class_code.add(method_code)

    def create_wrapper_for_method(self, cdcl, cpp_name, methods, class_code):

        if cpp_name == "operator[]":
            assert len(methods) == 1, "overloaded operator[] not suppored"
            self.create_special_getitem_method(methods[0], class_code)
            return

        if cpp_name == "operator==":
            if len(methods) != 1:
                print "overloaded operator== not suppored"
            self.create_special_eq_method(cdcl, class_code)
            return


        if len(methods) == 1:
            self.create_wrapper_for_nonoverloaded_method(cdcl, cpp_name,
                                                         cpp_name, methods[0],
                                                         class_code)
        else:
            # TODO: what happens if two distinct c++ types as float, double
            # map to the same python type ??
            # -> 1) detection
            # -> 2) force method renaming
            dispatched_m_names = []
            for (i, method) in enumerate(methods):
                dispatched_m_name = "_%s_%d" % (cpp_name, i)
                dispatched_m_names.append(dispatched_m_name)
                self.create_wrapper_for_nonoverloaded_method(cdcl,
                                                             dispatched_m_name,
                                                             cpp_name,
                                                             method,
                                                             class_code
                                                             )

            self._create_overloaded_method_decl(class_code,
                                                cpp_name,
                                                dispatched_m_names,
                                                methods,
                                                True)

    def _create_fun_decl_and_input_conversion(self,
                                              code,
                                              py_name,
                                              method,
                                              is_free_fun=False):
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
        if not is_free_fun:
            py_signature_parts.insert(0, "self")
        py_signature = ", ".join(py_signature_parts)
        code.add("""def $py_name($py_signature):""", locals())

        # create code which convert python input args to c++ args of wrapped
        # method:
        for n, check in checks:
            code.add("    assert %s, 'arg %s invalid'" % (check, n))
        for conv_code in input_conversion_codes:
            code.add(conv_code)

        return call_args, cleanups, in_types

    def create_wrapper_for_nonoverloaded_method(self, cdcl, py_name, cpp_name,
            method, class_code):

        meth_code = Code.Code()

        call_args, cleanups, in_types =\
                         self._create_fun_decl_and_input_conversion(meth_code,
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

        out_vars = ["py_result"]
        if "ref-arg-out" in method.cpp_decl.annotations:
            out_ixs = map(int, method.cpp_decl.annotations["ref-arg-out"])
            for i, (type_, call_arg) in enumerate(zip(in_types, call_args)):
                if i in out_ixs:
                    to_py_code = self.cr.get(type_).output_conversion(type_,
                                                                    call_arg,
                                                                    "pyr_%d" %i)
                    out_vars.append("pyr_%d" % i)
                    if isinstance(to_py_code, basestring):
                        to_py_code = "    %s" % to_py_code
                    meth_code.add(to_py_code)

        for cleanup in reversed(cleanups):
            if not cleanup:
                continue
            if isinstance(cleanup, basestring):
                cleanup = "    %s" % cleanup
            meth_code.add(cleanup)

        to_py_code = out_converter.output_conversion(res_t, "_r", "py_result")

        if to_py_code is not None:  # for non void return value

            if isinstance(to_py_code, basestring):
                to_py_code = "    %s" % to_py_code
            meth_code.add(to_py_code)
            meth_code.add("    return %s" % (", ".join(out_vars)))

        class_code.add(meth_code)

    def create_wrapper_for_free_function(self, decl):
        fun_code = Code.Code()

        call_args, cleanups, in_types =\
                self._create_fun_decl_and_input_conversion(fun_code,
                                                           decl.name,
                                                           decl,
                                                           is_free_fun=True)

        call_args_str = ", ".join(call_args)
        cy_call_str = "_%s(%s)" % (decl.name, call_args_str)

        res_t = decl.result_type
        out_converter = self.cr.get(res_t)
        full_call_stmt = out_converter.call_method(res_t, cy_call_str)

        if isinstance(full_call_stmt, basestring):
            fun_code.add("""
                |    $full_call_stmt
                """, locals())
        else:
            fun_code.add(full_call_stmt)


        for cleanup in reversed(cleanups):
            if not cleanup:
                continue
            if isinstance(cleanup, basestring):
                cleanup = "    %s" % cleanup
            fun_code.add(cleanup)

        to_py_code = out_converter.output_conversion(res_t, "_r", "py_result")

        out_vars = ["py_result"]
        if to_py_code is not None:  # for non void return value

            if isinstance(to_py_code, basestring):
                to_py_code = "    %s" % to_py_code
            fun_code.add(to_py_code)
            fun_code.add("    return %s" % (", ".join(out_vars)))

        self.top_level_code.append(fun_code)


    def create_wrapper_for_constructor(self, class_decl, constructors, class_code):
        real_constructors = []
        for cons in constructors:
            if len(cons.arguments) == 1:
                (n, t), = cons.arguments
                if t.base_type == class_decl.name and t.is_ref:
                    self.create_special_copy_method(class_decl, class_code)
                    continue
            real_constructors.append(cons)

        if len(real_constructors) == 1:
            self.create_wrapper_for_nonoverloaded_constructor(class_decl,
                                              "__init__", real_constructors[0],
                                              class_code)
        else:
            dispatched_cons_names =[]
            for (i, constructor) in enumerate(real_constructors):
                dispatched_cons_name = "_init_%d" % i
                dispatched_cons_names.append(dispatched_cons_name)
                self.create_wrapper_for_nonoverloaded_constructor(class_decl,
                                             dispatched_cons_name, constructor,
                                             class_code)
            self._create_overloaded_method_decl(class_code,
                                                "__init__",
                                                dispatched_cons_names,
                                                constructors,
                                                False)

    def create_wrapper_for_nonoverloaded_constructor(self, class_decl, py_name,
                                                           cons_decl,
                                                           code):

        """ py_name ist name for constructor, as we dispatch overloaded
            constructors in __init__() the name of the method calling the
            c++ constructor is variable and given by `py_name`.

        """
        cons_code = Code.Code()

        call_args, cleanups, in_types =\
                         self._create_fun_decl_and_input_conversion(cons_code,
                                                                    py_name,
                                                                    cons_decl)

        # create instance of wrapped class
        call_args_str = ", ".join(call_args)
        name = class_decl.name
        cy_type = self.cr.cy_decl_str(name)
        cons_code.add("""    self.inst = shared_ptr[$cy_type](new $cy_type($call_args_str))""", locals())

        for cleanup in reversed(cleanups):
            if not cleanup:
                continue
            if isinstance(cleanup, basestring):
                cleanup = "    %s" % cleanup
            cons_code.add(cleanup)

        # add cons code to overall code:
        code.add(cons_code)

    def create_special_getitem_method(self, mdcl, class_code):
        meth_code = Code.Code()

        call_args, cleanups, in_types =\
                    self._create_fun_decl_and_input_conversion(meth_code,
                                                               "__getitem__",
                                                               mdcl)

        # call wrapped method and convert result value back to python

        call_args_str = ", ".join(call_args)
        cy_call_str = "deref(self.inst.get())[%s]" % call_args_str

        res_t = mdcl.result_type
        out_converter = self.cr.get(res_t)
        full_call_stmt = out_converter.call_method(res_t, cy_call_str)

        if isinstance(full_call_stmt, basestring):
            meth_code.add("""
                |    $full_call_stmt
                """, locals())
        else:
            meth_code.add(full_call_stmt)

        for cleanup in reversed(cleanups):
            if not cleanup:
                continue
            if isinstance(cleanup, basestring):
                cleanup = Code.Code().add(cleanup)
            meth_code.add(cleanup)

        out_var = "py_result"
        to_py_code = out_converter.output_conversion(res_t, "_r", out_var)
        if to_py_code is not None:  # for non void return value

            if isinstance(to_py_code, basestring):
                to_py_code = "    %s" % to_py_code
            meth_code.add(to_py_code)
            meth_code.add("    return $out_var", locals())

        class_code.add(meth_code)



    def create_special_eq_method(self, class_decl, class_code):
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
        class_code.add(meth_code)

    def create_special_copy_method(self, class_decl, class_code):
        meth_code = Code.Code()
        name = class_decl.name
        meth_code.add("""def __copy__(self):
                        |   cdef $name rv = $name.__new__($name)
                        |   rv.inst = shared_ptr[_$name](new _$name(deref(self.inst.get())))
                        |   return rv
                        """, locals())
        class_code.add(meth_code)

    def create_cimports(self):
        self.create_std_cimports()
        code = Code.Code()
        for decl in self.instances:
            if decl.__class__ in (ResolvedMethod, ResolvedFunction,
                                  ResolvedEnum, ResolvedClass):
                cpp_decl = decl.cpp_decl
                pxd_path = cpp_decl.pxd_path
                name = cpp_decl.name
            else:
                continue

            rel_pxd_path = os.path.relpath(pxd_path, self.target_path)
            cython_dir_name = rel_pxd_path.replace(os.sep, ".")
            if os.altsep:
                cython_dir_name = cython_dir_name.replace(os.altsep, ".")
            import_from = decl.pxd_import_path
            code.add("from $from_ cimport $name as _$name",
                                      from_=import_from, name=name)
        self.top_level_code.append(code)

    def create_std_cimports(self):
        code = Code.Code()
        code.add("""
                   |from  libcpp.string  cimport string as libcpp_string
                   |from  libcpp.vector  cimport vector as libcpp_vector
                   |from  libcpp.pair    cimport pair as libcpp_pair
                   |from  libcpp cimport bool
                   |from  libc.stdint  cimport *
                   |from  libc.stddef  cimport *
                   |from smart_ptr cimport shared_ptr
                   |cimport numpy as np
                   |import numpy as np
                   |from cython.operator cimport dereference as deref,
                   + preincrement as inc, address as address""")
        self.top_level_code.insert(0, code)

    def create_includes(self):
        code = Code.Code()
        code.add("""
                |cdef extern from "autowrap_tools.hpp":
                |    char * _cast_const_away(char *)
                """)

        self.top_level_code.insert(0, code)


