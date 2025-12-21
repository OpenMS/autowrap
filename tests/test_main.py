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


def test_from_command_line():
    import os

    old_dir = os.path.abspath(os.getcwd())
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(script_dir, "test_files"))
    args = [
        "pxds/*.pxd",
        "--out",
        "generated/out.pyx",
        "--addons=/addons",
        "--converters=converters",
    ]
    from autowrap.Main import _main

    try:
        _main(args)
    finally:
        os.chdir(old_dir)


def test_run():
    from autowrap.Main import run
    from autowrap.Utils import compile_and_import

    import glob
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))

    pxds = glob.glob(script_dir + "/test_files/pxds/*.pxd")
    assert pxds

    addons = glob.glob(script_dir + "/test_files/addons/*.pyx")
    assert addons

    converters = [script_dir + "/test_files/converters"]

    extra_includes = [script_dir + "/test_files/includes"]
    includes = run(pxds, addons, converters, script_dir + "/test_files/generated/out.pyx", extra_includes)

    mod = compile_and_import("out", [script_dir + "/test_files/generated/out.cpp"], includes)

    ih = mod.IntHolder()
    ih.set_(3)
    assert ih.get() == 3

    # automatic IntHolder <-> int conversions:
    b = mod.B()
    b.set_(7)
    assert b.get() == 7

    # test iter wrapping
    (ih,) = list(b)
    assert ih.get() == 7

    # manually generated method
    assert b.super_get(3) == 4

    # uses extra cimport for M_PI
    assert abs(b.get_pi() - 3.141) < 0.001

    # type without automatic conversion:
    c = mod.C()
    fh = mod.FloatHolder(2.0)
    c.set_(fh)
    assert c.get().get() == 2.0

    (fh,) = list(c)
    assert fh.get() == 2.0

    # manual class:
    assert mod.CC.cc == 3

    assert mod.SharedPtrTestInt().sum_values(ih, ih) == 14

    mod.SharedPtrTestFloat().set_inner_value(fh, 12.0)
    assert fh.get() == 12.0
