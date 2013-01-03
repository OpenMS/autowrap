import string, re

class Code(object):

    def __init__(self):
        self.content = []

    def add(self,  what, *a, **kw):
        if a:  # if dict given
            kw.update(a[0])
        if "self" in kw:
            del kw["self"] # self causes problems in substitude call below
        if isinstance(what, basestring):
            #print repr(what)
            res = string.Template(what).substitute(**kw)
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
