import glob
import PXDParser

for p in glob.glob("pxd/*.pxd"):
    cpp_clz = PXDParser.parse(p)
    break

