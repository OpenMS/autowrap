from __future__ import print_function
from __future__ import absolute_import

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
import autowrap

import os

test_files = os.path.join(os.path.dirname(__file__), "test_files")


def test_hash_functionality():
    """Test wrap-hash directive with both expression-based and std::hash approaches"""
    # Use a different module name than the pxd file to avoid Cython conflicts
    target = os.path.join(test_files, "generated", "hash_test_wrapper.pyx")

    include_dirs = autowrap.parse_and_generate_code(
        ["hash_test.pxd"], root=test_files, target=target, debug=True
    )

    hash_mod = autowrap.Utils.compile_and_import(
        "hash_test_wrapper",
        [target],
        include_dirs,
    )
    assert hash_mod.__name__ == "hash_test_wrapper"
    print(dir(hash_mod))

    # Test expression-based hash (old behavior - regression test)
    sub_test_expr_hash(hash_mod)

    # Test std::hash-based hash (new behavior)
    sub_test_std_hash(hash_mod)

    # Test templated class with std::hash
    sub_test_templated_hash(hash_mod)


def sub_test_expr_hash(hash_mod):
    """Test expression-based hash (old behavior, regression test)"""
    print("Testing expression-based hash (ExprHashClass)...")

    # Create instances with different values
    obj1 = hash_mod.ExprHashClass(42, b"test")
    obj2 = hash_mod.ExprHashClass(42, b"test")
    obj3 = hash_mod.ExprHashClass(100, b"other")

    # Test __hash__ is defined
    assert hasattr(obj1, "__hash__"), "ExprHashClass should have __hash__ method"

    # Test hash() works
    h1 = hash(obj1)
    h2 = hash(obj2)
    h3 = hash(obj3)

    # Equal objects should have same hash (same getValue())
    # Note: obj1 and obj2 have same value (42), so hash should be the same
    assert h1 == h2, f"Equal objects should have equal hash: {h1} != {h2}"

    # Different objects can have different hashes
    assert h3 != h1, f"Different values should have different hashes: {h3} == {h1}"

    # Test using in set
    s = {obj1, obj2}
    assert len(s) == 1, f"Set should dedupe equal objects, got {len(s)}"

    s.add(obj3)
    assert len(s) == 2, f"Set should have 2 different objects, got {len(s)}"

    # Test using as dict key
    d = {obj1: "first", obj3: "second"}
    assert len(d) == 2, f"Dict should have 2 entries, got {len(d)}"
    assert d[obj1] == "first"
    assert d[obj3] == "second"

    # Using obj2 (equal to obj1) should find the same entry
    assert d[obj2] == "first", "Equal object should find same dict entry"

    print("  Expression-based hash tests passed!")


def sub_test_std_hash(hash_mod):
    """Test std::hash-based hash (new behavior)"""
    print("Testing std::hash-based hash (StdHashClass)...")

    # Create instances with different values
    obj1 = hash_mod.StdHashClass(1, b"label1")
    obj2 = hash_mod.StdHashClass(1, b"label1")
    obj3 = hash_mod.StdHashClass(2, b"label2")

    # Test __hash__ is defined
    assert hasattr(obj1, "__hash__"), "StdHashClass should have __hash__ method"

    # Test hash() works
    h1 = hash(obj1)
    h2 = hash(obj2)
    h3 = hash(obj3)

    # Equal objects should have same hash
    assert h1 == h2, f"Equal objects should have equal hash: {h1} != {h2}"

    # Different objects should (likely) have different hashes
    # Note: Not guaranteed by hash contract, but expected for this implementation
    assert h3 != h1, f"Different values should have different hashes: {h3} == {h1}"

    # Test using in set
    s = {obj1, obj2}
    assert len(s) == 1, f"Set should dedupe equal objects, got {len(s)}"

    s.add(obj3)
    assert len(s) == 2, f"Set should have 2 different objects, got {len(s)}"

    # Test using as dict key
    d = {obj1: "first", obj3: "second"}
    assert len(d) == 2, f"Dict should have 2 entries, got {len(d)}"
    assert d[obj1] == "first"
    assert d[obj3] == "second"

    # Using obj2 (equal to obj1) should find the same entry
    assert d[obj2] == "first", "Equal object should find same dict entry"

    print("  std::hash-based hash tests passed!")


def sub_test_templated_hash(hash_mod):
    """Test templated class with std::hash"""
    print("Testing templated class with std::hash (TemplatedHashInt)...")

    # Create instances with different values
    obj1 = hash_mod.TemplatedHashInt(42)
    obj2 = hash_mod.TemplatedHashInt(42)
    obj3 = hash_mod.TemplatedHashInt(100)

    # Test __hash__ is defined
    assert hasattr(obj1, "__hash__"), "TemplatedHashInt should have __hash__ method"

    # Test hash() works
    h1 = hash(obj1)
    h2 = hash(obj2)
    h3 = hash(obj3)

    # Equal objects should have same hash
    assert h1 == h2, f"Equal objects should have equal hash: {h1} != {h2}"

    # Different objects should have different hashes
    assert h3 != h1, f"Different values should have different hashes: {h3} == {h1}"

    # Test using in set
    s = {obj1, obj2}
    assert len(s) == 1, f"Set should dedupe equal objects, got {len(s)}"

    s.add(obj3)
    assert len(s) == 2, f"Set should have 2 different objects, got {len(s)}"

    # Test using as dict key
    d = {obj1: "first", obj3: "second"}
    assert len(d) == 2, f"Dict should have 2 entries, got {len(d)}"

    print("  Templated class std::hash tests passed!")


def test_hash_consistency():
    """Test that hash values are consistent across multiple calls"""
    target = os.path.join(test_files, "generated", "hash_test_wrapper.pyx")

    include_dirs = autowrap.parse_and_generate_code(
        ["hash_test.pxd"], root=test_files, target=target, debug=True
    )

    hash_mod = autowrap.Utils.compile_and_import(
        "hash_test_wrapper",
        [target],
        include_dirs,
    )

    # Test expression-based hash consistency
    expr_obj = hash_mod.ExprHashClass(42, b"test")
    h1 = hash(expr_obj)
    h2 = hash(expr_obj)
    assert h1 == h2, "Hash should be consistent across calls"

    # Test std::hash consistency
    std_obj = hash_mod.StdHashClass(42, b"test")
    h3 = hash(std_obj)
    h4 = hash(std_obj)
    assert h3 == h4, "Hash should be consistent across calls"

    # Test templated hash consistency
    tmpl_obj = hash_mod.TemplatedHashInt(42)
    h5 = hash(tmpl_obj)
    h6 = hash(tmpl_obj)
    assert h5 == h6, "Hash should be consistent across calls"
