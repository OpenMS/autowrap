# encoding: utf-8

from __future__ import print_function
from __future__ import annotations
from typing import Union, List

__license__ = """

Copyright (c) 2012-2014, Uwe Schmitt, all rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

Neither the name of the ETH Zurich nor the names of its contributors may be
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

import string
import re

try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


class Code(object):
    def __init__(self):
        self.content: List[Union[Code, str]] = []

    def __len__(self):
        return sum(len(c) if isinstance(c, Code) else 1 for c in self.content)

    def extend(self, other: Code) -> None:
        # keeps indentation
        self.content.extend(other.content)

    def addRawList(self, lst):
        # keeps indentation
        self.content.extend(lst)

    def add(self, what: Union[str, bytes, Code], *a, **kw) -> Code:
        # may increase indent!
        if a:  # if dict given
            kw.update(a[0])
        if "self" in kw:
            del kw["self"]  # self causes problems in substitute call below
        if isinstance(what, basestring):
            try:
                res = string.Template(what).substitute(**kw)
            except ValueError:
                print(what)
                print(kw)
                raise
            res = re.sub(r"^[ ]*\n[ ]*\|", "", res)  # ltrim first line
            res = re.sub(r"\n+ *\+", "", res)
            for line in re.split(r"\n *\|", res):
                self.content.append(line.rstrip())
        else:  # TODO do we really want to allow adding "ANYTHING" e.g. even None?
            self.content.append(what)
        return self

    def _render(self, _indent="") -> List[str]:
        result = []
        for content in self.content:
            if isinstance(content, basestring):
                result.append(_indent + content)
            else:
                newindent = _indent + " " * 4
                for line in content._render(_indent=newindent):
                    result.append(line)
        return result

    def render(self, indent=0) -> str:
        i = " " * indent
        return "\n".join(self._render(_indent=i))
