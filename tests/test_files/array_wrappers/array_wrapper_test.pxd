from libcpp.vector cimport vector as libcpp_vector

cdef extern from "array_wrapper_test.hpp":
    cdef cppclass ArrayWrapperTest:
        ArrayWrapperTest()
        
        # Return by value - suitable for owning wrapper
        libcpp_vector[double] getDataCopy(size_t size)
        
        # Return const reference - suitable for const view
        const libcpp_vector[double]& getConstRefData()
        
        # Return non-const reference - suitable for mutable view
        libcpp_vector[double]& getMutableRefData()
        
        # Float data
        const libcpp_vector[float]& getFloatData()
        libcpp_vector[float]& getMutableFloatData()
        
        # Int data
        const libcpp_vector[int]& getIntData()
        libcpp_vector[int]& getMutableIntData()
        
        # Compute sums (to verify modifications)
        double sumInternalData()
        float sumFloatData()
        int sumIntData()
