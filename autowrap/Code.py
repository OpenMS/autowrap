import string, re

class Code(object):

    def __init__(self):
        self.content = []

    def extend(self, other):
        # keeps identation
        self.content.extend(other.content)

    def add(self,  what, *a, **kw):
        # may increase indent !
        if a:  # if dict given
            kw.update(a[0])
        if "self" in kw:
            del kw["self"] # self causes problems in substitude call below
        if isinstance(what, basestring):
            #print repr(what)
            try:
                res = string.Template(what).substitute(**kw)
            except:
                print what
                print kw
                raise
            res = re.sub("^[ ]*\n[ ]*\|", "", res)     # ltrim first line
            res = re.sub("\n+ *\+", "", res)
            for line in re.split("\n *\|", res):
                self.content.append(line.rstrip())
        else:
            self.content.append(what)
        return self

    def _render(self, _indent=""):
        result = []
        for content in self.content:
            if isinstance(content, basestring):
                result.append(_indent + content)
            else:
                for line in content._render(_indent = _indent + "    "):
                    result.append(line)
        return result

    def render(self):
        return "\n".join(self._render())
