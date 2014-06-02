# encoding: utf-8

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


# for backwards compatibility with python 2.6 we use our own implementation
# of an OrderedDictionary, which is not feature complete but simple and
# sufficient for our uses

class OrderKeepingDictionary(object):

    def __init__(self):
        self._dd = dict()
        self._keys = []

    def __setitem__(self, k, v):
        if k not in self._keys:
            self._keys.append(k)
        self._dd[k] = v

    def __getitem__(self, k):
        return self._dd[k]

    def update(self):
        raise NotImplementedError("update not implemented")

    def iterkeys(self):
        for k in self._keys:
            yield k

    __iter__ = iterkeys

    def itervalues(self):
        for k in self._keys:
            yield self._dd[k]

    def iteritems(self):
        for k in self._keys:
            yield (k, self._dd[k])

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self.iteritems())

    def get(self, k, default=None):
        return self._dd.get(k, default)

    def setdefault(self, k, default):
        if k not in self._keys:
            self._keys.append(k)
        return self._dd.setdefault(k, default)

    def __delitem__(self, k):
        raise NotImplementedError("__delitem__ not implemented")

    def __len__(self):
        return len(self._dd)
