from extra cimport M_PI


    def super_get(self, int i):
        cdef _Holder[int] ih
        ih.set(i+1)
        return ih.get()

    def get_pi(self):
        return M_PI
