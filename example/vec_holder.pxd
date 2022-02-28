from libcpp.vector cimport vector as libcpp_vector

cdef extern from "vec_holder.hpp":
    cdef cppclass VecHolder:
        # wrap-buffer-protocol:
        #    data_.data(),float,size()
        #
        libcpp_vector[float] data_

        VecHolder()
        VecHolder(libcpp_vector[float] data)

        size_t add(float value)
        float& operator[](size_t index) #wrap-upper-limit:size()
        size_t size()

