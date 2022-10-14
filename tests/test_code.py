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

import autowrap.Code


def test():
    Code = autowrap.Code.Code
    c = Code()
    c.add("def $name(x):", name="fun")

    inner = Code()
    inner.add(
        """if x
                + == 3:
                |    return
                + 4
              """
    )
    inner.add("else:")

    inner2 = Code()
    inner2.add(
        """return
                 + 2*x"""
    )

    inner.add(inner2)

    c.add(inner)

    result = c.render()
    assert len(c) == 5
    lines = [line.rstrip() for line in result.split("\n")]
    assert lines[0] == "def fun(x):", repr(lines[0])
    assert lines[1] == "    if x == 3:", repr(lines[1])
    assert lines[2] == "        return 4", repr(lines[2])
    assert lines[3] == "    else:", repr(lines[3])
    assert lines[4] == "        return 2*x", repr(lines[4])
    assert len(lines) == 5
