from __future__ import print_function
from __future__ import absolute_import

import types

import pytest

__license__ = """

Copyright (c) 2012-2014, Uwe Schmitt, ETH Zurich, all rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

Neither the name of the mineway GmbH nor the names of its contributors may be
used to endorse or promote products derived from this software without specific
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import autowrap.DeclResolver
import autowrap.CodeGenerator
import autowrap.PXDParser
import autowrap.Utils
import autowrap.Code
import autowrap.Main
import autowrap
import os
import math
import sys

test_files = os.path.join(os.path.dirname(__file__), "test_files")


def test_enums():
    """
    Test wrapping of C++ enums, including enums with the same name in different namespaces.

    This test demonstrates how autowrap handles:
    1. Scoped enums (enum class) from C++ mapped to Python Enum classes
    2. Enums with the same name in different namespaces (Foo::MyEnum vs Foo2::MyEnum)
    3. Type-safe enum validation (passing wrong enum type raises AssertionError)
    4. Enum documentation via wrap-doc annotation

    Pattern for wrapping namespaced enums in .pxd files:
        cpdef enum class Foo_MyEnum "Foo::MyEnum":
            # wrap-attach:
            #   Foo
            # wrap-as:
            #   MyEnum
            A
            B
            C

    This creates Foo.MyEnum in Python that maps to Foo::MyEnum in C++.

    See tests/test_files/enums.pxd for the full example.
    """
    target = os.path.join(test_files, "generated", "enums.pyx")

    include_dirs = autowrap.parse_and_generate_code(
        ["enums.pxd"], root=test_files, target=target, debug=True
    )

    mod = autowrap.Utils.compile_and_import(
        "enummodule",
        [
            target,
        ],
        include_dirs,
    )

    # Test 1: Enums with same name in different namespaces are both accessible
    # Foo.MyEnum and Foo2.MyEnum are separate enum types
    assert mod.Foo.MyEnum
    assert mod.Foo.MyEnum.B
    assert mod.Foo2.MyEnum
    assert mod.Foo2.MyEnum.D

    # Test 2: Enum documentation is preserved via wrap-doc
    foo = mod.Foo()
    my_enum = mod.Foo.MyEnum
    assert "Testing Enum documentation." in my_enum.__doc__

    # Test 3: Correct enum type is accepted
    myenum_a = mod.Foo.MyEnum.A
    assert foo.enumToInt(myenum_a) == 1

    # Test 4: Wrong enum type raises AssertionError (type-safe validation)
    # Even though MyEnum2.A has the same numeric value as MyEnum.A,
    # it's a different enum type and should be rejected
    myenum2_a = mod.Foo.MyEnum2.A
    with pytest.raises(AssertionError):
        foo.enumToInt(myenum2_a)

    # Test 5: Overload resolution works correctly for different enum types
    # The process() method is overloaded: process(MyEnum) and process(MyEnum2)
    # Python should dispatch to the correct overload based on enum type
    assert foo.process(mod.Foo.MyEnum.A) == b"MyEnum"
    assert foo.process(mod.Foo.MyEnum.B) == b"MyEnum"
    assert foo.process(mod.Foo.MyEnum2.A) == b"MyEnum2"
    assert foo.process(mod.Foo.MyEnum2.C) == b"MyEnum2"

    # Test 6: Overloaded method rejects wrong enum type from different namespace
    with pytest.raises(Exception):
        foo.process(mod.Foo2.MyEnum.A)


def test_number_conv():
    target = os.path.join(test_files, "generated", "number_conv.pyx")

    include_dirs = autowrap.parse_and_generate_code(
        ["number_conv.pxd"], root=test_files, target=target, debug=True
    )

    mod = autowrap.Utils.compile_and_import(
        "number_conv",
        [
            target,
        ],
        include_dirs,
    )

    mf = mod.add_max_float(0)
    mf2 = mod.add_max_float(mf)
    assert not math.isinf(mf2), "somehow overflow happened"

    repr_ = "%.13e" % mod.pass_full_precision(0.05)
    assert repr_.startswith("5.0000000000000"), "loss of precision during conversion: %s" % repr_

    inl = [0.05]
    outl = mod.pass_full_precision_vec(inl)

    repr_ = "%.13e" % inl[0]
    assert repr_.startswith("5.0000000000000"), "loss of precision during conversion: %s" % repr_

    repr_ = "%.13e" % outl[0]
    assert repr_.startswith("5.0000000000000"), "loss of precision during conversion: %s" % repr_


def test_shared_ptr():
    target = os.path.join(test_files, "shared_ptr_test.pyx")
    include_dirs = autowrap.CodeGenerator.fixed_include_dirs() + [test_files]
    m = autowrap.Utils.compile_and_import(
        "m",
        [
            target,
        ],
        include_dirs,
    )
    assert m.__name__ == "m"

    h1 = m.Holder(b"uwe")
    assert h1.count() == 1
    assert h1.size() == 3
    h2 = h1.getRef()
    h3 = h1.getCopy()
    assert h1.count() == 2
    assert h1.size() == 3

    assert h2.count() == 2
    assert h2.size() == 3

    assert h3.count() == 1
    assert h3.size() == 3

    h2.addX()
    assert h1.count() == 2
    assert h1.size() == 4

    assert h2.count() == 2
    assert h2.size() == 4

    assert h3.count() == 1
    assert h3.size() == 3

    del h2

    assert h1.count() == 1
    assert h1.size() == 4


def test_inherited():
    target = os.path.join(test_files, "generated", "inherited.pyx")
    include_dirs = autowrap.parse_and_generate_code(
        ["inherited.pxd"], root=test_files, target=target, debug=True
    )

    mod = autowrap.Utils.compile_and_import(
        "inheritedmodule",
        [
            target,
        ],
        include_dirs,
    )
    print(mod.__name__)
    i = mod.InheritedInt()
    assert i.foo() == 1
    assert i.bar() == 0
    assert i.getBase() == 1
    assert i.getBaseZ() == 0


def test_templated():
    target = os.path.join(test_files, "generated", "templated_wrapper.pyx")

    decls, instance_map = autowrap.parse(["templated.pxd"], root=test_files)

    co = autowrap.Code.Code()
    co.add(
        """def special(self):
             |    return "hi" """
    )

    methods = dict(T=co)

    include_dirs = autowrap.generate_code(
        decls, instance_map, target=target, debug=True, manual_code=methods
    )

    cpp_source = os.path.join(test_files, "templated.cpp")
    cpp_sources = []

    twrapped = autowrap.Utils.compile_and_import("twrapped", [target] + cpp_sources, include_dirs)
    os.remove(target)
    assert twrapped.__name__ == "twrapped"

    t = twrapped.T(42)
    assert t.special() == "hi"
    templated = twrapped.Templated(t)
    assert templated.get().get() == 42

    assert templated.passs(templated) == templated

    in_ = [templated, templated]
    assert templated.summup(in_) == 42 + 42
    __, __, tn = in_
    assert tn.get().get() == 11

    tn, __, __ = templated.reverse(in_)
    assert tn.get().get() == 11

    y = twrapped.Y()
    _, __, tn = y.passs(in_)
    assert tn.get().get() == 11

    # renamed attribute
    templated.f_att = 2
    assert templated.f_att == 2.0
    templated.f_att = 4
    assert templated.f_att == 4.0

    t13 = twrapped.T(13)
    templated._x = t13
    assert templated._x.get() == 13
    t17 = twrapped.T(17)
    templated._x = t17
    assert templated._x.get() == 17

    templated.xi = [t13, t17]
    assert templated.xi[0].get() == 13
    assert templated.xi[1].get() == 17

    templated.xi = [t17, t13]
    assert templated.xi[0].get() == 17
    assert templated.xi[1].get() == 13

    # Test second template (it adds 1 to everything)
    t_o = twrapped.T2(42)
    templated_o = twrapped.Templated_other(t_o)
    assert templated_o.get().get() == 43
    assert templated_o.passs(templated_o) == templated_o

    # Try out the adding 1 thing
    t11 = twrapped.T2(10)
    t12 = twrapped.T2(11)

    templated_o.xi = [t11, t12]
    assert templated_o.xi[0].get() == 11
    assert templated_o.xi[1].get() == 12

    # Test (wrap-attached) free functions = old way to wrap static functions (can only be called with class)
    assert twrapped.Templated.computeEight() == 8
    assert twrapped.Templated_other.computeEight() == 8

    # Test static functions (can be called with or without object)
    assert templated.computeSeven() == 7
    assert templated_o.computeSeven() == 7
    assert twrapped.Templated.computeSeven() == 7
    assert twrapped.Templated_other.computeSeven() == 7


def test_gil_unlock():
    target = os.path.join(test_files, "generated", "gil_testing_wrapper.pyx")
    include_dirs = autowrap.parse_and_generate_code(
        ["gil_testing.pxd"], root=test_files, target=target, debug=True
    )

    wrapped = autowrap.Utils.compile_and_import(
        "gtwrapped",
        [
            target,
        ],
        include_dirs,
    )
    g = wrapped.GilTesting(b"Jack")
    g.do_something(b"How are you?")
    assert g.get_greetings() == b"Hello Jack, How are you?"


def test_automatic_string_conversion():
    target = os.path.join(test_files, "generated", "libcpp_utf8_string_test.pyx")
    include_dirs = autowrap.parse_and_generate_code(
        ["libcpp_utf8_string_test.pxd"], root=test_files, target=target, debug=True
    )

    wrapped = autowrap.Utils.compile_and_import(
        "libcpp_utf8_string_wrapped",
        [
            target,
        ],
        include_dirs,
    )
    h = wrapped.Hello()

    input_bytes = b"J\xc3\xbcrgen"
    input_unicode = b"J\xc3\xbcrgen".decode("utf-8")

    expected = b"Hello J\xc3\xbcrgen"

    msg = h.get(input_bytes)
    assert isinstance(msg, bytes)
    assert msg == expected

    msg = h.get(input_unicode)
    assert isinstance(msg, bytes)
    assert msg == expected

    input_greet_bytes = b"Hall\xc3\xb6chen"
    input_greet_unicode = input_greet_bytes.decode("utf-8")

    expected = b"Hall\xc3\xb6chen J\xc3\xbcrgen"

    msg = h.get_more({"greet": input_greet_unicode, "name": input_bytes})
    assert isinstance(msg, bytes)
    assert msg == expected


def test_automatic_output_string_conversion():
    target = os.path.join(test_files, "generated", "libcpp_utf8_output_string_test.pyx")
    include_dirs = autowrap.parse_and_generate_code(
        ["libcpp_utf8_output_string_test.pxd"],
        root=test_files,
        target=target,
        debug=True,
    )

    wrapped = autowrap.Utils.compile_and_import(
        "libcpp_utf8_output_string_wrapped",
        [
            target,
        ],
        include_dirs,
    )
    h = wrapped.LibCppUtf8OutputStringTest()

    input_bytes = b"J\xc3\xbcrgen"
    input_unicode = b"J\xc3\xbcrgen".decode("utf-8")

    expected = b"Hello J\xc3\xbcrgen".decode("utf-8")
    expected_type = str
    if sys.version_info[0] < 3:
        expected_type = unicode

    msg = h.get(input_bytes)
    assert isinstance(msg, expected_type)
    assert msg == expected

    msg = h.get(input_unicode)
    assert isinstance(msg, expected_type)
    assert msg == expected


def test_wrap_ignore_foreign_cimports():
    """
    Test that wrap-ignored classes are not included in foreign cimports.

    This test verifies the fix for GitHub issue #194:
    When a class has the wrap-ignore annotation, other modules should not
    generate cimport statements for it, as wrap-ignored classes don't have
    corresponding pxd files.

    The test creates a multi-module scenario where one module has a
    wrap-ignored class, and verifies that the generated code in the other
    module does not attempt to cimport the wrap-ignored class.
    """
    import tempfile
    import shutil
    from autowrap.CodeGenerator import CodeGenerator
    from autowrap.DeclResolver import ResolvedClass

    # Create a temporary directory for generated files
    test_dir = tempfile.mkdtemp()
    try:
        # Parse the libcpp_test.pxd which has AbstractBaseClass (wrap-ignore)
        # and ABS_Impl1, ABS_Impl2 which inherit from it
        pxd_files = ["libcpp_test.pxd"]
        full_pxd_files = [os.path.join(test_files, f) for f in pxd_files]
        decls, instance_map = autowrap.parse(full_pxd_files, test_files)

        # Find the wrap-ignored class (AbstractBaseClass)
        wrap_ignored_classes = [d for d in decls if isinstance(d, ResolvedClass) and d.wrap_ignore]
        assert len(wrap_ignored_classes) > 0, "Expected at least one wrap-ignored class"

        # Set up a multi-module scenario
        # Module "module1" contains all the classes
        # Module "module2" is our target module that will generate foreign cimports
        module1_decls = decls
        module2_decls = []  # Empty module that needs to import from module1

        master_dict = {
            "module1": {"decls": module1_decls, "addons": [], "files": full_pxd_files},
            "module2": {"decls": module2_decls, "addons": [], "files": []},
        }

        # Generate code for module2 which would need foreign cimports from module1
        target = os.path.join(test_dir, "module2.pyx")
        cg = CodeGenerator(
            module2_decls,
            instance_map,
            pyx_target_path=target,
            all_decl=master_dict,
        )

        # Call create_foreign_cimports
        cg.create_foreign_cimports()

        # Check the generated code for foreign cimports
        generated_code = ""
        for code_block in cg.top_level_code:
            generated_code += code_block.render()

        # Verify that wrap-ignored classes are NOT in the cimports
        for ignored_class in wrap_ignored_classes:
            # The cimport line would look like: "from .module1 cimport ClassName"
            cimport_pattern = f"cimport {ignored_class.name}"
            assert cimport_pattern not in generated_code, (
                f"Wrap-ignored class '{ignored_class.name}' should not be in foreign cimports. "
                f"Generated code:\n{generated_code}"
            )

        # Verify that non-ignored classes ARE in the cimports
        non_ignored_classes = [d for d in decls if isinstance(d, ResolvedClass) and not d.wrap_ignore]
        for normal_class in non_ignored_classes:
            # Skip classes with no_pxd_import or wrap-attach
            if normal_class.no_pxd_import:
                continue
            if normal_class.cpp_decl.annotations.get("wrap-attach"):
                continue
            cimport_pattern = f"cimport {normal_class.name}"
            assert cimport_pattern in generated_code, (
                f"Non-ignored class '{normal_class.name}' should be in foreign cimports. "
                f"Generated code:\n{generated_code}"
            )

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_enum_class_forward_declaration(tmpdir):
    """
    Regression test: Scoped enums (enum class) must not generate cdef class forward declarations.

    Background
    ----------
    When wrapping a C++ scoped enum (enum class) for use across multiple Python extension
    modules, autowrap generates two files:

    1. A .pxd file (Cython declaration file) - used by other modules to cimport symbols
    2. A .pyx file (Cython implementation file) - contains the actual Python wrapper code

    The Bug
    -------
    Previously, autowrap generated a `cdef class` forward declaration in the .pxd file
    for ALL enums, including scoped enums. However, scoped enums are implemented as
    regular Python classes (inheriting from Python's Enum), not as Cython extension types.

    This caused a type mismatch:
    - .pxd file declared: `cdef class Status: pass`  (Cython extension type)
    - .pyx file defined:  `class Status(_PyEnum): ...` (Python class)

    Impact
    ------
    In multi-module scenarios, when Module B tries to use an enum defined in Module A:

        # In Module B's .pyx file
        from ModuleA cimport Status  # Expects cdef class, gets Python class

    This mismatch could cause Cython compilation errors or runtime issues.

    The Fix
    -------
    Only generate `cdef class` forward declarations for unscoped enums (which ARE
    implemented as cdef classes). Scoped enums don't need forward declarations in
    the .pxd file since they're regular Python classes.

    Test Setup
    ----------
    This test creates a two-module scenario:
    - EnumModule: Defines a scoped enum `Status` and a class `StatusHandler`
    - ConsumerModule: Uses the `Status` enum from EnumModule

    The test verifies that no `cdef class Status:` forward declaration is generated
    in the .pxd file when `Status` is a scoped enum implemented as a Python Enum class.
    """
    import shutil
    import subprocess

    test_dir = tmpdir.strpath
    enum_fwd_test_files = os.path.join(
        os.path.dirname(__file__), "test_files", "enum_forward_decl"
    )

    curdir = os.getcwd()
    os.chdir(test_dir)

    # Copy test files to temp directory
    for f in ["EnumModule.hpp", "EnumModule.pxd", "ConsumerModule.hpp", "ConsumerModule.pxd"]:
        src = os.path.join(enum_fwd_test_files, f)
        dst = os.path.join(test_dir, f)
        shutil.copy(src, dst)

    try:
        mnames = ["EnumModule", "ConsumerModule"]

        # Step 1: parse all header files
        pxd_files = ["EnumModule.pxd", "ConsumerModule.pxd"]
        full_pxd_files = [os.path.join(test_dir, f) for f in pxd_files]
        decls, instance_map = autowrap.parse(full_pxd_files, test_dir, num_processes=1)

        # Step 2: Perform mapping
        pxd_decl_mapping = {}
        for de in decls:
            tmp = pxd_decl_mapping.get(de.cpp_decl.pxd_path, [])
            tmp.append(de)
            pxd_decl_mapping[de.cpp_decl.pxd_path] = tmp

        masterDict = {}
        masterDict[mnames[0]] = {
            "decls": pxd_decl_mapping[full_pxd_files[0]],
            "addons": [],
            "files": [full_pxd_files[0]],
        }
        masterDict[mnames[1]] = {
            "decls": pxd_decl_mapping[full_pxd_files[1]],
            "addons": [],
            "files": [full_pxd_files[1]],
        }

        # Step 3: Generate Cython code for each module
        converters = []
        generated_pxd_content = {}
        generated_pyx_content = {}

        for modname in mnames:
            m_filename = "%s.pyx" % modname
            cimports, manual_code = autowrap.Main.collect_manual_code(masterDict[modname]["addons"])
            autowrap.Main.register_converters(converters)
            autowrap_include_dirs = autowrap.generate_code(
                masterDict[modname]["decls"],
                instance_map,
                target=m_filename,
                debug=True,
                manual_code=manual_code,
                extra_cimports=cimports,
                all_decl=masterDict,
                add_relative=True,
            )
            masterDict[modname]["inc_dirs"] = autowrap_include_dirs

            # Read generated files to check for issues
            pxd_path = "%s.pxd" % modname
            if os.path.exists(pxd_path):
                with open(pxd_path, "r") as f:
                    generated_pxd_content[modname] = f.read()
            with open(m_filename, "r") as f:
                generated_pyx_content[modname] = f.read()

        # Check for the bug: scoped enum should NOT have cdef class forward declaration
        # when it's implemented as a regular Python class (inheriting from _PyEnum)
        enum_module_pxd = generated_pxd_content.get("EnumModule", "")
        enum_module_pyx = generated_pyx_content.get("EnumModule", "")

        # Find if Status is defined as "class Status(_PyEnum)" in pyx
        has_python_enum_class = "class Status(_PyEnum)" in enum_module_pyx

        # Find if Status has "cdef class Status:" forward declaration in pxd
        # Use regex to match exact class name (avoid matching "cdef class StatusHandler")
        import re
        has_cdef_class_forward_decl = re.search(r"cdef class Status\s*:", enum_module_pxd) is not None

        # This is the bug: scoped enums should NOT have cdef class forward declarations
        # because they are implemented as regular Python classes (Enum subclasses)
        if has_python_enum_class and has_cdef_class_forward_decl:
            pytest.fail(
                "Bug detected: Scoped enum 'Status' has a 'cdef class' forward declaration in .pxd "
                "but is implemented as a regular Python 'class' (Enum subclass) in .pyx. "
                "This mismatch will cause Cython compilation failures in multi-module scenarios.\n\n"
                f"PXD content:\n{enum_module_pxd}\n\n"
                f"PYX content:\n{enum_module_pyx}"
            )

        # Step 4: Generate CPP code (this is where Cython compilation happens)
        # If the bug exists, this step should fail with a Cython error
        for modname in mnames:
            m_filename = "%s.pyx" % modname
            autowrap_include_dirs = masterDict[modname]["inc_dirs"]
            autowrap.Main.run_cython(
                inc_dirs=autowrap_include_dirs, extra_opts=None, out=m_filename
            )

        print("Test passed: No forward declaration mismatch detected")

    finally:
        os.chdir(curdir)


def test_create_foreign_enum_imports():
    """
    Test that create_foreign_enum_imports() generates correct Python imports for
    scoped enums used across multiple modules.

    This test verifies:
    1. Scoped enums WITH wrap-attach get '_Py' prefix (e.g., '_PyStatus')
    2. Scoped enums WITHOUT wrap-attach keep original name (e.g., 'Status')
    3. Unscoped enums are NOT imported (they use cimport via create_foreign_cimports)
    4. wrap-ignored enums are skipped
    5. Imports are added to top_level_pyx_code (for .pyx), not top_level_code (for .pxd)

    Background:
    -----------
    When autowrap splits classes across multiple output modules for parallel
    compilation, scoped enum classes (e.g., _PyPolarity, _PySpectrumType) may be
    defined in one module but used in isinstance() type assertions in another.

    Scoped enums are implemented as Python IntEnum subclasses and need regular
    Python imports. Unscoped enums are cdef classes and use Cython cimport.
    """
    import tempfile
    import shutil
    from autowrap.CodeGenerator import CodeGenerator
    from autowrap.DeclResolver import ResolvedEnum
    from autowrap.PXDParser import EnumDecl

    # Create a temporary directory for generated files
    test_dir = tempfile.mkdtemp()
    try:
        # Create mock EnumDecl objects for testing
        def make_enum_decl(name, scoped, annotations=None):
            """Helper to create mock EnumDecl objects."""
            if annotations is None:
                annotations = {}
            decl = EnumDecl(
                name=name,
                scoped=scoped,
                items=[("A", 0), ("B", 1)],
                annotations=annotations,
                pxd_path="/fake/path.pxd"
            )
            return decl

        # Create mock ResolvedEnum objects
        def make_resolved_enum(name, scoped, wrap_ignore=False, wrap_attach=None):
            """Helper to create mock ResolvedEnum objects."""
            annotations = {"wrap-ignore": wrap_ignore}
            if wrap_attach:
                annotations["wrap-attach"] = wrap_attach
            decl = make_enum_decl(name, scoped, annotations)
            resolved = ResolvedEnum(decl)
            resolved.pxd_import_path = "module1"
            return resolved

        # Test enums in module1 (source module)
        scoped_with_attach = make_resolved_enum("Status", scoped=True, wrap_attach="SomeClass")
        scoped_no_attach = make_resolved_enum("Priority", scoped=True, wrap_attach=None)
        unscoped_enum = make_resolved_enum("OldEnum", scoped=False)
        ignored_enum = make_resolved_enum("IgnoredEnum", scoped=True, wrap_ignore=True)

        module1_decls = [scoped_with_attach, scoped_no_attach, unscoped_enum, ignored_enum]

        # Set up multi-module scenario
        # module1 contains the enums, module2 needs to import them
        master_dict = {
            "module1": {"decls": module1_decls, "addons": [], "files": []},
            "module2": {"decls": [], "addons": [], "files": []},
        }

        # Create CodeGenerator for module2
        target = os.path.join(test_dir, "module2.pyx")
        cg = CodeGenerator(
            [],  # module2 has no decls of its own
            {},  # empty instance_map
            pyx_target_path=target,
            all_decl=master_dict,
        )

        # Call the method we're testing
        cg.create_foreign_enum_imports()

        # Get the generated code from top_level_pyx_code (NOT top_level_code)
        pyx_generated_code = ""
        for code_block in cg.top_level_pyx_code:
            pyx_generated_code += code_block.render()

        pxd_generated_code = ""
        for code_block in cg.top_level_code:
            pxd_generated_code += code_block.render()

        # Test 1: Scoped enum WITH wrap-attach should use _Py prefix
        assert "from module1 import _PyStatus" in pyx_generated_code, (
            f"Expected 'from module1 import _PyStatus' for scoped enum with wrap-attach. "
            f"Generated pyx code:\n{pyx_generated_code}"
        )

        # Test 2: Scoped enum WITHOUT wrap-attach should use original name
        assert "from module1 import Priority" in pyx_generated_code, (
            f"Expected 'from module1 import Priority' for scoped enum without wrap-attach. "
            f"Generated pyx code:\n{pyx_generated_code}"
        )

        # Test 3: Unscoped enum should NOT be imported (uses cimport instead)
        assert "OldEnum" not in pyx_generated_code, (
            f"Unscoped enum 'OldEnum' should not be in Python imports (uses cimport). "
            f"Generated pyx code:\n{pyx_generated_code}"
        )

        # Test 4: wrap-ignored enum should NOT be imported
        assert "IgnoredEnum" not in pyx_generated_code, (
            f"wrap-ignored enum 'IgnoredEnum' should not be in imports. "
            f"Generated pyx code:\n{pyx_generated_code}"
        )

        # Test 5: Imports should be in top_level_pyx_code, NOT top_level_code
        # (top_level_code goes to .pxd, top_level_pyx_code goes to .pyx)
        assert "_PyStatus" not in pxd_generated_code, (
            f"Enum Python imports should not be in top_level_code (pxd). "
            f"Generated pxd code:\n{pxd_generated_code}"
        )
        assert "Priority" not in pxd_generated_code or "cimport" in pxd_generated_code, (
            f"Enum Python imports should not be in top_level_code (pxd). "
            f"Generated pxd code:\n{pxd_generated_code}"
        )

        print("Test passed: create_foreign_enum_imports generates correct imports")

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_cross_module_scoped_enum_imports(tmpdir):
    """
    Integration test for cross-module scoped enum imports.

    This test verifies that create_foreign_enum_imports() correctly generates
    Python imports for scoped enums used across module boundaries:

    1. Scoped enum WITH wrap-attach (Task.TaskStatus):
       - Should generate: from .EnumProvider import _PyTaskStatus
       - Used in isinstance() checks as _PyTaskStatus

    2. Scoped enum WITHOUT wrap-attach (Priority):
       - Should generate: from .EnumProvider import Priority
       - Used in isinstance() checks as Priority

    The test:
    - Parses two modules: EnumProvider (defines enums) and EnumConsumer (uses enums)
    - Generates Cython code for both modules
    - Verifies EnumConsumer.pyx contains correct Python imports for both enum types
    - Runs Cython compilation to ensure the generated code is valid
    """
    import shutil
    import re

    test_dir = tmpdir.strpath
    enum_test_files = os.path.join(
        os.path.dirname(__file__), "test_files", "enum_cross_module"
    )

    curdir = os.getcwd()
    os.chdir(test_dir)

    # Copy test files to temp directory
    for f in ["EnumProvider.hpp", "EnumProvider.pxd", "EnumConsumer.hpp", "EnumConsumer.pxd"]:
        src = os.path.join(enum_test_files, f)
        dst = os.path.join(test_dir, f)
        shutil.copy(src, dst)

    try:
        mnames = ["EnumProvider", "EnumConsumer"]

        # Step 1: Parse all pxd files
        pxd_files = ["EnumProvider.pxd", "EnumConsumer.pxd"]
        full_pxd_files = [os.path.join(test_dir, f) for f in pxd_files]
        decls, instance_map = autowrap.parse(full_pxd_files, test_dir, num_processes=1)

        # Step 2: Map declarations to their source modules
        pxd_decl_mapping = {}
        for de in decls:
            tmp = pxd_decl_mapping.get(de.cpp_decl.pxd_path, [])
            tmp.append(de)
            pxd_decl_mapping[de.cpp_decl.pxd_path] = tmp

        masterDict = {}
        masterDict[mnames[0]] = {
            "decls": pxd_decl_mapping.get(full_pxd_files[0], []),
            "addons": [],
            "files": [full_pxd_files[0]],
        }
        masterDict[mnames[1]] = {
            "decls": pxd_decl_mapping.get(full_pxd_files[1], []),
            "addons": [],
            "files": [full_pxd_files[1]],
        }

        # Step 3: Generate Cython code for each module
        converters = []
        generated_pyx_content = {}

        for modname in mnames:
            m_filename = "%s.pyx" % modname
            cimports, manual_code = autowrap.Main.collect_manual_code(masterDict[modname]["addons"])
            autowrap.Main.register_converters(converters)
            autowrap_include_dirs = autowrap.generate_code(
                masterDict[modname]["decls"],
                instance_map,
                target=m_filename,
                debug=True,
                manual_code=manual_code,
                extra_cimports=cimports,
                all_decl=masterDict,
                add_relative=True,
            )
            masterDict[modname]["inc_dirs"] = autowrap_include_dirs

            # Read generated pyx file
            with open(m_filename, "r") as f:
                generated_pyx_content[modname] = f.read()

        # Step 4: Verify EnumConsumer.pyx has correct Python imports
        consumer_pyx = generated_pyx_content.get("EnumConsumer", "")

        # Test 1: Scoped enum WITH wrap-attach should be imported with _Py prefix
        # Task_TaskStatus has wrap-attach:Task, so it becomes _PyTask_TaskStatus in Python
        # (the _Py prefix is added to the full Cython enum name)
        assert "from .EnumProvider import _PyTask_TaskStatus" in consumer_pyx, (
            f"Expected 'from .EnumProvider import _PyTask_TaskStatus' for scoped enum with wrap-attach.\n"
            f"EnumConsumer.pyx content:\n{consumer_pyx}"
        )

        # Test 2: Scoped enum WITHOUT wrap-attach should be imported with original name
        assert "from .EnumProvider import Priority" in consumer_pyx, (
            f"Expected 'from .EnumProvider import Priority' for scoped enum without wrap-attach.\n"
            f"EnumConsumer.pyx content:\n{consumer_pyx}"
        )

        # Test 3: Verify isinstance checks use the correct enum class names
        # For wrap-attach enum: isinstance(s, _PyTask_TaskStatus)
        assert "isinstance(s, _PyTask_TaskStatus)" in consumer_pyx, (
            f"Expected isinstance check with _PyTask_TaskStatus for wrap-attach enum.\n"
            f"EnumConsumer.pyx content:\n{consumer_pyx}"
        )

        # For non-wrap-attach enum: isinstance(p, Priority)
        assert "isinstance(p, Priority)" in consumer_pyx, (
            f"Expected isinstance check with Priority for non-wrap-attach enum.\n"
            f"EnumConsumer.pyx content:\n{consumer_pyx}"
        )

        # Step 5: Run Cython compilation to verify the generated code is valid
        for modname in mnames:
            m_filename = "%s.pyx" % modname
            autowrap_include_dirs = masterDict[modname]["inc_dirs"]
            autowrap.Main.run_cython(
                inc_dirs=autowrap_include_dirs, extra_opts=None, out=m_filename
            )

        print("Test passed: Cross-module scoped enum imports work correctly")

    finally:
        os.chdir(curdir)
