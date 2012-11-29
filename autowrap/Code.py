import string, re

class Code(string.Template):

    def render(self, **kw):
        res = self.substitute(**kw)
        res = re.sub(" *\|", "", res)
        res = re.sub("\n+ *\+", "", res)
        return res
        
