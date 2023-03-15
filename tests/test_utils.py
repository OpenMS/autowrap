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


import autowrap.Utils


def test_hierarchy_detector0():
    dd = dict()
    dd[1] = [2]
    dd[2] = [1]
    assert autowrap.Utils.find_cycle(dd) == [2, 1]

    dd = dict()
    dd[1] = [2]
    assert autowrap.Utils.find_cycle(dd) is None


def test_hierarchy_detector1():
    dd = dict()
    dd[1] = [2, 3]
    dd[2] = [3]
    assert autowrap.Utils.find_cycle(dd) is None


def test_hierarchy_detector2():
    dd = dict()
    dd[1] = [2, 3]
    dd[2] = [3]
    dd[3] = [4]
    dd[4] = [2]
    assert autowrap.Utils.find_cycle(dd) == [4, 2, 3]


def test_hierarchy_detector3():
    dd = dict()
    dd[1] = [2]
    dd[2] = [3, 4]
    dd[3] = [5]
    assert autowrap.Utils.find_cycle(dd) is None


def test_nested_mapping_flattening():
    from autowrap.Types import CppType

    B = CppType.from_string("B")
    Y = CppType.from_string("Y")
    Z = CppType.from_string("Z")
    CXD = CppType.from_string("C[X,D]")

    mapping = dict(A=B, B=CXD, C=Z, D=Y)
    autowrap.Utils.flatten(mapping)
    assert str(mapping["A"]) == "Z[X,Y]"
    assert str(mapping["B"]) == "Z[X,Y]"
    assert str(mapping["C"]) == "Z"
    assert str(mapping["D"]) == "Y"
