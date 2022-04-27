import py_vec_holder
import numpy as np

holder = py_vec_holder.VecHolder()
holder.add(1.0)
holder.add(2.0)
holder.add(3.0)

view = np.asarray(holder)
assert np.allclose(view, [1.0, 2.0, 3.0])
assert view.base.obj is holder