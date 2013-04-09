

# for backwards compatibility with python 2.6 we use our own implementation
# of an OrderedDictionary, which is not feature complete but simple and
# sufficient for our uses

class OrderKeepingDictionary(object):

    def __init__(self):
        self._dd  = dict()
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





